#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from post_freeze_extensions.strategy_maintenance import wind_support_preflight_v1 as ws

CONTRACT=ROOT/"post_freeze_extensions/strategy_maintenance/reaction_norm_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/strategy_maintenance/reaction_norm_structural_preflight_v2.json"
OUT_MD=ROOT/"post_freeze_extensions/strategy_maintenance/REACTION_NORM_STRUCTURAL_PREFLIGHT_V2.md"

def interval(vals):
    a=np.asarray(vals,dtype=float)
    if len(a)<2:
        return None
    return float(np.quantile(a,0.05)),float(np.quantile(a,0.95))

def self_sxx(rows):
    by=defaultdict(list)
    for r in rows:
        by[r["stratum"]].append(float(r["wind_speed"]))
    sxx=0.0
    for vals in by.values():
        m=float(np.mean(vals))
        sxx += float(np.sum((np.asarray(vals,dtype=float)-m)**2))
    return sxx

def evaluate(panel,eps,c):
    base_events,base_rows,base_inds=ws.xy_supported_universe(eps)
    expected=int(c["structural_gate"]["required_evaluable_individuals"][panel])
    baseline={"hypsignathus":19,"phyllostomus_2022":23,"phyllostomus_2023":11}[panel]
    if len(base_inds)!=baseline:
        raise RuntimeError(f"{panel}: inherited 500m n {len(base_inds)} != {baseline}")

    by_session=defaultdict(list); sessions_by_ind=defaultdict(list); inds_by_cohort=defaultdict(set)
    for r in base_events:
        key=(r["cohort"],r["session"])
        by_session[key].append(r)
    for key,vals in by_session.items():
        cohort,_=key; iid=vals[0]["iid"]
        sessions_by_ind[(cohort,iid)].append(key)
        inds_by_cohort[cohort].add(iid)

    rows=[]; eval_inds=set()
    for key,vals in sorted(by_session.items()):
        cohort,session=key; iid=vals[0]["iid"]
        self_keys=[k for k in sessions_by_ind[(cohort,iid)] if k!=key]
        if not self_keys:
            rows.append({"cohort":cohort,"session":session,"individual":iid,"environment_matched_events":0,"slope_sxx":0.0,"evaluable":False,"reason":"no_other_self_session"})
            continue

        self_train=[r for k in self_keys for r in by_session[k]]
        siv=interval([r["wind_speed"] for r in self_train])
        donors={}
        for other in inds_by_cohort[cohort]:
            if other==iid: continue
            ov=[r["wind_speed"] for k in sessions_by_ind[(cohort,other)] for r in by_session[k]]
            oiv=interval(ov)
            if oiv is not None: donors[other]=oiv

        matched=[]
        for r in vals:
            w=float(r["wind_speed"])
            self_ok=bool(siv and siv[0]<=w<=siv[1])
            donor_n=sum(lo<=w<=hi for lo,hi in donors.values())
            if self_ok and donor_n>=2:
                matched.append(r)

        sxx=self_sxx(self_train)
        ok=len(matched)>=int(c["conditioning"]["minimum_scored_target_events"]) and sxx>1e-12
        if ok: eval_inds.add(iid)
        rows.append({
            "cohort":cohort,"session":session,"individual":iid,
            "base_supported_events":len(vals),
            "environment_matched_events":len(matched),
            "environment_matched_fraction":len(matched)/len(vals) if vals else None,
            "self_wind_q05":siv[0] if siv else None,
            "self_wind_q95":siv[1] if siv else None,
            "other_donor_intervals":len(donors),
            "slope_sxx":float(sxx),
            "evaluable":bool(ok),
            "reason":"eligible" if ok else ("zero_within_stratum_wind_variation" if sxx<=1e-12 else "insufficient_environment_matched_events")
        })

    passed=len(eval_inds)>=expected
    return {
        "panel":panel,
        "baseline_500m_n":baseline,
        "required_n":expected,
        "continuous_slope_evaluable_individuals":len(eval_inds),
        "evaluable_individual_ids":sorted(eval_inds),
        "session_support":rows,
        "pass":bool(passed)
    }

def main():
    c=json.loads(CONTRACT.read_text())
    prepared={}
    for panel in c["panels"]:
        rec,src=ws.load_xy_time(panel)
        eps,thresholds=ws.kinematic_endpoints(rec)
        prepared[panel]={"eps":eps,"source":src,"thresholds":thresholds}

    ds=ws.open_era5()
    panels={}
    for panel,x in prepared.items():
        ws.annotate_wind(x["eps"],ds)
        res=evaluate(panel,x["eps"],c)
        res["source_structure"]=x["source"]; res["kinematic_thresholds"]=x["thresholds"]
        panels[panel]=res

    passed=all(x["pass"] for x in panels.values())
    payload={
        "schema_version":2,
        "study_id":"batter-strategy-maintenance-continuous-reaction-norm-structural-preflight-v2",
        "classification":"x-y-time + ERA5 wind only; numeric vertical response unopened",
        "withdrawn_preflight":"median-split wind-state structural preflight v1",
        "panels":panels,
        "all_three_pass":bool(passed),
        "vertical_outcome_may_open":bool(passed)
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    lines=[
        "# Continuous wind reaction-norm structural preflight v2","",
        "**X-Y-TIME + ERA5 WIND ONLY. Numeric vertical response unopened.**","",
        "The earlier median-split wind-state preflight is withdrawn before vertical opening.","",
        "| panel | inherited 500m n | required n | continuous-slope n | pass |",
        "|---|---:|---:|---:|---|"
    ]
    for p,x in panels.items():
        lines.append(f"| {p} | {x['baseline_500m_n']} | {x['required_n']} | {x['continuous_slope_evaluable_individuals']} | {'PASS' if x['pass'] else 'FAIL'} |")
    lines += ["",f"All three panels pass: **{passed}**",f"Vertical outcome may open: **{passed}**",""]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(json.dumps({"all_three_pass":passed,"panels":{p:{"n":x["continuous_slope_evaluable_individuals"],"required":x["required_n"],"pass":x["pass"]} for p,x in panels.items()}},sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
