#!/usr/bin/env python3
"""Post-primary early-seed vs recent-history ontogenetic diagnostic."""
from __future__ import annotations
import importlib.util,json,math
from collections import defaultdict
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"source_b_self_history_outcome_from_bridge_v1.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)

TARGETS=range(11,21)
N_PERM=9999
SEED=202610061001

def prepare(data):
    events=[];primary={}
    for cohort,people in data.items():
        complete=sorted([n for n,d in people.items() if len(d)>=20])
        primary[cohort]=complete
        if not complete:continue
        if len(complete)<4:raise RuntimeError(f"{cohort}: <4 complete juveniles")
        for target_name in complete:
            for t in TARGETS:
                tidx=t-1
                target=people[target_name][tidx]
                donors=[];de=[];dr=[]
                for donor in sorted(people):
                    if len(people[donor])<t:continue
                    early=people[donor][0:2]
                    recent=people[donor][tidx-2:tidx]
                    if len(early)!=2 or len(recent)!=2:continue
                    donors.append(donor)
                    de.append(P.mean_min_dist(target,early))
                    dr.append(P.mean_min_dist(target,recent))
                if target_name not in donors:raise RuntimeError(f"self absent {cohort}/{target_name}/t{t}")
                if len(donors)<4:raise RuntimeError(f"<4 donors {cohort}/{target_name}/t{t}")
                events.append({"cohort":cohort,"target":target_name,"t":t,
                               "donors":donors,"D_early":np.asarray(de,float),"D_recent":np.asarray(dr,float)})
    return events,primary

def advantage(ev,assigned,key):
    names=ev["donors"]
    if assigned not in names:raise RuntimeError("assigned pseudo-self absent")
    D=ev[key];j=names.index(assigned)
    other=(float(D.sum())-float(D[j]))/(len(D)-1)
    return other-float(D[j])

def identity(primary):
    return {c:{n:n for n in names} for c,names in primary.items()}

def perm(primary,rng):
    out={}
    for c,names in primary.items():
        p=list(rng.permutation(np.asarray(names,dtype=object)))
        out[c]={n:str(p[i]) for i,n in enumerate(names)}
    return out

def summarize(events,mapping):
    by=defaultdict(list)
    for ev in events:
        assigned=mapping[ev["cohort"]][ev["target"]]
        re=advantage(ev,assigned,"D_early")
        rr=advantage(ev,assigned,"D_recent")
        by[(ev["cohort"],ev["target"])].append((re,rr))
    ind=[]
    for (co,n),vals in sorted(by.items()):
        e=float(np.mean([x for x,_ in vals]))
        r=float(np.mean([y for _,y in vals]))
        q=r-e
        ind.append({"cohort":co,"individual":n,"E_i":e,"R_recent_i":r,"Q_i":q})
    E=float(np.mean([x["E_i"] for x in ind]))
    R=float(np.mean([x["R_recent_i"] for x in ind]))
    Q=float(np.mean([x["Q_i"] for x in ind]))
    return E,R,Q,ind

def calib(obs,null):
    a=np.asarray(null,float)
    return {"observed":float(obs),"null_mean":float(a.mean()),
            "excess":float(obs-a.mean()),
            "null_q025":float(np.quantile(a,.025)),
            "null_q975":float(np.quantile(a,.975)),
            "p_one_sided":float((1+np.sum(a>=obs))/(1+len(a)))}

def main():
    data,manifest=P.load_all()
    events,primary=prepare(data)
    E,R,Q,ind=summarize(events,identity(primary))
    n=len(ind)
    if n<5:raise RuntimeError("overall <5 juveniles")
    rng=np.random.default_rng(SEED);en=[];qn=[]
    for _ in range(N_PERM):
        e,r,q,_=summarize(events,perm(primary,rng));en.append(e);qn.append(q)
    ce=calib(E,en);cq=calib(Q,qn)
    posE=sum(x["E_i"]>0 for x in ind);posQ=sum(x["Q_i"]>0 for x in ind)
    need=math.ceil(.70*n)
    supportE=ce["excess"]>0 and ce["p_one_sided"]<=.05 and posE>=need
    supportQ=cq["excess"]>0 and cq["p_one_sided"]<=.05 and posQ>=need
    print(json.dumps({
      "contract":"EARLY_SEED_VS_RECENT_HISTORY_DIAGNOSTIC_V1.md",
      "status":"POST_PRIMARY_ONTOGENETIC_MECHANISM_DIAGNOSTIC",
      "n_individuals":n,"n_targets":len(events),
      "target_ordinals":"11-20","history_days_each":2,
      "early_seed":{
        **ce,"positive_individuals":posE,"required_positive":need,
        "positive_fraction":posE/n,
        "diagnostic_verdict":"SUPPORTED_EARLY_SEED_PERSISTENCE" if supportE else "UNSUPPORTED_EARLY_SEED_PERSISTENCE"
      },
      "recent_vs_early":{
        **cq,"recent_programme_mean":R,
        "positive_individuals":posQ,"required_positive":need,
        "positive_fraction":posQ/n,
        "diagnostic_verdict":"SUPPORTED_IDENTITY_SPECIFIC_REFINEMENT" if supportQ else "UNSUPPORTED_IDENTITY_SPECIFIC_REFINEMENT"
      },
      "individuals":ind,
      "permutations":N_PERM,"seed":SEED
    },indent=2))

if __name__=="__main__":main()
