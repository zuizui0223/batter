#!/usr/bin/env python3
"""Scale-free route-geometry identity after label-free FlightIntensity residualization."""
from __future__ import annotations

import collections, importlib.util, json, math
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("G",HERE/"geometry_only_policy_v1.py")
G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)

NPERM=9999
MIN_VALID=9500
SEED=202610061401

def build():
    traj=G.P.load_rhino()
    rows,support=G.build_rows(traj)
    if rows is None:
        raise RuntimeError(f"parent geometry support failed: {support}")
    if support.get("retained_features")!=G.FEATURES:
        raise RuntimeError("parent geometry feature set drift")

    r2_by_feature=collections.defaultdict(list)
    out=[]
    for e in support["usable_envs"]:
        rr=[r for r in rows if r["env"]==e]
        # Frozen movement-feature standardization used by Primary B.
        M=np.vstack([np.asarray(r["features"],float) for r in rr])
        mu=M.mean(axis=0);sd=M.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):
            raise RuntimeError(f"bad movement SD env={e}")
        Z=(M-mu)/sd
        I=np.mean(Z[:,:4],axis=1)

        X=np.column_stack([np.ones(len(I)),I])
        for row,g,i in zip(rr,np.vstack([r["z"] for r in rr]),I):
            q=dict(row)
            # fill after feature-wise fits below
            q["_g"]=np.asarray(g,float)
            q["_I"]=float(i)
            out.append(q)

        Gmat=np.vstack([r["z"] for r in rr])
        B=np.linalg.lstsq(X,Gmat,rcond=None)[0]  # 2 x 8
        fitted=X@B
        resid=Gmat-fitted

        for j,name in enumerate(G.FEATURES):
            y=Gmat[:,j]
            sst=float(np.sum((y-y.mean())**2))
            sse=float(np.sum((y-fitted[:,j])**2))
            r2=1-sse/sst if sst>0 else math.nan
            r2_by_feature[name].append(float(r2))

        # attach residuals in the same order as rr
        envout=[q for q in out if q["env"]==e]
        if len(envout)!=len(rr):
            raise RuntimeError("residual row alignment failed")
        for q,res in zip(envout,resid):
            q["z"]=np.asarray(res,float)

    diag={
        name:{
            "median_R2":float(np.median(v)),
            "min_R2":float(np.min(v)),
            "max_R2":float(np.max(v)),
        }
        for name,v in r2_by_feature.items()
    }
    return rows,out,support,diag

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
    parent,resid,support,diag=build()
    parent_obs,parent_ind=G.stat(parent)
    obs,ind=G.stat(resid)
    if parent_obs is None or obs is None:
        raise RuntimeError("observed identity support failed")

    ls=labelsets(resid,support["usable_envs"])
    rng=np.random.default_rng(SEED)
    null=[]
    for _ in range(NPERM):
        q,_=G.stat(resid,perm_map(ls,rng))
        if q is not None and math.isfinite(q):
            null.append(float(q))
    a=np.asarray(null,float)
    if len(a)<MIN_VALID:
        raise RuntimeError(f"randomization support {len(a)}")

    p=float((1+np.sum(a>=obs))/(1+len(a)))
    pos=sum(v>0 for v in ind.values())
    n=len(ind)
    supported=bool(obs>0 and p<=.05 and pos>=4)

    out={
        "contract":"GEOMETRY_BEYOND_FLIGHT_INTENSITY_CONTRACT_V1.md",
        "status":"POST_PRIMARY_MECHANISM_DIAGNOSTIC",
        "species":"Rhinolophus nippon",
        "parent_geometry_K":float(parent_obs),
        "residual_geometry":{
            "K":float(obs),
            "K_over_parent":float(obs/parent_obs) if parent_obs!=0 else None,
            "bat_means":ind,
            "positive_bats":int(pos),
            "n_bats":int(n),
            "positive_fraction":float(pos/n),
            "requested_permutations":NPERM,
            "valid_permutations":int(len(a)),
            "seed":SEED,
            "null_mean":float(a.mean()),
            "null_q025":float(np.quantile(a,.025)),
            "null_q975":float(np.quantile(a,.975)),
            "p_one_sided":p,
            "verdict":"SUPPORTED_GEOMETRY_BEYOND_FLIGHT_INTENSITY" if supported else "UNSUPPORTED_GEOMETRY_BEYOND_FLIGHT_INTENSITY",
        },
        "geometry_feature_linear_R2_from_FlightIntensity":diag,
    }
    print(json.dumps(out,indent=2))

if __name__=="__main__":
    main()
