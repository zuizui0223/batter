#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_tag_altitude_bias_shape as shape

CONTRACT=ROOT/"post_freeze_extensions/movement_state_conditioning/preflight_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/movement_state_conditioning/preflight_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/movement_state_conditioning/PREFLIGHT_RESULT_V1.md"


def step_table(records):
    by_session=defaultdict(list)
    for r in records:
        by_session[(r["cohort"],r["session"])].append(r)
    rows=[]
    dt_all=[]
    for (cohort,session),vals in sorted(by_session.items()):
        vals=sorted(vals,key=lambda x:x["t"])
        for i in range(1,len(vals)):
            a,b=vals[i-1],vals[i]
            dt=(b["t"]-a["t"]).total_seconds()
            if not math.isfinite(dt) or dt<=0:
                continue
            dt_all.append(dt)
            dist=math.hypot(b["x"]-a["x"],b["y"]-a["y"])
            speed=dist/dt
            rows.append({
                "cohort":cohort,
                "session":session,
                "iid":b["iid"],
                "x":b["x"],
                "y":b["y"],
                "dt":float(dt),
                "speed":float(speed),
            })
    return rows,dt_all


def state_thresholds(steps,max_dt,states):
    by_cohort=defaultdict(list)
    for r in steps:
        if r["dt"]<=max_dt:
            by_cohort[r["cohort"]].append(r["speed"])
    thresholds={}
    for cohort,vals in sorted(by_cohort.items()):
        a=np.asarray(vals,dtype=float)
        if len(a)<states:
            thresholds[cohort]=[]
            continue
        qs=[i/states for i in range(1,states)]
        thresholds[cohort]=[float(x) for x in np.quantile(a,qs)]
    return thresholds


def assign_states(steps,max_dt,states,thresholds):
    out=defaultdict(list)
    for r in steps:
        if r["dt"]>max_dt:
            continue
        cuts=thresholds.get(r["cohort"],[])
        if len(cuts)!=states-1:
            continue
        st=int(np.searchsorted(np.asarray(cuts),r["speed"],side="right"))
        coarse=(math.floor(r["x"]/5000.0),math.floor(r["y"]/5000.0))
        out[(r["cohort"],r["session"])].append({
            "iid":r["iid"],
            "coarse":coarse,
            "state":st,
        })
    return out


