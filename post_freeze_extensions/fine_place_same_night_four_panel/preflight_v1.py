#!/usr/bin/env python3
from __future__ import annotations

import json, math, sys
from collections import Counter, defaultdict
from datetime import timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from post_freeze_extensions.body_mass_transfer.preflight_v1 import xy_records
import numpy as np

CONTRACT=ROOT/"post_freeze_extensions/fine_place_same_night_four_panel/preflight_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/fine_place_same_night_four_panel/preflight_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/fine_place_same_night_four_panel/PREFLIGHT_RESULT_V1.md"

CAND={"id":"speed2_turn2","speed_bins":2,"speed_quantiles":[0.5],"turn_bins":2,"turn_quantiles":[0.5],"state_count":4}


def shifted_night(t):
    return (t-timedelta(hours=12)).date().isoformat()


def turn_angle(v1x,v1y,v2x,v2y):
    a=math.hypot(v1x,v1y); b=math.hypot(v2x,v2y)
    if a<=0 or b<=0:
        return None
    z=max(-1.0,min(1.0,(v1x*v2x+v1y*v2y)/(a*b)))
    return math.acos(z)


def timed_kinematic_endpoints(records,max_dt):
    by=defaultdict(list)
    for r in records:
        by[(r["cohort"],r["session"])].append(r)
    rows=[]
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
            tr=turn_angle(v1x,v1y,v2x,v2y)
            if tr is None:
                continue
            sp=math.hypot(v2x,v2y)/dt2
            rows.append({"cohort":cohort,"session":session,"iid":c["iid"],"t":c["t"],"x":c["x"],"y":c["y"],"speed":float(sp),"turn":float(tr)})
    speeds=defaultdict(list); turns=defaultdict(list)
    for r in rows:
        speeds[r["cohort"]].append(r["speed"]); turns[r["cohort"]].append(r["turn"])
    thresholds={cohort:{"speed":float(np.median(speeds[cohort])),"turn":float(np.median(turns[cohort]))} for cohort in sorted(speeds)}
    out=[]
    for r in rows:
        th=thresholds[r["cohort"]]
        state=int(r["speed"]>th["speed"])*2+int(r["turn"]>th["turn"])
        out.append({**r,"state":state})
    return out,thresholds


def evaluate(panel,c):
    records=xy_records(panel)
    eps,thresholds=timed_kinematic_endpoints(records,int(c["context"]["maximum_step_interval_seconds"]))

    grid=float(c["context"]["horizontal_cell_m"])
    by_session=defaultdict(list)
    for r in eps:
        key=(r["cohort"],r["session"])
        by_session[key].append({**r,"stratum":(math.floor(r["x"]/grid),math.floor(r["y"]/grid),r["state"])})

    purity=float(c["context"]["minimum_session_night_purity"])
    retained={}
    meta={}
    for key,vals in sorted(by_session.items()):
        cnt=Counter(shifted_night(r["t"]) for r in vals)
        night,n=cnt.most_common(1)[0]
        frac=n/len(vals)
        iid=vals[0]["iid"]
        meta[key]={"cohort":key[0],"session":key[1],"individual":iid,"night":night,"night_purity":frac}
        if frac>=purity:
            retained[key]=[r for r in vals if shifted_night(r["t"])==night]

    by_ind=defaultdict(list); by_night=defaultdict(list)
    support={}
    for key,vals in retained.items():
        m=meta[key]
        by_ind[(m["cohort"],m["individual"])].append(key)
        by_night[(m["cohort"],m["night"])].append(key)
        support[key]={r["stratum"] for r in vals}

    min_events=int(c["feasibility"]["minimum_supported_target_events"])
    eval_inds=set(); session_rows=[]
    for key,vals in sorted(retained.items()):
        m=meta[key]; cohort=m["cohort"]; iid=m["individual"]; night=m["night"]
        self_keys=[k for k in by_ind[(cohort,iid)] if k!=key]
        night_keys=[k for k in by_night[(cohort,night)] if meta[k]["individual"]!=iid]
        if not self_keys:
            session_rows.append({**m,"supported_events":0,"evaluable":False,"reason":"no_self_history","same_night_other_individual_count":0})
            continue
        if not night_keys:
            session_rows.append({**m,"supported_events":0,"evaluable":False,"reason":"no_same_night_other","same_night_other_individual_count":0})
            continue
        self_support=set().union(*(support[k] for k in self_keys))
        night_support=set().union(*(support[k] for k in night_keys))
        sup=sum(r["stratum"] in self_support and r["stratum"] in night_support for r in vals)
        other_ids=sorted({meta[k]["individual"] for k in night_keys})
        ok=sup>=min_events
        if ok: eval_inds.add(iid)
        session_rows.append({
            **m,
            "target_endpoints":len(vals),
            "supported_events":int(sup),
            "support_fraction":float(sup/len(vals)) if vals else None,
            "self_history_session_count":len(self_keys),
            "same_night_other_session_count":len(night_keys),
            "same_night_other_individual_count":len(other_ids),
            "same_night_other_individuals":other_ids,
            "evaluable":bool(ok),
            "reason":"eligible" if ok else "insufficient_common_support"
        })

    baseline=int(c["baseline_n"][panel])
    required=max(5,math.ceil(0.70*baseline))
    return {
        "baseline_n":baseline,
        "required_n":required,
        "evaluable_individuals":len(eval_inds),
        "evaluable_individual_ids":sorted(eval_inds),
        "retention_fraction":len(eval_inds)/baseline,
        "panel_pass":len(eval_inds)>=required,
        "cohort_thresholds":thresholds,
        "retained_session_count":len(retained),
        "session_support":session_rows
    }


def main():
    c=json.loads(CONTRACT.read_text())
    results={}; allpass=True
    for p in c["panels"]:
        x=evaluate(p,c)
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
      "# Four-panel 2-km fine-place × same-night preflight v1","",
      "**X-Y-TIME ONLY. No vertical outcome used.**","",
      f"Feasible: **{allpass}**","",
      "| panel | evaluable | required | retention |",
      "|---|---:|---:|---:|"
    ]
    for p,x in results.items():
        lines.append(f"| {p} | {x['evaluable_individuals']} | {x['required_n']} | {x['retention_fraction']:.2f} |")
    lines.append("")
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps({
        "feasible":allpass,
        "counts":{p:results[p]["evaluable_individuals"] for p in c["panels"]},
        "required":{p:results[p]["required_n"] for p in c["panels"]},
        "retention":{p:results[p]["retention_fraction"] for p in c["panels"]}
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
