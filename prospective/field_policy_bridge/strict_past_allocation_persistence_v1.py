#!/usr/bin/env python3
"""Strict-past field allocation persistence in P. hastatus."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("B",HERE/"phyllostomus_fixed_bin_harmonization_v2.py")
B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)

NPERM=9999
MIN_VALID=9500
PANELS={"2022":"phyllostomus_2022","2023":"phyllostomus_2023"}
SEEDS={"2022":202610051511,"2023":202610051512}

def prepared_rows(panel):
    rows,audit=B.prepare(panel)
    if not rows or not audit["colony_retention_pass"]:
        return None,audit
    h=B.standardize(rows,"F2_raw","H")
    v=B.standardize(rows,"F3_raw","V")
    if h is None or v is None:return None,audit

    path=B.W.PANELS[panel][0]
    raw,_,_,_=B.W.load_session_rows(panel,path)
    t0={}
    for key,vals in raw.items():
        if vals:
            t0[key]=min(x[0] for x in vals).timestamp()

    out=[]
    for a,b in zip(h,v):
        key=(a["cohort"],a["session"],a["iid"])
        if (a["cohort"],a["session"],a["iid"])!=(b["cohort"],b["session"],b["iid"]):
            raise RuntimeError("row alignment drift")
        if key not in t0:
            raise RuntimeError(f"missing session start {key}")
        H=float(a["H"]);V=float(b["V"])
        q=dict(a)
        q["A"]=(H-V)/math.sqrt(2.0)
        q["start"]=float(t0[key])
        out.append(q)
    return out,audit

def cohort_arrays(rows):
    out={}
    for co in sorted({r["cohort"] for r in rows}):
        rr=[r for r in rows if r["cohort"]==co]
        # stable order by start then session/id only as deterministic tie ordering;
        # equal-time groups are processed simultaneously below.
        rr=sorted(rr,key=lambda r:(r["start"],r["session"],r["iid"]))
        labels=sorted({r["iid"] for r in rr})
        li={b:i for i,b in enumerate(labels)}
        out[co]={
          "rows":rr,
          "labels":labels,
          "obs_label_idx":np.asarray([li[r["iid"]] for r in rr],dtype=np.int16),
          "A":np.asarray([r["A"] for r in rr],float),
          "time":np.asarray([r["start"] for r in rr],float),
        }
    return out

def one_cohort_stat(d,label_idx,min_prior=2,max_history=None):
    A=d["A"];time=d["time"];L=len(d["labels"])
    sums=np.zeros(L,float);counts=np.zeros(L,int)
    hist=[[] for _ in range(L)]
    ksum=np.zeros(L,float);kcount=np.zeros(L,int)
    prior_counts=[]

    # exact-time groups: evaluate before updating any member of group
    starts=np.r_[0,1+np.flatnonzero(np.diff(time)!=0)]
    ends=np.r_[starts[1:],len(time)]
    for a,b in zip(starts,ends):
        # history summary before this time
        if max_history is None:
            means=np.divide(sums,counts,out=np.full(L,np.nan),where=counts>0)
            eligible=counts>=min_prior
        else:
            means=np.full(L,np.nan,float);eligible=np.zeros(L,bool)
            for lab in range(L):
                hv=hist[lab]
                if len(hv)>=min_prior:
                    vv=hv[-max_history:] if max_history is not None else hv
                    means[lab]=float(np.mean(vv));eligible[lab]=True

        for i in range(a,b):
            lab=int(label_idx[i])
            if not eligible[lab]:continue
            donors=np.flatnonzero(eligible & (np.arange(L)!=lab))
            if len(donors)<2:continue
            z=float(A[i])
            ds=abs(z-float(means[lab]))
            do=float(np.mean(np.abs(z-means[donors])))
            K=do-ds
            ksum[lab]+=K;kcount[lab]+=1
            prior_counts.append(int(counts[lab]) if max_history is None else min(len(hist[lab]),max_history))

        # now update all histories at this timestamp
        for i in range(a,b):
            lab=int(label_idx[i]);z=float(A[i])
            sums[lab]+=z;counts[lab]+=1;hist[lab].append(z)

    ind={d["labels"][lab]:float(ksum[lab]/kcount[lab]) for lab in range(L) if kcount[lab]>0}
    return ind,prior_counts

def full_stat(struct,maps,min_prior=2,max_history=None):
    allind={}
    allprior=[]
    nt=0
    for co,d in struct.items():
        ind,pc=one_cohort_stat(d,maps[co],min_prior=min_prior,max_history=max_history)
        for lab,v in ind.items():
            allind[f"{co}:{lab}"]=v
        allprior.extend(pc);nt+=len(pc)
    if len(allind)<3:return None,{},nt,allprior
    return float(np.mean(list(allind.values()))),allind,nt,allprior

def perm_maps(struct,rng):
    out={}
    for co,d in struct.items():
        x=d["obs_label_idx"].copy()
        rng.shuffle(x)
        out[co]=x
    return out

def run(year,panel):
    rows,audit=prepared_rows(panel)
    if rows is None:return {"status":"STOP_SUPPORT","audit":audit}
    st=cohort_arrays(rows)
    obsmap={co:d["obs_label_idx"] for co,d in st.items()}
    obs,ind,nt,pc=full_stat(st,obsmap,min_prior=2,max_history=None)
    if obs is None:return {"status":"STOP_OBSERVED_SUPPORT"}

    rng=np.random.default_rng(SEEDS[year]);null=[]
    for _ in range(NPERM):
        q,_,_,_=full_stat(st,perm_maps(st,rng),min_prior=2,max_history=None)
        if q is not None and math.isfinite(q):null.append(q)
    a=np.asarray(null,float)
    pos=sum(v>0 for v in ind.values());frac=pos/len(ind)
    p=float((1+np.sum(a>=obs))/(1+len(a))) if len(a) else None

    recent={}
    for h in (1,2):
        q,qi,qnt,qpc=full_stat(st,obsmap,min_prior=h,max_history=h)
        recent[str(h)]={
          "K":q,"individual_K":qi,"n_targets":qnt,
          "positive_individuals":sum(v>0 for v in qi.values()),
          "n_individuals":len(qi),
          "positive_fraction":(sum(v>0 for v in qi.values())/len(qi)) if qi else None,
        }

    supported=bool(len(a)>=MIN_VALID and obs>0 and p is not None and p<=.05 and frac>=.70)
    return {
      "status":"DONE" if len(a)>=MIN_VALID else "STOP_RANDOMIZATION_SUPPORT",
      "K_past":float(obs),"individual_K":ind,
      "positive_individuals":pos,"n_individuals":len(ind),"positive_fraction":frac,
      "n_targets":nt,
      "prior_self_count_summary":{
        "min":int(min(pc)) if pc else None,
        "median":float(np.median(pc)) if pc else None,
        "max":int(max(pc)) if pc else None,
      },
      "valid_permutations":int(len(a)),"requested_permutations":NPERM,
      "seed":SEEDS[year],
      "null_mean":float(a.mean()) if len(a) else None,
      "null_q025":float(np.quantile(a,.025)) if len(a) else None,
      "null_q975":float(np.quantile(a,.975)) if len(a) else None,
      "p_one_sided":p,
      "recent_history_sensitivity":recent,
      "diagnostic_verdict":"SUPPORTED_STRICT_PAST_MAINTENANCE" if supported else "UNSUPPORTED_STRICT_PAST_MAINTENANCE"
    }

def main():
    print(json.dumps({
      "contract":"STRICT_PAST_ALLOCATION_PERSISTENCE_CONTRACT_V1.md",
      "status":"POST_OUTCOME_TEMPORAL_MAINTENANCE_DIAGNOSTIC",
      "years":{y:run(y,p) for y,p in PANELS.items()}
    },ensure_ascii=False,indent=2))

if __name__=="__main__":main()
