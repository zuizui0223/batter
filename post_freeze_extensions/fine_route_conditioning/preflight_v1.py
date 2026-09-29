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

CONTRACT=ROOT/"post_freeze_extensions/fine_route_conditioning/preflight_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/fine_route_conditioning/preflight_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/fine_route_conditioning/PREFLIGHT_RESULT_V1.md"


def state_valid_steps(records,c):
    max_dt=int(c["movement_state"]["max_dt_seconds"])
    by_session=defaultdict(list)
    for r in records:
        by_session[(r["cohort"],r["session"])].append(r)

    raw=[]
    speeds=defaultdict(list)
    for (cohort,session),vals in sorted(by_session.items()):
        vals=sorted(vals,key=lambda x:x["t"])
        for i in range(1,len(vals)):
            a,b=vals[i-1],vals[i]
            dt=(b["t"]-a["t"]).total_seconds()
            if not math.isfinite(dt) or dt<=0 or dt>max_dt:
                continue
            speed=math.hypot(b["x"]-a["x"],b["y"]-a["y"])/dt
            raw.append({
                "cohort":cohort,"session":session,"iid":b["iid"],
                "x":b["x"],"y":b["y"],"speed":float(speed)
            })
            speeds[cohort].append(float(speed))

    thresholds={}
    for cohort,vals in sorted(speeds.items()):
        thresholds[cohort]=[float(x) for x in np.quantile(np.asarray(vals),[1/3,2/3])]

    steps=[]
    for r in raw:
        st=int(np.searchsorted(np.asarray(thresholds[r["cohort"]]),r["speed"],side="right"))
        steps.append({**r,"state":st})
    return steps,thresholds


def evaluate(records,cell_m,c,baseline_n):
    steps,thresholds=state_valid_steps(records,c)
    ss=defaultdict(list)
    for r in steps:
        cell=(math.floor(r["x"]/cell_m),math.floor(r["y"]/cell_m))
        ss[(r["cohort"],r["session"])].append({
            "iid":r["iid"],"cell":cell,"state":r["state"]
        })

    session_iid={}
    sessions_by_ind=defaultdict(list)
    inds_by_cohort=defaultdict(set)
    for key,vals in ss.items():
        if not vals: continue
        cohort,session=key
        iid=vals[0]["iid"]
        session_iid[key]=iid
        sessions_by_ind[(cohort,iid)].append(key)
        inds_by_cohort[cohort].add(iid)

    pairsets={key:{(v["cell"],v["state"]) for v in vals} for key,vals in ss.items()}
    min_events=int(c["feasibility"]["minimum_supported_target_events"])
    eval_ind=set()
    session_rows=[]
    for key,vals in sorted(ss.items()):
        cohort,session=key
        iid=session_iid[key]
        self_keys=[k for k in sessions_by_ind[(cohort,iid)] if k!=key]
        if not self_keys:
            session_rows.append({"cohort":cohort,"session":session,"individual":iid,"valid_events":len(vals),"supported_events":0,"evaluable":False,"reason":"no_other_self_session"})
            continue
        self_support=set().union(*(pairsets[k] for k in self_keys))
        other_keys=[]
        for other in inds_by_cohort[cohort]:
            if other==iid: continue
            other_keys.extend(sessions_by_ind[(cohort,other)])
        if not other_keys:
            session_rows.append({"cohort":cohort,"session":session,"individual":iid,"valid_events":len(vals),"supported_events":0,"evaluable":False,"reason":"no_other_individual"})
            continue
        other_support=set().union(*(pairsets[k] for k in other_keys))
        supported=sum(((v["cell"],v["state"]) in self_support and (v["cell"],v["state"]) in other_support) for v in vals)
        ok=supported>=min_events
        if ok: eval_ind.add(iid)
        session_rows.append({
            "cohort":cohort,"session":session,"individual":iid,
            "valid_events":len(vals),"supported_events":int(supported),
            "support_fraction":float(supported/len(vals)) if vals else None,
            "evaluable":bool(ok),"reason":"eligible" if ok else "insufficient_fine_cell_state_support"
        })

    need=max(5,math.ceil(0.70*baseline_n))
    return {
        "cell_m":int(cell_m),
        "baseline_evaluable_individuals":int(baseline_n),
        "evaluable_individuals":len(eval_ind),
        "retention_fraction":float(len(eval_ind)/baseline_n),
        "required_for_candidate_pass":int(need),
        "candidate_pass":bool(len(eval_ind)>=need),
        "evaluable_individual_ids":sorted(eval_ind),
        "cohort_speed_thresholds_m_s":thresholds,
        "session_support":session_rows
    }


def main():
    c=json.loads(CONTRACT.read_text(encoding="utf-8"))
    results={}
    sources={}
    for panel in c["primary_panels"]:
        records,source=shape.panel_raw(panel)
        sources[panel]=source
        results[panel]={}
        for cand in c["candidates_in_priority_order"]:
            results[panel][cand["id"]]=evaluate(
                records,
                int(cand["cell_m"]),
                c,
                int(c["baseline_evaluable_individuals"][panel])
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
        "selected_cell_m":next((int(x["cell_m"]) for x in c["candidates_in_priority_order"] if x["id"]==selected),None),
        "feasible_to_open_vertical_outcome":selected is not None,
        "selection_rule":c["feasibility"]["selection_rule"],
        "stop_rule":c["stop_rule"]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    lines=[
        "# Fine-route conditioning feasibility preflight v1","",
        "**X-Y-TIME ONLY. No vertical outcome was used to select the horizontal grain.**","",
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
        "selected_cell_m":payload["selected_cell_m"],
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
