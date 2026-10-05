#!/usr/bin/env python3
"""Peer-day-adjusted within-individual temporal persistence of field allocation state."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("S",HERE/"strict_past_allocation_persistence_v1.py")
S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)

NPERM=9999
MIN_VALID=9500
MIN_INDIVIDUALS=5
MIN_PAIRS=15
SEEDS={"2022":202610051601,"2023":202610051602}

def prepared_adjusted(panel):
    rows,audit=S.prepared_rows(panel)
    if rows is None:return None,audit,{}

    path=S.B.W.PANELS[panel][0]
    raw,_,_,_=S.B.W.load_session_rows(panel,path)
    day={}
    for key,vals in raw.items():
        if vals:
            dt=min(x[0] for x in vals)
            day[(str(key[0]),str(key[1]),str(key[2]))]=dt.date().isoformat()

    q=[]
    missing_day=0
    for r in rows:
        key=(str(r["cohort"]),str(r["session"]),str(r["iid"]))
        if key not in day:
            missing_day+=1
            continue
        z=dict(r);z["source_day"]=day[key];q.append(z)

    # cohort-day peer daily means, equal peer-individual weighting.
    peer_daily=collections.defaultdict(lambda:collections.defaultdict(list))
    for r in q:
        peer_daily[(str(r["cohort"]),str(r["source_day"]))][str(r["iid"])].append(float(r["A"]))
    peer_daily_mean={
      cd:{iid:float(np.mean(vals)) for iid,vals in by.items()}
      for cd,by in peer_daily.items()
    }

    adjusted=[]
    peer_counts=[]
    for r in q:
        cd=(str(r["cohort"]),str(r["source_day"]))
        iid=str(r["iid"])
        peers=[v for j,v in peer_daily_mean[cd].items() if j!=iid]
        if len(peers)<2:continue
        z=dict(r)
        z["peer_day_mean"]=float(np.mean(peers))
        z["A_star"]=float(r["A"]-z["peer_day_mean"])
        z["n_peer_individuals"]=len(peers)
        adjusted.append(z)
        peer_counts.append(len(peers))

    support={
      "original_policy_sessions":len(rows),
      "sessions_with_source_day":len(q),
      "missing_source_day_sessions":missing_day,
      "peer_day_adjusted_sessions":len(adjusted),
      "peer_day_coverage_fraction":len(adjusted)/len(rows) if rows else None,
      "peer_individual_count_summary":{
        "min":int(min(peer_counts)) if peer_counts else None,
        "median":float(np.median(peer_counts)) if peer_counts else None,
        "max":int(max(peer_counts)) if peer_counts else None,
      },
    }
    return adjusted,audit,support

def series(panel):
    rows,audit,support=prepared_adjusted(panel)
    if rows is None:return None,audit,support
    by=collections.defaultdict(list)
    for r in rows:
        by[(str(r["cohort"]),str(r["iid"]))].append(
            (float(r["start"]),float(r["A_star"]),str(r["source_day"]))
        )
    out={}
    for k,v in by.items():
        vv=sorted(v,key=lambda x:x[0])
        if len(vv)>=4:out[k]=vv
    support={**support,
             "eligible_individuals_pre_pair_filter":len(out),
             "adjusted_sessions_by_eligible_individual":{
               "::".join(k):len(v) for k,v in sorted(out.items())
             }}
    return out,audit,support

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
    vals={};pairs=[]
    for k,v in by.items():
        q,d=ri(v)
        if q is None:continue
        vals["::".join(k)]=q
        for p,g in zip(d["products"],d["gaps"]):
            pairs.append((p/d["den"],g))
    if len(vals)<3:return None,{},pairs
    return float(np.mean(list(vals.values()))),vals,pairs

def permute(by,rng):
    out={}
    for k,v in by.items():
        t=[x[0] for x in v];days=[x[2] for x in v]
        a=np.asarray([x[1] for x in v],float).copy()
        rng.shuffle(a)
        out[k]=[(tt,float(aa),dd) for tt,aa,dd in zip(t,a,days)]
    return out

def run(year,panel):
    by,audit,support=series(panel)
    if by is None:return {"status":"STOP_SUPPORT","audit":audit,**support}
    obs,ind,pairs=stat(by)
    if obs is None:return {"status":"STOP_OBSERVED_SUPPORT","audit":audit,**support}
    if len(ind)<MIN_INDIVIDUALS or len(pairs)<MIN_PAIRS:
        return {"status":"STOP_STRUCTURAL_SUPPORT","audit":audit,**support,
                "n_evaluable_individuals":len(ind),"n_adjacent_pairs":len(pairs)}

    rng=np.random.default_rng(SEEDS[year]);null=[]
    for _ in range(NPERM):
        q,_,_=stat(permute(by,rng))
        if q is not None and math.isfinite(q):null.append(q)
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs))/(1+len(a))) if len(a) else None

    gaps=np.asarray([g for _,g in pairs],float)
    med=float(np.median(gaps))
    short=[x for x,g in pairs if g<=med]
    long=[x for x,g in pairs if g>med]
    pos=sum(v>0 for v in ind.values())

    return {
      "status":"DONE" if len(a)>=MIN_VALID else "STOP_RANDOMIZATION_SUPPORT",
      "audit":audit,
      **support,
      "R_peerday":float(obs),
      "individual_R":ind,
      "positive_individuals":pos,
      "n_individuals":len(ind),
      "positive_fraction":pos/len(ind),
      "n_adjacent_pairs":len(pairs),
      "gap_seconds":{"min":float(gaps.min()),"median":med,"max":float(gaps.max())},
      "short_gap_mean_normalized_product":float(np.mean(short)) if short else None,
      "long_gap_mean_normalized_product":float(np.mean(long)) if long else None,
      "requested_permutations":NPERM,
      "valid_permutations":int(len(a)),
      "seed":SEEDS[year],
      "null_mean":float(a.mean()) if len(a) else None,
      "null_q025":float(np.quantile(a,.025)) if len(a) else None,
      "null_q975":float(np.quantile(a,.975)) if len(a) else None,
      "p_one_sided":p,
      "diagnostic_verdict":"SUPPORTED_PEER_DAY_ADJUSTED_STATE"
        if (len(a)>=MIN_VALID and obs>0 and p is not None and p<=.05)
        else "UNSUPPORTED_PEER_DAY_ADJUSTED_STATE"
    }

def main():
    print(json.dumps({
      "contract":"PEER_DAY_ADJUSTED_STATE_CONTRACT_V1.md",
      "status":"POST_OUTCOME_DYNAMIC_STATE_FALSIFICATION_DIAGNOSTIC",
      "years":{y:run(y,p) for y,p in S.PANELS.items()}
    },ensure_ascii=False,indent=2))

if __name__=="__main__":main()
