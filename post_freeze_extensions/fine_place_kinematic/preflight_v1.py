#!/usr/bin/env python3
from __future__ import annotations

import json, math, sys
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_tag_altitude_bias_shape as shape
from post_freeze_extensions.kinematic_state_conditioning.preflight_v1 import (
    endpoints as kin_endpoints,
    assign_states as kin_assign_states,
    evaluate as kin_evaluate,
)

CONTRACT=ROOT/"post_freeze_extensions/fine_place_kinematic/preflight_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/fine_place_kinematic/preflight_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/fine_place_kinematic/PREFLIGHT_RESULT_V1.md"

KIN_CAND={
    "id":"speed2_turn2",
    "speed_bins":2,
    "speed_quantiles":[0.5],
    "turn_bins":2,
    "turn_quantiles":[0.5],
    "state_count":4,
}


def evaluate_grid(records,grid_m,c):
    eps=kin_endpoints(records,int(c["state_definition"]["maximum_step_interval_seconds"]))
    eps,thresholds=kin_assign_states(eps,KIN_CAND)

    by_session=defaultdict(list)
    sessions_by_ind=defaultdict(list)
    inds_by_cohort=defaultdict(set)
    for r in eps:
        key=(r["cohort"],r["session"])
        stratum=(math.floor(r["x"]/grid_m),math.floor(r["y"]/grid_m),r["state"])
        by_session[key].append((r["iid"],stratum))
    for key,vals in by_session.items():
        iid=vals[0][0]; cohort=key[0]
        sessions_by_ind[(cohort,iid)].append(key)
        inds_by_cohort[cohort].add(iid)

    supports={k:{x[1] for x in vals} for k,vals in by_session.items()}
    min_events=int(c["feasibility"]["minimum_supported_target_events"])
    eval_inds=set(); session_rows=[]

    for key,vals in sorted(by_session.items()):
        cohort,session=key; iid=vals[0][0]
        self_keys=[k for k in sessions_by_ind[(cohort,iid)] if k!=key]
        if not self_keys:
            session_rows.append({"cohort":cohort,"session":session,"individual":iid,"supported_events":0,"evaluable":False,"reason":"no_other_self_session"})
            continue
        self_support=set().union(*(supports[k] for k in self_keys))
        other_keys=[]
        for other in inds_by_cohort[cohort]:
            if other!=iid:
                other_keys.extend(sessions_by_ind[(cohort,other)])
        if not other_keys:
            session_rows.append({"cohort":cohort,"session":session,"individual":iid,"supported_events":0,"evaluable":False,"reason":"no_other_individual"})
            continue
        other_support=set().union(*(supports[k] for k in other_keys))
        supported=sum(stratum in self_support and stratum in other_support for _,stratum in vals)
        ok=supported>=min_events
        if ok:
            eval_inds.add(iid)
        session_rows.append({
            "cohort":cohort,"session":session,"individual":iid,
            "kinematic_endpoints":len(vals),"supported_events":int(supported),
            "support_fraction":float(supported/len(vals)) if vals else None,
            "evaluable":bool(ok),"reason":"eligible" if ok else "insufficient_fine_place_kinematic_support"
        })

    return {
        "fine_grid_m":int(grid_m),
        "evaluable_individuals":len(eval_inds),
        "evaluable_individual_ids":sorted(eval_inds),
        "cohort_thresholds":thresholds,
        "session_support":session_rows
    }


def main():
    c=json.loads(CONTRACT.read_text())
    results={}
    for panel in c["panels"]:
        records,source=shape.panel_raw(panel)
        # First reproduce the already-frozen 5-km kinematic preflight n exactly.
        base=kin_evaluate(records,KIN_CAND,{
            "kinematics":{"maximum_step_interval_seconds":int(c["state_definition"]["maximum_step_interval_seconds"])},
            "feasibility":{"minimum_supported_target_events":int(c["feasibility"]["minimum_supported_target_events"])}
        })
        expected=int(c["kinematic_baseline_n"][panel])
        if base["evaluable_individuals"]!=expected:
            raise RuntimeError(f"{panel}: 5-km kinematic baseline n {base['evaluable_individuals']} != expected {expected}")

        results[panel]={"source":source,"verified_5km_kinematic_baseline_n":expected,"candidates":{}}
        for cand in c["fine_place_candidates_in_priority_order"]:
            x=evaluate_grid(records,int(cand["fine_grid_m"]),c)
            x["baseline_n"]=expected
            x["retention_fraction"]=x["evaluable_individuals"]/expected
            x["retains_70_percent"]=x["evaluable_individuals"]>=math.ceil(0.70*expected)
            x["retains_at_least_5"]=x["evaluable_individuals"]>=5
            x["candidate_pass"]=bool(x["retains_70_percent"] and x["retains_at_least_5"])
            results[panel]["candidates"][cand["id"]]=x

    selected=None
    for cand in c["fine_place_candidates_in_priority_order"]:
        cid=cand["id"]
        if all(results[p]["candidates"][cid]["candidate_pass"] for p in c["panels"]):
            selected=cid
            break

    grid=next((int(x["fine_grid_m"]) for x in c["fine_place_candidates_in_priority_order"] if x["id"]==selected),None)
    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "vertical_values_used_for_selection":False,
        "verified_same_kinematic_definition_as_outcome_family":True,
        "panel_results":results,
        "selected_candidate_id":selected,
        "selected_grid_m":grid,
        "feasible_to_open_five_panel_vertical_outcome":selected is not None,
        "stop_rule":c["stop_rule"]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    lines=[
        "# Fine-place × speed-turn kinematic feasibility preflight v1","",
        "**X-Y-TIME ONLY. The same frozen speed2_turn2 definition is used throughout.**","",
        f"Selected candidate: **{selected if selected else 'NONE'}**","",
        "| candidate | "+" | ".join(c["panels"])+" |",
        "|---|"+"|".join(["---:"]*len(c["panels"]))+"|"
    ]
    for cand in c["fine_place_candidates_in_priority_order"]:
        cid=cand["id"]
        vals=[f"{results[p]['candidates'][cid]['evaluable_individuals']}/{c['kinematic_baseline_n'][p]}" for p in c["panels"]]
        lines.append("| "+cid+" | "+" | ".join(vals)+" |")
    lines += ["",f"Five-panel vertical outcome may be opened: **{selected is not None}**",""]
    OUT_MD.write_text("\n".join(lines))

    print(json.dumps({
        "selected_candidate_id":selected,
        "selected_grid_m":grid,
        "feasible":selected is not None,
        "counts":{cand["id"]:{p:results[p]["candidates"][cand["id"]]["evaluable_individuals"] for p in c["panels"]} for cand in c["fine_place_candidates_in_priority_order"]},
        "baseline":c["kinematic_baseline_n"]
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
