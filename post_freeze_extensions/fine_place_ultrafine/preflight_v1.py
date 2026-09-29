#!/usr/bin/env python3
from __future__ import annotations

import json, math, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_tag_altitude_bias_shape as shape
from post_freeze_extensions.fine_place_kinematic.preflight_v1 import evaluate_grid

CONTRACT=ROOT/"post_freeze_extensions/fine_place_ultrafine/preflight_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/fine_place_ultrafine/preflight_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/fine_place_ultrafine/PREFLIGHT_RESULT_V1.md"

def panel_eval(records,grid,c,baseline_n):
    # evaluate_grid only needs state dt and minimum supported-event rules
    x=evaluate_grid(records,int(grid),{
        "state_definition":{"maximum_step_interval_seconds":int(c["state_definition"]["maximum_step_interval_seconds"])},
        "feasibility":{"minimum_supported_target_events":int(c["feasibility"]["minimum_supported_target_events"])}
    })
    req=max(5,math.ceil(0.70*baseline_n))
    x["baseline_n"]=int(baseline_n)
    x["required_n"]=int(req)
    x["retention_fraction"]=float(x["evaluable_individuals"]/baseline_n)
    x["panel_pass"]=bool(x["evaluable_individuals"]>=req)
    return x

def main():
    c=json.loads(CONTRACT.read_text())
    results={}
    stage1_all=True

    # First reproduce the authoritative 500-m x-y-time support counts exactly.
    for p in c["panels"]:
        records,source=shape.panel_raw(p)
        baseline=int(c["baseline"]["expected_500m_evaluable_n"][p])
        verify=panel_eval(records,500,c,baseline)
        if verify["evaluable_individuals"]!=baseline:
            raise RuntimeError(f"{p}: reproduced 500m n {verify['evaluable_individuals']} != frozen baseline {baseline}")
        p250=panel_eval(records,250,c,baseline)
        results[p]={
            "source":source,
            "verified_500m_n":baseline,
            "grid250":p250
        }
        stage1_all=stage1_all and p250["panel_pass"]

    selected=None
    stage2_evaluated=False
    if stage1_all:
        stage2_evaluated=True
        stage2_all=True
        for p in c["panels"]:
            records,_=shape.panel_raw(p)
            baseline=int(c["baseline"]["expected_500m_evaluable_n"][p])
            p100=panel_eval(records,100,c,baseline)
            results[p]["grid100"]=p100
            stage2_all=stage2_all and p100["panel_pass"]
        selected="grid100" if stage2_all else "grid250"

    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "vertical_values_used_for_selection":False,
        "panel_results":results,
        "stage1_250m_all_panels_pass":bool(stage1_all),
        "stage2_100m_evaluated":bool(stage2_evaluated),
        "selected_candidate_id":selected,
        "selected_grid_m":100 if selected=="grid100" else (250 if selected=="grid250" else None),
        "feasible_to_open_ultrafine_vertical_outcome":selected is not None,
        "stop_rule":c["stop_rule"]
    }

    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    lines=[
        "# Ultrafine-place × speed-turn feasibility preflight v1","",
        "**X-Y-TIME ONLY. No <500-m vertical outcome was opened.**","",
        f"250-m stage all-panels PASS: **{stage1_all}**",
        f"100-m stage evaluated: **{stage2_evaluated}**",
        f"Selected grid: **{payload['selected_grid_m'] if payload['selected_grid_m'] else 'NONE'} m**","",
        "| panel | 500-m baseline | required | 250 m | 100 m |",
        "|---|---:|---:|---:|---:|"
    ]
    for p in c["panels"]:
        r=results[p]
        g100=r.get("grid100")
        lines.append(
            f"| {p} | {r['verified_500m_n']} | {r['grid250']['required_n']} | "
            f"{r['grid250']['evaluable_individuals']} | "
            f"{g100['evaluable_individuals'] if g100 else 'not opened'} |"
        )
    lines.append("")
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps({
        "stage1_250m_all_pass":stage1_all,
        "stage2_100m_evaluated":stage2_evaluated,
        "selected_grid_m":payload["selected_grid_m"],
        "counts_250":{p:results[p]["grid250"]["evaluable_individuals"] for p in c["panels"]},
        "counts_100":{p:(results[p].get("grid100") or {}).get("evaluable_individuals") for p in c["panels"]},
        "required":{p:results[p]["grid250"]["required_n"] for p in c["panels"]}
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
