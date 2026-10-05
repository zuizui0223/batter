#!/usr/bin/env python3
"""Peer-controlled within-individual temporal persistence of P. hastatus allocation."""
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
SEEDS={"2022":202610051551,"2023":202610051552}

def residual_series(panel,window_h):
    rows,audit=S.prepared_rows(panel)
    if rows is None:return None,audit
    byco=collections.defaultdict(list)
    for r in rows:byco[str(r["cohort"])].append(r)

    perind=collections.defaultdict(list)
    w=window_h*3600.0
    for co,rr in byco.items():
        for q in rr:
            donors=collections.defaultdict(list)
            tq=float(q["start"])
            for p in rr:
                if str(p["iid"])==str(q["iid"]):continue
                if abs(float(p["start"])-tq)<=w:
                    donors[str(p["iid"])].append(float(p["A"]))
            if len(donors)<2:continue
            dmeans=[float(np.mean(v)) for v in donors.values()]
            resid=float(q["A"]-np.mean(dmeans))
            perind[(co,str(q["iid"]))].append((tq,resid))
    out={}
    for k,v in perind.items():
        vv=sorted(v,key=lambda x:(x[0]))
        if len(vv)>=4:out[k]=vv
    return out,audit

def ri(v):
    if len(v)<4:return None,None
    t=np.asarray([x[0] for x in v],float)
    a=np.asarray([x[1] for x in v],float)
    u=a-a.mean()
    den=float(np.mean(u*u))
    if not (math.isfinite(den) and den>0):return None,None
    vals=[];gaps=[]
    for k in range(1,len(v)):
        gap=t[k]-t[k-1]
        if not (math.isfinite(gap) and gap>0):continue
        vals.append(float(u[k]*u[k-1]/den));gaps.append(float(gap))
    if len(vals)<3:return None,None
    return float(np.mean(vals)),{"contrib":vals,"gaps":gaps}

def stat(by):
    ind={};pairs=[]
    for k,v in by.items():
        q,d=ri(v)
        if q is None:continue
        ind["::".join(k)]=q
        pairs.extend(zip(d["contrib"],d["gaps"]))
    if len(ind)<3:return None,{},pairs
    return float(np.mean(list(ind.values()))),ind,pairs

def permute(by,rng):
    out={}
    for k,v in by.items():
        t=[x[0] for x in v]
        a=np.asarray([x[1] for x in v],float).copy()
        rng.shuffle(a)
        out[k]=list(zip(t,a.tolist()))
    return out

def observed_window(panel,h):
    by,audit=residual_series(panel,h)
    if by is None:return None,{},[],audit
    q,ind,pairs=stat(by)
    return q,ind,pairs,audit

def run(year,panel):
    obs,ind,pairs,audit=observed_window(panel,12)
    if obs is None:return {"status":"STOP_OBSERVED_SUPPORT","audit":audit}
    by,_=residual_series(panel,12)
    rng=np.random.default_rng(SEEDS[year]);null=[]
    for _ in range(NPERM):
        q,_,_=stat(permute(by,rng))
        if q is not None and math.isfinite(q):null.append(q)
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs))/(1+len(a))) if len(a) else None
    pos=sum(v>0 for v in ind.values());frac=pos/len(ind)

    sens={}
    for h in (6,24):
        q,ii,pp,_=observed_window(panel,h)
        sens[str(h)]={
          "R":q,"n_individuals":len(ii),
          "positive_individuals":sum(v>0 for v in ii.values()),
          "positive_fraction":(sum(v>0 for v in ii.values())/len(ii)) if ii else None,
          "n_adjacent_pairs":len(pp)
        }

    gaps=np.asarray([g for _,g in pairs],float)
    supported=bool(len(a)>=MIN_VALID and obs>0 and p is not None and p<=.05)
    return {
      "status":"DONE" if len(a)>=MIN_VALID else "STOP_RANDOMIZATION_SUPPORT",
      "peer_window_hours":12,
      "R_peer":float(obs),"individual_R":ind,
      "positive_individuals":pos,"n_individuals":len(ind),"positive_fraction":frac,
      "n_adjacent_pairs":len(pairs),
      "gap_seconds":{"min":float(gaps.min()) if len(gaps) else None,
                     "median":float(np.median(gaps)) if len(gaps) else None,
                     "max":float(gaps.max()) if len(gaps) else None},
      "valid_permutations":int(len(a)),"requested_permutations":NPERM,
      "seed":SEEDS[year],
      "null_mean":float(a.mean()) if len(a) else None,
      "null_q025":float(np.quantile(a,.025)) if len(a) else None,
      "null_q975":float(np.quantile(a,.975)) if len(a) else None,
      "p_one_sided":p,
      "window_sensitivity":sens,
      "diagnostic_verdict":"SUPPORTED_INDIVIDUAL_STATE_AFTER_PEER_CONTROL" if supported else "UNSUPPORTED_AFTER_PEER_CONTROL"
    }

def main():
    print(json.dumps({
      "contract":"PEER_CONTROLLED_STATE_PERSISTENCE_CONTRACT_V1.md",
      "status":"POST_OUTCOME_SHARED_ENVIRONMENT_ROBUSTNESS",
      "years":{y:run(y,p) for y,p in PANELS.items()}
    },ensure_ascii=False,indent=2))
if __name__=="__main__":main()
