#!/usr/bin/env python3
from __future__ import annotations

import json, math, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_tag_altitude_bias_shape as shape

CONTRACT=ROOT/"post_freeze_extensions/fine_place_state_conditioning/preflight_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/fine_place_state_conditioning/preflight_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/fine_place_state_conditioning/PREFLIGHT_RESULT_V1.md"


def build_steps(records,max_dt):
    by=defaultdict(list)
    for r in records:
        by[(r["cohort"],r["session"])].append(r)
    steps=[]
    for (cohort,session),vals in sorted(by.items()):
        vals=sorted(vals,key=lambda x:x["t"])
        for i in range(1,len(vals)):
            a,b=vals[i-1],vals[i]
            dt=(b["t"]-a["t"]).total_seconds()
            if not math.isfinite(dt) or dt<=0 or dt>max_dt:
                continue
            speed=math.hypot(b["x"]-a["x"],b["y"]-a["y"])/dt
            steps.append({"cohort":cohort,"session":session,"iid":b["iid"],"x":b["x"],"y":b["y"],"speed":float(speed)})
    return steps


def assign_states(steps):
    by=defaultdict(list)
    for r in steps:
        by[r["cohort"]].append(r["speed"])
    cuts={c:[float(x) for x in np.quantile(np.asarray(v),[1/3,2/3])] for c,v in sorted(by.items())}
    out=[]
    for r in steps:
        st=int(np.searchsorted(np.asarray(cuts[r["cohort"]]),r["speed"],side="right"))
        out.append({**r,"state":st})
    return out,cuts


def evaluate(records,grid_m,c):
    steps=build_steps(records,int(c["movement_state"]["maximum_step_interval_seconds"]))
    steps,cuts=assign_states(steps)
    by_session=defaultdict(list)
    sessions_by_ind=defaultdict(list)
    inds_by_cohort=defaultdict(set)
    for r in steps:
        key=(r["cohort"],r["session"])
        fine=(math.floor(r["x"]/grid_m),math.floor(r["y"]/grid_m),r["state"])
        by_session[key].append((r["iid"],fine))
    for key,vals in by_session.items():
        iid=vals[0][0]
        cohort=key[0]
        sessions_by_ind[(cohort,iid)].append(key)
        inds_by_cohort[cohort].add(iid)

    supports={k:{x[1] for x in vals} for k,vals in by_session.items()}
    eval_inds=set()
    session_rows=[]
    min_events=int(c["feasibility"]["minimum_supported_target_events"])

    for key,vals in sorted(by_session.items()):
        cohort,session=key
        iid=vals[0][0]
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
        sup=sum((fine in self_support and fine in other_support) for _,fine in vals)
        ok=sup>=min_events
        if ok:
            eval_inds.add(iid)
        session_rows.append({
            "cohort":cohort,"session":session,"individual":iid,
            "state_valid_endpoints":len(vals),"supported_events":int(sup),
            "support_fraction":float(sup/len(vals)) if vals else None,
            "evaluable":bool(ok),"reason":"eligible" if ok else "insufficient_fine_place_state_support"
        })

    return {
        "fine_grid_m":int(grid_m),
        "evaluable_individuals":len(eval_inds),
        "evaluable_individual_ids":sorted(eval_inds),
        "cohort_speed_thresholds_m_s":cuts,
        "session_support":session_rows
    }


def main():
    c=json.loads(CONTRACT.read_text())
    results={}
    for panel in c["primary_panels"]:
        records,source=shape.panel_raw(panel)
        results[panel]={"source":source,"candidates":{}}
        base=int(c["state_conditioned_baseline_n"][panel])
        for cand in c["fine_place_candidates_in_priority_order"]:
            x=evaluate(records,int(cand["fine_grid_m"]),c)
            x["baseline_n"]=base
            x["retention_fraction"]=x["evaluable_individuals"]/base
            x["retains_70_percent"]=x["evaluable_individuals"]>=math.ceil(0.70*base)
            x["retains_at_least_5"]=x["evaluable_individuals"]>=5
            x["candidate_pass"]=x["retains_70_percent"] and x["retains_at_least_5"]
            results[panel]["candidates"][cand["id"]]=x

    selected=None
    for cand in c["fine_place_candidates_in_priority_order"]:
        cid=cand["id"]
        if all(results[p]["candidates"][cid]["candidate_pass"] for p in c["primary_panels"]):
            selected=cid
            break

    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "vertical_values_used_for_selection":False,
        "panel_results":results,
        "selected_candidate_id":selected,
        "selected_grid_m": next((x["fine_grid_m"] for x in c["fine_place_candidates_in_priority_order"] if x["id"]==selected),None),
        "feasible_to_open_vertical_outcome":selected is not None,
        "selection_rule":c["feasibility"]["selection_rule"],
        "stop_rule":c["stop_rule"]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    lines=["# Fine-place × movement-state feasibility preflight v1","",
           "**X-Y-TIME ONLY. No vertical outcome was used to select the fine grid.**","",
           f"Selected candidate: **{selected if selected else 'NONE'}**","",
           "| candidate | "+" | ".join(c["primary_panels"])+" |",
           "|---|"+"|".join(["---:"]*len(c["primary_panels"]))+"|"]
    for cand in c["fine_place_candidates_in_priority_order"]:
        cid=cand["id"]
        vals=[f"{results[p]['candidates'][cid]['evaluable_individuals']}/{c['state_conditioned_baseline_n'][p]}" for p in c["primary_panels"]]
        lines.append("| "+cid+" | "+" | ".join(vals)+" |")
    lines += ["",f"Feasible to open vertical outcome: **{selected is not None}**",""]
    OUT_MD.write_text("\n".join(lines))

    print(json.dumps({
        "selected_candidate_id":selected,
        "selected_grid_m":payload["selected_grid_m"],
        "feasible":payload["feasible_to_open_vertical_outcome"],
        "counts":{cand["id"]:{p:results[p]["candidates"][cand["id"]]["evaluable_individuals"] for p in c["primary_panels"]} for cand in c["fine_place_candidates_in_priority_order"]}
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
