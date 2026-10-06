#!/usr/bin/env python3
"""Fast equivalent implementation of cross-fitted I/M -> geometry residual identity."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("B",HERE/"geometry_crossfit_im_expression_v1.py")
B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)

def precompute(rows,envs):
    folds={}
    for e0 in envs:
        rr=B.fold_residuals(rows,e0)
        if rr is None: raise RuntimeError(f"fold residualization failed env={e0}")
        folds[e0]=rr
    return folds

def stat_fast(folds,envs,mapping):
    vals=collections.defaultdict(list)
    for e0 in envs:
        rr=folds[e0]
        cent=collections.defaultdict(lambda:collections.defaultdict(list))
        for r in rr:
            if r["env"]==e0: continue
            lab=mapping[(r["env"],r["bat"])]
            cent[lab][r["env"]].append(r["resid"])
        train={}
        for b,d in cent.items():
            envc=[np.mean(np.vstack(v),0) for _,v in sorted(d.items()) if v]
            if len(envc)>=2: train[b]=np.mean(np.vstack(envc),0)
        if len(train)<3: continue
        for r in [x for x in rr if x["env"]==e0]:
            lab=mapping[(e0,r["bat"])]
            if lab not in train: continue
            donors=[b for b in train if b!=lab]
            if len(donors)<2: continue
            ds=float(np.linalg.norm(r["resid"]-train[lab]))
            do=float(np.mean([np.linalg.norm(r["resid"]-train[b]) for b in donors]))
            vals[lab].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in vals.items() if v}
    if len(bm)<3:return None,bm
    return float(np.mean(list(bm.values()))),bm

def main():
    rows,envs=B.rows_raw()
    if envs!=list(range(1,8)):raise RuntimeError(f"environment drift {envs}")
    folds=precompute(rows,envs)
    obs,bm=stat_fast(folds,envs,B.idmap(rows))
    if obs is None:raise RuntimeError("observed support failed")
    rng=np.random.default_rng(B.SEED);null=[]
    for _ in range(B.NPERM):
        s,_=stat_fast(folds,envs,B.permmap(rows,rng))
        if s is not None and math.isfinite(s): null.append(float(s))
    a=np.asarray(null,float)
    if len(a)<B.MIN_VALID:raise RuntimeError(f"randomization support {len(a)}")
    p=float((1+np.sum(a>=obs))/(1+len(a)))
    pos=sum(v>0 for v in bm.values())
    support=bool(obs>0 and p<=.05 and pos>=4)
    print(json.dumps({
      "contract":"GEOMETRY_CROSSFIT_IM_EXPRESSION_CONTRACT_V1.md",
      "implementation":"FAST_EQUIVALENT_PRECOMPUTED_LABEL_FREE_FOLDS",
      "status":"POST_PRIMARY_FALSIFICATION_DIAGNOSTIC",
      "n_trajectories":len(rows),"environments":envs,
      "residual_geometry_identity":{
        "K":float(obs),"bat_means":bm,"positive_bats":int(pos),
        "n_bats":len(bm),"positive_fraction":float(pos/len(bm)),
        "requested_permutations":B.NPERM,"valid_permutations":len(a),"seed":B.SEED,
        "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
        "null_q975":float(np.quantile(a,.975)),"p_one_sided":p,
        "verdict":"SUPPORTED_GEOMETRY_BEYOND_CROSSFIT_IM" if support else "UNSUPPORTED_GEOMETRY_BEYOND_CROSSFIT_IM"
      }
    },indent=2))

if __name__=="__main__": main()
