#!/usr/bin/env python3
"""Support-match harmonized 2022 P. hastatus to the exact 2023 session-count profile."""
from __future__ import annotations
import collections, importlib.util, json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("H",HERE/"phyllostomus_measurement_harmonization_v1.py")
H=importlib.util.module_from_spec(spec);spec.loader.exec_module(H)

N_ACCEPT=9999
MAX_ATTEMPTS=1_000_000
SEED=202610051431
OBS_H_2023=0.055658227354875606
OBS_F_2023=0.5

def structural_rows(panel):
    rows,hf,nfail=H.prepare(panel)
    return rows,hf,nfail

def counts_by_ind(rows):
    c=collections.Counter((r["cohort"],r["iid"]) for r in rows)
    return c

def observed_h(rows):
    rr=H.standardize(rows,"I360_raw","I360")
    if rr is None:return None
    return H.stat_scalar(rr,"I360")

def main():
    r22,h22,nf22=structural_rows("phyllostomus_2022")
    r23,h23,nf23=structural_rows("phyllostomus_2023")
    c22=counts_by_ind(r22);c23=counts_by_ind(r23)

    target_counts=sorted(c23.values(),reverse=True)
    if len(target_counts)!=6 or sum(target_counts)!=25:
        print(json.dumps({
          "contract":"PHYLLOSTOMUS_HARMONIZED_SUPPORT_MATCHED_CONTRACT_V1.md",
          "status":"STOP_TARGET_SUPPORT_DRIFT",
          "target_counts":target_counts,
          "n_individuals":len(target_counts),
          "n_sessions":sum(target_counts)
        },indent=2))
        return

    obs23=observed_h(r23)
    if obs23 is None:
        raise RuntimeError("2023 observed harmonized H unavailable")
    h23_obs,ind23=obs23
    f23_obs=sum(v>0 for v in ind23.values())/len(ind23)
    if abs(h23_obs-OBS_H_2023)>1e-12 or abs(f23_obs-OBS_F_2023)>1e-12:
        raise RuntimeError(f"2023 observed result drift: H={h23_obs} F={f23_obs}")

    donor_keys=sorted(c22)
    rows_by_key=collections.defaultdict(list)
    for r in r22: rows_by_key[(r["cohort"],r["iid"])].append(r)

    rng=np.random.default_rng(SEED)
    hs=[];fs=[];accepted_profiles=[];attempts=0
    while len(hs)<N_ACCEPT and attempts<MAX_ATTEMPTS:
        attempts+=1
        chosen=list(rng.choice(np.array(donor_keys,dtype=object),size=6,replace=False))
        # numpy object array may return tuple elements as ndarray-ish; normalize.
        chosen=[tuple(x) if not isinstance(x,tuple) else x for x in chosen]
        tc=list(rng.permutation(np.asarray(target_counts,int)))
        if any(c22[k] < int(n) for k,n in zip(chosen,tc)):
            continue

        sample=[]
        for k,n in zip(chosen,tc):
            pool=rows_by_key[k]
            idx=rng.choice(len(pool),size=int(n),replace=False)
            for j in idx:
                sample.append(dict(pool[int(j)]))

        rr=H.standardize(sample,"I360_raw","I360")
        if rr is None:
            continue
        st=H.stat_scalar(rr,"I360")
        if st is None:
            continue
        h,ind=st
        if len(ind)!=6:
            continue
        f=sum(v>0 for v in ind.values())/len(ind)
        hs.append(float(h));fs.append(float(f))
        if len(accepted_profiles)<20:
            accepted_profiles.append({
                "donors":[f"{k[0]}:{k[1]}" for k in chosen],
                "assigned_session_counts":[int(x) for x in tc]
            })

    a=np.asarray(hs,float);b=np.asarray(fs,float)
    status="DONE" if len(a)>=9500 else "STOP_MONTE_CARLO_SUPPORT"
    out={
      "contract":"PHYLLOSTOMUS_HARMONIZED_SUPPORT_MATCHED_CONTRACT_V1.md",
      "status":"POST_OUTCOME_BOUNDARY_DIAGNOSTIC",
      "donor_year":2022,
      "target_year":2023,
      "height_fields":{"2022":h22,"2023":h23},
      "numeric_parse_failures":{"2022":nf22,"2023":nf23},
      "target_session_count_multiset":target_counts,
      "target_individuals":len(target_counts),
      "target_sessions":sum(target_counts),
      "donor_eligible_individuals":len(c22),
      "donor_eligible_sessions":len(r22),
      "observed_2023":{"H":float(h23_obs),"positive_fraction":float(f23_obs)},
      "requested_pseudo_panels":N_ACCEPT,
      "accepted_pseudo_panels":int(len(a)),
      "attempts":attempts,
      "seed":SEED,
      "example_accepted_profiles":accepted_profiles,
      "H_support_matched_2022":{
          "median":float(np.median(a)) if len(a) else None,
          "q025":float(np.quantile(a,.025)) if len(a) else None,
          "q975":float(np.quantile(a,.975)) if len(a) else None,
          "fraction_H_le_observed_2023":float(np.mean(a<=h23_obs)) if len(a) else None,
          "fraction_H_le_zero":float(np.mean(a<=0)) if len(a) else None,
      },
      "positive_fraction_support_matched_2022":{
          "median":float(np.median(b)) if len(b) else None,
          "q025":float(np.quantile(b,.025)) if len(b) else None,
          "q975":float(np.quantile(b,.975)) if len(b) else None,
          "fraction_F_le_observed_2023":float(np.mean(b<=f23_obs)) if len(b) else None,
      },
      "diagnostic_status":status,
    }
    if status=="DONE":
        # Descriptive boundary label only.
        qlow=float(np.quantile(a,.025))
        out["diagnostic_verdict"]=(
            "2023_WITHIN_MATCHED_2022_RANGE" if h23_obs>=qlow
            else "2023_BELOW_MATCHED_2022_RANGE"
        )
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
