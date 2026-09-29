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
from post_freeze_extensions.kinematic_state_conditioning.preflight_v1 import evaluate as kin_evaluate

CONTRACT=ROOT/"post_freeze_extensions/temporal_phase_kinematic/preflight_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/temporal_phase_kinematic/preflight_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/temporal_phase_kinematic/PREFLIGHT_RESULT_V1.md"

KIN_CAND={
    "id":"speed2_turn2","speed_bins":2,"speed_quantiles":[0.5],
    "turn_bins":2,"turn_quantiles":[0.5],"state_count":4
}


def turn_angle(a,b,c):
    v1x,v1y=b["x"]-a["x"],b["y"]-a["y"]
    v2x,v2y=c["x"]-b["x"],c["y"]-b["y"]
    n1=math.hypot(v1x,v1y); n2=math.hypot(v2x,v2y)
    if n1<=0 or n2<=0:
        return None
    z=max(-1.0,min(1.0,(v1x*v2x+v1y*v2y)/(n1*n2)))
    return math.acos(z)


def state_endpoints(records,max_dt):
    by=defaultdict(list)
    for r in records:
        by[(r["cohort"],r["session"])].append(r)
    out=[]
    for (cohort,session),vals in sorted(by.items()):
        vals=sorted(vals,key=lambda x:x["t"])
        for i in range(2,len(vals)):
            a,b,c=vals[i-2],vals[i-1],vals[i]
            d1=(b["t"]-a["t"]).total_seconds()
            d2=(c["t"]-b["t"]).total_seconds()
            if not all(math.isfinite(d) and d>0 and d<=max_dt for d in (d1,d2)):
                continue
            tr=turn_angle(a,b,c)
            if tr is None:
                continue
            sp=math.hypot(c["x"]-b["x"],c["y"]-b["y"])/d2
            out.append({
                "cohort":cohort,"session":session,"iid":c["iid"],"t":c["t"],
                "x":c["x"],"y":c["y"],"speed":float(sp),"turn":float(tr)
            })
    sp=defaultdict(list);tu=defaultdict(list)
    for r in out:
        sp[r["cohort"]].append(r["speed"]);tu[r["cohort"]].append(r["turn"])
    th={cohort:{
        "speed":float(np.median(np.asarray(sp[cohort],dtype=float))),
        "turn":float(np.median(np.asarray(tu[cohort],dtype=float)))
    } for cohort in sp}
    assigned=[]
    for r in out:
        q=th[r["cohort"]]
        state=int(r["speed"]>q["speed"])*2+int(r["turn"]>q["turn"])
        assigned.append({**r,"state":state})
    return assigned,th


def phase_assign(rows,bins):
    by=defaultdict(list)
    for r in rows:
        by[(r["cohort"],r["session"])].append(r)
    out=[]
    for key,vals in by.items():
        vals=sorted(vals,key=lambda x:x["t"])
        t0=vals[0]["t"]; t1=vals[-1]["t"]
        dur=(t1-t0).total_seconds()
        if dur<=0:
            continue
        for r in vals:
            frac=(r["t"]-t0).total_seconds()/dur
            phase=min(bins-1,max(0,int(frac*bins)))
            out.append({**r,"phase":phase})
    return out


def evaluate(rows,bins,min_events):
    rows=phase_assign(rows,bins)
    by_session=defaultdict(list)
    sessions_by_ind=defaultdict(list)
    inds_by_cohort=defaultdict(set)
    for r in rows:
        key=(r["cohort"],r["session"])
        stratum=(math.floor(r["x"]/5000.0),math.floor(r["y"]/5000.0),r["state"],r["phase"])
        by_session[key].append((r["iid"],stratum))
    for key,vals in by_session.items():
        iid=vals[0][0];cohort=key[0]
        sessions_by_ind[(cohort,iid)].append(key)
        inds_by_cohort[cohort].add(iid)
    support={k:{v[1] for v in vals} for k,vals in by_session.items()}
    eval_inds=set();session_rows=[]
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
        session_rows.append({"cohort":cohort,"session":session,"individual":iid,"phase_valid_endpoints":len(vals),"supported_events":int(sup),"evaluable":bool(ok),"reason":"eligible" if ok else "insufficient_joint_support"})
    return {"evaluable_individuals":len(eval_inds),"evaluable_individual_ids":sorted(eval_inds),"session_support":session_rows}


def main():
    c=json.loads(CONTRACT.read_text())
    results={}
    for panel in c["panels"]:
        records,source=shape.panel_raw(panel)
        # Assert known speed×turn structural baseline with exactly the same state proxy family.
        base=kin_evaluate(records,KIN_CAND,{
            "kinematics":{"maximum_step_interval_seconds":int(c["kinematic_state"]["maximum_step_interval_seconds"])},
            "feasibility":{"minimum_supported_target_events":int(c["feasibility"]["minimum_supported_target_events"])}
        })
        expected=int(c["kinematic_baseline_n"][panel])
        if base["evaluable_individuals"]!=expected:
            raise RuntimeError(f"{panel}: kinematic baseline {base['evaluable_individuals']} != {expected}")

        eps,thresholds=state_endpoints(records,int(c["kinematic_state"]["maximum_step_interval_seconds"]))
        results[panel]={"source":source,"verified_kinematic_baseline_n":expected,"cohort_thresholds":thresholds,"candidates":{}}
        for cand in c["temporal_phase"]["candidates_in_priority_order"]:
            x=evaluate(eps,int(cand["bins"]),int(c["feasibility"]["minimum_supported_target_events"]))
            x["baseline_n"]=expected
            x["retention_fraction"]=x["evaluable_individuals"]/expected
            x["retains_70_percent"]=x["evaluable_individuals"]>=math.ceil(0.70*expected)
            x["retains_at_least_5"]=x["evaluable_individuals"]>=5
            x["candidate_pass"]=bool(x["retains_70_percent"] and x["retains_at_least_5"])
            results[panel]["candidates"][cand["id"]]=x

    selected=None
    for cand in c["temporal_phase"]["candidates_in_priority_order"]:
        if all(results[p]["candidates"][cand["id"]]["candidate_pass"] for p in c["panels"]):
            selected=cand["id"];break

    payload={
        "schema_version":1,"study_id":c["study_id"],
        "vertical_values_used_for_selection":False,
        "panel_results":results,
        "selected_candidate_id":selected,
        "feasible_to_open_vertical_outcome":selected is not None,
        "stop_rule":c["stop_rule"]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    lines=["# Temporal-phase × kinematic feasibility preflight v1","",
           "**X-Y-TIME ONLY. No vertical outcome was used.**","",
           f"Selected candidate: **{selected if selected else 'NONE'}**","",
           "| candidate | "+" | ".join(c["panels"])+" |",
           "|---|"+"|".join(["---:"]*len(c["panels"]))+"|"]
    for cand in c["temporal_phase"]["candidates_in_priority_order"]:
        cid=cand["id"]
        vals=[f"{results[p]['candidates'][cid]['evaluable_individuals']}/{c['kinematic_baseline_n'][p]}" for p in c["panels"]]
        lines.append("| "+cid+" | "+" | ".join(vals)+" |")
    lines += ["",f"Vertical outcome may be opened: **{selected is not None}**",""]
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps({
        "selected_candidate_id":selected,
        "feasible":selected is not None,
        "counts":{cand["id"]:{p:results[p]["candidates"][cand["id"]]["evaluable_individuals"] for p in c["panels"]} for cand in c["temporal_phase"]["candidates_in_priority_order"]},
        "baseline":c["kinematic_baseline_n"]
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
