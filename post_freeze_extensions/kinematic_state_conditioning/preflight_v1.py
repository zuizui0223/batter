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

CONTRACT=ROOT/"post_freeze_extensions/kinematic_state_conditioning/preflight_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/kinematic_state_conditioning/preflight_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/kinematic_state_conditioning/PREFLIGHT_RESULT_V1.md"


def angle(v1x,v1y,v2x,v2y):
    a=math.hypot(v1x,v1y); b=math.hypot(v2x,v2y)
    if a<=0 or b<=0:
        return None
    c=max(-1.0,min(1.0,(v1x*v2x+v1y*v2y)/(a*b)))
    return math.acos(c)


def endpoints(records,max_dt):
    by=defaultdict(list)
    for r in records:
        by[(r["cohort"],r["session"])].append(r)
    out=[]
    for (cohort,session),vals in sorted(by.items()):
        vals=sorted(vals,key=lambda x:x["t"])
        for i in range(2,len(vals)):
            a,b,c=vals[i-2],vals[i-1],vals[i]
            dt1=(b["t"]-a["t"]).total_seconds()
            dt2=(c["t"]-b["t"]).total_seconds()
            if not all(math.isfinite(x) and x>0 and x<=max_dt for x in (dt1,dt2)):
                continue
            v1x,v1y=b["x"]-a["x"],b["y"]-a["y"]
            v2x,v2y=c["x"]-b["x"],c["y"]-b["y"]
            turn=angle(v1x,v1y,v2x,v2y)
            if turn is None:
                continue
            speed=math.hypot(v2x,v2y)/dt2
            out.append({
                "cohort":cohort,"session":session,"iid":c["iid"],
                "x":c["x"],"y":c["y"],"speed":float(speed),"turn":float(turn)
            })
    return out


def assign_states(rows,cand):
    sp=defaultdict(list); tu=defaultdict(list)
    for r in rows:
        sp[r["cohort"]].append(r["speed"]); tu[r["cohort"]].append(r["turn"])
    thresholds={}
    for cohort in sorted(sp):
        s=np.asarray(sp[cohort],dtype=float); t=np.asarray(tu[cohort],dtype=float)
        sc=[float(x) for x in np.quantile(s,cand["speed_quantiles"])] if cand["speed_quantiles"] else []
        tc=[float(x) for x in np.quantile(t,cand["turn_quantiles"])] if cand["turn_quantiles"] else []
        thresholds[cohort]={"speed":sc,"turn":tc}
    out=[]
    for r in rows:
        th=thresholds[r["cohort"]]
        sb=int(np.searchsorted(np.asarray(th["speed"]),r["speed"],side="right"))
        tb=int(np.searchsorted(np.asarray(th["turn"]),r["turn"],side="right"))
        state=sb*int(cand["turn_bins"])+tb
        out.append({**r,"state":state})
    return out,thresholds


