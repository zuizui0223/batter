#!/usr/bin/env python3
"""Exhaustive one-trial deletion audit for negative Carollia fixed-geometry external result."""
from __future__ import annotations

import collections, importlib.util, json, math
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("E",HERE/"carollia_fixed_geometry_external_v1.py")
E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)

NPERM=9999
MIN_VALID=9500

def base_rows():
    rows,support=E.load_rows()
    if rows is None:
        raise RuntimeError(f"base support failed: {support}")
    return rows

def standardize_fresh(rows):
    out=[]
    for r in rows:
        q=dict(r)
        if "gfeat" in q:
            q["gfeat"]=np.asarray(q["gfeat"],float).copy()
        q.pop("zgeom",None)
        out.append(q)
    for date in E.P.FIXED_BLOCKS:
        rr=[r for r in out if r["date"]==date and r["valid"]]
        X=np.vstack([r["gfeat"] for r in rr])
        mu=X.mean(axis=0);sd=X.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):
            raise RuntimeError(f"bad geometry SD after deletion in {date}")
        for r in rr:
            r["zgeom"]=(r["gfeat"]-mu)/sd
    return out

def evaluate(rows,seed):
    rr=standardize_fresh(rows)
    obs=E.stat(rr)
    if obs is None:
        raise RuntimeError("observed stat failed")
    rng=np.random.default_rng(seed)
    null=[]
    for _ in range(NPERM):
        q=E.stat(rr,E.conditional_perm_labels(rr,rng))
        if q is not None and math.isfinite(q["K"]):
            null.append(float(q["K"]))
    a=np.asarray(null,float)
    if len(a)<MIN_VALID:
        raise RuntimeError(f"randomization support {len(a)}")
    p=float((1+np.sum(a>=obs["K"]))/(1+len(a)))
    pos=sum(v>0 for v in obs["bat_means"].values())
    n=len(obs["bat_means"])
    supported=bool(
        obs["K"]>0 and p<=.05 and pos/n>=.70
        and all(v>0 for v in obs["block_means"].values())
    )
    return {
        "K":float(obs["K"]),
        "block_means":obs["block_means"],
        "positive_bats":int(pos),
        "n_bats":int(n),
        "positive_fraction":float(pos/n),
        "valid_permutations":int(len(a)),
        "p_one_sided":p,
        "null_mean":float(a.mean()),
        "null_q025":float(np.quantile(a,.025)),
        "null_q975":float(np.quantile(a,.975)),
        "would_support_fixed_geometry_external":supported,
    }

def main():
    rows=base_rows()
    counts=collections.Counter((r["date"],r["bat"]) for r in rows if r["valid"])
    admissible=sorted(
        r["filename"] for r in rows
        if r["valid"] and counts[(r["date"],r["bat"])]>3
    )
    if len(admissible)!=22:
        raise RuntimeError(f"expected 22 admissible deletions, got {len(admissible)}")

    results=[]
    for k,name in enumerate(admissible,1):
        sub=[r for r in rows if r["filename"]!=name]
        q=evaluate(sub,202610061500+k)
        results.append({"removed":name,"seed":202610061500+k,**q})

    c3=next(
        x for x in results
        if x["removed"]=="C3_2_20231216_traj_bat_pos_RESULTS.mat"
    )
    out={
        "contract":"CAROLLIA_FIXED_GEOMETRY_LOO_ROBUSTNESS_CONTRACT_V1.md",
        "status":"POST_OUTCOME_ROBUSTNESS_AUDIT",
        "n_admissible_deletions":len(results),
        "deletion_results":results,
        "summary":{
            "min_K":float(min(x["K"] for x in results)),
            "max_K":float(max(x["K"] for x in results)),
            "min_p":float(min(x["p_one_sided"] for x in results)),
            "max_p":float(max(x["p_one_sided"] for x in results)),
            "min_positive_fraction":float(min(x["positive_fraction"] for x in results)),
            "max_positive_fraction":float(max(x["positive_fraction"] for x in results)),
            "n_deletions_yielding_support":int(sum(x["would_support_fixed_geometry_external"] for x in results)),
            "all_deletions_remain_unsupported":bool(all(not x["would_support_fixed_geometry_external"] for x in results)),
            "C3_2_deletion":c3,
        }
    }
    print(json.dumps(out,indent=2))

if __name__=="__main__":
    main()
