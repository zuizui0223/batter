#!/usr/bin/env python3
"""Post-primary latent dimensionality of cross-environment movement policy."""
from __future__ import annotations

import collections
import importlib.util
import json
import math
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"rhino_configuration_identity_primary_v1.py")
P=importlib.util.module_from_spec(spec); spec.loader.exec_module(P)

PCA_DIMS=list(range(1,9))
ID_DIMS=list(range(1,5))
NPERM=9999
MIN_VALID=9500

def standardized_rows():
    traj=P.load_rhino()
    ft=[r for r in traj if r["feature_valid"]]
    envs=sorted(set(r["env"] for r in ft))
    rows=[]
    stats={}
    for e in envs:
        rr=[r for r in ft if r["env"]==e]
        M=np.vstack([r["features"] for r in rr]).astype(float)
        mu=M.mean(axis=0); sd=M.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):
            raise RuntimeError(f"bad feature SD env={e}")
        stats[e]=(mu,sd)
        for r in rr:
            q=dict(r)
            q["z8"]=(r["features"]-mu)/sd
            rows.append(q)
    if len(rows)!=45:
        raise RuntimeError(f"expected 45 rows, got {len(rows)}")
    return rows,envs

def env_label_sets(rows,envs):
    return {e:sorted(set(r["bat"] for r in rows if r["env"]==e)) for e in envs}

def observed_mapping(rows,envs):
    return {(e,b):b for e in envs for b in sorted(set(r["bat"] for r in rows if r["env"]==e))}

def perm_mapping(labelsets,rng):
    mp={}
    for e,labs in labelsets.items():
        perm=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,perm):
            mp[(e,old)]=str(new)
    return mp

def assigned_label(r,mapping):
    return mapping[(r["env"],r["bat"])]

def pca_basis(trainX):
    mu=trainX.mean(axis=0)
    X=trainX-mu
    U,S,Vt=np.linalg.svd(X,full_matrices=False)
    var=(S*S)/(len(X)-1)
    ratio=var/var.sum()
    return mu,Vt,ratio

def identity_basis(rows,target_env,mapping):
    train=[r for r in rows if r["env"]!=target_env]
    envs=sorted(set(r["env"] for r in train))
    labels=sorted(set(assigned_label(r,mapping) for r in train))
    env_cent={}
    for e in envs:
        for b in labels:
            vals=[r["z8"] for r in train if r["env"]==e and assigned_label(r,mapping)==b]
            if vals:
                env_cent[(e,b)]=np.mean(np.vstack(vals),axis=0)
    bat_cent=[]
    used=[]
    for b in labels:
        vals=[env_cent[(e,b)] for e in envs if (e,b) in env_cent]
        if len(vals)>=2:
            bat_cent.append(np.mean(np.vstack(vals),axis=0))
            used.append(b)
    if len(used)<5:
        return None
    M=np.vstack(bat_cent)
    grand=M.mean(axis=0)
    C=M-grand
    U,S,Vt=np.linalg.svd(C,full_matrices=False)
    return grand,Vt,S,used

def project_pca_folds(rows,envs):
    folds={}
    for e in envs:
        train=[r for r in rows if r["env"]!=e]
        X=np.vstack([r["z8"] for r in train])
        mu,Vt,ratio=pca_basis(X)
        coords=[]
        for r in rows:
            coords.append((r["z8"]-mu)@Vt.T)
        folds[e]={"scores":coords,"basis":Vt,"ratio":ratio}
    return folds

def k_stat(rows,envs,mapping,coord_by_fold,d):
    by_bat=collections.defaultdict(list)
    for e0 in envs:
        coords=coord_by_fold[e0]
        train_envs=[e for e in envs if e!=e0]
        # Equal-environment centroid for each assigned label.
        labels=sorted(set(assigned_label(r,mapping) for r in rows))
        cent={}
        presence=collections.defaultdict(list)
        for b in labels:
            per=[]
            for e in train_envs:
                idx=[i for i,r in enumerate(rows) if r["env"]==e and assigned_label(r,mapping)==b]
                if idx:
                    per.append(np.mean(np.vstack([coords[i][:d] for i in idx]),axis=0))
                    presence[b].append(e)
            if len(per)>=2:
                cent[b]=np.mean(np.vstack(per),axis=0)
        if len(cent)<3:
            return None,{}
        for i,r in enumerate(rows):
            if r["env"]!=e0: continue
            b=assigned_label(r,mapping)
            if b not in cent: continue
            donors=[bb for bb in cent if bb!=b]
            if len(donors)<2: continue
            z=coords[i][:d]
            ds=float(np.linalg.norm(z-cent[b]))
            do=float(np.mean([np.linalg.norm(z-cent[bb]) for bb in donors]))
            by_bat[b].append(do-ds)
    indiv={b:float(np.mean(v)) for b,v in by_bat.items() if v}
    if len(indiv)<3:
        return None,indiv
    return float(np.mean(list(indiv.values()))),indiv

def identity_coord_folds(rows,envs,mapping):
    folds={}
    loadings={}
    for e0 in envs:
        obj=identity_basis(rows,e0,mapping)
        if obj is None:
            return None,None
        grand,Vt,S,used=obj
        coords=[(r["z8"]-grand)@Vt.T for r in rows]
        folds[e0]=coords
        loadings[e0]=Vt
    return folds,loadings

