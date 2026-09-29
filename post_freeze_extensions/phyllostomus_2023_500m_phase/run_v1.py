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

CONTRACT=ROOT/"post_freeze_extensions/phyllostomus_2023_500m_phase/contract_v1.json"
OUT=ROOT/"post_freeze_extensions/phyllostomus_2023_500m_phase/result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/phyllostomus_2023_500m_phase/RESULT_V1.md"
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
    max_dt=int(c["context"]["maximum_step_interval_seconds"])
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
            cell=(math.floor(r["x"]/float(c["context"]["fine_grid_m"])),math.floor(r["y"]/float(c["context"]["fine_grid_m"])),r["state"],phase)
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
    expected=int(c["preflight"]["exact_evaluable_n"])
    settings={c["panel"]:{"panel":c["panel"],"B":c["calibration"]["B"],"seed":c["calibration"]["seed"]}}
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



def main():
    c=json.loads(CONTRACT.read_text())
    panel=c["panel"]
    payload=run_panel(panel,c)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    x=payload["permutation"]["phase_kinematic_identity"]
    passed=payload["primary_verdict"]["pass"]
    lines=[
        "# P. hastatus 2023: 500-m place × kinematic × phase vertical identity v1","",
        "**POST-HOC MECHANISTIC DRILL-DOWN.**","",
        f"- n: **{payload['observed']['eligible_individuals']}**",
        f"- calibrated excess: **{x['observed_minus_null_mean']:+.4f}**",
        f"- p(null >= observed): **{x['p_null_ge_observed']:.4f}**",
        f"- frozen verdict: **{'PASS' if passed else 'FAIL'}**","",
        "## Interpretation","",
        c["interpretation"]["if_pass" if passed else "if_fail"],""
    ]
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps({
        "panel":panel,
        "n":payload["observed"]["eligible_individuals"],
        "calibrated_excess":x["observed_minus_null_mean"],
        "p_upper":x["p_null_ge_observed"],
        "pass":passed
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
