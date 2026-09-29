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

CONTRACT=ROOT/"post_freeze_extensions/temporal_phase_kinematic_four_panel/contract_v1.json"
OUT=ROOT/"post_freeze_extensions/temporal_phase_kinematic_four_panel/result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/temporal_phase_kinematic_four_panel/RESULT_V1.md"
EDGES=(-math.inf,-400.0,-200.0,-100.0,-50.0,0.0,50.0,100.0,200.0,400.0,math.inf)


def turn_angle(a,b,c):
    v1x,v1y=b["x"]-a["x"],b["y"]-a["y"]
    v2x,v2y=c["x"]-b["x"],c["y"]-b["y"]
    n1=math.hypot(v1x,v1y); n2=math.hypot(v2x,v2y)
    if n1<=0 or n2<=0:
        return None
    z=max(-1.0,min(1.0,(v1x*v2x+v1y*v2y)/(n1*n2)))
    return math.acos(z)


def build_events(panel,c):
    records,source=shape.panel_raw(panel)
    by_session=defaultdict(list)
    for r in records:
        by_session[(r["cohort"],r["session"])].append(r)

    medians={}
    raw_endpoints=[]
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
            tr=turn_angle(a,b,d)
            if tr is None:
                continue
            sp=math.hypot(d["x"]-b["x"],d["y"]-b["y"])/dt2
            raw_endpoints.append({
                "cohort":d["cohort"],"session":d["session"],"iid":d["iid"],
                "t":d["t"],"x":d["x"],"y":d["y"],"h":d["h"],
                "speed":float(sp),"turn":float(tr)
            })

    sp=defaultdict(list);tu=defaultdict(list)
    for r in raw_endpoints:
        sp[r["cohort"]].append(r["speed"]);tu[r["cohort"]].append(r["turn"])
    thresholds={cohort:{
        "speed_median":float(np.median(np.asarray(sp[cohort],dtype=float))),
        "turn_median_rad":float(np.median(np.asarray(tu[cohort],dtype=float)))
    } for cohort in sp}

    tmp=defaultdict(list)
    for r in raw_endpoints:
        th=thresholds[r["cohort"]]
        state=int(r["speed"]>th["speed_median"])*2+int(r["turn"]>th["turn_median_rad"])
        tmp[(r["cohort"],r["session"])].append({**r,"state":state})

    events=defaultdict(list)
    phase_counts=defaultdict(lambda:[0,0,0])
    for key,vals in sorted(tmp.items()):
        vals=sorted(vals,key=lambda x:x["t"])
        t0=vals[0]["t"];t1=vals[-1]["t"]
        dur=(t1-t0).total_seconds()
        if dur<=0:
            continue
        med=medians[key]
        for r in vals:
            frac=(r["t"]-t0).total_seconds()/dur
            phase=min(2,max(0,int(frac*3)))
            resid=float(r["h"]-med)
            cell=(math.floor(r["x"]/5000.0),math.floor(r["y"]/5000.0),r["state"],phase)
            events[r["cohort"]].append(Event(
                individual=r["iid"],timestamp=r["t"],cell=cell,
                zbin=z_bin(resid,edges=EDGES),session=r["session"]
            ))
            phase_counts[r["cohort"]][phase]+=1

    return dict(events),{
        "source":source,
        "cohort_thresholds":thresholds,
        "cohort_phase_counts":dict(phase_counts),
        "kinematic_endpoint_count":len(raw_endpoints),
        "session_count":len(by_session)
    }


def run_panel(panel,c):
    expected=int(c["preflight"]["expected_evaluable_individuals"][panel])
    settings={x["panel"]:x for x in c["calibration"]["settings"]}
    events_by_cohort,diag=build_events(panel,c)
    arrays={cohort:cal.make_cohort_arrays(events,len(EDGES)-1) for cohort,events in sorted(events_by_cohort.items())}
    observed,per_ind,session_rows=cal.observed_eval(arrays)
    if observed["eligible_individuals"]!=expected:
        raise RuntimeError(f"{panel}: evaluable n {observed['eligible_individuals']} != expected {expected}")

    setting=settings[panel]
    rng=np.random.default_rng(int(setting["seed"]))
    null=[];eligible=[];invalid=0
    for _ in range(int(setting["B"])):
        p=cal.perm_eval(arrays,rng)
        if p["eligible_individuals"]<1 or p["common_cell_marginal"] is None:
            invalid+=1;continue
        null.append(float(p["common_cell_marginal"]))
        eligible.append(int(p["eligible_individuals"]))
    if not null:
        raise RuntimeError(f"{panel}: no valid permutations")

    identity=cal.tail_summary(null,float(observed["common_cell_marginal"]))
    passed=(
        observed["eligible_individuals"]==expected
        and identity["observed_minus_null_mean"]>0
        and identity["p_null_ge_observed"]<=0.05
    )
    return {
        "schema_version":1,"study_id":c["study_id"],"panel":panel,
        "diagnostics":diag,
        "observed":{**observed,"individual_results":per_ind,"session_results":session_rows},
        "permutation":{
            "B":int(setting["B"]),"seed":int(setting["seed"]),
            "valid_replicates":len(null),"invalid_replicates":invalid,
            "eligible_individual_count_min":int(min(eligible)),
            "eligible_individual_count_max":int(max(eligible)),
            "phase_kinematic_identity":identity
        },
        "primary_verdict":{
            "expected_evaluable_individuals":expected,
            "exact_n_met":observed["eligible_individuals"]==expected,
            "calibrated_identity_positive":identity["observed_minus_null_mean"]>0,
            "upper_tail_le_0_05":identity["p_null_ge_observed"]<=0.05,
            "pass":bool(passed)
        },
        "claim_boundary":c["claim_boundary"]
    }


