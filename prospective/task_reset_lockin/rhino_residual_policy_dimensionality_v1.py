#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("L",HERE/"latent_policy_dimensionality_v1.py")
L=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(L)

NPERM=9999
MIN_VALID=9500

def k_selected(rows,envs,mapping,coord_by_fold,indices):
    # Reuse the same K architecture as L.k_stat, but select arbitrary axes.
    import collections
    by_bat=collections.defaultdict(list)
    for e0 in envs:
        coords=coord_by_fold[e0]
        train_envs=[e for e in envs if e!=e0]
        labels=sorted(set(L.assigned_label(r,mapping) for r in rows))
        cent={}
        for b in labels:
            per=[]
            for e in train_envs:
                idx=[i for i,r in enumerate(rows) if r["env"]==e and L.assigned_label(r,mapping)==b]
                if idx:
                    per.append(np.mean(np.vstack([coords[i][indices] for i in idx]),axis=0))
            if len(per)>=2:
                cent[b]=np.mean(np.vstack(per),axis=0)
        if len(cent)<3:
            return None,{}
        for i,r in enumerate(rows):
            if r["env"]!=e0: continue
            b=L.assigned_label(r,mapping)
            if b not in cent: continue
            donors=[bb for bb in cent if bb!=b]
            if len(donors)<2: continue
            z=np.asarray(coords[i][indices],float)
            ds=float(np.linalg.norm(z-cent[b]))
            do=float(np.mean([np.linalg.norm(z-cent[bb]) for bb in donors]))
            by_bat[b].append(do-ds)
    indiv={b:float(np.mean(v)) for b,v in by_bat.items() if v}
    if len(indiv)<3:
        return None,indiv
    return float(np.mean(list(indiv.values()))),indiv

def summarize(obs,bm,null,seed):
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs))/(1+len(a))) if len(a) else math.nan
    pos=sum(v>0 for v in bm.values())
    return {
      "K":float(obs),"bat_means":bm,
      "positive_bats":pos,"n_bats":len(bm),"positive_fraction":pos/len(bm),
      "valid_permutations":int(len(a)),"requested_permutations":NPERM,
      "seed":seed,"null_mean":float(a.mean()) if len(a) else None,
      "null_q025":float(np.quantile(a,.025)) if len(a) else None,
      "null_q975":float(np.quantile(a,.975)) if len(a) else None,
      "p_one_sided":p,
      "supported":bool(len(a)>=MIN_VALID and obs>0 and p<=.05 and pos/len(bm)>=.70)
    }

def run_pca(rows,envs):
    folds=L.project_pca_folds(rows,envs)
    coords={e:folds[e]["scores"] for e in envs}
    obsmap=L.observed_mapping(rows,envs)
    ls=L.env_label_sets(rows,envs)
    out={}
    for end in range(2,9):
        inds=np.arange(1,end,dtype=int)  # PC2 ... PC_end, zero indexed
        obs,bm=k_selected(rows,envs,obsmap,coords,inds)
        if obs is None: raise RuntimeError(f"PCA residual observed support end={end}")
        rng=np.random.default_rng(20261008000+end)
        null=[]
        for _ in range(NPERM):
            mp=L.perm_mapping(ls,rng)
            q,_=k_selected(rows,envs,mp,coords,inds)
            if q is not None:null.append(q)
        out[f"PC2_to_PC{end}"]=summarize(obs,bm,null,20261008000+end)
    return out

def run_identity(rows,envs):
    obsmap=L.observed_mapping(rows,envs)
    obsfolds,_=L.identity_coord_folds(rows,envs,obsmap)
    if obsfolds is None: raise RuntimeError("identity observed folds")
    ls=L.env_label_sets(rows,envs)
    out={}
    for end in range(2,5):
        inds=np.arange(1,end,dtype=int)
        obs,bm=k_selected(rows,envs,obsmap,obsfolds,inds)
        if obs is None: raise RuntimeError(f"identity residual observed support end={end}")
        rng=np.random.default_rng(20261008020+end)
        null=[]
        for _ in range(NPERM):
            mp=L.perm_mapping(ls,rng)
            folds,_=L.identity_coord_folds(rows,envs,mp)
            if folds is None:continue
            q,_=k_selected(rows,envs,mp,folds,inds)
            if q is not None:null.append(q)
        out[f"Axis2_to_Axis{end}"]=summarize(obs,bm,null,20261008020+end)
    return out

def main():
    rows,envs=L.standardized_rows()
    pca=run_pca(rows,envs)
    ident=run_identity(rows,envs)
    supported=[k for k,v in {**pca,**ident}.items() if v["supported"]]
    out={
      "contract":"RHINO_RESIDUAL_POLICY_DIMENSIONALITY_CONTRACT_V1.md",
      "status":"POST_PRIMARY_MATHEMATICAL_STRUCTURE_DIAGNOSTIC",
      "species":"Rhinolophus nippon",
      "n_trajectories":len(rows),
      "R1_PCA_residual":pca,
      "R2_identity_residual":ident,
      "supported_residual_sets":supported,
      "interpretation":"ADDITIONAL_STABLE_DIMENSIONS_BEYOND_AXIS1" if supported else "AXIS1_APPROXIMATELY_EXHAUSTIVE"
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
