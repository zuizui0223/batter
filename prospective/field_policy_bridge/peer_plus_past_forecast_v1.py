#!/usr/bin/env python3
from __future__ import annotations
import collections,importlib.util,json,math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("BV",HERE/"phyllostomus_fixed_bin_bivariate_carrier_v1.py")
BV=importlib.util.module_from_spec(spec);spec.loader.exec_module(BV)

NPERM=9999
SEEDS={"2022":202610052001,"2023":202610052002}

def rows(panel):
    x,audit=BV.B.prepare(panel)
    if not x or not audit["colony_retention_pass"]:return None,audit
    rr=BV.standardize_2d(x)
    path=BV.B.W.PANELS[panel][0]
    raw,_,_,_=BV.B.W.load_session_rows(panel,path)
    meta={}
    for k,v in raw.items():
        if v:
            t=min(z[0] for z in v)
            meta[(str(k[0]),str(k[1]),str(k[2]))]=(t.timestamp(),t.date().isoformat())
    q=[]
    for r in rr:
        k=(str(r["cohort"]),str(r["session"]),str(r["iid"]))
        if k in meta:
            t,d=meta[k]
            q.append({"cohort":str(r["cohort"]),"iid":str(r["iid"]),"session":str(r["session"]),
                      "start":float(t),"day":d,"policy":np.asarray(r["policy2"],float)})
    # equal-individual peer-day means
    byday=collections.defaultdict(lambda:collections.defaultdict(list))
    for r in q:byday[(r["cohort"],r["day"])][r["iid"]].append(r["policy"])
    means={k:{i:np.mean(np.vstack(v),axis=0) for i,v in d.items()} for k,d in byday.items()}
    out=[]
    for r in q:
        d=means[(r["cohort"],r["day"])]
        peers=[v for i,v in d.items() if i!=r["iid"]]
        if len(peers)<2:continue
        z=dict(r);z["resid"]=r["policy"]-np.mean(np.vstack(peers),axis=0);out.append(z)
    return out,audit

def stat(rr,labels):
    by=collections.defaultdict(list)
    for r,l in zip(rr,labels):by[(r["cohort"],l)].append(r)
    imp=collections.defaultdict(list);sse0=[];sse1=[]
    for key,v in by.items():
        v=sorted(v,key=lambda r:(r["start"],r["session"]))
        for k in range(len(v)):
            prior=[p["resid"] for p in v[:k] if p["start"]<v[k]["start"]]
            if len(prior)<2:continue
            pred=np.mean(np.vstack(prior),axis=0);y=v[k]["resid"]
            e0=float(y@y);e1=float((y-pred)@(y-pred))
            imp[key].append(e0-e1);sse0.append(e0);sse1.append(e1)
    ind={"::".join(k):float(np.mean(v)) for k,v in imp.items() if v}
    if len(ind)<3 or not sse0 or sum(sse0)<=0:return None
    return {"Delta":float(np.mean(list(ind.values()))),"individual_Delta":ind,
            "R2_pooled":float(1-sum(sse1)/sum(sse0)),"n_targets":len(sse0)}

def perm_labels(rr,rng):
    out=[r["iid"] for r in rr]
    clusters=collections.defaultdict(lambda:collections.defaultdict(list))
    for idx,r in enumerate(rr):clusters[(r["cohort"],r["day"])][r["iid"]].append(idx)
    for _,d in clusters.items():
        ids=sorted(d);p=list(rng.permutation(np.asarray(ids,dtype=object)))
        for old,new in zip(ids,p):
            for idx in d[old]:out[idx]=str(new)
    return out

def run(year,panel):
    rr,audit=rows(panel)
    if rr is None:return {"status":"STOP_SUPPORT","audit":audit}
    labs=[r["iid"] for r in rr];obs=stat(rr,labs)
    if obs is None:return {"status":"STOP_OBSERVED","audit":audit}
    rng=np.random.default_rng(SEEDS[year]);null=[]
    for _ in range(NPERM):
        q=stat(rr,perm_labels(rr,rng))
        if q is not None and math.isfinite(q["Delta"]):null.append(q["Delta"])
    a=np.asarray(null,float);p=float((1+np.sum(a>=obs["Delta"]))/(1+len(a)))
    pos=sum(v>0 for v in obs["individual_Delta"].values());n=len(obs["individual_Delta"])
    return {"status":"DONE","peer_controlled_sessions":len(rr),**obs,
            "positive_individuals":pos,"n_individuals":n,"positive_fraction":pos/n,
            "valid_permutations":len(a),"p_one_sided":p,"null_mean":float(a.mean()),
            "null_q025":float(np.quantile(a,.025)),"null_q975":float(np.quantile(a,.975)),
            "diagnostic_verdict":"SUPPORTED_PEER_PLUS_PAST" if obs["Delta"]>0 and p<=.05 and pos/n>=.70 else "UNSUPPORTED_PEER_PLUS_PAST"}

def main():
    print(json.dumps({"contract":"PEER_PLUS_PAST_FORECAST_V1.md",
      "years":{y:run(y,p) for y,p in BV.PANELS.items()}},indent=2))
if __name__=="__main__":main()
