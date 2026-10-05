#!/usr/bin/env python3
"""Fixed-bin 360-s measurement harmonization for P. hastatus 2022/2023."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("W",HERE/"wild_flight_intensity_persistence_v1.py")
W=importlib.util.module_from_spec(spec);spec.loader.exec_module(W)

BIN=360.0
MIN_INTERVALS=20
NPERM=9999
PANELS={
 "2022":("phyllostomus_2022",202610051431,202610051433,202610051435),
 "2023":("phyllostomus_2023",202610051432,202610051434,202610051436),
}

def bin_features(vals):
    bins=collections.defaultdict(list)
    for t,x,y,z in vals:
        try:u=float(t.timestamp())
        except Exception:continue
        if not all(math.isfinite(float(v)) for v in (u,x,y,z)):continue
        b=int(math.floor(u/BIN))
        bins[b].append((float(x),float(y),float(z)))
    centers={}
    for b,rr in bins.items():
        A=np.asarray(rr,float)
        centers[b]=np.median(A,axis=0)
    keys=sorted(centers)
    s3=[];sh=[];sv=[]
    for a,b in zip(keys[:-1],keys[1:]):
        if b-a!=1:continue
        d=centers[b]-centers[a]
        h=float(math.hypot(d[0],d[1]))
        s3.append(float(np.linalg.norm(d)/BIN))
        sh.append(h/BIN)
        sv.append(abs(float(d[2]))/BIN)
    if len(s3)<MIN_INTERVALS:
        return None,{"occupied_bins":len(keys),"consecutive_bin_intervals":len(s3)}
    s3=np.asarray(s3,float);sh=np.asarray(sh,float);sv=np.asarray(sv,float)
    f={
      "F1_raw":np.asarray([np.median(s3),np.percentile(s3,90),np.median(sv),np.percentile(sv,90)],float),
      "F2_raw":np.asarray([np.median(sh),np.percentile(sh,90)],float),
      "F3_raw":np.asarray([np.median(sv),np.percentile(sv,90)],float),
    }
    return f,{"occupied_bins":len(keys),"consecutive_bin_intervals":len(s3)}

def original_repeat_by_cohort(panel):
    path=W.PANELS[panel][0]
    sessions,_=W.prepare(panel,path)
    c=collections.Counter((s["cohort"],s["iid"]) for s in sessions)
    out=collections.Counter()
    for (co,iid),n in c.items():
        if n>=2:out[co]+=1
    return dict(out)

def prepare(panel):
    path=W.PANELS[panel][0]
    by,pre,nfail,hf=W.load_session_rows(panel,path)
    rows=[]
    audit=[]
    for (co,sid,iid),vals in sorted(by.items()):
        f,a=bin_features(vals)
        audit.append({"cohort":co,"session":sid,"iid":iid,**a,"valid":f is not None})
        if f is not None:
            rows.append({"cohort":co,"session":sid,"iid":iid,**a,**f})
    counts=collections.Counter((r["cohort"],r["iid"]) for r in rows)
    elig={k for k,n in counts.items() if n>=2}
    rows=[r for r in rows if (r["cohort"],r["iid"]) in elig]
    original=original_repeat_by_cohort(panel)
    retained=collections.Counter(co for co,iid in elig)
    retained={co:len({iid for c,iid in elig if c==co}) for co in sorted({c for c,i in elig})}
    required={co:3 for co,n in original.items() if n>=5}
    colony_pass=all(retained.get(co,0)>=req for co,req in required.items())
    return rows,{
      "height_field":hf,
      "numeric_parse_failures":nfail,
      "original_repeat_individuals_by_cohort":original,
      "retained_repeat_individuals_by_cohort":retained,
      "required_retained_by_cohort":required,
      "colony_retention_pass":colony_pass,
      "session_audit":audit,
    }

def standardize(rows,rawkey,outkey):
    q=[dict(r) for r in rows]
    for co in sorted({r["cohort"] for r in q}):
        ix=[i for i,r in enumerate(q) if r["cohort"]==co]
        M=np.vstack([q[i][rawkey] for i in ix]).astype(float)
        if len(M)<2:return None
        mu=M.mean(axis=0);sd=M.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):return None
        for i in ix:
            q[i][outkey]=float(np.mean((q[i][rawkey]-mu)/sd))
    return q

def perm_labels(rows,rng):
    labs=[r["iid"] for r in rows];out=list(labs)
    byco=collections.defaultdict(list)
    for i,r in enumerate(rows):byco[r["cohort"]].append(i)
    for idxs in byco.values():
        x=np.asarray([labs[i] for i in idxs],dtype=object);rng.shuffle(x)
        for k,i in enumerate(idxs):out[i]=str(x[k])
    return out

def statistic(rows,key,seed):
    temp=[]
    for r in rows:
        q=dict(r);q["I"]=float(r[key]);temp.append(q)
    obs,ind=W.stat(temp,[r["iid"] for r in temp])
    if obs is None:return {"status":"STOP_OBSERVED_SUPPORT"}
    rng=np.random.default_rng(seed);null=[]
    for _ in range(NPERM):
        s,_=W.stat(temp,perm_labels(temp,rng))
        if s is not None:null.append(s)
    a=np.asarray(null,float)
    pos=sum(v>0 for v in ind.values())
    return {
      "status":"DONE","H":float(obs),"individual_H":ind,
      "positive_individuals":pos,"n_individuals":len(ind),
      "positive_fraction":float(pos/len(ind)),
      "n_sessions":len(temp),"valid_permutations":int(len(a)),
      "seed":seed,"p_one_sided":float((1+np.sum(a>=obs))/(1+len(a))),
      "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
      "null_q975":float(np.quantile(a,.975))
    }

def run_year(year,panel,seeds):
    rows,audit=prepare(panel)
    nind=len(set((r["cohort"],r["iid"]) for r in rows))
    support={
      **audit,
      "eligible_individuals":nind,
      "eligible_sessions":len(rows),
      "valid_session_interval_summary":{
        "median":float(np.median([r["consecutive_bin_intervals"] for r in rows])) if rows else None,
        "min":int(min([r["consecutive_bin_intervals"] for r in rows])) if rows else None,
        "max":int(max([r["consecutive_bin_intervals"] for r in rows])) if rows else None,
      }
    }
    if nind<5 or not audit["colony_retention_pass"]:
        return {"status":"STOP_STRUCTURAL_OR_COLONY_SUPPORT",**support}
    out={"status":"DONE",**support,"diagnostics":{}}
    for raw,key,seed in [("F1_raw","F1_I_bin360",seeds[0]),("F2_raw","F2_IH_bin360",seeds[1]),("F3_raw","F3_IV_bin360",seeds[2])]:
        rr=standardize(rows,raw,key)
        out["diagnostics"][key]=({"status":"STOP_STANDARDIZATION"} if rr is None else statistic(rr,key,seed))
    return out

def main():
    results={}
    for year,(panel,*seeds) in PANELS.items():
        results[year]=run_year(year,panel,seeds)
    print(json.dumps({
      "contract":"PHYLLOSTOMUS_FIXED_BIN_HARMONIZATION_CONTRACT_V2.md",
      "status":"POST_OUTCOME_MEASUREMENT_DIAGNOSTIC",
      "bin_seconds":BIN,
      "minimum_consecutive_bin_intervals":MIN_INTERVALS,
      "years":results
    },ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
