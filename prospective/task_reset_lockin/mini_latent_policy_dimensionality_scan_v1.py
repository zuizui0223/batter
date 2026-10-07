#!/usr/bin/env python3
from __future__ import annotations
import collections
import importlib.util
import json
import math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("M",HERE/"cross_species_policy_axis_v1.py")
M=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(M)

PCA_DIMS=list(range(1,9))
ID_DIMS=list(range(1,4))
NPERM=9999
MIN_VALID=9500

def rows_envs():
    rows=M.mini_standardized()
    if len(rows)!=19:
        raise RuntimeError(f"expected 19 rows, got {len(rows)}")
    envs=sorted(set(r["env"] for r in rows))
    return rows,envs

def labelsets(rows,envs):
    return {e:sorted(set(r["bat"] for r in rows if r["env"]==e)) for e in envs}

def identity_mapping(ls):
    return {(e,b):b for e,labs in ls.items() for b in labs}

def perm_mapping(ls,rng):
    mp={}
    for e,labs in ls.items():
        perm=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,perm):
            mp[(e,old)]=str(new)
    return mp

def assigned(r,mapping):
    return mapping[(r["env"],r["bat"])]

def pca_folds(rows,envs):
    folds={}
    for e0 in envs:
        train=[r for r in rows if r["env"]!=e0]
        X=np.vstack([r["z8"] for r in train]).astype(float)
        mu=X.mean(axis=0)
        Xc=X-mu
        _,s,Vt=np.linalg.svd(Xc,full_matrices=False)
        ratio=(s*s)/np.sum(s*s)
        scores=[(np.asarray(r["z8"])-mu)@Vt.T for r in rows]
        folds[e0]={"scores":scores,"basis":Vt,"ratio":ratio}
    return folds

def identity_basis(rows,envs,target,mapping):
    train_envs=[e for e in envs if e!=target]
    labs=sorted(set(assigned(r,mapping) for r in rows if r["env"]!=target))
    bat_cent=[]
    used=[]
    for b in labs:
        per=[]
        for e in train_envs:
            vals=[r["z8"] for r in rows if r["env"]==e and assigned(r,mapping)==b]
            if vals:
                per.append(np.mean(np.vstack(vals),axis=0))
        if len(per)>=2:
            bat_cent.append(np.mean(np.vstack(per),axis=0))
            used.append(b)
    if len(used)<4:
        return None
    B=np.vstack(bat_cent)
    grand=B.mean(axis=0)
    _,s,Vt=np.linalg.svd(B-grand,full_matrices=False)
    return grand,Vt,s,used

def identity_folds(rows,envs,mapping):
    folds={}
    bases={}
    for e0 in envs:
        obj=identity_basis(rows,envs,e0,mapping)
        if obj is None:
            return None,None
        grand,Vt,s,used=obj
        folds[e0]=[(np.asarray(r["z8"])-grand)@Vt.T for r in rows]
        bases[e0]=Vt
    return folds,bases

def k_stat(rows,envs,mapping,coords_by_fold,d):
    perbat=collections.defaultdict(list)
    for e0 in envs:
        coords=coords_by_fold[e0]
        train_envs=[e for e in envs if e!=e0]
        labs=sorted(set(assigned(r,mapping) for r in rows))
        cent={}
        for b in labs:
            per=[]
            for e in train_envs:
                ix=[i for i,r in enumerate(rows) if r["env"]==e and assigned(r,mapping)==b]
                if ix:
                    per.append(np.mean(np.vstack([coords[i][:d] for i in ix]),axis=0))
            if len(per)>=2:
                cent[b]=np.mean(np.vstack(per),axis=0)
        if len(cent)<3:
            continue
        for i,r in enumerate(rows):
            if r["env"]!=e0:
                continue
            b=assigned(r,mapping)
            if b not in cent:
                continue
            donors=[bb for bb in cent if bb!=b]
            if len(donors)<2:
                continue
            z=np.asarray(coords[i][:d],float)
            ds=float(np.linalg.norm(z-cent[b]))
            do=float(np.mean([np.linalg.norm(z-cent[bb]) for bb in donors]))
            perbat[b].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in perbat.items() if v}
    if len(bm)<3:
        return None,bm
    return float(np.mean(list(bm.values()))),bm

