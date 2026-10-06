#!/usr/bin/env python3
"""Scale-free route geometry after linear removal of transparent I and M policy axes."""
from __future__ import annotations

import importlib.util, json, math
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("G",HERE/"geometry_only_policy_v1.py")
G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)

NPERM=9999
MIN_VALID=9500
SEED=202610061402

def build():
    traj=G.P.load_rhino()
    parent,support=G.build_rows(traj)
    if parent is None:
        raise RuntimeError(f"parent geometry support failed: {support}")
    if support.get("retained_features")!=G.FEATURES:
        raise RuntimeError("geometry feature set drift")

    i_only=[]
    im_resid=[]
    r2_by_feature={name:[] for name in G.FEATURES}

    for e in support["usable_envs"]:
        rr=[r for r in parent if r["env"]==e]
        move=np.vstack([np.asarray(r["features"],float) for r in rr])
        mu=move.mean(axis=0);sd=move.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):
            raise RuntimeError(f"bad movement SD env={e}")
        Z=(move-mu)/sd
        I=np.mean(Z[:,:4],axis=1)
        M=np.mean(np.column_stack([-Z[:,0],Z[:,4],Z[:,5],Z[:,6],Z[:,7]]),axis=1)

        geom=np.vstack([np.asarray(r["z"],float) for r in rr])

        X1=np.column_stack([np.ones(len(rr)),I])
        B1=np.linalg.lstsq(X1,geom,rcond=None)[0]
        resid1=geom-X1@B1

        X2=np.column_stack([np.ones(len(rr)),I,M])
        B2=np.linalg.lstsq(X2,geom,rcond=None)[0]
        fitted2=X2@B2
        resid2=geom-fitted2

        for j,name in enumerate(G.FEATURES):
            y=geom[:,j]
            sst=float(np.sum((y-y.mean())**2))
            sse=float(np.sum((y-fitted2[:,j])**2))
            r2=1-sse/sst if sst>0 else math.nan
            r2_by_feature[name].append(float(r2))

        for r,a,b in zip(rr,resid1,resid2):
            q1=dict(r);q1["z"]=np.asarray(a,float);i_only.append(q1)
            q2=dict(r);q2["z"]=np.asarray(b,float);im_resid.append(q2)

    diag={
        name:{
            "median_R2":float(np.median(v)),
            "min_R2":float(np.min(v)),
            "max_R2":float(np.max(v)),
        }
        for name,v in r2_by_feature.items()
    }
    return parent,i_only,im_resid,support,diag

def labelsets(rows,envs):
    return {e:sorted(set(r["bat"] for r in rows if r["env"]==e)) for e in envs}

def perm_map(ls,rng):
    mp={}
    for e,labs in ls.items():
        p=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,p):
            mp[(e,old)]=str(new)
    return mp

def main():
    parent,i_only,im_resid,support,diag=build()
    pobs,_=G.stat(parent)
    iobs,_=G.stat(i_only)
    obs,ind=G.stat(im_resid)
    if pobs is None or iobs is None or obs is None:
        raise RuntimeError("observed identity support failed")

    ls=labelsets(im_resid,support["usable_envs"])
    rng=np.random.default_rng(SEED)
    null=[]
    for _ in range(NPERM):
        q,_=G.stat(im_resid,perm_map(ls,rng))
        if q is not None and math.isfinite(q):
            null.append(float(q))
    a=np.asarray(null,float)
    if len(a)<MIN_VALID:
        raise RuntimeError(f"randomization support {len(a)}")

    p=float((1+np.sum(a>=obs))/(1+len(a)))
    pos=sum(v>0 for v in ind.values())
    supported=bool(obs>0 and p<=.05 and pos>=4)

    print(json.dumps({
        "contract":"GEOMETRY_BEYOND_TRANSPARENT_TWO_AXIS_CONTRACT_V1.md",
        "status":"POST_PRIMARY_FALSIFICATION_DIAGNOSTIC",
        "species":"Rhinolophus nippon",
        "parent_geometry_K":float(pobs),
        "I_only_residual_geometry_K_recomputed":float(iobs),
        "IM_residual_geometry":{
            "K":float(obs),
            "K_over_parent":float(obs/pobs) if pobs!=0 else None,
            "K_over_I_only_residual":float(obs/iobs) if iobs!=0 else None,
            "bat_means":ind,
            "positive_bats":int(pos),
            "n_bats":int(len(ind)),
            "positive_fraction":float(pos/len(ind)),
            "requested_permutations":NPERM,
            "valid_permutations":int(len(a)),
            "seed":SEED,
            "null_mean":float(a.mean()),
            "null_q025":float(np.quantile(a,.025)),
            "null_q975":float(np.quantile(a,.975)),
            "p_one_sided":p,
            "verdict":"SUPPORTED_GEOMETRY_BEYOND_TRANSPARENT_TWO_AXIS" if supported else "UNSUPPORTED_GEOMETRY_BEYOND_TRANSPARENT_TWO_AXIS",
        },
        "geometry_feature_linear_R2_from_I_and_M":diag,
    },indent=2))

if __name__=="__main__":
    main()