def aggregate(c,panel_dir):
    panels={}
    for p in c["preflight"]["included_panels"]:
        path=panel_dir/f"panel_{p}_v1.json"
        if not path.exists(): raise RuntimeError(f"missing panel {path}")
        panels[p]=json.loads(path.read_text())
    n=sum(int(v["primary_verdict"]["pass"]) for v in panels.values())
    cat="3_or_4_pass" if n>=3 else ("1_or_2_pass" if n>=1 else "0_pass")
    return {
        "schema_version":1,"study_id":c["study_id"],"submission_claims_unchanged":True,
        "panels":panels,
        "synthesis":{"pass_count":n,"panel_count":len(panels),"category":cat,
                     "interpretation":c["synthesis"]["decision_matrix"][cat]},
        "generalization_limit":c["synthesis"]["generalization_limit"],
        "claim_boundary":c["claim_boundary"],"stop_rule":c["stop_rule"]
    }


def markdown(payload):
    s=payload["synthesis"]
    lines=["# Four-panel temporal-phase × kinematic vertical identity v1","",
           "**POST-FREEZE STRUCTURALLY-EVALUABLE SUBSET TEST. No inference to Eidolon.**","",
           f"- passing panels: **{s['pass_count']}/{s['panel_count']}**",
           f"- synthesis: **{s['category']}**","",
           "| panel | n | calibrated excess | p(null >= observed) | pass |",
           "|---|---:|---:|---:|---:|"]
    for p,v in payload["panels"].items():
        x=v["permutation"]["phase_kinematic_identity"]
        lines.append(f"| {p} | {v['observed']['eligible_individuals']} | {x['observed_minus_null_mean']:+.3f} | {x['p_null_ge_observed']:.4f} | {'PASS' if v['primary_verdict']['pass'] else 'FAIL'} |")
    lines += ["","## Interpretation","",s["interpretation"],"",
              "Relative tracked-session phase is a proxy, not solar/circadian phase.",""]
    return "\n".join(lines)


def main():
    ap=argparse.ArgumentParser()
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--panel")
    g.add_argument("--aggregate",action="store_true")
    ap.add_argument("--panel-dir",default="post_freeze_extensions/temporal_phase_kinematic_four_panel/panel_results")
    args=ap.parse_args()
    c=json.loads(CONTRACT.read_text())
    panel_dir=ROOT/args.panel_dir
    if args.panel:
        if args.panel not in c["preflight"]["included_panels"]: raise SystemExit("unknown panel")
        payload=run_panel(args.panel,c)
        panel_dir.mkdir(parents=True,exist_ok=True)
        (panel_dir/f"panel_{args.panel}_v1.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
        x=payload["permutation"]["phase_kinematic_identity"]
        print(json.dumps({"panel":args.panel,"n":payload["observed"]["eligible_individuals"],"calibrated_excess":x["observed_minus_null_mean"],"p_upper":x["p_null_ge_observed"],"pass":payload["primary_verdict"]["pass"]},sort_keys=True))
        return 0
    payload=aggregate(c,panel_dir)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    OUT_MD.write_text(markdown(payload))
    print(json.dumps({"pass_count":payload["synthesis"]["pass_count"],"category":payload["synthesis"]["category"],"panels":{p:{"calibrated_excess":v["permutation"]["phase_kinematic_identity"]["observed_minus_null_mean"],"p_upper":v["permutation"]["phase_kinematic_identity"]["p_null_ge_observed"],"pass":v["primary_verdict"]["pass"]} for p,v in payload["panels"].items()}},sort_keys=True))
    return 0

if __name__=="__main__": raise SystemExit(main())
