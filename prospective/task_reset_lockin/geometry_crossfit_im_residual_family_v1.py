#!/usr/bin/env python3
"""Family localization of geometry identity remaining beyond cross-fitted I/M."""
from __future__ import annotations
import collections,importlib.util,json,math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("X",HERE/"geometry_crossfit_im_expression_v1.py")
X=importlib.util.module_from_spec(spec);spec.loader.exec_module(X)

NPERM=9999
MIN_VALID=9500
FAMILIES={
 "G":([0,1,2,3],202610062001),
 "H":([4,5],202610062002),
 "V":([6,7],202610062003),
}

def build_folds(rows,envs):
    out={}
    for e0 in envs:
        rr=X.fold_residuals(rows,e0)
        if rr is None:raise RuntimeError(f"fold residual support env={e0}")
        out[e0]=rr
    return out

def stat(folds,envs,mapping,idx):
    vals=collections.defaultdict(list)
    for e0 in envs:
        rr=folds[e0]
        cent=collections.defaultdict(lambda:collections.defaultdict(list))
        for r in rr:
            if r["env"]==e0:continue
            lab=mapping[(r["env"],r["bat"])]
            cent[lab][r["env"]].append(np.asarray(r["resid"],float)[idx])
        train={}
        for b,d in cent.items():
            envc=[np.mean(np.vstack(v),axis=0) for _,v in sorted(d.items()) if v]
            if len(envc)>=2:train[b]=np.mean(np.vstack(envc),axis=0)
        if len(train)<3:continue
        for r in [q for q in rr if q["env"]==e0]:
            lab=mapping[(e0,r["bat"])]
            if lab not in train:continue
            donors=[b for b in train if b!=lab]
            if len(donors)<2:continue
            x=np.asarray(r["resid"],float)[idx]
            ds=float(np.linalg.norm(x-train[lab]))
            do=float(np.mean([np.linalg.norm(x-train[b]) for b in donors]))
            vals[lab].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in vals.items() if v}
    if len(bm)<3:return None,bm
    return float(np.mean(list(bm.values()))),bm

def labelsets(rows,envs):
    return {e:sorted(set(r["bat"] for r in rows if r["env"]==e)) for e in envs}

def obsmap(rows,envs):
    return {(e,b):b for e,labs in labelsets(rows,envs).items() for b in labs}

def permmap(ls,rng):
    mp={}
    for e,labs in ls.items():
        p=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,p):mp[(e,old)]=str(new)
    return mp

def run(folds,rows,envs,idx,seed):
    obs,bm=stat(folds,envs,obsmap(rows,envs),idx)
    if obs is None:return {"status":"STOP_OBSERVED_SUPPORT"}
    ls=labelsets(rows,envs);rng=np.random.default_rng(seed);null=[]
    for _ in range(NPERM):
        s,_=stat(folds,envs,permmap(ls,rng),idx)
        if s is not None and math.isfinite(s):null.append(float(s))
    a=np.asarray(null,float)
    if len(a)<MIN_VALID:return {"status":"STOP_RANDOMIZATION_SUPPORT","valid_permutations":len(a)}
    p=float((1+np.sum(a>=obs))/(1+len(a)))
    pos=sum(v>0 for v in bm.values())
    return {
      "status":"DONE","K":float(obs),"bat_means":bm,
      "positive_bats":int(pos),"n_bats":len(bm),
      "positive_fraction":float(pos/len(bm)),
      "requested_permutations":NPERM,"valid_permutations":len(a),"seed":seed,
      "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
      "null_q975":float(np.quantile(a,.975)),"p_one_sided":p,
      "supported":bool(obs>0 and p<=.05 and pos>=4)
    }

def main():
    rows,envs=X.rows_raw()
    if envs!=list(range(1,8)):raise RuntimeError(f"environment drift {envs}")
    folds=build_folds(rows,envs)
    results={name:run(folds,rows,envs,idx,seed) for name,(idx,seed) in FAMILIES.items()}
    supported=[k for k,v in results.items() if v.get("supported",False)]
    verdict=(
      f"RESIDUAL_IDENTITY_LOCALIZED_{supported[0]}" if len(supported)==1 else
      "RESIDUAL_IDENTITY_DISTRIBUTED_MULTIPLE_FAMILIES" if len(supported)>1 else
      "NO_SINGLE_FAMILY_RESIDUAL_CARRIER"
    )
    print(json.dumps({
      "contract":"GEOMETRY_CROSSFIT_IM_RESIDUAL_FAMILY_CONTRACT_V1.md",
      "status":"POST_PRIMARY_EXPLORATORY_LOCALIZATION_DIAGNOSTIC",
      "n_trajectories":len(rows),"environments":envs,
      "families":{
        "G":["path_efficiency_3d","horizontal_displacement_ratio","abs_vertical_displacement_ratio","vertical_range_ratio"],
        "H":["median_abs_horizontal_turn_angle","p90_abs_horizontal_turn_angle"],
        "V":["median_abs_vertical_slope","p90_abs_vertical_slope"]
      },
      "results":results,
      "diagnostic_verdict":verdict
    },indent=2))

if __name__=="__main__":main()