def summarize_loadings(vts,maxpc):
    out={}
    for pc in range(maxpc):
        vals=[]
        for e,Vt in vts.items():
            if pc<Vt.shape[0]:
                vals.append(Vt[pc]**2)
        A=np.vstack(vals)
        out[str(pc+1)]={
          "median_squared_loading":np.median(A,axis=0).tolist(),
          "min_squared_loading":np.min(A,axis=0).tolist(),
          "max_squared_loading":np.max(A,axis=0).tolist(),
        }
    return out

def run_pca(rows,envs):
    folds=project_pca_folds(rows,envs)
    obsmap=observed_mapping(rows,envs)
    obs={}
    variance={}
    for d in PCA_DIMS:
        st,bm=k_stat(rows,envs,obsmap,{e:folds[e]["scores"] for e in envs},d)
        if st is None: raise RuntimeError(f"PCA observed support d={d}")
        cum=[float(np.sum(folds[e]["ratio"][:d])) for e in envs]
        variance[str(d)]={
          "median_cumulative_explained":float(np.median(cum)),
          "min_cumulative_explained":float(np.min(cum)),
          "max_cumulative_explained":float(np.max(cum)),
        }
        obs[d]=(st,bm)
    results={}
    labelsets=env_label_sets(rows,envs)
    for d in PCA_DIMS:
        rng=np.random.default_rng(202610042281+d)
        null=[]
        coords={e:folds[e]["scores"] for e in envs}
        for _ in range(NPERM):
            mp=perm_mapping(labelsets,rng)
            st,_=k_stat(rows,envs,mp,coords,d)
            if st is not None:null.append(st)
        a=np.asarray(null,float)
        st,bm=obs[d]
        p=float((1+np.sum(a>=st))/(1+len(a))) if len(a) else math.nan
        pos=sum(v>0 for v in bm.values()); frac=pos/len(bm)
        sufficient=bool(len(a)>=MIN_VALID and st>0 and p<=.05 and frac>=.70)
        results[str(d)]={
          "K":float(st),"bat_means":bm,"positive_bats":pos,
          "n_bats":len(bm),"positive_fraction":frac,
          "valid_permutations":int(len(a)),"requested_permutations":NPERM,
          "seed":202610042281+d,
          "null_mean":float(np.mean(a)) if len(a) else None,
          "null_q025":float(np.quantile(a,.025)) if len(a) else None,
          "null_q975":float(np.quantile(a,.975)) if len(a) else None,
          "p_one_sided":p,"sufficient":sufficient,
        }
    mind=min([int(d) for d,r in results.items() if r["sufficient"]],default=None)
    vts={e:folds[e]["basis"] for e in envs}
    return {
      "minimal_sufficient_dimension":mind,
      "dimensions":results,
      "variance":variance,
      "loading_summary_pc1_pc3":summarize_loadings(vts,3),
    }

def run_identity(rows,envs):
    obsmap=observed_mapping(rows,envs)
    obsfolds,obsload=identity_coord_folds(rows,envs,obsmap)
    if obsfolds is None:raise RuntimeError("identity observed fold support")
    obs={}
    for d in ID_DIMS:
        st,bm=k_stat(rows,envs,obsmap,obsfolds,d)
        if st is None:raise RuntimeError(f"identity observed d={d}")
        obs[d]=(st,bm)
    results={}
    labelsets=env_label_sets(rows,envs)
    for d in ID_DIMS:
        rng=np.random.default_rng(202610042291+d)
        null=[]
        for _ in range(NPERM):
            mp=perm_mapping(labelsets,rng)
            folds,_=identity_coord_folds(rows,envs,mp)
            if folds is None:continue
            st,_=k_stat(rows,envs,mp,folds,d)
            if st is not None:null.append(st)
        a=np.asarray(null,float)
        st,bm=obs[d]
        p=float((1+np.sum(a>=st))/(1+len(a))) if len(a) else math.nan
        pos=sum(v>0 for v in bm.values());frac=pos/len(bm)
        sufficient=bool(len(a)>=MIN_VALID and st>0 and p<=.05 and frac>=.70)
        results[str(d)]={
          "K":float(st),"bat_means":bm,"positive_bats":pos,
          "n_bats":len(bm),"positive_fraction":frac,
          "valid_permutations":int(len(a)),"requested_permutations":NPERM,
          "seed":202610042291+d,
          "null_mean":float(np.mean(a)) if len(a) else None,
          "null_q025":float(np.quantile(a,.025)) if len(a) else None,
          "null_q975":float(np.quantile(a,.975)) if len(a) else None,
          "p_one_sided":p,"sufficient":sufficient,
        }
    mind=min([int(d) for d,r in results.items() if r["sufficient"]],default=None)
    return {
      "minimal_sufficient_dimension":mind,
      "dimensions":results,
      "loading_summary_axis1_axis4":summarize_loadings(obsload,4),
    }

def main():
    rows,envs=standardized_rows()
    out={
      "contract":"LATENT_POLICY_DIMENSIONALITY_CONTRACT_V1.md",
      "status":"POST_PRIMARY_MECHANISM_DIAGNOSTIC",
      "species":"Rhinolophus nippon",
      "n_trajectories":len(rows),
      "environments":envs,
      "feature_names":P.FEATURES,
      "D1_unsupervised_PCA":run_pca(rows,envs),
      "D2_training_only_identity_subspace":run_identity(rows,envs),
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
