#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import io
import json
import math
import sys
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

CONTRACT=ROOT/"post_freeze_extensions/noctule_independent_validation/contract_v1.json"
PREFLIGHT=ROOT/"post_freeze_extensions/noctule_independent_validation/preflight_summary_v1.json"
OUT=ROOT/"post_freeze_extensions/noctule_independent_validation/result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/noctule_independent_validation/RESULT_V1.md"
UA={"User-Agent":"batter-noctule-independent-validation-v1/1.0"}
EDGES=(-math.inf,-400.0,-200.0,-100.0,-50.0,0.0,50.0,100.0,200.0,400.0,math.inf)

def present(s):
    txt=s.astype(str).str.strip()
    return s.notna() & txt.ne("") & ~txt.str.lower().isin({"na","nan","null","none"})

def load_source(c):
    src=c["source"]
    r=requests.get(src["download_url"],headers=UA,timeout=180)
    r.raise_for_status()
    data=r.content
    sha=hashlib.sha256(data).hexdigest()
    if sha!=src["sha256"]:
        raise RuntimeError(f"source sha256 {sha} != frozen {src['sha256']}")
    df=pd.read_csv(io.BytesIO(data),dtype=str,low_memory=False)
    if len(df)!=int(src["row_count_expected"]):
        raise RuntimeError(f"row count {len(df)} != frozen {src['row_count_expected']}")
    return df,sha

def build_events(c):
    df,sha=load_source(c)
    f=c["source"]["fields"]
    need=[f["individual"],f["session"],f["timestamp"],f["x"],f["y"],f["native_vertical"],f["year"],f["field_period"]]
    for col in need:
        if col not in df.columns:
            raise RuntimeError(f"missing frozen field {col}")

    mask=pd.Series(True,index=df.index)
    for col in need:
        mask &= present(df[col])
    d=df.loc[mask,need].copy()

    d["x_num"]=pd.to_numeric(d[f["x"]],errors="coerce")
    d["y_num"]=pd.to_numeric(d[f["y"]],errors="coerce")
    # Numeric Height is opened here for the first time, after frozen preflight.
    d["h_num"]=pd.to_numeric(d[f["native_vertical"]],errors="coerce")
    d["t_num"]=pd.to_datetime(d[f["timestamp"]],errors="coerce",utc=True)
    d=d.loc[
        d["x_num"].notna() & d["y_num"].notna() &
        d["h_num"].notna() & d["t_num"].notna()
    ].copy()
    d["iid_raw"]=d[f["individual"]].astype(str)
    d["session_raw"]=d[f["session"]].astype(str)
    d["cohort"]=d[f["year"]].astype(str)+"::"+d[f["field_period"]].astype(str)

    min_session=int(c["preflight"]["minimum_presence_qualified_fixes_per_session"])
    counts=d.groupby(["cohort","iid_raw","session_raw"]).size().rename("n").reset_index()
    elig=counts.loc[counts["n"]>=min_session].copy()
    eligible_keys=set(zip(elig["cohort"],elig["iid_raw"],elig["session_raw"]))
    d=d.loc[d.apply(lambda z:(z["cohort"],z["iid_raw"],z["session_raw"]) in eligible_keys,axis=1)].copy()

    grid=float(c["primary_validation_if_preflight_passes"]["horizontal_cell_m"])
    d["cx"]=(d["x_num"]/grid).apply(math.floor)
    d["cy"]=(d["y_num"]/grid).apply(math.floor)

    events=defaultdict(list)
    diag={"source_sha256":sha,"numeric_height_rows":int(len(d)),"cohorts":{}}
    for (cohort,iid,sid),g in d.groupby(["cohort","iid_raw","session_raw"],sort=True):
        med=float(np.median(g["h_num"].to_numpy(dtype=float)))
        iid_key=f"{cohort}::{iid}"
        sid_key=f"{cohort}::{sid}"
        for _,r in g.iterrows():
            resid=float(r["h_num"]-med)
            events[cohort].append(Event(
                individual=iid_key,
                timestamp=r["t_num"].to_pydatetime(),
                cell=(int(r["cx"]),int(r["cy"])),
                zbin=z_bin(resid,edges=EDGES),
                session=sid_key
            ))
        diag["cohorts"].setdefault(cohort,{"sessions":0,"individuals":set(),"rows":0})
        diag["cohorts"][cohort]["sessions"]+=1
        diag["cohorts"][cohort]["individuals"].add(iid_key)
        diag["cohorts"][cohort]["rows"]+=len(g)

    for cohort,x in diag["cohorts"].items():
        x["individuals"]=len(x["individuals"])

    return dict(events),diag

