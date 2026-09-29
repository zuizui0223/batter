#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, math, sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from batter.analysis import Event, z_bin
import scripts.run_cross_panel_estimator_calibration as cal
import scripts.run_tag_altitude_bias_shape as shape

CONTRACT=ROOT/"post_freeze_extensions/kinematic_state_conditioning/contract_v1.json"
OUT=ROOT/"post_freeze_extensions/kinematic_state_conditioning/result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/kinematic_state_conditioning/RESULT_V1.md"
EDGES=(-math.inf,-400.0,-200.0,-100.0,-50.0,0.0,50.0,100.0,200.0,400.0,math.inf)
CELL=5000.0


def turn_angle(v1x,v1y,v2x,v2y):
    a=math.hypot(v1x,v1y); b=math.hypot(v2x,v2y)
    if a<=0 or b<=0:
        return None
    c=max(-1.0,min(1.0,(v1x*v2x+v1y*v2y)/(a*b)))
    return math.acos(c)


def build_events(panel,c):
    records,source=shape.panel_raw(panel)
    by_session=defaultdict(list)
    for r in records:
        by_session[(r["cohort"],r["session"])].append(r)

    medians={}
    endpoints=[]
    max_dt=int(c["state_definition"]["maximum_step_interval_seconds"])
    for key,vals in sorted(by_session.items()):
        vals=sorted(vals,key=lambda x:x["t"])
        medians[key]=float(np.median([r["h"] for r in vals]))
        for i in range(2,len(vals)):
            a,b,d=vals[i-2],vals[i-1],vals[i]
            dt1=(b["t"]-a["t"]).total_seconds()
            dt2=(d["t"]-b["t"]).total_seconds()
            if not all(math.isfinite(x) and x>0 and x<=max_dt for x in (dt1,dt2)):
                continue
            v1x,v1y=b["x"]-a["x"],b["y"]-a["y"]
            v2x,v2y=d["x"]-b["x"],d["y"]-b["y"]
            turn=turn_angle(v1x,v1y,v2x,v2y)
            if turn is None:
                continue
            speed=math.hypot(v2x,v2y)/dt2
            endpoints.append({
                "cohort":d["cohort"],"session":d["session"],"iid":d["iid"],
                "t":d["t"],"x":d["x"],"y":d["y"],"h":d["h"],
                "speed":float(speed),"turn":float(turn)
            })

    sp=defaultdict(list); tu=defaultdict(list)
    for r in endpoints:
        sp[r["cohort"]].append(r["speed"]); tu[r["cohort"]].append(r["turn"])
    thresholds={}
    for cohort in sorted(sp):
        thresholds[cohort]={
            "speed_median":float(np.median(np.asarray(sp[cohort],dtype=float))),
            "turn_median_rad":float(np.median(np.asarray(tu[cohort],dtype=float)))
        }

    events=defaultdict(list)
    counts=defaultdict(lambda:[0,0,0,0])
    for r in endpoints:
        th=thresholds[r["cohort"]]
        sb=int(r["speed"]>th["speed_median"])
        tb=int(r["turn"]>th["turn_median_rad"])
        state=sb*2+tb
        med=medians[(r["cohort"],r["session"])]
        resid=float(r["h"]-med)
        stratum=(math.floor(r["x"]/CELL),math.floor(r["y"]/CELL),state)
        events[r["cohort"]].append(Event(
            individual=r["iid"],timestamp=r["t"],cell=stratum,
            zbin=z_bin(resid,edges=EDGES),session=r["session"]
        ))
        counts[r["cohort"]][state]+=1

    return dict(events),{
        "source":source,
        "total_retained_numeric_height_records":len(records),
        "kinematic_valid_endpoint_records":len(endpoints),
        "cohort_thresholds":thresholds,
        "cohort_state_counts":dict(counts),
        "session_count":len(by_session)
    }


def run_panel(panel,c):
    expected=int(c["estimator"]["expected_evaluable_individuals"][panel])
    settings={x["panel"]:x for x in c["calibration"]["settings"]}
    events_by_cohort,diag=build_events(panel,c)
    arrays={cohort:cal.make_cohort_arrays(events,len(EDGES)-1) for cohort,events in sorted(events_by_cohort.items())}
    observed,per_ind,session_rows=cal.observed_eval(arrays)
    if observed["eligible_individuals"]!=expected:
        raise RuntimeError(f"{panel}: evaluable n {observed['eligible_individuals']} != expected {expected}")

    setting=settings[panel]
    rng=np.random.default_rng(int(setting["seed"]))
    null=[]; null_adv=[]; eligible=[]; invalid=0
    for _ in range(int(setting["B"])):
        p=cal.perm_eval(arrays,rng)
        if p["eligible_individuals"]<1 or p["common_cell_marginal"] is None:
            invalid+=1; continue
        null.append(float(p["common_cell_marginal"]))
        null_adv.append(float(p["common_cell_advantage"]))
        eligible.append(int(p["eligible_individuals"]))
    if not null:
        raise RuntimeError(f"{panel}: no valid null replicates")

    identity=cal.tail_summary(null,float(observed["common_cell_marginal"]))
    advantage=cal.tail_summary(null_adv,float(observed["common_cell_advantage"]))
    passed=(
        observed["eligible_individuals"]==expected
        and identity["observed_minus_null_mean"]>0
        and identity["p_null_ge_observed"]<=0.05
    )
    baseline=float(c["synthesis"]["descriptive_baseline_state_conditioned_excess"][panel])

    return {
        "schema_version":1,"study_id":c["study_id"],"panel":panel,
        "preflight_selected_candidate":c["preflight"]["selected_candidate_id"],
        "diagnostics":diag,
        "observed":{**observed,"individual_results":per_ind,"session_results":session_rows},
        "permutation":{
            "B":int(setting["B"]),"seed":int(setting["seed"]),
            "valid_replicates":len(null),"invalid_replicates":invalid,
            "eligible_individual_count_min":int(min(eligible)),
            "eligible_individual_count_max":int(max(eligible)),
            "kinematic_state_identity":identity,
            "kinematic_state_advantage":advantage
        },
        "primary_verdict":{
            "expected_evaluable_individuals":expected,
            "exact_n_met":observed["eligible_individuals"]==expected,
            "calibrated_identity_positive":identity["observed_minus_null_mean"]>0,
            "upper_tail_le_0_05":identity["p_null_ge_observed"]<=0.05,
            "pass":bool(passed)
        },
        "descriptive_comparison":{
            "speed_only_state_conditioned_excess":baseline,
            "speed_turn_state_conditioned_excess":identity["observed_minus_null_mean"],
            "difference":identity["observed_minus_null_mean"]-baseline,
            "retained_fraction_of_speed_only_excess":identity["observed_minus_null_mean"]/baseline if baseline!=0 else None,
            "not_an_inferential_attenuation_test":True
        },
        "claim_boundary":c["claim_boundary"]
    }


