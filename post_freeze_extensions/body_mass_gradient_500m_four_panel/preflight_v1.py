#!/usr/bin/env python3
from __future__ import annotations

import json, math, sys
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from post_freeze_extensions.body_mass_transfer.preflight_v1 import ref_mass, xy_records
from post_freeze_extensions.fine_place_kinematic.preflight_v1 import evaluate_grid, KIN_CAND
from post_freeze_extensions.kinematic_state_conditioning.preflight_v1 import endpoints as kin_endpoints, assign_states as kin_assign_states

CONTRACT=ROOT/"post_freeze_extensions/body_mass_gradient_500m_four_panel/preflight_contract_v1.json"
FINE_CONTRACT=ROOT/"post_freeze_extensions/fine_place_kinematic/preflight_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/body_mass_gradient_500m_four_panel/preflight_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/body_mass_gradient_500m_four_panel/PREFLIGHT_RESULT_V1.md"


def evaluate_panel(panel,c,fine_c):
    records=xy_records(panel)
    mass=ref_mass(panel)

    fine=evaluate_grid(records,500,fine_c)
    baseline_ids=set(fine["evaluable_individual_ids"])
    expected=int(c["baseline"]["expected_evaluable_n"][panel])
    if len(baseline_ids)!=expected:
        raise RuntimeError(f"{panel}: reproduced 500-m baseline n {len(baseline_ids)} != {expected}")

    eps=kin_endpoints(records,1800)
    eps,_=kin_assign_states(eps,KIN_CAND)

    by_session=defaultdict(list)
    sessions_by_ind=defaultdict(list)
    inds_by_cohort=defaultdict(set)
    for r in eps:
        key=(r["cohort"],r["session"])
        rr={**r,"stratum":(math.floor(r["x"]/500.0),math.floor(r["y"]/500.0),r["state"])}
        by_session[key].append(rr)
    for key,vals in by_session.items():
        iid=vals[0]["iid"]; cohort=key[0]
        sessions_by_ind[(cohort,iid)].append(key)
        inds_by_cohort[cohort].add(iid)

    support={k:{r["stratum"] for r in vals} for k,vals in by_session.items()}
    min_events=int(c["feasibility"]["minimum_supported_target_events_per_donor"])
    min_donors=4
    min_distinct=3

    targets={}
    eligible=set()

    for target in sorted(baseline_ids):
        tmass=mass.get(target)
        if tmass is None:
            targets[target]={"evaluable":False,"reason":"missing_target_mass","evaluable_donor_count":0}
            continue

        target_sessions=[k for k,vals in by_session.items() if vals and vals[0]["iid"]==target]
        donor_counts=defaultdict(list)

        for key in target_sessions:
            cohort=key[0]
            tvals=by_session[key]
            donors=sorted(d for d in inds_by_cohort[cohort] if d!=target and d in mass)
            for donor in donors:
                dkeys=sessions_by_ind.get((cohort,donor),[])
                if not dkeys:
                    continue
                ds=set().union(*(support[k] for k in dkeys))
                donor_counts[donor].append(int(sum(r["stratum"] in ds for r in tvals)))

        evaluable_donors=sorted(d for d,counts in donor_counts.items() if any(x>=min_events for x in counts))
        distances=[abs(float(mass[d])-float(tmass)) for d in evaluable_donors]
        distinct=len(set(distances))
        ok=len(evaluable_donors)>=min_donors and distinct>=min_distinct
        if ok:
            eligible.add(target)

        targets[target]={
            "target_mass":float(tmass),
            "evaluable":bool(ok),
            "reason":"eligible" if ok else (
                "fewer_than_four_donors" if len(evaluable_donors)<min_donors
                else "fewer_than_three_distinct_mass_distances"
            ),
            "evaluable_donor_count":len(evaluable_donors),
            "evaluable_donors":evaluable_donors,
            "distinct_mass_distance_count":distinct,
            "mass_distances":{d:abs(float(mass[d])-float(tmass)) for d in evaluable_donors},
            "supported_event_counts_by_target_session":dict(donor_counts)
        }

    required=max(5,math.ceil(0.70*expected))
    return {
        "baseline_n":expected,
        "baseline_individual_ids":sorted(baseline_ids),
        "required_n":required,
        "evaluable_target_n":len(eligible),
        "evaluable_target_ids":sorted(eligible),
        "retention_fraction":len(eligible)/expected,
        "panel_pass":len(eligible)>=required,
        "targets":targets
    }


def main():
    c=json.loads(CONTRACT.read_text())
    fine_c=json.loads(FINE_CONTRACT.read_text())
    results={}
    allpass=True
    for panel in c["panels"]:
        x=evaluate_panel(panel,c,fine_c)
        results[panel]=x
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
        "# 500-m body-mass donor-gradient feasibility preflight v1","",
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
