#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, math
from collections import defaultdict
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location("P",HERE/"rhino_configuration_identity_primary_v1.py")
P=importlib.util.module_from_spec(sp); sp.loader.exec_module(P)
sg=importlib.util.spec_from_file_location("G",HERE/"geometry_only_policy_v1.py")
G=importlib.util.module_from_spec(sg); sg.loader.exec_module(G)

DIMS=[1,2,3,4]; B=9999; SEED=20261007951

def rows():
    traj=P.load_rhino()
    out=[]
    for r in traj:
        gf=G.geometry_features(r)
        if r["feature_valid"] and gf is not None:
            q=dict(r); q["x16"]=np.r_[np.asarray(r["features"],float),np.asarray(gf,float)]
            out.append(q)
    if len(out)!=45: raise RuntimeError(f"expected 45 rows got {len(out)}")
    envs=sorted(set(r["env"] for r in out))
    zrows=[]
    for e in envs:
        rr=[r for r in out if r["env"]==e]
        M=np.vstack([r["x16"] for r in rr])
        mu=M.mean(axis=0); sd=M.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0): raise RuntimeError(f"bad sd env={e}")
        for r,z in zip(rr,(M-mu)/sd):
            q=dict(r); q["z16"]=z; zrows.append(q)
    return zrows,envs

def labelsets(rs,envs):
    return {e:sorted(set(r["bat"] for r in rs if r["env"]==e)) for e in envs}
def idmap(ls): return {(e,b):b for e,l in ls.items() for b in l}
def permap(ls,rng):
    m={}
    for e,labs in ls.items():
        p=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,p): m[(e,old)]=str(new)
    return m
def lab(r,m): return m[(r["env"],r["bat"])]

def fold_coords(rs,envs,m):
    folds={}
    for e0 in envs:
        tr=[r for r in rs if r["env"]!=e0]
        labels=sorted(set(lab(r,m) for r in tr))
        cents=[]; used=[]
        for b in labels:
            ev=[]
            for e in envs:
                if e==e0: continue
                vv=[r["z16"] for r in tr if r["env"]==e and lab(r,m)==b]
                if vv: ev.append(np.mean(np.vstack(vv),axis=0))
            if len(ev)>=2:
                cents.append(np.mean(np.vstack(ev),axis=0)); used.append(b)
        if len(used)<5: return None
        C=np.vstack(cents); grand=C.mean(axis=0)
        _,_,Vt=np.linalg.svd(C-grand,full_matrices=False)
        folds[e0]={"coords":np.vstack([(r["z16"]-grand)@Vt.T for r in rs]),"Vt":Vt}
    return folds

def stat(rs,envs,m,folds,d):
    per=defaultdict(list)
    for e0 in envs:
        C=folds[e0]["coords"]
        labels=sorted(set(lab(r,m) for r in rs))
        cent={}
        for b in labels:
            ev=[]
            for e in envs:
                if e==e0: continue
                ix=[i for i,r in enumerate(rs) if r["env"]==e and lab(r,m)==b]
                if ix: ev.append(np.mean(C[ix,:d],axis=0))
            if len(ev)>=2: cent[b]=np.mean(np.vstack(ev),axis=0)
        for i,r in enumerate(rs):
            if r["env"]!=e0: continue
            b=lab(r,m)
            if b not in cent: continue
            donors=[bb for bb in cent if bb!=b]
            if len(donors)<2: continue
            z=C[i,:d]
            ds=float(np.linalg.norm(z-cent[b]))
            do=float(np.mean([np.linalg.norm(z-cent[bb]) for bb in donors]))
            per[b].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in per.items() if v}
    return (float(np.mean(list(bm.values()))),bm) if len(bm)>=3 else (None,bm)

def main():
    rs,envs=rows(); ls=labelsets(rs,envs); obsmap=idmap(ls)
    f=fold_coords(rs,envs,obsmap)
    obs={}
    for d in DIMS:
        k,bm=stat(rs,envs,obsmap,f,d)
        obs[d]={"K":k,"bat_means":bm,"positive_bats":sum(v>0 for v in bm.values())}
    rng=np.random.default_rng(SEED); mx=[]
    for _ in range(B):
        m=permap(ls,rng); ff=fold_coords(rs,envs,m)
        if ff is None: continue
        ks=[]
        for d in DIMS:
            k,_=stat(rs,envs,m,ff,d)
            if k is not None and math.isfinite(k): ks.append(k)
        if ks: mx.append(max(ks))
    a=np.asarray(mx,float)
    out={"status":"POST_PRIMARY_MATHEMATICAL_STRUCTURE_DIAGNOSTIC","n_trajectories":len(rs),"permutations":len(a),"seed":SEED,"dimensions":{}}
    for d in DIMS:
        q=obs[d]; p=float((1+np.sum(a>=q["K"]))/(1+len(a)))
        sup=bool(q["K"]>0 and p<=.05 and q["positive_bats"]>=4 and len(q["bat_means"])==5)
        out["dimensions"][str(d)]={**q,"adjusted_p_maxT":p,"supported":sup}
    out["minimal_supported_dimension"]=min([d for d in DIMS if out["dimensions"][str(d)]["supported"]],default=None)
    # descriptive loadings from observed training folds
    load={}
    names=P.FEATURES+G.FEATURES
    for ax in range(4):
        A=np.vstack([f[e]["Vt"][ax]**2 for e in envs])
        load[str(ax+1)]={n:float(v) for n,v in zip(names,np.median(A,axis=0))}
    out["median_squared_loadings_by_axis"]=load
    print(json.dumps(out,indent=2))
if __name__=="__main__": main()
