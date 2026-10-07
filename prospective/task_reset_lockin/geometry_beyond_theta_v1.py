#!/usr/bin/env python3
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent

spec=importlib.util.spec_from_file_location("G",HERE/"geometry_only_policy_v1.py")
G=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(G)

spec=importlib.util.spec_from_file_location("F",HERE/"flight_intensity_scalar_v1.py")
F=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(F)

NPERM=9999
SEED=20261007921
MIN_VALID=9500
RAW_K=0.3885703906333845

def prepare():
    traj=G.P.load_rhino()
    grows,support=G.build_rows(traj)
    if grows is None:
        raise RuntimeError(f"geometry support failed: {support}")
    frows,_=F.load_scalar_rows()
    fmap={r["name"]:float(r["flight_intensity"]) for r in frows}
    rows=[]
    for r in grows:
        if r["name"] not in fmap:
            raise RuntimeError(f"missing FI {r['name']}")
        q=dict(r)
        q["fi"]=fmap[r["name"]]
        rows.append(q)
    if len(rows)!=45:
        raise RuntimeError(f"expected 45 common rows, got {len(rows)}")
    envs=sorted(set(r["env"] for r in rows))
    return rows,envs,support

def residual_folds(rows,envs):
    folds={}
    slopes={}
    for e0 in envs:
        train=[r for r in rows if r["env"]!=e0]
        X=np.asarray([[1.0,r["fi"]] for r in train],float)
        Y=np.vstack([r["z"] for r in train]).astype(float)
        coef=np.linalg.lstsq(X,Y,rcond=None)[0]  # 2 x p
        foldrows=[]
        for r in rows:
            pred=coef[0]+coef[1]*float(r["fi"])
            foldrows.append(np.asarray(r["z"],float)-pred)
        folds[e0]=foldrows
        slopes[e0]=coef[1].tolist()
    return folds,slopes

def labelsets(rows,envs):
    return {e:sorted(set(r["bat"] for r in rows if r["env"]==e)) for e in envs}

def identity_mapping(ls):
    return {(e,b):b for e,labs in ls.items() for b in labs}

def perm_mapping(ls,rng):
    out={}
    for e,labs in ls.items():
        p=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,p):
            out[(e,old)]=str(new)
    return out

def lab(r,mapping):
    return mapping[(r["env"],r["bat"])]

def stat(rows,envs,folds,mapping):
    perbat=collections.defaultdict(list)
    for e0 in envs:
        coords=folds[e0]
        train_envs=[e for e in envs if e!=e0]
        labels=sorted(set(lab(r,mapping) for r in rows))
        cent={}
        presence=collections.defaultdict(list)
        for b in labels:
            ee_means=[]
            for e in train_envs:
                ix=[i for i,r in enumerate(rows) if r["env"]==e and lab(r,mapping)==b]
                if ix:
                    ee_means.append(np.mean(np.vstack([coords[i] for i in ix]),axis=0))
                    presence[b].append(e)
            if len(ee_means)>=2:
                cent[b]=np.mean(np.vstack(ee_means),axis=0)
        if len(cent)<3:
            return None,{}
        for i,r in enumerate(rows):
            if r["env"]!=e0:
                continue
            b=lab(r,mapping)
            if b not in cent:
                continue
            donors=[bb for bb in cent if bb!=b]
            if len(donors)<2:
                continue
            z=np.asarray(coords[i],float)
            ds=float(np.linalg.norm(z-cent[b]))
            do=float(np.mean([np.linalg.norm(z-cent[bb]) for bb in donors]))
            perbat[b].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in perbat.items() if v}
    if len(bm)<3:
        return None,bm
    return float(np.mean(list(bm.values()))),bm

def main():
    rows,envs,support=prepare()
    folds,slopes=residual_folds(rows,envs)
    ls=labelsets(rows,envs)
    obs,bm=stat(rows,envs,folds,identity_mapping(ls))
    if obs is None:
        raise RuntimeError("observed residual identity support failed")
    rng=np.random.default_rng(SEED)
    null=[]
    for _ in range(NPERM):
        s,_=stat(rows,envs,folds,perm_mapping(ls,rng))
        if s is not None:
            null.append(s)
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs))/(1+len(a)))
    pos=sum(v>0 for v in bm.values())
    supported=bool(len(a)>=MIN_VALID and obs>0 and p<=.05 and pos/len(bm)>=.70)
    out={
        "contract":"GEOMETRY_BEYOND_THETA_CONTRACT_V1.md",
        "status":"POST_PRIMARY_MATHEMATICAL_STRUCTURE_DIAGNOSTIC",
        "species":"Rhinolophus nippon",
        "n_trajectories":len(rows),
        "environments":envs,
        "geometry_features":support["retained_features"],
        "raw_geometry_reference_K":RAW_K,
        "residual_geometry_K":float(obs),
        "residual_over_raw_K":float(obs/RAW_K),
        "bat_means":bm,
        "positive_bats":pos,
        "n_bats":len(bm),
        "positive_fraction":pos/len(bm),
        "fold_theta_slopes":{str(e):slopes[e] for e in envs},
        "permutation":{
            "requested":NPERM,
            "valid":int(len(a)),
            "seed":SEED,
            "null_mean":float(a.mean()),
            "null_q025":float(np.quantile(a,.025)),
            "null_q975":float(np.quantile(a,.975)),
            "p_one_sided":p
        },
        "supported":supported,
        "verdict":"SUPPORTED_GEOMETRY_BEYOND_THETA" if supported else "UNSUPPORTED_GEOMETRY_BEYOND_THETA"
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
