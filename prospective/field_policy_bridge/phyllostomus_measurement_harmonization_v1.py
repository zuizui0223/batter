#!/usr/bin/env python3
"""Post-outcome 360-s harmonization diagnostics for P. hastatus 2022 vs 2023."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("W",HERE/"wild_flight_intensity_persistence_v1.py")
W=importlib.util.module_from_spec(spec);spec.loader.exec_module(W)

LAG=360.0
MIN_LAG_INTERVALS=30
NPERM=9999

PANELS={
    "2022":("phyllostomus_2022",202610051421,202610051423,202610051425),
    "2023":("phyllostomus_2023",202610051422,202610051424,202610051426),
}

def exact_lag_features(vals):
    # vals = (datetime,x,y,z); first duplicate timestamp retained.
    vals=sorted(vals,key=lambda x:x[0])
    first={}
    for v in vals:
        first.setdefault(v[0],v)
    times=sorted(first)
    lookup={t:first[t] for t in times}
    s3=[]; sh=[]; sv=[]
    from datetime import timedelta
    delta=timedelta(seconds=int(LAG))
    for t in times:
        t2=t+delta
        if t2 not in lookup:continue
        a=lookup[t];b=lookup[t2]
        dx=b[1]-a[1];dy=b[2]-a[2];dz=b[3]-a[3]
        if not all(math.isfinite(float(x)) for x in (dx,dy,dz)):continue
        sh.append(math.hypot(dx,dy)/LAG)
        s3.append(math.sqrt(dx*dx+dy*dy+dz*dz)/LAG)
        sv.append(abs(dz)/LAG)
    if len(s3)<MIN_LAG_INTERVALS:
        return None,len(s3)
    a=np.asarray(s3,float);h=np.asarray(sh,float);v=np.asarray(sv,float)
    return {
      "I360_raw":np.asarray([np.median(a),np.percentile(a,90),np.median(v),np.percentile(v,90)],float),
      "IH_raw":np.asarray([np.median(h),np.percentile(h,90)],float),
      "IV_raw":np.asarray([np.median(v),np.percentile(v,90)],float),
    },len(s3)

def prepare(panel):
    path=W.PANELS[panel][0]
    by,pre,nfail,hf=W.load_session_rows(panel,path)
    rows=[]
    for (co,sid,iid),vals in sorted(by.items()):
        f,n=exact_lag_features(vals)
        if f is None:continue
        rows.append({"cohort":co,"session":sid,"iid":iid,"n_lag_intervals":n,**f})
    counts=collections.Counter((r["cohort"],r["iid"]) for r in rows)
    elig={k for k,n in counts.items() if n>=2}
    rows=[r for r in rows if (r["cohort"],r["iid"]) in elig]
    return rows,hf,nfail

def standardize(rows,raw_key,out_key):
    rr=[dict(r) for r in rows]
    for co in sorted(set(r["cohort"] for r in rr)):
        ix=[i for i,r in enumerate(rr) if r["cohort"]==co]
        M=np.vstack([rr[i][raw_key] for i in ix]).astype(float)
        if len(M)<2:return None
        mu=M.mean(axis=0);sd=M.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):return None
        for i in ix:
            z=(rr[i][raw_key]-mu)/sd
            rr[i][out_key]=float(np.mean(z))
    return rr

def stat_scalar(rows,key):
    # Use algebraically same architecture as W.stat, substituting selected scalar.
    tmp=[]
    for r in rows:
        q=dict(r);q["I"]=float(r[key]);tmp.append(q)
    labs=[r["iid"] for r in tmp]
    return W.stat(tmp,labs)

def perm_labels(rows,rng):
    labels=[r["iid"] for r in rows]
    out=list(labels)
    byco=collections.defaultdict(list)
    for i,r in enumerate(rows):byco[r["cohort"]].append(i)
    for idxs in byco.values():
        vals=np.asarray([labels[i] for i in idxs],dtype=object)
        rng.shuffle(vals)
        for j,i in enumerate(idxs):out[i]=str(vals[j])
    return out

def perm_stat(rows,key,seed):
    tmp=[]
    for r in rows:
        q=dict(r);q["I"]=float(r[key]);tmp.append(q)
    obs,ind=W.stat(tmp,[r["iid"] for r in tmp])
    if obs is None:return {"status":"STOP_OBSERVED_SUPPORT"}
    rng=np.random.default_rng(seed);null=[]
    for _ in range(NPERM):
        labs=perm_labels(tmp,rng)
        s,_=W.stat(tmp,labs)
        if s is not None:null.append(s)
    a=np.asarray(null,float)
    pos=sum(v>0 for v in ind.values());n=len(ind)
    p=float((1+np.sum(a>=obs))/(1+len(a)))
    return {
      "status":"DONE","H":float(obs),"individual_H":ind,
      "positive_individuals":pos,"n_individuals":n,
      "positive_fraction":pos/n,
      "n_sessions":len(tmp),
      "valid_permutations":int(len(a)),
      "p_one_sided":p,
      "null_mean":float(a.mean()),
      "null_q025":float(np.quantile(a,.025)),
      "null_q975":float(np.quantile(a,.975)),
      "seed":seed,
    }

def run_year(year,panel,seeds):
    rows,hf,nfail=prepare(panel)
    nind=len(set((r["cohort"],r["iid"]) for r in rows))
    support={"height_field":hf,"numeric_parse_failures":nfail,
             "eligible_individuals":nind,"eligible_sessions":len(rows),
             "lag_intervals_per_session":{
               "median":float(np.median([r["n_lag_intervals"] for r in rows])) if rows else None,
               "min":int(min([r["n_lag_intervals"] for r in rows])) if rows else None,
               "max":int(max([r["n_lag_intervals"] for r in rows])) if rows else None,
             }}
    if nind<5:
        return {"status":"STOP_STRUCTURAL_SUPPORT",**support}
    configs=[("I360_raw","I360",seeds[0]),("IH_raw","IH",seeds[1]),("IV_raw","IV",seeds[2])]
    out={"status":"DONE",**support,"diagnostics":{}}
    for raw,key,seed in configs:
        rr=standardize(rows,raw,key)
        if rr is None:
            out["diagnostics"][key]={"status":"STOP_STANDARDIZATION"}
        else:
            out["diagnostics"][key]=perm_stat(rr,key,seed)
    return out

def main():
    results={}
    for year,(panel,*seeds) in PANELS.items():
        results[year]=run_year(year,panel,seeds)
    out={
      "contract":"PHYLLOSTOMUS_MEASUREMENT_HARMONIZATION_CONTRACT_V1.md",
      "status":"POST_OUTCOME_MEASUREMENT_DIAGNOSTIC",
      "lag_seconds":LAG,
      "minimum_exact_lag_intervals":MIN_LAG_INTERVALS,
      "years":results,
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
