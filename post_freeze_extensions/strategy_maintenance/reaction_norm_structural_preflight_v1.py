#!/usr/bin/env python3
from __future__ import annotations
import json, math, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from post_freeze_extensions.strategy_maintenance import wind_support_preflight_v1 as ws

CONTRACT=ROOT/"post_freeze_extensions/strategy_maintenance/reaction_norm_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/strategy_maintenance/reaction_norm_structural_preflight_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/strategy_maintenance/REACTION_NORM_STRUCTURAL_PREFLIGHT_V1.md"
BASE_N={"hypsignathus":19,"phyllostomus_2022":23,"phyllostomus_2023":11}


def evaluate(panel,eps):
    # Verify exact inherited 500-m x-y-time support before wind-state refinement.
    _,base_rows,base_inds=ws.xy_supported_universe(eps)
    if len(base_inds)!=BASE_N[panel]:
        raise RuntimeError(f"{panel}: inherited 500m n {len(base_inds)} != {BASE_N[panel]}")

    # Wind state is cohort median, outcome-blind.
    med={}
    for cohort in sorted({r["cohort"] for r in eps}):
        vv=[r["wind_speed"] for r in eps if r["cohort"]==cohort]
        med[cohort]=float(np.median(np.asarray(vv,dtype=float)))
    for r in eps:
        r["wind_state"]=int(r["wind_speed"]>med[r["cohort"]])
        r["base_stratum"]=(math.floor(r["x"]/500.0),math.floor(r["y"]/500.0),r["state"])
        r["wind_stratum"]=r["base_stratum"]+(r["wind_state"],)

    by_session=defaultdict(list); sessions_by_ind=defaultdict(list); inds_by_cohort=defaultdict(set)
    for r in eps:
        key=(r["cohort"],r["session"])
        by_session[key].append(r)
    for key,vals in by_session.items():
        iid=vals[0]["iid"]; cohort=key[0]
        sessions_by_ind[(cohort,iid)].append(key)
        inds_by_cohort[cohort].add(iid)

    base_support={k:{r["base_stratum"] for r in vals} for k,vals in by_session.items()}
    wind_support={k:{r["wind_stratum"] for r in vals} for k,vals in by_session.items()}

    rows=[]; eval_inds=set()
    for key,vals in sorted(by_session.items()):
        cohort,session=key; iid=vals[0]["iid"]
        self_keys=[k for k in sessions_by_ind[(cohort,iid)] if k!=key]
        if not self_keys:
            rows.append({"cohort":cohort,"session":session,"individual":iid,"supported_events":0,"evaluable":False,"reason":"no_other_self_session"})
            continue
        self_base=set().union(*(base_support[k] for k in self_keys))
        self_wind=set().union(*(wind_support[k] for k in self_keys))
        other_keys=[]
        for other in inds_by_cohort[cohort]:
            if other!=iid:
                other_keys.extend(sessions_by_ind[(cohort,other)])
        if not other_keys:
            rows.append({"cohort":cohort,"session":session,"individual":iid,"supported_events":0,"evaluable":False,"reason":"no_other_individual"})
            continue
        other_wind=set().union(*(wind_support[k] for k in other_keys))
        supported=[r for r in vals if r["base_stratum"] in self_base and r["wind_stratum"] in self_wind and r["wind_stratum"] in other_wind]
        ok=len(supported)>=50
        if ok: eval_inds.add(iid)
        rows.append({"cohort":cohort,"session":session,"individual":iid,"kinematic_endpoints":len(vals),"supported_events":len(supported),"support_fraction":len(supported)/len(vals) if vals else None,"evaluable":bool(ok),"reason":"eligible" if ok else "insufficient_all_predictor_support"})

    need={"hypsignathus":14,"phyllostomus_2022":17,"phyllostomus_2023":8}[panel]
    return {"panel":panel,"baseline_n":BASE_N[panel],"required_n":need,"evaluable_individuals":len(eval_inds),"evaluable_individual_ids":sorted(eval_inds),"cohort_wind_medians_m_s":med,"session_support":rows,"pass":len(eval_inds)>=need}


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
        res=evaluate(panel,x["eps"])
        res["source_structure"]=x["source"]
        res["kinematic_thresholds"]=x["thresholds"]
        panels[panel]=res

    passed=all(x["pass"] for x in panels.values())
    payload={"schema_version":1,"study_id":"batter-strategy-maintenance-reaction-norm-structural-preflight-v1","classification":"x-y-time + ERA5 wind only; numeric vertical response unopened","panels":panels,"all_three_pass":passed,"vertical_outcome_may_open":passed}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    lines=["# Reaction-norm structural preflight v1","","**X-Y-TIME + ERA5 WIND ONLY. Numeric vertical response unopened.**","","| panel | inherited 500m n | required n | wind-conditioned n | pass |","|---|---:|---:|---:|---|"]
    for p,x in panels.items():
        lines.append(f"| {p} | {x['baseline_n']} | {x['required_n']} | {x['evaluable_individuals']} | {'PASS' if x['pass'] else 'FAIL'} |")
    lines += ["",f"All three panels pass: **{passed}**",f"Vertical outcome may open: **{passed}**",""]
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps({"all_three_pass":passed,"panels":{p:{"n":x["evaluable_individuals"],"required":x["required_n"],"pass":x["pass"]} for p,x in panels.items()}},sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
