#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from batter.analysis import Event, z_bin
import scripts.run_cross_panel_estimator_calibration as cal
import scripts.run_tag_altitude_bias_shape as shape

CONTRACT=ROOT/"post_freeze_extensions/movement_state_conditioning/contract_v1.json"
OUT=ROOT/"post_freeze_extensions/movement_state_conditioning/result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/movement_state_conditioning/RESULT_V1.md"

EDGES=(-math.inf,-400.0,-200.0,-100.0,-50.0,0.0,50.0,100.0,200.0,400.0,math.inf)
CELL=5000.0


def build_events(panel,c):
    records,source=shape.panel_raw(panel)
    by_session=defaultdict(list)
    for r in records:
        by_session[(r["cohort"],r["session"])].append(r)

    session_medians={}
    steps=[]
    total_records=len(records)
    for key,vals in sorted(by_session.items()):
        vals=sorted(vals,key=lambda x:x["t"])
        session_medians[key]=float(np.median([r["h"] for r in vals]))
        for i in range(1,len(vals)):
            a,b=vals[i-1],vals[i]
            dt=(b["t"]-a["t"]).total_seconds()
            if not math.isfinite(dt) or dt<=0 or dt>int(c["state_definition"]["maximum_step_interval_seconds"]):
                continue
            speed=math.hypot(b["x"]-a["x"],b["y"]-a["y"])/dt
            steps.append({
                "cohort":b["cohort"],"session":b["session"],"iid":b["iid"],
                "t":b["t"],"x":b["x"],"y":b["y"],"h":b["h"],"speed":float(speed)
            })

    speeds=defaultdict(list)
    for r in steps:
        speeds[r["cohort"]].append(r["speed"])
    thresholds={}
    for cohort,vals in sorted(speeds.items()):
        a=np.asarray(vals,dtype=float)
        thresholds[cohort]=[float(x) for x in np.quantile(a,[1/3,2/3])]

    events=defaultdict(list)
    state_counts=defaultdict(lambda:[0,0,0])
    for r in steps:
        cuts=thresholds[r["cohort"]]
        st=int(np.searchsorted(np.asarray(cuts),r["speed"],side="right"))
        med=session_medians[(r["cohort"],r["session"])]
        resid=float(r["h"]-med)
        coarse=(math.floor(r["x"]/CELL),math.floor(r["y"]/CELL),st)
        events[r["cohort"]].append(Event(
            individual=r["iid"],
            timestamp=r["t"],
            cell=coarse,
            zbin=z_bin(resid,edges=EDGES),
            session=r["session"]
        ))
        state_counts[r["cohort"]][st]+=1

    diagnostics={
        "source":source,
        "total_retained_numeric_height_records":total_records,
        "state_valid_endpoint_records":len(steps),
        "state_valid_fraction":float(len(steps)/total_records) if total_records else None,
        "cohort_speed_thresholds_m_s":thresholds,
        "cohort_state_event_counts":dict(state_counts),
        "session_count":len(by_session)
    }
    return dict(events),diagnostics


def run_panel(panel,c):
    settings={x["panel"]:x for x in c["calibration"]["settings"]}
    expected=int(c["estimator"]["expected_evaluable_individuals"][panel])
    events_by_cohort,diag=build_events(panel,c)
    arrays={cohort:cal.make_cohort_arrays(events,len(EDGES)-1) for cohort,events in sorted(events_by_cohort.items())}
    observed,per_ind,session_rows=cal.observed_eval(arrays)
    if observed["eligible_individuals"]!=expected:
        raise RuntimeError(f"{panel}: evaluable n {observed['eligible_individuals']} != preflight expected {expected}")

    setting=settings[panel]
    rng=np.random.default_rng(int(setting["seed"]))
    null=[]
    null_adv=[]
    eligible=[]
    invalid=0
    for _ in range(int(setting["B"])):
        p=cal.perm_eval(arrays,rng)
        if p["eligible_individuals"]<1 or p["common_cell_marginal"] is None:
            invalid+=1
            continue
        null.append(float(p["common_cell_marginal"]))
        null_adv.append(float(p["common_cell_advantage"]))
        eligible.append(int(p["eligible_individuals"]))
    if not null:
        raise RuntimeError(f"{panel}: no valid permutations")

    identity=cal.tail_summary(null,float(observed["common_cell_marginal"]))
    advantage=cal.tail_summary(null_adv,float(observed["common_cell_advantage"]))
    passed=(
        observed["eligible_individuals"]==expected
        and identity["observed_minus_null_mean"]>0
        and identity["p_null_ge_observed"]<=0.05
    )
    baseline={
        "eidolon":0.443,
        "hypsignathus":0.177,
        "phyllostomus_2022":0.111,
        "phyllostomus_2023":0.118,
        "phyllostomus_2016":0.574
    }[panel]
    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "panel":panel,
        "preflight_selected_candidate":c["preflight"]["selected_candidate_id"],
        "diagnostics":diag,
        "observed":{
            **observed,
            "individual_results":per_ind,
            "session_results":session_rows
        },
        "permutation":{
            "B":int(setting["B"]),
            "seed":int(setting["seed"]),
            "valid_replicates":len(null),
            "invalid_replicates":invalid,
            "eligible_individual_count_min":int(min(eligible)),
            "eligible_individual_count_max":int(max(eligible)),
            "joint_cell_state_identity":identity,
            "joint_cell_state_advantage":advantage
        },
        "primary_verdict":{
            "expected_evaluable_individuals":expected,
            "exact_n_met":observed["eligible_individuals"]==expected,
            "calibrated_identity_positive":identity["observed_minus_null_mean"]>0,
            "upper_tail_le_0_05":identity["p_null_ge_observed"]<=0.05,
            "pass":bool(passed)
        },
        "descriptive_comparison":{
            "frozen_baseline_centered_shape_calibrated_excess":baseline,
            "state_conditioned_calibrated_excess":identity["observed_minus_null_mean"],
            "difference_state_conditioned_minus_baseline":identity["observed_minus_null_mean"]-baseline,
            "not_an_inferential_attenuation_test":True
        },
        "claim_boundary":c["claim_boundary"]
    }
    return payload


