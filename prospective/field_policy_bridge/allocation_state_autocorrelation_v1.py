#!/usr/bin/env python3
"""Within-individual temporal persistence of the P. hastatus allocation state."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("S",HERE/"strict_past_allocation_persistence_v1.py")
S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)

NPERM=9999
MIN_VALID=9500
PANELS=S.PANELS
SEEDS={"2022":202610051541,"2023":202610051542}

def series(panel):
    rows,audit=S.prepared_rows(panel)
    if rows is None:return None,audit
    by=collections.defaultdict(list)
    for r in rows:
        by[(str(r["cohort"]),str(r["iid"]))].append((float(r["start"]),float(r["A"])))
    out={}
    for k,v in by.items():
        vv=sorted(v,key=lambda x:x[0])
        if len(vv)>=4:
            out[k]=vv
    return out,audit

def ri(v):
    if len(v)<4:return None,None
    t=np.asarray([x[0] for x in v],float)
    a=np.asarray([x[1] for x in v],float)
    u=a-a.mean()
    den=float(np.mean(u*u))
    if not (math.isfinite(den) and den>0):return None,None
    prod=[];gaps=[]
    for k in range(1,len(v)):
        gap=t[k]-t[k-1]
        if not (math.isfinite(gap) and gap>0):continue
        prod.append(float(u[k]*u[k-1]))
        gaps.append(float(gap))
    if len(prod)<3:return None,None
    return float(np.mean(prod)/den),{"products":prod,"gaps":gaps,"den":den}

def stat(by):
    vals={};allpairs=[]
    for k,v in by.items():
        q,d=ri(v)
        if q is None:continue
        vals["::".join(k)]=q
        for p,g in zip(d["products"],d["gaps"]):
            allpairs.append((p/d["den"],g))
    if len(vals)<3:return None,{},allpairs
    return float(np.mean(list(vals.values()))),vals,allpairs

def permute(by,rng):
    out={}
    for k,v in by.items():
        t=[x[0] for x in v]
        a=np.asarray([x[1] for x in v],float).copy()
        rng.shuffle(a)
        out[k]=list(zip(t,a.tolist()))
    return out

def run(year,panel):
    by,audit=series(panel)
    if by is None:return {"status":"STOP_SUPPORT","audit":audit}
    obs,ind,pairs=stat(by)
    if obs is None:return {"status":"STOP_OBSERVED_SUPPORT"}
    rng=np.random.default_rng(SEEDS[year]);null=[]
    for _ in range(NPERM):
        q,_,_=stat(permute(by,rng))
        if q is not None and math.isfinite(q):null.append(q)
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs))/(1+len(a))) if len(a) else None

    gaps=np.asarray([g for _,g in pairs],float)
    med=float(np.median(gaps)) if len(gaps) else None
    short=[x for x,g in pairs if g<=med] if med is not None else []
    long=[x for x,g in pairs if g>med] if med is not None else []
    out={
      "status":"DONE" if len(a)>=MIN_VALID else "STOP_RANDOMIZATION_SUPPORT",
      "R_year":float(obs),
      "individual_R":ind,
      "positive_individuals":sum(v>0 for v in ind.values()),
      "n_individuals":len(ind),
      "positive_fraction":sum(v>0 for v in ind.values())/len(ind),
      "n_adjacent_pairs":len(pairs),
      "gap_seconds":{"min":float(gaps.min()) if len(gaps) else None,
                     "median":med,
                     "max":float(gaps.max()) if len(gaps) else None},
      "short_gap_mean_normalized_product":float(np.mean(short)) if short else None,
      "long_gap_mean_normalized_product":float(np.mean(long)) if long else None,
      "requested_permutations":NPERM,"valid_permutations":int(len(a)),
      "seed":SEEDS[year],
      "null_mean":float(a.mean()) if len(a) else None,
      "null_q025":float(np.quantile(a,.025)) if len(a) else None,
      "null_q975":float(np.quantile(a,.975)) if len(a) else None,
      "p_one_sided":p,
      "diagnostic_verdict":"SUPPORTED_DYNAMIC_STATE"
        if (len(a)>=MIN_VALID and obs>0 and p is not None and p<=.05)
        else "UNSUPPORTED_DYNAMIC_STATE"
    }
    return out

def main():
    print(json.dumps({
      "contract":"ALLOCATION_STATE_AUTOCORRELATION_CONTRACT_V1.md",
      "status":"POST_OUTCOME_DYNAMIC_STATE_DIAGNOSTIC",
      "years":{y:run(y,p) for y,p in PANELS.items()}
    },ensure_ascii=False,indent=2))
if __name__=="__main__":main()