def main():
    c=json.loads(CONTRACT.read_text())
    pf=json.loads(PREFLIGHT.read_text())
    if not pf.get("preflight_pass"):
        raise RuntimeError("frozen preflight did not pass")

    events_by_cohort,diag=build_events(c)
    K=len(EDGES)-1
    arrays={cohort:cal.make_cohort_arrays(events,K) for cohort,events in sorted(events_by_cohort.items())}

    observed,per_ind,session_rows=cal.observed_eval(arrays)
    expected=int(pf["evaluable_individual_cohort_units_total"])
    if observed["eligible_individuals"]!=expected:
        raise RuntimeError(f"observed evaluable n {observed['eligible_individuals']} != frozen preflight {expected}")

    settings=c["primary_validation_if_preflight_passes"]["calibration"]
    B=int(settings["B"]); seed=int(settings["seed"])
    rng=np.random.default_rng(seed)
    null=[]; null_cond=[]; null_adv=[]; eligible=[]; invalid=0
    for _ in range(B):
        p=cal.perm_eval(arrays,rng)
        if p["eligible_individuals"]<1 or p["common_cell_marginal"] is None:
            invalid+=1
            continue
        null.append(float(p["common_cell_marginal"]))
        null_cond.append(float(p["conditional"]))
        null_adv.append(float(p["common_cell_advantage"]))
        eligible.append(int(p["eligible_individuals"]))

    primary=cal.tail_summary(null,float(observed["common_cell_marginal"]))
    conditional=cal.tail_summary(null_cond,float(observed["conditional"]))
    advantage=cal.tail_summary(null_adv,float(observed["common_cell_advantage"]))
    passed=(
        observed["eligible_individuals"]==expected and
        primary["observed_minus_null_mean"]>0 and
        primary["p_null_ge_observed"]<=0.05
    )

    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "source":c["source"],
        "preflight":pf,
        "diagnostics":diag,
        "numeric_height_opened_after_preflight":True,
        "observed":{**observed,"individual_results":per_ind,"session_results":session_rows},
        "permutation":{
            "B":B,"seed":seed,
            "valid_replicates":len(null),"invalid_replicates":invalid,
            "eligible_individual_count_min":int(min(eligible)),
            "eligible_individual_count_max":int(max(eligible)),
            "centered_common_cell_identity":primary,
            "centered_conditional_identity":conditional,
            "centered_common_cell_advantage":advantage
        },
        "primary_verdict":{
            "expected_evaluable_individual_cohort_units":expected,
            "exact_n_met":observed["eligible_individuals"]==expected,
            "calibrated_identity_positive":primary["observed_minus_null_mean"]>0,
            "upper_tail_le_0_05":primary["p_null_ge_observed"]<=0.05,
            "pass":bool(passed)
        },
        "mechanism_extension_may_open":bool(passed),
        "claim_boundary":c["claim_boundary"],
        "stop_rule":c["stop_rule"]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    lines=[
        "# Independent common-noctule centered-shape validation v1","",
        "**PROSPECTIVE EXTERNAL VALIDATION. Source selected and structural eligibility frozen before numeric Height was opened.**","",
        f"- evaluable individual×cohort units: **{observed['eligible_individuals']}**",
        f"- observed centered common-cell identity: **{observed['common_cell_marginal']:+.4f} nats/fix**",
        f"- null mean: **{primary['mean']:+.4f}**",
        f"- calibrated excess: **{primary['observed_minus_null_mean']:+.4f}**",
        f"- p(null >= observed): **{primary['p_null_ge_observed']:.5f}**",
        f"- frozen primary verdict: **{'PASS' if passed else 'FAIL'}**","",
        "Mechanism extensions may open only if the primary verdict is PASS.",""
    ]
    OUT_MD.write_text("\n".join(lines))

    print(json.dumps({
        "n":observed["eligible_individuals"],
        "observed":observed["common_cell_marginal"],
        "null_mean":primary["mean"],
        "calibrated_excess":primary["observed_minus_null_mean"],
        "p_upper":primary["p_null_ge_observed"],
        "pass":passed,
        "mechanism_extension_may_open":passed
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