def aggregate(c,panel_dir):
    panels={}
    for p in c["preflight"]["evaluable_individuals"]:
        path=panel_dir/f"panel_{p}_v1.json"
        if not path.exists():
            raise RuntimeError(f"missing panel file {path}")
        panels[p]=json.loads(path.read_text(encoding="utf-8"))

    pass_count=sum(int(v["primary_verdict"]["pass"]) for v in panels.values())
    if pass_count>=4:
        category="4_or_5_pass"
    elif pass_count>=2:
        category="2_or_3_pass"
    else:
        category="0_or_1_pass"
    interpretation=c["synthesis"]["decision_matrix"][category]

    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "submission_claims_unchanged":True,
        "selected_movement_state_definition":c["state_definition"],
        "panels":panels,
        "synthesis":{
            "pass_count":pass_count,
            "panel_count":len(panels),
            "category":category,
            "interpretation":interpretation
        },
        "claim_boundary":c["claim_boundary"],
        "stop_rule":c["stop_rule"]
    }
    return payload


def markdown(payload):
    s=payload["synthesis"]
    lines=[
        "# Movement-state-conditioned vertical identity v1","",
        "**POST-FREEZE EXPLORATORY MECHANISM TEST. The frozen v0.3.8 submission claims are unchanged.**","",
        "## Mechanistic question","",
        "Does individual vertical-distribution identity survive after self and other profiles are evaluated under identical 5-km cell × x-y-time movement-intensity-state weights?","",
        "## Result","",
        f"- panels passing state-conditioned identity: **{s['pass_count']}/{s['panel_count']}**",
        f"- frozen synthesis category: **{s['category']}**",
        "",
        "| panel | n | calibrated excess | p(null >= observed) | pass |",
        "|---|---:|---:|---:|---:|"
    ]
    for p,v in payload["panels"].items():
        x=v["permutation"]["joint_cell_state_identity"]
        lines.append(f"| {p} | {v['observed']['eligible_individuals']} | {x['observed_minus_null_mean']:+.3f} | {x['p_null_ge_observed']:.4f} | {'PASS' if v['primary_verdict']['pass'] else 'FAIL'} |")
    lines += ["","## Interpretation","",s["interpretation"],"",
              "Movement states are horizontal-speed quantile proxies, not validated commuting or foraging labels. Persistence therefore establishes within-state individuality only relative to this broad movement-intensity proxy.",""]
    return "\n".join(lines)


def main():
    ap=argparse.ArgumentParser()
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--panel")
    g.add_argument("--aggregate",action="store_true")
    ap.add_argument("--panel-dir",default="post_freeze_extensions/movement_state_conditioning/panel_results")
    args=ap.parse_args()
    c=json.loads(CONTRACT.read_text(encoding="utf-8"))
    panel_dir=ROOT/args.panel_dir

    if args.panel:
        if args.panel not in c["preflight"]["evaluable_individuals"]:
            raise SystemExit(f"unknown panel {args.panel}")
        payload=run_panel(args.panel,c)
        panel_dir.mkdir(parents=True,exist_ok=True)
        path=panel_dir/f"panel_{args.panel}_v1.json"
        path.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        x=payload["permutation"]["joint_cell_state_identity"]
        print(json.dumps({
            "panel":args.panel,
            "n":payload["observed"]["eligible_individuals"],
            "observed":x["observed"],
            "null_mean":x["mean"],
            "calibrated_excess":x["observed_minus_null_mean"],
            "p_upper":x["p_null_ge_observed"],
            "pass":payload["primary_verdict"]["pass"]
        },sort_keys=True))
        return 0

    payload=aggregate(c,panel_dir)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    OUT_MD.write_text(markdown(payload),encoding="utf-8")
    print(json.dumps({
        "pass_count":payload["synthesis"]["pass_count"],
        "category":payload["synthesis"]["category"],
        "panel_results":{
            p:{
                "calibrated_excess":v["permutation"]["joint_cell_state_identity"]["observed_minus_null_mean"],
                "p_upper":v["permutation"]["joint_cell_state_identity"]["p_null_ge_observed"],
                "pass":v["primary_verdict"]["pass"]
            } for p,v in payload["panels"].items()
        }
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