def evaluate(records,cand,c):
    rows=endpoints(records,int(c["kinematics"]["maximum_step_interval_seconds"]))
    rows,thresholds=assign_states(rows,cand)
    by_session=defaultdict(list); sessions_by_ind=defaultdict(list); inds_by_cohort=defaultdict(set)
    for r in rows:
        key=(r["cohort"],r["session"])
        stratum=(math.floor(r["x"]/5000.0),math.floor(r["y"]/5000.0),r["state"])
        by_session[key].append((r["iid"],stratum))
    for key,vals in by_session.items():
        iid=vals[0][0]; cohort=key[0]
        sessions_by_ind[(cohort,iid)].append(key)
        inds_by_cohort[cohort].add(iid)
    supports={k:{x[1] for x in vals} for k,vals in by_session.items()}
    eval_inds=set(); session_rows=[]
    min_events=int(c["feasibility"]["minimum_supported_target_events"])
    for key,vals in sorted(by_session.items()):
        cohort,session=key; iid=vals[0][0]
        self_keys=[k for k in sessions_by_ind[(cohort,iid)] if k!=key]
        if not self_keys:
            session_rows.append({"cohort":cohort,"session":session,"individual":iid,"evaluable":False,"supported_events":0,"reason":"no_other_self_session"})
            continue
        self_support=set().union(*(supports[k] for k in self_keys))
        other_keys=[]
        for other in inds_by_cohort[cohort]:
            if other!=iid: other_keys.extend(sessions_by_ind[(cohort,other)])
        if not other_keys:
            session_rows.append({"cohort":cohort,"session":session,"individual":iid,"evaluable":False,"supported_events":0,"reason":"no_other_individual"})
            continue
        other_support=set().union(*(supports[k] for k in other_keys))
        sup=sum((st in self_support and st in other_support) for _,st in vals)
        ok=sup>=min_events
        if ok: eval_inds.add(iid)
        session_rows.append({
            "cohort":cohort,"session":session,"individual":iid,"kinematic_endpoints":len(vals),
            "supported_events":int(sup),"support_fraction":float(sup/len(vals)) if vals else None,
            "evaluable":bool(ok),"reason":"eligible" if ok else "insufficient_cell_kinematic_state_support"
        })
    return {
        "candidate_id":cand["id"],"state_count":int(cand["state_count"]),
        "evaluable_individuals":len(eval_inds),"evaluable_individual_ids":sorted(eval_inds),
        "cohort_thresholds":thresholds,"session_support":session_rows
    }


def main():
    c=json.loads(CONTRACT.read_text())
    results={}
    for panel in c["primary_panels"]:
        records,source=shape.panel_raw(panel)
        base=int(c["speed_state_baseline_n"][panel])
        results[panel]={"source":source,"candidates":{}}
        for cand in c["candidates_in_priority_order"]:
            x=evaluate(records,cand,c)
            x["baseline_n"]=base
            x["retention_fraction"]=x["evaluable_individuals"]/base
            x["retains_70_percent"]=x["evaluable_individuals"]>=math.ceil(0.70*base)
            x["retains_at_least_5"]=x["evaluable_individuals"]>=5
            x["candidate_pass"]=x["retains_70_percent"] and x["retains_at_least_5"]
            results[panel]["candidates"][cand["id"]]=x
    selected=None
    for cand in c["candidates_in_priority_order"]:
        cid=cand["id"]
        if all(results[p]["candidates"][cid]["candidate_pass"] for p in c["primary_panels"]):
            selected=cid; break
    payload={
        "schema_version":1,"study_id":c["study_id"],"vertical_values_used_for_selection":False,
        "panel_results":results,"selected_candidate_id":selected,
        "feasible_to_open_vertical_outcome":selected is not None,
        "selection_rule":c["feasibility"]["selection_rule"],"stop_rule":c["stop_rule"]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    lines=["# Kinematic-state feasibility preflight v1","",
           "**X-Y-TIME ONLY. No vertical outcome was used to select the state definition.**","",
           f"Selected candidate: **{selected if selected else 'NONE'}**","",
           "| candidate | "+" | ".join(c["primary_panels"])+" |",
           "|---|"+"|".join(["---:"]*len(c["primary_panels"]))+"|"]
    for cand in c["candidates_in_priority_order"]:
        cid=cand["id"]
        vals=[f"{results[p]['candidates'][cid]['evaluable_individuals']}/{c['speed_state_baseline_n'][p]}" for p in c["primary_panels"]]
        lines.append("| "+cid+" | "+" | ".join(vals)+" |")
    lines += ["",f"Feasible to open vertical outcome: **{selected is not None}**",""]
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps({
        "selected_candidate_id":selected,"feasible":selected is not None,
        "counts":{cand["id"]:{p:results[p]["candidates"][cand["id"]]["evaluable_individuals"] for p in c["primary_panels"]} for cand in c["candidates_in_priority_order"]}
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
