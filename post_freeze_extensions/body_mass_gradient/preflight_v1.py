#!/usr/bin/env python3
from __future__ import annotations

import json, math, sys
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from post_freeze_extensions.body_mass_transfer.preflight_v1 import ref_mass, xy_records, state_endpoints
from post_freeze_extensions.kinematic_state_conditioning.preflight_v1 import evaluate as kinematic_preflight_evaluate

CONTRACT=ROOT/"post_freeze_extensions/body_mass_gradient/preflight_contract_v1.json"
KIN_PREFLIGHT=ROOT/"post_freeze_extensions/kinematic_state_conditioning/preflight_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/body_mass_gradient/preflight_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/body_mass_gradient/PREFLIGHT_RESULT_V1.md"

SPEED2_TURN2={
    "id":"speed2_turn2",
    "speed_bins":2,
    "speed_quantiles":[0.5],
    "turn_bins":2,
    "turn_quantiles":[0.5],
    "state_count":4
}


def evaluate_panel(panel,c,kin_c):
    records=xy_records(panel)
    mass=ref_mass(panel)

    # Reproduce the frozen x-y-time kinematic eligibility set and assert its size.
    base=kinematic_preflight_evaluate(records,SPEED2_TURN2,kin_c)
    baseline_ids=set(base["evaluable_individual_ids"])
    expected=int(c["baseline_n"][panel])
    if len(baseline_ids)!=expected:
        raise RuntimeError(f"{panel}: reproduced baseline n {len(baseline_ids)} != {expected}")

    endpoints=state_endpoints(records,int(c["kinematic_context"]["maximum_step_interval_seconds"]))
    by_session=defaultdict(list)
    sessions_by_ind=defaultdict(list)
    inds_by_cohort=defaultdict(set)
    for r in endpoints:
        key=(r["cohort"],r["session"])
        by_session[key].append(r)
    for key,vals in by_session.items():
        iid=vals[0]["iid"]; cohort=key[0]
        sessions_by_ind[(cohort,iid)].append(key)
        inds_by_cohort[cohort].add(iid)

    donor_support={
        key:{r["stratum"] for r in vals}
        for key,vals in by_session.items()
    }
    min_events=int(c["feasibility"]["minimum_supported_target_events_per_donor"])
    min_donors=int(c["feasibility"]["target_individual_evaluable"].split("at least ")[1].split(" ")[0])
    min_distinct=3

    target_records={}
    eligible_targets=set()
    for target in sorted(baseline_ids):
        target_sessions=[
            key for key,vals in by_session.items()
            if vals and vals[0]["iid"]==target
        ]
        donor_event_counts=defaultdict(list)
        donor_cohorts=defaultdict(set)
        target_mass=mass.get(target)
        if target_mass is None:
            target_records[target]={
                "target_mass":None,"evaluable":False,"reason":"missing_target_mass",
                "evaluable_donors":[]
            }
            continue

        for key in target_sessions:
            cohort=key[0]
            tvals=by_session[key]
            donors=sorted(
                d for d in inds_by_cohort[cohort]
                if d!=target and d in mass
            )
            for donor in donors:
                dkeys=sessions_by_ind.get((cohort,donor),[])
                if not dkeys:
                    continue
                ds=set().union(*(donor_support[k] for k in dkeys))
                supported=sum(r["stratum"] in ds for r in tvals)
                donor_event_counts[donor].append(int(supported))
                donor_cohorts[donor].add(cohort)

        evaluable_donors=sorted(
            donor for donor,counts in donor_event_counts.items()
            if any(x>=min_events for x in counts)
        )
        distances=[
            abs(float(mass[d])-float(target_mass))
            for d in evaluable_donors
        ]
        distinct=len(set(distances))
        ok=len(evaluable_donors)>=min_donors and distinct>=min_distinct
        if ok:
            eligible_targets.add(target)
        target_records[target]={
            "target_mass":float(target_mass),
            "evaluable":bool(ok),
            "reason":"eligible" if ok else (
                "fewer_than_four_donors" if len(evaluable_donors)<min_donors
                else "fewer_than_three_distinct_mass_distances"
            ),
            "evaluable_donor_count":len(evaluable_donors),
            "evaluable_donors":evaluable_donors,
            "distinct_mass_distance_count":distinct,
            "mass_distances":{d:abs(float(mass[d])-float(target_mass)) for d in evaluable_donors},
            "supported_event_counts_by_target_session":dict(donor_event_counts)
        }

    required=max(5,math.ceil(0.70*expected))
    return {
        "baseline_n":expected,
        "baseline_individual_ids":sorted(baseline_ids),
        "required_n":required,
        "evaluable_target_n":len(eligible_targets),
        "evaluable_target_ids":sorted(eligible_targets),
        "retention_fraction":len(eligible_targets)/expected,
        "panel_pass":len(eligible_targets)>=required,
        "targets":target_records
    }


def main():
    c=json.loads(CONTRACT.read_text())
    kin_c=json.loads(KIN_PREFLIGHT.read_text())
    results={}
    allpass=True
    for p in c["panels"]:
        x=evaluate_panel(p,c,kin_c)
        results[p]=x
        allpass=allpass and x["panel_pass"]

    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "vertical_values_used":False,
        "panel_results":results,
        "feasible_to_open_vertical_outcome":bool(allpass),
        "stop_rule":c["stop_rule"]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    lines=[
        "# Continuous body-mass transfer gradient feasibility preflight v1","",
        "**MASS + X-Y-TIME ONLY. No vertical donor score was used.**","",
        f"Feasible to open vertical outcome: **{allpass}**","",
        "| panel | evaluable targets | required | retention |",
        "|---|---:|---:|---:|"
    ]
    for p,x in results.items():
        lines.append(f"| {p} | {x['evaluable_target_n']} | {x['required_n']} | {x['retention_fraction']:.2f} |")
    lines.append("")
    OUT_MD.write_text("\n".join(lines))

    print(json.dumps({
        "feasible":allpass,
        "counts":{p:results[p]["evaluable_target_n"] for p in c["panels"]},
        "required":{p:results[p]["required_n"] for p in c["panels"]},
        "retention":{p:results[p]["retention_fraction"] for p in c["panels"]}
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
