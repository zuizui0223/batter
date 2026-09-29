#!/usr/bin/env python3
from __future__ import annotations

import json, math, sys
from collections import Counter, defaultdict
from datetime import timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from post_freeze_extensions.body_mass_transfer.preflight_v1 import xy_records, state_endpoints

CONTRACT=ROOT/"post_freeze_extensions/cross_panel_night_context/preflight_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/cross_panel_night_context/preflight_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/cross_panel_night_context/PREFLIGHT_RESULT_V1.md"


def shifted_night(t):
    return (t-timedelta(hours=12)).date().isoformat()


def evaluate(panel,c):
    endpoints=state_endpoints(xy_records(panel),int(c["kinematic_state"]["maximum_step_interval_seconds"]))
    by_session=defaultdict(list)
    for r in endpoints:
        by_session[(r["cohort"],r["session"])].append(r)

    purity=float(c["night_definition"]["minimum_session_night_purity"])
    session_meta={}
    retained={}
    for key,vals in sorted(by_session.items()):
        counts=Counter(shifted_night(r["t"]) for r in vals)
        night,n=counts.most_common(1)[0]
        frac=n/len(vals)
        iid=vals[0]["iid"]
        session_meta[key]={
            "cohort":key[0],"session":key[1],"individual":iid,
            "state_valid_endpoints":len(vals),"dominant_night":night,"night_purity":frac,
            "retained":frac>=purity
        }
        if frac>=purity:
            retained[key]=[r for r in vals if shifted_night(r["t"])==night]

    sessions_by_ind=defaultdict(list)
    sessions_by_night=defaultdict(list)
    inds_by_cohort=defaultdict(set)
    support={}
    for key,vals in retained.items():
        meta=session_meta[key];cohort=meta["cohort"];iid=meta["individual"];night=meta["dominant_night"]
        sessions_by_ind[(cohort,iid)].append(key)
        sessions_by_night[(cohort,night)].append(key)
        inds_by_cohort[cohort].add(iid)
        support[key]={r["stratum"] for r in vals}

    min_events=int(c["feasibility"]["minimum_supported_target_events"])
    eval_inds=set(); rows=[]
    for key,vals in sorted(retained.items()):
        meta=session_meta[key];cohort=meta["cohort"];iid=meta["individual"];night=meta["dominant_night"]
        self_keys=[k for k in sessions_by_ind[(cohort,iid)] if k!=key]
        night_keys=[k for k in sessions_by_night[(cohort,night)] if session_meta[k]["individual"]!=iid]
        night_other_ids=sorted({session_meta[k]["individual"] for k in night_keys})
        if not self_keys:
            rows.append({**meta,"supported_events":0,"same_night_other_individuals":night_other_ids,"evaluable":False,"reason":"no_self_history"})
            continue
        if not night_keys:
            rows.append({**meta,"supported_events":0,"same_night_other_individuals":[],"evaluable":False,"reason":"no_same_night_other"})
            continue
        self_support=set().union(*(support[k] for k in self_keys))
        night_support=set().union(*(support[k] for k in night_keys))
        sup=sum(r["stratum"] in self_support and r["stratum"] in night_support for r in vals)
        ok=sup>=min_events
        if ok: eval_inds.add(iid)
        rows.append({
            **meta,
            "self_history_session_count":len(self_keys),
            "same_night_other_session_count":len(night_keys),
            "same_night_other_individuals":night_other_ids,
            "same_night_other_individual_count":len(night_other_ids),
            "supported_events":int(sup),
            "support_fraction":float(sup/len(vals)) if vals else None,
            "evaluable":bool(ok),
            "reason":"eligible" if ok else "insufficient_common_support"
        })

    baseline=int(c["baseline_evaluable_n"][panel])
    required=max(5,math.ceil(0.70*baseline))
    return {
        "baseline_n":baseline,
        "required_n":required,
        "evaluable_individuals":len(eval_inds),
        "retention_fraction":len(eval_inds)/baseline,
        "panel_pass":len(eval_inds)>=required,
        "evaluable_individual_ids":sorted(eval_inds),
        "retained_session_count":len(retained),
        "session_meta":{f"{k[0]}::{k[1]}":v for k,v in session_meta.items()},
        "session_support":rows
    }


def main():
    c=json.loads(CONTRACT.read_text())
    results={}
    allpass=True
    for p in c["panels"]:
        x=evaluate(p,c)
        allpass=allpass and x["panel_pass"]
        results[p]=x
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
        "# Cross-panel same-night context feasibility preflight v1","",
        "**X-Y-TIME ONLY. No vertical outcome was used.**","",
        f"Feasible to open vertical outcome: **{allpass}**","",
        "| panel | evaluable n | required n | retention |",
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
