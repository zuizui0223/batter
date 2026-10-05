#!/usr/bin/env python3
"""Older-than-latest strict-past allocation persistence in P. hastatus."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("S",HERE/"strict_past_allocation_persistence_v1.py")
S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)

NPERM=9999
MIN_VALID=9500
SEEDS={"2022":202610051521,"2023":202610051522}
PANELS=S.PANELS

def one_cohort(d,label_idx,min_older=1):
    A=d["A"];time=d["time"];L=len(d["labels"])
    hist=[[] for _ in range(L)]
    ksum=np.zeros(L,float);kcount=np.zeros(L,int)
    starts=np.r_[0,1+np.flatnonzero(np.diff(time)!=0)]
    ends=np.r_[starts[1:],len(time)]

    for a,b in zip(starts,ends):
        means=np.full(L,np.nan,float);eligible=np.zeros(L,bool)
        for lab in range(L):
            hv=hist[lab]
            if len(hv)-1>=min_older:
                means[lab]=float(np.mean(hv[:-1]))
                eligible[lab]=True

        for i in range(a,b):
            lab=int(label_idx[i])
            if not eligible[lab]:continue
            donors=np.flatnonzero(eligible & (np.arange(L)!=lab))
            if len(donors)<2:continue
            z=float(A[i])
            K=float(np.mean(np.abs(z-means[donors]))-abs(z-means[lab]))
            ksum[lab]+=K;kcount[lab]+=1

        for i in range(a,b):
            hist[int(label_idx[i])].append(float(A[i]))

    ind={d["labels"][lab]:float(ksum[lab]/kcount[lab]) for lab in range(L) if kcount[lab]>0}
    return ind,int(np.sum(kcount))

def full_stat(st,maps,min_older=1):
    indall={};nt=0
    for co,d in st.items():
        ind,n=one_cohort(d,maps[co],min_older=min_older);nt+=n
        for lab,v in ind.items():indall[f"{co}:{lab}"]=v
    if len(indall)<3:return None,{},nt
    return float(np.mean(list(indall.values()))),indall,nt

def run(year,panel):
    rows,audit=S.prepared_rows(panel)
    if rows is None:return {"status":"STOP_SUPPORT","audit":audit}
    st=S.cohort_arrays(rows)
    obsmap={co:d["obs_label_idx"] for co,d in st.items()}
    obs,ind,nt=full_stat(st,obsmap,min_older=1)
    if obs is None:return {"status":"STOP_OBSERVED_SUPPORT"}

    rng=np.random.default_rng(SEEDS[year]);null=[]
    for _ in range(NPERM):
        q,_,_=full_stat(st,S.perm_maps(st,rng),min_older=1)
        if q is not None and math.isfinite(q):null.append(q)
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs))/(1+len(a))) if len(a) else None
    pos=sum(v>0 for v in ind.values());frac=pos/len(ind)

    strict2,ind2,nt2=full_stat(st,obsmap,min_older=2)
    supported=bool(len(a)>=MIN_VALID and obs>0 and p is not None and p<=.05 and frac>=.70)
    return {
      "status":"DONE" if len(a)>=MIN_VALID else "STOP_RANDOMIZATION_SUPPORT",
      "K_older":float(obs),"individual_K":ind,
      "positive_individuals":pos,"n_individuals":len(ind),"positive_fraction":frac,
      "n_targets":nt,
      "valid_permutations":int(len(a)),"requested_permutations":NPERM,
      "seed":SEEDS[year],
      "null_mean":float(a.mean()) if len(a) else None,
      "null_q025":float(np.quantile(a,.025)) if len(a) else None,
      "null_q975":float(np.quantile(a,.975)) if len(a) else None,
      "p_one_sided":p,
      "stricter_ge2_older_observed":{
        "K":strict2,"individual_K":ind2,"n_targets":nt2,
        "positive_individuals":sum(v>0 for v in ind2.values()),
        "n_individuals":len(ind2),
        "positive_fraction":(sum(v>0 for v in ind2.values())/len(ind2)) if ind2 else None
      },
      "diagnostic_verdict":"SUPPORTED_OLDER_HISTORY_PERSISTENCE" if supported else "UNSUPPORTED_OLDER_HISTORY_PERSISTENCE"
    }

def main():
    print(json.dumps({
      "contract":"OLDER_HISTORY_ALLOCATION_PERSISTENCE_CONTRACT_V1.md",
      "status":"POST_OUTCOME_TEMPORAL_MAINTENANCE_FALSIFICATION",
      "years":{y:run(y,p) for y,p in PANELS.items()}
    },ensure_ascii=False,indent=2))
if __name__=="__main__":main()
