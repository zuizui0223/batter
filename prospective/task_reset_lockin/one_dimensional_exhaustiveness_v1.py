#!/usr/bin/env python3
from __future__ import annotations

import collections
import importlib.util
import json
import math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("L",HERE/"latent_policy_dimensionality_v1.py")
L=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(L)

NPERM=9999
MIN_VALID=9500
SEEDS={"flight":20261008301,"pca":20261008302,"identity":20261008303}

def candidate_targets(rows,envs,mapping):
    presence=collections.defaultdict(set)
    for r in rows:
        presence[L.assigned_label(r,mapping)].add(r["env"])
    labels=sorted(presence)
    targets=[]
    for i,r in enumerate(rows):
        b=L.assigned_label(r,mapping); e=r["env"]
        if len([x for x in presence[b] if x!=e])<2: continue
        donors=[]
        for j in labels:
            if j==b: continue
            if len([x for x in presence[j] if x!=e])>=2: donors.append(j)
        if len(donors)>=2: targets.append(i)
    return targets

def fold_stat(rows,envs,mapping,fold_coords):
    per=collections.defaultdict(list)
    targets=candidate_targets(rows,envs,mapping)
    for e0 in envs:
        coords=fold_coords[e0]
        train_envs=[e for e in envs if e!=e0]
        labels=sorted(set(L.assigned_label(r,mapping) for r in rows))
        cent={}
        for b in labels:
            per_env=[]
            for e in train_envs:
                ix=[i for i,r in enumerate(rows)
                    if r["env"]==e and L.assigned_label(r,mapping)==b]
                if ix:
                    per_env.append(np.mean(np.vstack([coords[i] for i in ix]),axis=0))
            if len(per_env)>=2:
                cent[b]=np.mean(np.vstack(per_env),axis=0)
        for i in targets:
            r=rows[i]
            if r["env"]!=e0: continue
            b=L.assigned_label(r,mapping)
            if b not in cent: continue
            donors=[bb for bb in cent if bb!=b]
            if len(donors)<2: continue
            z=coords[i]
            ds=float(np.linalg.norm(z-cent[b]))
            do=float(np.mean([np.linalg.norm(z-cent[bb]) for bb in donors]))
            per[b].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in per.items() if v}
    if len(bm)<3:return None,bm
    return float(np.mean(list(bm.values()))),bm

def orth_basis(u):
    u=np.asarray(u,float)
    u=u/np.linalg.norm(u)
    _,_,Vt=np.linalg.svd(u.reshape(1,-1),full_matrices=True)
    return Vt[1:].T

def fixed_flight_folds(rows,envs):
    u=np.array([.5,.5,.5,.5,0,0,0,0],float)
    Q=orth_basis(u)
    coords=[np.asarray(r["z8"])@Q for r in rows]
    return {e:coords for e in envs}

def pca_residual_folds(rows,envs):
    folds={}
    for e0 in envs:
        train=np.vstack([r["z8"] for r in rows if r["env"]!=e0])
        mu=train.mean(axis=0)
        X=train-mu
        _,_,Vt=np.linalg.svd(X,full_matrices=False)
        Q=orth_basis(Vt[0])
        folds[e0]=[(np.asarray(r["z8"])-mu)@Q for r in rows]
    return folds

def identity_residual_folds(rows,envs,mapping):
    folds={}
    for e0 in envs:
        obj=L.identity_basis(rows,e0,mapping)
        if obj is None:return None
        grand,Vt,S,used=obj
        Q=orth_basis(Vt[0])
        folds[e0]=[(np.asarray(r["z8"])-grand)@Q for r in rows]
    return folds

def summarize(obs,bm,null,seed):
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs))/(1+len(a))) if len(a) else math.nan
    pos=sum(v>0 for v in bm.values())
    return {
      "K":float(obs),"bat_means":bm,"positive_bats":pos,"n_bats":len(bm),
      "positive_fraction":pos/len(bm),
      "requested_permutations":NPERM,"valid_permutations":int(len(a)),
      "seed":seed,
      "null_mean":float(np.mean(a)) if len(a) else None,
      "null_q025":float(np.quantile(a,.025)) if len(a) else None,
      "null_q975":float(np.quantile(a,.975)) if len(a) else None,
      "p_one_sided":p,
      "supported":bool(len(a)>=MIN_VALID and obs>0 and p<=.05 and pos/len(bm)>=.70)
    }

def run_fixed(rows,envs,labelsets):
    mp=L.observed_mapping(rows,envs)
    folds=fixed_flight_folds(rows,envs)
    obs,bm=fold_stat(rows,envs,mp,folds)
    rng=np.random.default_rng(SEEDS["flight"]); null=[]
    for _ in range(NPERM):
        pm=L.perm_mapping(labelsets,rng)
        q,_=fold_stat(rows,envs,pm,folds)
        if q is not None:null.append(q)
    return summarize(obs,bm,null,SEEDS["flight"])

def run_pca(rows,envs,labelsets):
    mp=L.observed_mapping(rows,envs)
    folds=pca_residual_folds(rows,envs)
    obs,bm=fold_stat(rows,envs,mp,folds)
    rng=np.random.default_rng(SEEDS["pca"]); null=[]
    for _ in range(NPERM):
        pm=L.perm_mapping(labelsets,rng)
        q,_=fold_stat(rows,envs,pm,folds)
        if q is not None:null.append(q)
    return summarize(obs,bm,null,SEEDS["pca"])

def run_identity(rows,envs,labelsets):
    mp=L.observed_mapping(rows,envs)
    folds=identity_residual_folds(rows,envs,mp)
    if folds is None:raise RuntimeError("observed identity residual support")
    obs,bm=fold_stat(rows,envs,mp,folds)
    rng=np.random.default_rng(SEEDS["identity"]); null=[]
    for _ in range(NPERM):
        pm=L.perm_mapping(labelsets,rng)
        pf=identity_residual_folds(rows,envs,pm)
        if pf is None:continue
        q,_=fold_stat(rows,envs,pm,pf)
        if q is not None:null.append(q)
    return summarize(obs,bm,null,SEEDS["identity"])

def main():
    rows,envs=L.standardized_rows()
    if len(rows)!=45:raise RuntimeError(f"row drift {len(rows)}")
    ls=L.env_label_sets(rows,envs)
    out={
      "status":"POST_PRIMARY_MATHEMATICAL_STRUCTURE_DIAGNOSTIC",
      "contract":"ONE_DIMENSIONAL_EXHAUSTIVENESS_CONTRACT_V1.md",
      "species":"Rhinolophus nippon",
      "n_trajectories":len(rows),
      "R1_after_fixed_FlightIntensity":run_fixed(rows,envs,ls),
      "R2_after_training_PCA1":run_pca(rows,envs,ls),
      "R3_after_training_identity_axis":run_identity(rows,envs,ls)
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
