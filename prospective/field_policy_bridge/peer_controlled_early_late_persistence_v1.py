#!/usr/bin/env python3
"""Peer-controlled early-to-late persistent individual allocation policy."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"peer_controlled_state_persistence_v1.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)

NPERM=9999
MIN_VALID=9500
PANELS=P.PANELS
SEEDS={"2022":202610051561,"2023":202610051562}

def ranks_average(x):
    x=np.asarray(x,float)
    o=np.argsort(x,kind="mergesort")
    r=np.empty(len(x),float)
    i=0
    while i<len(o):
        j=i+1
        while j<len(o) and x[o[j]]==x[o[i]]:j+=1
        rr=(i+1+j)/2.0
        r[o[i:j]]=rr
        i=j
    return r

def spearman(x,y):
    if len(x)<3:return None
    rx=ranks_average(x);ry=ranks_average(y)
    if np.std(rx,ddof=1)<=0 or np.std(ry,ddof=1)<=0:return None
    return float(np.corrcoef(rx,ry)[0,1])

def prepare(panel):
    by,audit=P.residual_series(panel,12)
    if by is None:return None,audit
    d={}
    for (co,iid),v in by.items():
        vv=sorted(v,key=lambda x:x[0])
        n=len(vv)
        cut=n//2
        if n<4 or cut<2 or n-cut<2:continue
        early=np.asarray([x[1] for x in vv[:cut]],float)
        late=np.asarray([x[1] for x in vv[cut:]],float)
        d[(co,iid)]={
          "early":early,"late":late,
          "early_mean":float(early.mean()),"late_mean":float(late.mean()),
          "n_early":len(early),"n_late":len(late)
        }
    return d,audit

def stat(d,early_label_map=None):
    # early_label_map maps (co,source_iid)->target_iid; observed is identity.
    byco=collections.defaultdict(list)
    for k in d:byco[k[0]].append(k)
    indiv={}
    target_count=0
    for co,keys in byco.items():
        # Build assigned early centroids by target label.
        cent={}
        for key in keys:
            src=key[1]
            lab=early_label_map.get(key,src) if early_label_map is not None else src
            cent[lab]=d[key]["early_mean"]
        for key in keys:
            iid=key[1]
            if iid not in cent:continue
            donors=[b for b in cent if b!=iid]
            if len(donors)<2:continue
            vals=[]
            for z in d[key]["late"]:
                ds=abs(float(z)-cent[iid])
                do=float(np.mean([abs(float(z)-cent[b]) for b in donors]))
                vals.append(do-ds)
            if vals:
                indiv[f"{co}::{iid}"]=float(np.mean(vals))
                target_count+=len(vals)
    if len(indiv)<3:return None,{},target_count
    return float(np.mean(list(indiv.values()))),indiv,target_count

def perm_map(d,rng):
    byco=collections.defaultdict(list)
    for k in d:byco[k[0]].append(k)
    mp={}
    for co,keys in byco.items():
        keys=sorted(keys)
        labs=[k[1] for k in keys]
        perm=list(rng.permutation(np.asarray(labs,dtype=object)))
        for key,lab in zip(keys,perm):mp[key]=str(lab)
    return mp

def rank_stat(d):
    byco=collections.defaultdict(list)
    for (co,iid),q in d.items():
        byco[co].append((q["early_mean"],q["late_mean"]))
    vals=[]
    detail={}
    for co,v in sorted(byco.items()):
        rho=spearman([x for x,y in v],[y for x,y in v])
        detail[co]={"n":len(v),"rho":rho}
        if rho is not None:vals.append(rho)
    return {"cohorts":detail,"equal_cohort_mean_rho":float(np.mean(vals)) if vals else None}

def run(year,panel):
    d,audit=prepare(panel)
    if d is None:return {"status":"STOP_SUPPORT","audit":audit}
    obs,ind,nt=stat(d)
    if obs is None:return {"status":"STOP_OBSERVED_SUPPORT","eligible_individuals":len(d)}
    rng=np.random.default_rng(SEEDS[year]);null=[]
    for _ in range(NPERM):
        q,_,_=stat(d,perm_map(d,rng))
        if q is not None and math.isfinite(q):null.append(q)
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs))/(1+len(a))) if len(a) else None
    pos=sum(v>0 for v in ind.values());frac=pos/len(ind)
    support=[{
      "cohort":co,"individual":iid,
      "n_early":q["n_early"],"n_late":q["n_late"],
      "early_mean":q["early_mean"],"late_mean":q["late_mean"]
    } for (co,iid),q in sorted(d.items())]
    supported=bool(len(a)>=MIN_VALID and obs>0 and p is not None and p<=.05 and frac>=.70)
    return {
      "status":"DONE" if len(a)>=MIN_VALID else "STOP_RANDOMIZATION_SUPPORT",
      "K_early_to_late":float(obs),
      "individual_K":ind,
      "positive_individuals":pos,"n_individuals":len(ind),"positive_fraction":frac,
      "n_late_targets":nt,
      "support":support,
      "rank_secondary":rank_stat(d),
      "requested_permutations":NPERM,"valid_permutations":int(len(a)),
      "seed":SEEDS[year],
      "null_mean":float(a.mean()) if len(a) else None,
      "null_q025":float(np.quantile(a,.025)) if len(a) else None,
      "null_q975":float(np.quantile(a,.975)) if len(a) else None,
      "p_one_sided":p,
      "diagnostic_verdict":"SUPPORTED_STABLE_PEER_CONTROLLED_POLICY" if supported else "UNSUPPORTED_STABLE_PEER_CONTROLLED_POLICY"
    }

def main():
    print(json.dumps({
      "contract":"PEER_CONTROLLED_EARLY_LATE_PERSISTENCE_CONTRACT_V1.md",
      "status":"POST_OUTCOME_STABLE_POLICY_DIAGNOSTIC",
      "years":{y:run(y,p) for y,p in PANELS.items()}
    },ensure_ascii=False,indent=2))

if __name__=="__main__":main()
