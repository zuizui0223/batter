#!/usr/bin/env python3
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("R",HERE/"geometry_beyond_theta_v1.py")
R=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(R)

PCA_DIMS=list(range(1,9))
ID_DIMS=list(range(1,5))
NPERM=9999
MIN_VALID=9500

def labelsets(rows,envs):
    return {e:sorted(set(r["bat"] for r in rows if r["env"]==e)) for e in envs}

def idmap(ls):
    return {(e,b):b for e,labs in ls.items() for b in labs}

def permap(ls,rng):
    mp={}
    for e,labs in ls.items():
        p=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,p): mp[(e,old)]=str(new)
    return mp

def lab(r,mp):
    return mp[(r["env"],r["bat"])]

def pca_coord_folds(rows,envs,resid):
    folds={}
    ratios={}
    for e0 in envs:
        ix=[i for i,r in enumerate(rows) if r["env"]!=e0]
        X=np.vstack([resid[e0][i] for i in ix]).astype(float)
        mu=X.mean(axis=0); Xc=X-mu
        _,s,Vt=np.linalg.svd(Xc,full_matrices=False)
        ratio=(s*s)/np.sum(s*s)
        folds[e0]=[(np.asarray(resid[e0][i])-mu)@Vt.T for i in range(len(rows))]
        ratios[e0]=ratio
    return folds,ratios

def identity_coord_folds(rows,envs,resid,mp):
    folds={}
    for e0 in envs:
        train_envs=[e for e in envs if e!=e0]
        labels=sorted(set(lab(r,mp) for r in rows if r["env"]!=e0))
        cent=[]
        used=[]
        for b in labels:
            per=[]
            for e in train_envs:
                ix=[i for i,r in enumerate(rows) if r["env"]==e and lab(r,mp)==b]
                if ix: per.append(np.mean(np.vstack([resid[e0][i] for i in ix]),axis=0))
            if len(per)>=2:
                cent.append(np.mean(np.vstack(per),axis=0)); used.append(b)
        if len(used)<5: return None
        C=np.vstack(cent)
        grand=C.mean(axis=0)
        _,_,Vt=np.linalg.svd(C-grand,full_matrices=False)
        folds[e0]=[(np.asarray(resid[e0][i])-grand)@Vt.T for i in range(len(rows))]
    return folds

def kstat(rows,envs,coords,mp,d):
    per=collections.defaultdict(list)
    for e0 in envs:
        train_envs=[e for e in envs if e!=e0]
        labels=sorted(set(lab(r,mp) for r in rows))
        cent={}
        for b in labels:
            ev=[]
            for e in train_envs:
                ix=[i for i,r in enumerate(rows) if r["env"]==e and lab(r,mp)==b]
                if ix: ev.append(np.mean(np.vstack([coords[e0][i][:d] for i in ix]),axis=0))
            if len(ev)>=2: cent[b]=np.mean(np.vstack(ev),axis=0)
        if len(cent)<3: return None,{}
        for i,r in enumerate(rows):
            if r["env"]!=e0:continue
            b=lab(r,mp)
            if b not in cent:continue
            donors=[bb for bb in cent if bb!=b]
            if len(donors)<2:continue
            z=np.asarray(coords[e0][i][:d],float)
            ds=float(np.linalg.norm(z-cent[b]))
            do=float(np.mean([np.linalg.norm(z-cent[bb]) for bb in donors]))
            per[b].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in per.items() if v}
    if len(bm)<3:return None,bm
    return float(np.mean(list(bm.values()))),bm

def summarize(obs,bm,null,seed):
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs))/(1+len(a)))
    pos=sum(v>0 for v in bm.values())
    return {
      "K":float(obs),"bat_means":bm,"positive_bats":pos,"n_bats":len(bm),
      "positive_fraction":pos/len(bm),"requested_permutations":NPERM,
      "valid_permutations":len(a),"seed":seed,"null_mean":float(a.mean()),
      "null_q025":float(np.quantile(a,.025)),"null_q975":float(np.quantile(a,.975)),
      "p_one_sided":p,
      "sufficient":bool(len(a)>=MIN_VALID and obs>0 and p<=.05 and pos/len(bm)>=.70)
    }

def run_d1(rows,envs,resid,ls):
    coords,ratios=pca_coord_folds(rows,envs,resid)
    obsmap=idmap(ls); out={}; var={}
    for d in PCA_DIMS:
        obs,bm=kstat(rows,envs,coords,obsmap,d)
        if obs is None:raise RuntimeError(f"D1 observed support d={d}")
        rng=np.random.default_rng(20261007960+d)
        null=[]
        for _ in range(NPERM):
            q,_=kstat(rows,envs,coords,permap(ls,rng),d)
            if q is not None:null.append(q)
        out[str(d)]=summarize(obs,bm,null,20261007960+d)
        cum=[float(np.sum(ratios[e][:d])) for e in envs]
        var[str(d)]={"median_cumulative_explained":float(np.median(cum)),
                     "min":float(np.min(cum)),"max":float(np.max(cum))}
    mind=min([int(k) for k,v in out.items() if v["sufficient"]],default=None)
    return {"minimal_sufficient_dimension":mind,"dimensions":out,"variance":var}

def run_d2(rows,envs,resid,ls):
    obsmap=idmap(ls)
    obscoords=identity_coord_folds(rows,envs,resid,obsmap)
    if obscoords is None:raise RuntimeError("D2 observed support")
    observed={}
    for d in ID_DIMS:
        observed[d]=kstat(rows,envs,obscoords,obsmap,d)
    out={}
    for d in ID_DIMS:
        obs,bm=observed[d]
        rng=np.random.default_rng(20261007980+d)
        null=[]
        for _ in range(NPERM):
            mp=permap(ls,rng)
            coords=identity_coord_folds(rows,envs,resid,mp)
            if coords is None:continue
            q,_=kstat(rows,envs,coords,mp,d)
            if q is not None:null.append(q)
        out[str(d)]=summarize(obs,bm,null,20261007980+d)
    mind=min([int(k) for k,v in out.items() if v["sufficient"]],default=None)
    return {"minimal_sufficient_dimension":mind,"dimensions":out}

def main():
    rows,envs,_=R.prepare()
    resid,_=R.residual_folds(rows,envs)
    ls=labelsets(rows,envs)
    out={
      "status":"POST_PRIMARY_MATHEMATICAL_STRUCTURE_DIAGNOSTIC",
      "contract":"RESIDUAL_GEOMETRY_DIMENSIONALITY_CONTRACT_V1.md",
      "species":"Rhinolophus nippon",
      "n_trajectories":len(rows),
      "D1_residual_PCA":run_d1(rows,envs,resid,ls),
      "D2_residual_identity_subspace":run_d2(rows,envs,resid,ls),
      "reference_residual_geometry_K":0.45399404566326673
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
