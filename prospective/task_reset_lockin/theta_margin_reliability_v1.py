#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("O",HERE/"one_parameter_calibration_v1.py")
O=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(O)

NPERM=9999
SEED=20261007901
MIN_VALID=9500
THRESHOLDS=(0.25,0.50,0.75,1.00)

def average_ranks(x):
    x=np.asarray(x,float)
    order=np.argsort(x,kind="mergesort")
    ranks=np.empty(len(x),float)
    i=0
    while i<len(x):
        j=i+1
        while j<len(x) and x[order[j]]==x[order[i]]:
            j+=1
        r=0.5*((i+1)+j)
        ranks[order[i:j]]=r
        i=j
    return ranks

def spearman(x,y):
    x=np.asarray(x,float); y=np.asarray(y,float)
    if len(x)<3:return math.nan
    rx=average_ranks(x); ry=average_ranks(y)
    if np.std(rx,ddof=1)<=0 or np.std(ry,ddof=1)<=0:
        return math.nan
    return float(np.corrcoef(rx,ry)[0,1])

def margin_stat(cal):
    pts=cal["points"]
    margin=[]
    correct=[]
    pairs=[]
    for p in pts:
        x=float(p["predicted_difference"])
        y=float(p["observed_difference"])
        c=0.5 if x==0 or y==0 else (1.0 if np.sign(x)==np.sign(y) else 0.0)
        margin.append(abs(x)); correct.append(c); pairs.append(p["pair"])
    rho=spearman(margin,correct)
    table={}
    for t in THRESHOLDS:
        ix=[i for i,m in enumerate(margin) if m>=t]
        table[f"{t:.2f}"]={
            "n_points":len(ix),
            "n_pairs":len(set(pairs[i] for i in ix)),
            "sign_accuracy":float(np.mean([correct[i] for i in ix])) if ix else None,
        }
    return {
        "rho_margin_correctness":rho,
        "n_points":len(margin),
        "n_pairs":len(set(pairs)),
        "overall_accuracy":float(np.mean(correct)),
        "thresholds":table,
        "points":[
            {
                **p,
                "margin":abs(float(p["predicted_difference"])),
                "correct":correct[i]
            }
            for i,p in enumerate(pts)
        ]
    }

def main():
    rows,envs=O.F.load_scalar_rows()
    cm=O.cluster_centroids(rows,envs)
    ls=O.F.labelsets(rows,envs)
    obsmap=O.F.observed_mapping(rows,envs)
    cal=O.calibration(cm,envs,obsmap)
    if cal is None: raise RuntimeError("observed calibration support")
    obs=margin_stat(cal)
    if not math.isfinite(obs["rho_margin_correctness"]):
        raise RuntimeError("observed margin statistic undefined")

    rng=np.random.default_rng(SEED)
    null=[]
    invalid=0
    for _ in range(NPERM):
        mp=O.F.perm_mapping(ls,rng)
        q=O.calibration(cm,envs,mp)
        if q is None:
            invalid+=1; continue
        s=margin_stat(q)["rho_margin_correctness"]
        if math.isfinite(s): null.append(s)
        else: invalid+=1
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs["rho_margin_correctness"]))/(1+len(a))) if len(a) else math.nan
    supported=bool(len(a)>=MIN_VALID and obs["rho_margin_correctness"]>0 and p<=.05)

    out={
        "status":"POST_PRIMARY_MATHEMATICAL_STRUCTURE_DIAGNOSTIC",
        "contract":"THETA_MARGIN_RELIABILITY_CONTRACT_V1.md",
        "species":"Rhinolophus nippon",
        "observed":obs,
        "permutation":{
            "requested":NPERM,
            "valid":int(len(a)),
            "invalid":int(invalid),
            "seed":SEED,
            "null_mean":float(a.mean()) if len(a) else None,
            "null_q025":float(np.quantile(a,.025)) if len(a) else None,
            "null_q975":float(np.quantile(a,.975)) if len(a) else None,
            "p_one_sided":p
        },
        "supported":supported,
        "interpretation":"SUPPORTED_STABLE_THETA_PLUS_CONTEXT_NOISE" if supported else "UNSUPPORTED_MARGIN_RELIABILITY"
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