def summarize(obs,bm,null,seed):
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs))/(1+len(a))) if len(a) else math.nan
    pos=sum(v>0 for v in bm.values())
    sufficient=bool(
        len(a)>=MIN_VALID and obs>0 and p<=.05 and pos>=3
    )
    return {
        "K":float(obs),
        "bat_means":bm,
        "positive_bats":pos,
        "n_bats":len(bm),
        "positive_fraction":pos/len(bm),
        "requested_permutations":NPERM,
        "valid_permutations":int(len(a)),
        "seed":seed,
        "null_mean":float(np.mean(a)) if len(a) else None,
        "null_q025":float(np.quantile(a,.025)) if len(a) else None,
        "null_q975":float(np.quantile(a,.975)) if len(a) else None,
        "p_one_sided":p,
        "sufficient":sufficient
    }

def run_d1(rows,envs):
    folds=pca_folds(rows,envs)
    ls=labelsets(rows,envs)
    obsmap=identity_mapping(ls)
    coords={e:folds[e]["scores"] for e in envs}
    out={}
    variance={}
    for d in PCA_DIMS:
        obs,bm=k_stat(rows,envs,obsmap,coords,d)
        if obs is None:
            raise RuntimeError(f"D1 observed support d={d}")
        rng=np.random.default_rng(20261007800+d)
        null=[]
        for _ in range(NPERM):
            q,_=k_stat(rows,envs,perm_mapping(ls,rng),coords,d)
            if q is not None:
                null.append(q)
        out[str(d)]=summarize(obs,bm,null,20261007800+d)
        cum=[float(np.sum(folds[e]["ratio"][:d])) for e in envs]
        variance[str(d)]={
            "median_cumulative_explained":float(np.median(cum)),
            "min_cumulative_explained":float(np.min(cum)),
            "max_cumulative_explained":float(np.max(cum))
        }
    mind=min([int(k) for k,v in out.items() if v["sufficient"]],default=None)
    return {"minimal_sufficient_dimension":mind,"dimensions":out,"variance":variance}

def run_d2(rows,envs):
    ls=labelsets(rows,envs)
    obsmap=identity_mapping(ls)
    obsfolds,_=identity_folds(rows,envs,obsmap)
    if obsfolds is None:
        raise RuntimeError("D2 observed fold support")
    out={}
    obs_cache={}
    for d in ID_DIMS:
        obs,bm=k_stat(rows,envs,obsmap,obsfolds,d)
        if obs is None:
            raise RuntimeError(f"D2 observed support d={d}")
        obs_cache[d]=(obs,bm)
    for d in ID_DIMS:
        rng=np.random.default_rng(20261007820+d)
        null=[]
        for _ in range(NPERM):
            mp=perm_mapping(ls,rng)
            folds,_=identity_folds(rows,envs,mp)
            if folds is None:
                continue
            q,_=k_stat(rows,envs,mp,folds,d)
            if q is not None:
                null.append(q)
        obs,bm=obs_cache[d]
        out[str(d)]=summarize(obs,bm,null,20261007820+d)
    mind=min([int(k) for k,v in out.items() if v["sufficient"]],default=None)
    return {"minimal_sufficient_dimension":mind,"dimensions":out}

def main():
    rows,envs=rows_envs()
    out={
        "status":"POST_PRIMARY_EXPLORATORY_DIMENSIONALITY_DIAGNOSTIC",
        "contract":"MINI_LATENT_POLICY_DIMENSIONALITY_SCAN_CONTRACT_V1.md",
        "species":"Miniopterus fuliginosus",
        "n_trajectories":len(rows),
        "environments":envs,
        "D1_unsupervised_PCA":run_d1(rows,envs),
        "D2_training_only_identity_subspace":run_d2(rows,envs),
        "references":{
            "previous_PCA1_K":-0.1688,
            "previous_PCA1_p":0.2529,
            "full8_primary_K":-0.013597525318187484,
            "full8_primary_p":0.1687
        }
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