def evaluate_panel(records,candidate,baseline_n,min_events):
    steps,dt_all=step_table(records)
    max_dt=int(candidate["max_dt_seconds"])
    states=int(candidate["states"])
    thresholds=state_thresholds(steps,max_dt,states)
    ss=assign_states(steps,max_dt,states,thresholds)

    session_iid={}
    sessions_by_ind=defaultdict(list)
    inds_by_cohort=defaultdict(set)
    for (cohort,session),vals in ss.items():
        if not vals:
            continue
        iid=vals[0]["iid"]
        session_iid[(cohort,session)]=iid
        sessions_by_ind[(cohort,iid)].append((cohort,session))
        inds_by_cohort[cohort].add(iid)

    pairsets={key:{(v["coarse"],v["state"]) for v in vals} for key,vals in ss.items()}
    session_rows=[]
    eval_ind=set()
    for key,vals in sorted(ss.items()):
        cohort,session=key
        if not vals:
            continue
        iid=session_iid[key]
        self_sessions=[k for k in sessions_by_ind[(cohort,iid)] if k!=key]
        if not self_sessions:
            session_rows.append({
                "cohort":cohort,"session":session,"individual":iid,
                "valid_state_events":len(vals),"supported_events":0,
                "evaluable":False,"reason":"no_other_self_session"
            })
            continue
        self_support=set().union(*(pairsets[k] for k in self_sessions))
        other_keys=[]
        for other in inds_by_cohort[cohort]:
            if other==iid:
                continue
            other_keys.extend(sessions_by_ind.get((cohort,other),[]))
        if not other_keys:
            session_rows.append({
                "cohort":cohort,"session":session,"individual":iid,
                "valid_state_events":len(vals),"supported_events":0,
                "evaluable":False,"reason":"no_other_individual"
            })
            continue
        other_support=set().union(*(pairsets[k] for k in other_keys))
        supported=sum(((v["coarse"],v["state"]) in self_support and (v["coarse"],v["state"]) in other_support) for v in vals)
        ok=supported>=min_events
        if ok:
            eval_ind.add(iid)
        session_rows.append({
            "cohort":cohort,"session":session,"individual":iid,
            "valid_state_events":len(vals),"supported_events":int(supported),
            "support_fraction":float(supported/len(vals)) if vals else None,
            "evaluable":bool(ok),
            "reason":"eligible" if ok else "insufficient_cell_state_support"
        })

    dt=np.asarray(dt_all,dtype=float)
    valid_cap=sum(r["dt"]<=max_dt for r in steps)
    panel={
        "candidate_id":candidate["id"],
        "states":states,
        "max_dt_seconds":max_dt,
        "baseline_evaluable_individuals":int(baseline_n),
        "evaluable_individuals":len(eval_ind),
        "retention_fraction":float(len(eval_ind)/baseline_n),
        "retains_70_percent":bool(len(eval_ind)>=math.ceil(0.70*baseline_n)),
        "retains_at_least_5":bool(len(eval_ind)>=5),
        "candidate_pass":bool(len(eval_ind)>=math.ceil(0.70*baseline_n) and len(eval_ind)>=5),
        "step_count_positive_dt":len(steps),
        "step_count_within_cap":int(valid_cap),
        "step_fraction_within_cap":float(valid_cap/len(steps)) if steps else None,
        "dt_seconds_q50":float(np.quantile(dt,0.5)) if len(dt) else None,
        "dt_seconds_q90":float(np.quantile(dt,0.9)) if len(dt) else None,
        "dt_seconds_q95":float(np.quantile(dt,0.95)) if len(dt) else None,
        "cohort_speed_thresholds_m_s":thresholds,
        "evaluable_individual_ids":sorted(eval_ind),
        "session_support":session_rows
    }
    return panel


def main():
    c=json.loads(CONTRACT.read_text(encoding="utf-8"))
    results={}
    sources={}
    for panel in c["primary_panels"]:
        records,source=shape.panel_raw(panel)
        sources[panel]=source
        results[panel]={}
        for cand in c["candidates_in_priority_order"]:
            results[panel][cand["id"]]=evaluate_panel(
                records,cand,
                int(c["baseline_evaluable_individuals"][panel]),
                int(c["feasibility"]["minimum_supported_target_events"])
            )

    selected=None
    for cand in c["candidates_in_priority_order"]:
        cid=cand["id"]
        if all(results[p][cid]["candidate_pass"] for p in c["primary_panels"]):
            selected=cid
            break

    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "vertical_values_used_for_selection":False,
        "sources":sources,
        "panel_results":results,
        "selected_candidate_id":selected,
        "feasible_to_open_vertical_outcome":selected is not None,
        "selection_rule":c["feasibility"]["selection_rule"],
        "stop_rule":c["stop_rule"]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    lines=[
        "# Movement-state conditioning feasibility preflight v1","",
        "**X-Y-TIME ONLY. No vertical outcome was used to select the movement-state definition.**","",
        f"Selected candidate: **{selected if selected else 'NONE'}**","",
        "| candidate | "+" | ".join(c["primary_panels"])+" |",
        "|---|"+"|".join(["---:"]*len(c["primary_panels"]))+"|"
    ]
    for cand in c["candidates_in_priority_order"]:
        cid=cand["id"]
        vals=[f"{results[p][cid]['evaluable_individuals']}/{c['baseline_evaluable_individuals'][p]}" for p in c["primary_panels"]]
        lines.append("| "+cid+" | "+" | ".join(vals)+" |")
    lines += ["",f"Feasible to open vertical outcome: **{selected is not None}**",""]
    OUT_MD.write_text("\n".join(lines),encoding="utf-8")

    print(json.dumps({
        "selected_candidate_id":selected,
        "feasible":selected is not None,
        "candidate_counts":{
            cand["id"]:{p:results[p][cand["id"]]["evaluable_individuals"] for p in c["primary_panels"]}
            for cand in c["candidates_in_priority_order"]
        },
        "baseline":c["baseline_evaluable_individuals"]
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
