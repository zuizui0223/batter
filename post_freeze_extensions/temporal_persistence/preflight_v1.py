#!/usr/bin/env python3
from __future__ import annotations

import json, math, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from post_freeze_extensions.body_mass_transfer.preflight_v1 import xy_records
from post_freeze_extensions.kinematic_state_conditioning.preflight_v1 import evaluate as kin_evaluate

CONTRACT=ROOT/"post_freeze_extensions/temporal_persistence/preflight_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/temporal_persistence/preflight_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/temporal_persistence/PREFLIGHT_RESULT_V1.md"

KIN_CAND={
    "id":"speed2_turn2",
    "speed_bins":2,
    "speed_quantiles":[0.5],
    "turn_bins":2,
    "turn_quantiles":[0.5],
    "state_count":4,
}

def turn_angle(a,b,c):
    v1x,v1y=b["x"]-a["x"],b["y"]-a["y"]
    v2x,v2y=c["x"]-b["x"],c["y"]-b["y"]
    n1=math.hypot(v1x,v1y); n2=math.hypot(v2x,v2y)
    if n1<=0 or n2<=0:
        return None
    z=max(-1.0,min(1.0,(v1x*v2x+v1y*v2y)/(n1*n2)))
    return math.acos(z)

def valid_endpoints(records,max_dt):
    by=defaultdict(list)
    for r in records:
        by[(r["cohort"],r["session"])].append(r)
    rows=[]
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
            rows.append({
                "cohort":cohort,"session":session,"iid":c["iid"],"t":c["t"],
                "x":c["x"],"y":c["y"],"speed":float(sp),"turn":float(tr)
            })
    speeds=defaultdict(list);turns=defaultdict(list)
    for r in rows:
        speeds[r["cohort"]].append(r["speed"])
        turns[r["cohort"]].append(r["turn"])
    th={cohort:{
        "speed":float(np.median(np.asarray(speeds[cohort],dtype=float))),
        "turn":float(np.median(np.asarray(turns[cohort],dtype=float)))
    } for cohort in speeds}
    out=[]
    for r in rows:
        q=th[r["cohort"]]
        state=int(r["speed"]>q["speed"])*2+int(r["turn"]>q["turn"])
        stratum=(math.floor(r["x"]/5000.0),math.floor(r["y"]/5000.0),state)
        out.append({**r,"state":state,"stratum":stratum})
    return out,th

