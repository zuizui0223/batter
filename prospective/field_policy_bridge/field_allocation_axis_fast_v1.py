#!/usr/bin/env python3
"""Vectorized exact-equivalent transparent field allocation-axis diagnostic."""
from __future__ import annotations
import importlib.util,json,math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("A",HERE/"field_allocation_axis_v1.py")
A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)

NPERM=A.NPERM

def encode(rows,key):
    out=[]
    for co in sorted({r["cohort"] for r in rows}):
        rr=[r for r in rows if r["cohort"]==co]
        ids=sorted({r["iid"] for r in rr}); mp={x:k for k,x in enumerate(ids)}
        x=np.asarray([float(r[key]) for r in rr],float)
        lab=np.asarray([mp[r["iid"]] for r in rr],int)
        cnt=np.bincount(lab,minlength=len(ids)).astype(int)
        out.append((co,ids,x,lab,cnt))
    return out

def cohort_stat(x,lab,cnt):
    L=len(cnt); n=len(lab)
    sums=np.bincount(lab,weights=x,minlength=L)
    cents=sums/cnt
    D=np.abs(x[:,None]-cents[None,:])
    donor=(D.sum(axis=1)-D[np.arange(n),lab])/(L-1)
    selfc=(sums[lab]-x)/(cnt[lab]-1)
    adv=donor-np.abs(x-selfc)
    return np.bincount(lab,weights=adv,minlength=L)/cnt

def full(cohorts,override=None):
    vals=[]; detail={}
    for z,(co,ids,x,lab,cnt) in enumerate(cohorts):
        ll=lab if override is None else override[z]
        im=cohort_stat(x,ll,cnt)
        vals.extend(im.tolist())
        if override is None:
            for k,v in enumerate(im):detail[f"{co}::{ids[k]}"]=float(v)
    return float(np.mean(vals)),detail

def ident(rows,year,key):
    cohorts=encode(rows,key)
    obs,ind=full(cohorts)
    rng=np.random.default_rng(A.SEEDS[(year,key)])
    null=np.empty(NPERM,float)
    for z in range(NPERM):
        null[z]=full(cohorts,[rng.permutation(c[3]) for c in cohorts])[0]
    pos=sum(v>0 for v in ind.values());frac=pos/len(ind)
    p=float((1+np.sum(null>=obs))/(NPERM+1))
    return {"status":"DONE","K":obs,"individual_K":ind,
      "positive_individuals":pos,"n_individuals":len(ind),"positive_fraction":frac,
      "p_one_sided":p,"null_mean":float(null.mean()),
      "null_q025":float(np.quantile(null,.025)),"null_q975":float(np.quantile(null,.975)),
      "seed":A.SEEDS[(year,key)],
      "diagnostic_verdict":"SUPPORTED" if obs>0 and p<=.05 and frac>=.70 else "UNSUPPORTED"}

def run(year,panel):
    rows,audit=A.rows_axes(panel)
    if rows is None:return {"status":"STOP_SUPPORT"}
    return {"status":"DONE","n_sessions":len(rows),
      "allocation_A":ident(rows,year,"A"),
      "overall_I":ident(rows,year,"I"),
      "axis_geometry":A.geometry(rows)}

def main():
    print(json.dumps({"contract":"FIELD_ALLOCATION_AXIS_CONTRACT_V1.md",
      "implementation":"vectorized_exact_equivalent_v1",
      "status":"POST_OUTCOME_INTERPRETABILITY_DIAGNOSTIC",
      "years":{y:run(y,p) for y,p in A.PANELS.items()}},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
