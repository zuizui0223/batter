#!/usr/bin/env python3
"""Support-matched sparsity diagnostic for P. hastatus 2023 field carrier failure."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("W",HERE/"wild_flight_intensity_persistence_v1.py")
W=importlib.util.module_from_spec(spec);spec.loader.exec_module(W)

NREP=9999
SEED=202610051401
MIN_VALID=9500
OBS_H=-0.12643411022038945
OBS_F=0.4117647058823529

def base_cohort(c):
    return c.rsplit("::",1)[0]

def load_sessions(panel):
    path=W.PANELS[panel][0]
    s,a=W.prepare(panel,path)
    return s

def support_template(sessions):
    byco=collections.defaultdict(lambda:collections.Counter())
    for s in sessions:
        byco[base_cohort(s["cohort"])][s["iid"]]+=1
    return {
      co:sorted(cnt.values(),reverse=True)
      for co,cnt in sorted(byco.items())
    }

def donor_pool(sessions):
    byco=collections.defaultdict(lambda:collections.defaultdict(list))
    for s in sessions:
        byco[base_cohort(s["cohort"])][s["iid"]].append(s)
    return byco

def sample_assignment(pool,target_counts,rng,max_attempts=10000):
    ids=list(pool)
    n=len(target_counts)
    if len(ids)<n:return None
    tc=list(target_counts)
    for _ in range(max_attempts):
        chosen=list(rng.choice(np.asarray(ids,dtype=object),size=n,replace=False))
        counts=list(tc)
        rng.shuffle(counts)
        if all(len(pool[i])>=c for i,c in zip(chosen,counts)):
            return list(zip(chosen,counts))
    return None

def make_replicate(pool,template,rng):
    sampled=[]
    for co,counts in template.items():
        if co not in pool:return None
        ass=sample_assignment(pool[co],counts,rng)
        if ass is None:return None
        cohort_rows=[]
        for iid,n in ass:
            rows=pool[co][iid]
            idx=rng.choice(np.arange(len(rows)),size=n,replace=False)
            for j in idx:
                r=dict(rows[int(j)])
                r["cohort"]=co+"::pseudo2023"
                cohort_rows.append(r)
        # Re-standardize the four raw features within this sampled colony.
        M=np.vstack([r["features"] for r in cohort_rows]).astype(float)
        if M.shape[0]<2:return None
        mu=M.mean(axis=0);sd=M.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):return None
        for r in cohort_rows:
            z=(r["features"]-mu)/sd
            r["I"]=float(np.mean(z))
        sampled.extend(cohort_rows)
    return sampled

def panel_stat(sessions):
    labs=[s["iid"] for s in sessions]
    h,ind=W.stat(sessions,labs)
    if h is None or not ind:return None
    pos=sum(v>0 for v in ind.values())
    return float(h),float(pos/len(ind)),ind

def main():
    s22=load_sessions("phyllostomus_2022")
    s23=load_sessions("phyllostomus_2023")
    template=support_template(s23)
    pool=donor_pool(s22)

    obs=panel_stat(s23)
    if obs is None:raise RuntimeError("2023 observed support failed")
    if abs(obs[0]-OBS_H)>1e-12 or abs(obs[1]-OBS_F)>1e-12:
        raise RuntimeError(f"2023 observed drift {obs[:2]}")

    rng=np.random.default_rng(SEED)
    hs=[];fs=[];invalid=0
    for _ in range(NREP):
        q=make_replicate(pool,template,rng)
        if q is None:
            invalid+=1;continue
        st=panel_stat(q)
        if st is None:
            invalid+=1;continue
        hs.append(st[0]);fs.append(st[1])

    H=np.asarray(hs,float);F=np.asarray(fs,float)
    status="DONE" if len(H)>=MIN_VALID else "STOP_MONTE_CARLO_SUPPORT"
    out={
      "contract":"PHYLLOSTOMUS_2023_SUPPORT_MATCHED_SPARSITY_CONTRACT_V1.md",
      "status":"POST_OUTCOME_BOUNDARY_DIAGNOSTIC",
      "species":"Phyllostomus hastatus",
      "donor_year":2022,
      "target_support_year":2023,
      "target_support_template":template,
      "donor_individual_capacity":{
        co:{iid:len(rows) for iid,rows in sorted(d.items())}
        for co,d in sorted(pool.items())
      },
      "observed_2023":{
        "H_panel":obs[0],"positive_fraction":obs[1],
        "n_individuals":len(obs[2]),"n_sessions":len(s23),
      },
      "requested_pseudo_panels":NREP,
      "valid_pseudo_panels":int(len(H)),
      "invalid_pseudo_panels":int(invalid),
      "seed":SEED,
      "H_support_matched_2022":{
        "median":float(np.median(H)) if len(H) else None,
        "q025":float(np.quantile(H,.025)) if len(H) else None,
        "q975":float(np.quantile(H,.975)) if len(H) else None,
        "fraction_H_le_observed_2023":float(np.mean(H<=obs[0])) if len(H) else None,
        "fraction_H_le_zero":float(np.mean(H<=0)) if len(H) else None,
      },
      "positive_fraction_support_matched_2022":{
        "median":float(np.median(F)) if len(F) else None,
        "q025":float(np.quantile(F,.025)) if len(F) else None,
        "q975":float(np.quantile(F,.975)) if len(F) else None,
        "fraction_F_le_observed_2023":float(np.mean(F<=obs[1])) if len(F) else None,
      },
      "diagnostic_status":status,
    }
    if status=="DONE":
        tail=float(np.mean(H<=obs[0]))
        out["diagnostic_verdict"]=(
          "SPARSITY_ALONE_UNLIKELY"
          if tail<.025
          else "SPARSITY_REMAINS_PLAUSIBLE"
        )
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
