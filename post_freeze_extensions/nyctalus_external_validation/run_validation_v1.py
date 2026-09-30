#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, io, json, math, sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from batter.analysis import Event, z_bin
import scripts.run_cross_panel_estimator_calibration as cal

CONTRACT=ROOT/"post_freeze_extensions/nyctalus_external_validation/validation_contract_v1.json"
OUTDIR=ROOT/"post_freeze_extensions/nyctalus_external_validation/test_results"
FINAL_JSON=ROOT/"post_freeze_extensions/nyctalus_external_validation/result_v1.json"
FINAL_MD=ROOT/"post_freeze_extensions/nyctalus_external_validation/RESULT_V1.md"
HEADERS={"User-Agent":"batter-nyctalus-independent-validation-v1/1.0"}
EDGES=(-math.inf,-400.0,-200.0,-100.0,-50.0,0.0,50.0,100.0,200.0,400.0,math.inf)
K=len(EDGES)-1

def present(s):
    x=s.notna()
    txt=s.astype(str).str.strip()
    x &= txt.ne("")
    x &= ~txt.str.lower().isin({"na","nan","null","none"})
    return x

def fetch_df(c):
    meta=requests.get(f"https://zenodo.org/api/records/{c['source']['record_id']}",headers=HEADERS,timeout=90)
    meta.raise_for_status()
    j=meta.json()
    target=None
    for f in j.get("files",[]):
        if (f.get("key") or f.get("filename"))==c["source"]["file"]:
            target=f;break
    if target is None:
        raise RuntimeError("source file not found")
    url=(target.get("links") or {}).get("content") or (target.get("links") or {}).get("self")
    r=requests.get(url,headers=HEADERS,timeout=180)
    r.raise_for_status()
    data=r.content
    sha=hashlib.sha256(data).hexdigest()
    if sha!=c["source"]["sha256"]:
        raise RuntimeError(f"source SHA mismatch {sha}")
    df=pd.read_csv(io.BytesIO(data),dtype=str,low_memory=False)
    return df,sha,len(data)

def prepare_base(df):
    req=["bat_id","trackid","utc","x","y","Height","Year","field_period","move_state"]
    missing=[x for x in req if x not in df.columns]
    if missing:
        raise RuntimeError(f"missing columns {missing}")
    mask=pd.Series(True,index=df.index)
    for col in ["bat_id","trackid","utc","x","y","Height","Year","field_period"]:
        mask &= present(df[col])
    d=df.loc[mask,req].copy()
    d["x_num"]=pd.to_numeric(d["x"],errors="coerce")
    d["y_num"]=pd.to_numeric(d["y"],errors="coerce")
    d["t"]=pd.to_datetime(d["utc"],errors="coerce",utc=True)
    if d["x_num"].isna().any() or d["y_num"].isna().any() or d["t"].isna().any():
        raise RuntimeError("nonvertical parse failure relative to frozen preflight rows")

    # First and only opening of numeric native Height in this family.
    h=pd.to_numeric(d["Height"],errors="coerce")
    if h.isna().any() or not np.isfinite(h.to_numpy(dtype=float)).all():
        bad=int(h.isna().sum() + np.sum(~np.isfinite(h.fillna(0).to_numpy(dtype=float))))
        raise RuntimeError(f"Height parse/nonfinite failures: {bad}")
    d["height_num"]=h.astype(float)
    d["bat_id"]=d["bat_id"].astype(str)
    d["trackid"]=d["trackid"].astype(str)
    d["cohort"]=d["Year"].astype(str).str.strip()+"::"+d["field_period"].astype(str).str.strip()
    d["move_state"]=d["move_state"].astype(str).str.strip()

    # Center on the full retained source track before any state filtering.
    med=d.groupby(["cohort","trackid"])["height_num"].transform("median")
    d["resid_height"]=d["height_num"]-med
    return d

def build_events(d,test,c):
    if test=="primary":
        q=d.copy()
        expected=int(c["primary_external_replication"]["expected_observed_evaluable_individuals"])
        grid=int(c["primary_external_replication"]["horizontal_grid_m"])
        seed=int(c["primary_external_replication"]["permutation"]["seed"])
        B=int(c["primary_external_replication"]["permutation"]["B"])
        state=False
    elif test=="state":
        q=d[d["move_state"].isin(c["frozen_context"]["valid_move_states"])].copy()
        expected=int(c["independent_mechanism_replication"]["expected_observed_evaluable_individuals"])
        grid=int(c["independent_mechanism_replication"]["horizontal_grid_m"])
        seed=int(c["independent_mechanism_replication"]["permutation"]["seed"])
        B=int(c["independent_mechanism_replication"]["permutation"]["B"])
        state=True
    else:
        raise ValueError(test)

    events=defaultdict(list)
    for r in q.itertuples(index=False):
        cell=(math.floor(float(r.x_num)/grid),math.floor(float(r.y_num)/grid))
        if state:
            cell=cell+(str(r.move_state),)
        events[str(r.cohort)].append(Event(
            individual=str(r.bat_id),
            timestamp=r.t.to_pydatetime(),
            cell=cell,
            zbin=z_bin(float(r.resid_height),edges=EDGES),
            session=str(r.trackid),
        ))
    return dict(events),expected,seed,B,{
        "test":test,
        "retained_events":int(len(q)),
        "grid_m":grid,
        "state_conditioned":state,
        "cohorts":sorted(events)
    }