def median_time(vals):
    ts=sorted(r["t"] for r in vals)
    n=len(ts)
    if n%2:
        return ts[n//2]
    a,b=ts[n//2-1],ts[n//2]
    return a+(b-a)/2

def evaluate_lag(records,minimum_days,min_events):
    eps,thresholds=valid_endpoints(records,1800)
    by_session=defaultdict(list)
    sessions_by_ind=defaultdict(list)
    inds_by_cohort=defaultdict(set)
    session_mid={}
    for r in eps:
        key=(r["cohort"],r["session"])
        by_session[key].append(r)
    for key,vals in by_session.items():
        cohort=key[0];iid=vals[0]["iid"]
        sessions_by_ind[(cohort,iid)].append(key)
        inds_by_cohort[cohort].add(iid)
        session_mid[key]=median_time(vals)
    support={k:{r["stratum"] for r in vals} for k,vals in by_session.items()}
    lag_seconds=float(minimum_days)*86400.0
    eval_inds=set();session_rows=[]
    for key,vals in sorted(by_session.items()):
        cohort,session=key;iid=vals[0]["iid"]
        t0=session_mid[key]
        self_keys=[
            k for k in sessions_by_ind[(cohort,iid)]
            if k!=key and abs((session_mid[k]-t0).total_seconds())>=lag_seconds
        ]
        if not self_keys:
            session_rows.append({
                "cohort":cohort,"session":session,"individual":iid,
                "evaluable":False,"supported_events":0,"reason":"no_lag_qualified_self_session"
            })
            continue
        other_keys=[
            k for other in inds_by_cohort[cohort] if other!=iid
            for k in sessions_by_ind[(cohort,other)]
        ]
        if not other_keys:
            session_rows.append({
                "cohort":cohort,"session":session,"individual":iid,
                "evaluable":False,"supported_events":0,"reason":"no_other_individual"
            })
            continue
        self_support=set().union(*(support[k] for k in self_keys))
        other_support=set().union(*(support[k] for k in other_keys))
        sup=sum(r["stratum"] in self_support and r["stratum"] in other_support for r in vals)
        ok=sup>=min_events
        if ok:
            eval_inds.add(iid)
        lags=[abs((session_mid[k]-t0).total_seconds())/86400.0 for k in self_keys]
        session_rows.append({
            "cohort":cohort,"session":session,"individual":iid,
            "lag_qualified_self_sessions":len(self_keys),
            "minimum_self_lag_days":float(min(lags)) if lags else None,
            "maximum_self_lag_days":float(max(lags)) if lags else None,
            "target_endpoints":len(vals),"supported_events":int(sup),
            "support_fraction":float(sup/len(vals)) if vals else None,
            "evaluable":bool(ok),"reason":"eligible" if ok else "insufficient_common_support"
        })
    return {
        "minimum_days":float(minimum_days),
        "evaluable_individuals":len(eval_inds),
        "evaluable_individual_ids":sorted(eval_inds),
        "session_support":session_rows,
        "cohort_thresholds":thresholds
    }

def main():
    c=json.loads(CONTRACT.read_text())
    results={}
    selected=None
    for p in c["panels"]:
        records=xy_records(p)
        expected=int(c["kinematic_baseline_n"][p])
        base=kin_evaluate(records,KIN_CAND,{
            "kinematics":{"maximum_step_interval_seconds":1800},
            "feasibility":{"minimum_supported_target_events":50}
        })
        if base["evaluable_individuals"]!=expected:
            raise RuntimeError(f"{p}: reproduced kinematic baseline {base['evaluable_individuals']} != {expected}")
        results[p]={"verified_kinematic_baseline_n":expected,"candidates":{}}

    for cand in c["lag_candidates_in_priority_order"]:
        cid=cand["id"];days=float(cand["minimum_days"])
        allpass=True
        for p in c["panels"]:
            records=xy_records(p)
            expected=int(c["kinematic_baseline_n"][p])
            x=evaluate_lag(records,days,int(c["feasibility"]["minimum_supported_target_events"]))
            req=max(5,math.ceil(0.70*expected))
            x["baseline_n"]=expected;x["required_n"]=req
            x["retention_fraction"]=x["evaluable_individuals"]/expected
            x["panel_pass"]=x["evaluable_individuals"]>=req
            results[p]["candidates"][cid]=x
            allpass=allpass and x["panel_pass"]
        if allpass:
            selected=cid
            break

    selected_days=next((x["minimum_days"] for x in c["lag_candidates_in_priority_order"] if x["id"]==selected),None)
    payload={
        "schema_version":1,"study_id":c["study_id"],
        "vertical_values_used_for_selection":False,
        "panel_results":results,
        "selected_candidate_id":selected,
        "selected_minimum_lag_days":selected_days,
        "feasible_to_open_vertical_outcome":selected is not None,
        "stop_rule":c["stop_rule"]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    lines=["# Multi-day temporal-persistence feasibility preflight v1","",
           "**X-Y-TIME ONLY. No vertical outcome was used to select lag.**","",
           f"Selected minimum lag: **{selected_days if selected_days is not None else 'NONE'} days**","",
           "| lag | "+" | ".join(c["panels"])+" |",
           "|---|"+"|".join(["---:"]*len(c["panels"]))+"|"]
    for cand in c["lag_candidates_in_priority_order"]:
        cid=cand["id"]
        if any(cid not in results[p]["candidates"] for p in c["panels"]):
            continue
        vals=[f"{results[p]['candidates'][cid]['evaluable_individuals']}/{c['kinematic_baseline_n'][p]}" for p in c["panels"]]
        lines.append(f"| >= {cand['minimum_days']} d | "+" | ".join(vals)+" |")
    lines.append("")
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps({
        "selected_candidate_id":selected,
        "selected_minimum_lag_days":selected_days,
        "feasible":selected is not None,
        "counts":{cid:{p:results[p]["candidates"].get(cid,{}).get("evaluable_individuals") for p in c["panels"]} for cid in [x["id"] for x in c["lag_candidates_in_priority_order"]]},
        "baseline":c["kinematic_baseline_n"]
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