def aggregate(c,panel_dir):
    panels={}
    for p in c["preflight"]["evaluable_individuals"]:
        path=panel_dir/f"panel_{p}_v1.json"
        if not path.exists(): raise RuntimeError(f"missing panel {path}")
        panels[p]=json.loads(path.read_text())
    n=sum(int(v["primary_verdict"]["pass"]) for v in panels.values())
    category="4_or_5_pass" if n>=4 else ("2_or_3_pass" if n>=2 else "0_or_1_pass")
    return {
        "schema_version":1,"study_id":c["study_id"],"submission_claims_unchanged":True,
        "panels":panels,
        "synthesis":{"pass_count":n,"panel_count":len(panels),"category":category,
                     "interpretation":c["synthesis"]["decision_matrix"][category]},
        "claim_boundary":c["claim_boundary"],"stop_rule":c["stop_rule"]
    }


def markdown(payload):
    s=payload["synthesis"]
    lines=["# Speed × turning-state-conditioned vertical identity v1","",
           "**POST-FREEZE EXPLORATORY MECHANISM TEST. Frozen v0.3.8 claims are unchanged.**","",
           f"- panels passing: **{s['pass_count']}/{s['panel_count']}**",
           f"- synthesis: **{s['category']}**","",
           "| panel | n | calibrated excess | p(null >= observed) | retained vs speed-only | pass |",
           "|---|---:|---:|---:|---:|---:|"]
    for p,v in payload["panels"].items():
        x=v["permutation"]["kinematic_state_identity"]
        frac=v["descriptive_comparison"]["retained_fraction_of_speed_only_excess"]
        lines.append(f"| {p} | {v['observed']['eligible_individuals']} | {x['observed_minus_null_mean']:+.3f} | {x['p_null_ge_observed']:.4f} | {frac:.2f} | {'PASS' if v['primary_verdict']['pass'] else 'FAIL'} |")
    lines += ["","## Interpretation","",s["interpretation"],"",
              "These are speed × turning kinematic proxies, not validated foraging/commuting states.",""]
    return "\n".join(lines)


def main():
    ap=argparse.ArgumentParser()
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--panel")
    g.add_argument("--aggregate",action="store_true")
    ap.add_argument("--panel-dir",default="post_freeze_extensions/kinematic_state_conditioning/panel_results")
    args=ap.parse_args()
    c=json.loads(CONTRACT.read_text())
    panel_dir=ROOT/args.panel_dir

    if args.panel:
        if args.panel not in c["preflight"]["evaluable_individuals"]:
            raise SystemExit(f"unknown panel {args.panel}")
        payload=run_panel(args.panel,c)
        panel_dir.mkdir(parents=True,exist_ok=True)
        path=panel_dir/f"panel_{args.panel}_v1.json"
        path.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
        x=payload["permutation"]["kinematic_state_identity"]
        print(json.dumps({
            "panel":args.panel,"n":payload["observed"]["eligible_individuals"],
            "calibrated_excess":x["observed_minus_null_mean"],"p_upper":x["p_null_ge_observed"],
            "retained_fraction":payload["descriptive_comparison"]["retained_fraction_of_speed_only_excess"],
            "pass":payload["primary_verdict"]["pass"]
        },sort_keys=True))
        return 0

    payload=aggregate(c,panel_dir)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    OUT_MD.write_text(markdown(payload))
    print(json.dumps({
        "pass_count":payload["synthesis"]["pass_count"],
        "category":payload["synthesis"]["category"],
        "panels":{p:{
            "calibrated_excess":v["permutation"]["kinematic_state_identity"]["observed_minus_null_mean"],
            "p_upper":v["permutation"]["kinematic_state_identity"]["p_null_ge_observed"],
            "retained_fraction":v["descriptive_comparison"]["retained_fraction_of_speed_only_excess"],
            "pass":v["primary_verdict"]["pass"]
        } for p,v in payload["panels"].items()}
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