def run_test(test):
    c=json.loads(CONTRACT.read_text())
    df,sha,size=fetch_df(c)
    d=prepare_base(df)
    if len(d)!=8129:
        raise RuntimeError(f"retained row count {len(d)} != frozen schema rows 8129")
    events_by_cohort,expected,seed,B,diag=build_events(d,test,c)
    arrays={cohort:cal.make_cohort_arrays(events,K) for cohort,events in sorted(events_by_cohort.items())}

    observed,per_ind,session_rows=cal.observed_eval(arrays)
    if observed["eligible_individuals"]!=expected:
        raise RuntimeError(f"{test}: exact observed n {observed['eligible_individuals']} != frozen {expected}")

    obs=float(observed["common_cell_marginal"])
    rng=np.random.default_rng(seed)
    null=[];eligible=[];invalid=0
    for _ in range(B):
        p=cal.perm_eval(arrays,rng)
        if p["eligible_individuals"]<1 or p["common_cell_marginal"] is None:
            invalid+=1;continue
        null.append(float(p["common_cell_marginal"]))
        eligible.append(int(p["eligible_individuals"]))
    if not null:
        raise RuntimeError("no valid permutation replicates")

    calibration=cal.tail_summary(null,obs)
    passed=calibration["observed_minus_null_mean"]>0 and calibration["p_null_ge_observed"]<=0.05

    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "test_id":test,
        "source_sha256":sha,
        "source_size_bytes":size,
        "numeric_height_opened":True,
        "diagnostics":diag,
        "observed":{
            **observed,
            "individual_results":per_ind,
            "session_results":session_rows
        },
        "permutation":{
            "B":B,"seed":seed,
            "valid_replicates":len(null),"invalid_replicates":invalid,
            "eligible_individual_count_min":int(min(eligible)),
            "eligible_individual_count_max":int(max(eligible)),
            "common_cell_marginal_identity":calibration
        },
        "primary_verdict":{
            "expected_evaluable_individuals":expected,
            "exact_n_met":True,
            "calibrated_identity_positive":calibration["observed_minus_null_mean"]>0,
            "upper_tail_le_0_05":calibration["p_null_ge_observed"]<=0.05,
            "pass":bool(passed)
        },
        "claim_boundary":c["claim_boundary"],
        "stop_rule":c["stop_rule"]
    }
    OUTDIR.mkdir(parents=True,exist_ok=True)
    (OUTDIR/f"{test}_v1.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "test":test,
        "n":observed["eligible_individuals"],
        "observed":obs,
        "null_mean":calibration["mean"],
        "calibrated_excess":calibration["observed_minus_null_mean"],
        "p_upper":calibration["p_null_ge_observed"],
        "pass":passed
    },sort_keys=True))
    return payload

def aggregate():
    c=json.loads(CONTRACT.read_text())
    tests={}
    for test in ("primary","state"):
        path=OUTDIR/f"{test}_v1.json"
        if not path.exists():
            raise RuntimeError(f"missing {path}")
        tests[test]=json.loads(path.read_text())
    p=tests["primary"]["primary_verdict"]["pass"]
    s=tests["state"]["primary_verdict"]["pass"]
    key=("primary_PASS_state_PASS" if p and s else
         "primary_PASS_state_FAIL" if p and not s else
         "primary_FAIL_state_PASS" if (not p and s) else
         "primary_FAIL")
    interpretation=c["prospective_interpretation_matrix"][key]
    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "source":c["source"],
        "prospective_contract_frozen_before_height":True,
        "tests":tests,
        "synthesis_key":key,
        "interpretation":interpretation,
        "stopped_families":c["stopped_families"],
        "claim_boundary":c["claim_boundary"]
    }
    FINAL_JSON.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    lines=[
        "# Nyctalus independent external validation v1","",
        "**Fully prospective external validation: source, cohorts, exact n, estimators, permutation seeds and interpretation matrix were frozen before numeric Height values were opened.**","",
        "| test | n | calibrated excess | p(null >= observed) | verdict |",
        "|---|---:|---:|---:|---|"
    ]
    for test,label in [("primary","5-km centered identity"),("state","5-km × source HMM state")]:
        v=tests[test]
        x=v["permutation"]["common_cell_marginal_identity"]
        lines.append(f"| {label} | {v['observed']['eligible_individuals']} | {x['observed_minus_null_mean']:+.4f} | {x['p_null_ge_observed']:.5f} | **{'PASS' if v['primary_verdict']['pass'] else 'FAIL'}** |")
    lines += ["","## Prospective synthesis","",interpretation,"",
              "500-m and >=1-day families were stopped structurally before Height and were not opened.",""]
    FINAL_MD.write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps({
        "synthesis_key":key,
        "interpretation":interpretation,
        "primary":tests["primary"]["primary_verdict"],
        "state":tests["state"]["primary_verdict"]
    },sort_keys=True))
    return 0

def main():
    ap=argparse.ArgumentParser()
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--test",choices=["primary","state"])
    g.add_argument("--aggregate",action="store_true")
    args=ap.parse_args()
    if args.test:
        run_test(args.test);return 0
    return aggregate()

if __name__=="__main__":
    raise SystemExit(main())
