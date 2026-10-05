#!/usr/bin/env python3
"""Leave-one-session residual individual identity after peer-day adjustment."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("D",HERE/"peer_day_adjusted_state_v1.py")
D=importlib.util.module_from_spec(spec);spec.loader.exec_module(D)

NPERM=9999
MIN_VALID=9500
SEEDS={"2022":202610051571,"2023":202610051572}

def rows(panel):
    rr,audit,support=D.prepared_adjusted(panel)
    if rr is None:return None,audit,support
    out=[]
    for r in rr:
        out.append({
          "cohort":str(r["cohort"]),
          "iid":str(r["iid"]),
          "A_star":float(r["A_star"]),
          "start":float(r["start"]),
          "source_day":str(r["source_day"]),
        })
    return out,audit,support

def stat(rr,labels):
    byco=collections.defaultdict(list)
    for i,r in enumerate(rr):byco[r["cohort"]].append(i)
    vals=collections.defaultdict(list)

    for co,idxs in byco.items():
        groups=collections.defaultdict(list)
        for i in idxs:
            groups[labels[i]].append(i)
        eligible={b for b,ii in groups.items() if len(ii)>=2}
        if len(eligible)<3:continue

        cent={}
        for b in eligible:
            cent[b]=float(np.mean([rr[i]["A_star"] for i in groups[b]]))

        for i in idxs:
            b=labels[i]
            if b not in eligible:continue
            self_idx=[j for j in groups[b] if j!=i]
            if not self_idx:continue
            donors=[d for d in eligible if d!=b]
            if len(donors)<2:continue
            z=rr[i]["A_star"]
            selfc=float(np.mean([rr[j]["A_star"] for j in self_idx]))
            ds=abs(z-selfc)
            do=float(np.mean([abs(z-cent[d]) for d in donors]))
            vals[(co,b)].append(do-ds)

    ind={"::".join(k):float(np.mean(v)) for k,v in vals.items() if v}
    if len(ind)<3:return None,{}
    return float(np.mean(list(ind.values()))),ind

def permute_labels(rr,rng):
    labs=[r["iid"] for r in rr]
    out=list(labs)
    byco=collections.defaultdict(list)
    for i,r in enumerate(rr):byco[r["cohort"]].append(i)
    for idxs in byco.values():
        x=np.asarray([labs[i] for i in idxs],dtype=object)
        rng.shuffle(x)
        for k,i in enumerate(idxs):out[i]=str(x[k])
    return out

def run(year,panel):
    rr,audit,support=rows(panel)
    if rr is None:return {"status":"STOP_SUPPORT","audit":audit,**support}
    obslabels=[r["iid"] for r in rr]
    obs,ind=stat(rr,obslabels)
    if obs is None:return {"status":"STOP_OBSERVED_SUPPORT","audit":audit,**support}
    rng=np.random.default_rng(SEEDS[year]);null=[]
    for _ in range(NPERM):
        q,_=stat(rr,permute_labels(rr,rng))
        if q is not None and math.isfinite(q):null.append(q)
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs))/(1+len(a))) if len(a) else None
    pos=sum(v>0 for v in ind.values());frac=pos/len(ind)
    supported=bool(len(a)>=MIN_VALID and obs>0 and p is not None and p<=.05 and frac>=.70)
    return {
      "status":"DONE" if len(a)>=MIN_VALID else "STOP_RANDOMIZATION_SUPPORT",
      "audit":audit,**support,
      "K_peerday":float(obs),
      "individual_K":ind,
      "positive_individuals":pos,
      "n_individuals":len(ind),
      "positive_fraction":frac,
      "requested_permutations":NPERM,
      "valid_permutations":int(len(a)),
      "seed":SEEDS[year],
      "null_mean":float(a.mean()) if len(a) else None,
      "null_q025":float(np.quantile(a,.025)) if len(a) else None,
      "null_q975":float(np.quantile(a,.975)) if len(a) else None,
      "p_one_sided":p,
      "diagnostic_verdict":"SUPPORTED_PEER_DAY_RESIDUAL_IDENTITY" if supported else "UNSUPPORTED_PEER_DAY_RESIDUAL_IDENTITY"
    }

def main():
    print(json.dumps({
      "contract":"PEER_DAY_RESIDUAL_IDENTITY_CONTRACT_V1.md",
      "status":"POST_OUTCOME_STABLE_COMPONENT_FALSIFICATION",
      "years":{y:run(y,p) for y,p in D.S.PANELS.items()}
    },ensure_ascii=False,indent=2))

if __name__=="__main__":main()
