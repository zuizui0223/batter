#!/usr/bin/env python3
from __future__ import annotations

import json, math, sys
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_tag_altitude_bias_shape as shape
from post_freeze_extensions.temporal_phase_kinematic.preflight_v1 import state_endpoints, phase_assign

CONTRACT=ROOT/"post_freeze_extensions/phyllostomus_2023_500m_phase/preflight_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/phyllostomus_2023_500m_phase/preflight_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/phyllostomus_2023_500m_phase/PREFLIGHT_RESULT_V1.md"


def evaluate(rows,grid_m,min_events):
    rows=phase_assign(rows,3)
    by_session=defaultdict(list)
    sessions_by_ind=defaultdict(list)
    inds_by_cohort=defaultdict(set)
    for r in rows:
        key=(r["cohort"],r["session"])
        stratum=(math.floor(r["x"]/grid_m),math.floor(r["y"]/grid_m),r["state"],r["phase"])
        by_session[key].append((r["iid"],stratum))
    for key,vals in by_session.items():
        iid=vals[0][0];cohort=key[0]
        sessions_by_ind[(cohort,iid)].append(key)
        inds_by_cohort[cohort].add(iid)
    support={k:{v[1] for v in vals} for k,vals in by_session.items()}
    eval_inds=set(); session_rows=[]
    for key,vals in sorted(by_session.items()):
        cohort,session=key;iid=vals[0][0]
        self_keys=[k for k in sessions_by_ind[(cohort,iid)] if k!=key]
        if not self_keys:
            session_rows.append({"cohort":cohort,"session":session,"individual":iid,"supported_events":0,"evaluable":False,"reason":"no_other_self_session"});continue
        self_support=set().union(*(support[k] for k in self_keys))
        other_keys=[k for other in inds_by_cohort[cohort] if other!=iid for k in sessions_by_ind[(cohort,other)]]
        if not other_keys:
            session_rows.append({"cohort":cohort,"session":session,"individual":iid,"supported_events":0,"evaluable":False,"reason":"no_other_individual"});continue
        other_support=set().union(*(support[k] for k in other_keys))
        sup=sum(st in self_support and st in other_support for _,st in vals)
        ok=sup>=min_events
        if ok: eval_inds.add(iid)
        session_rows.append({"cohort":cohort,"session":session,"individual":iid,"phase_valid_endpoints":len(vals),"supported_events":int(sup),"support_fraction":sup/len(vals) if vals else None,"evaluable":bool(ok),"reason":"eligible" if ok else "insufficient_joint_support"})
    return {"evaluable_individuals":len(eval_inds),"evaluable_individual_ids":sorted(eval_inds),"session_support":session_rows}


def main():
    c=json.loads(CONTRACT.read_text())
    records,source=shape.panel_raw(c["panel"])
    eps,thresholds=state_endpoints(records,int(c["context"]["maximum_step_interval_seconds"]))
    result=evaluate(eps,int(c["context"]["fine_grid_m"]),int(c["feasibility"]["minimum_supported_target_events"]))
    required=int(c["feasibility"]["required_evaluable_n"])
    passed=result["evaluable_individuals"]>=required
    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "vertical_values_used":False,
        "source":source,
        "cohort_kinematic_thresholds":thresholds,
        "result":result,
        "required_n":required,
        "preflight_pass":passed,
        "may_open_vertical_outcome":passed,
        "stop_rule":c["stop_rule"]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    OUT_MD.write_text(
        "# P. hastatus 2023: 500-m place × kinematic × phase preflight v1\n\n"
        "**X-Y-TIME ONLY. No vertical outcome used.**\n\n"
        f"Evaluable individuals: **{result['evaluable_individuals']}**; required: **{required}**\n\n"
        f"Preflight PASS: **{passed}**\n"
    )
    print(json.dumps({"evaluable_n":result["evaluable_individuals"],"required_n":required,"pass":passed,"ids":result["evaluable_individual_ids"]},sort_keys=True))
    return 0

if __name__=="__main__": raise SystemExit(main())
