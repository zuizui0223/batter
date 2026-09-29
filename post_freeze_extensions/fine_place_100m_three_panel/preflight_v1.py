#!/usr/bin/env python3
from __future__ import annotations
import json, math, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_tag_altitude_bias_shape as shape
from post_freeze_extensions.fine_place_kinematic.preflight_v1 import evaluate_grid

CONTRACT=ROOT/"post_freeze_extensions/fine_place_100m_three_panel/preflight_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/fine_place_100m_three_panel/preflight_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/fine_place_100m_three_panel/PREFLIGHT_RESULT_V1.md"

def main():
    c=json.loads(CONTRACT.read_text())
    results={}
    allpass=True
    for p in c["panels"]:
        records,source=shape.panel_raw(p)
        baseline=int(c["baseline_250m_n"][p])

        # Reproduce frozen 250-m support count exactly before testing 100 m.
        verify=evaluate_grid(records,250,{
            "state_definition":{"maximum_step_interval_seconds":int(c["context"]["maximum_step_interval_seconds"])},
            "feasibility":{"minimum_supported_target_events":int(c["feasibility"]["minimum_supported_target_events"])}
        })
        if verify["evaluable_individuals"]!=baseline:
            raise RuntimeError(f"{p}: reproduced 250m n {verify['evaluable_individuals']} != frozen baseline {baseline}")

        x=evaluate_grid(records,100,{
            "state_definition":{"maximum_step_interval_seconds":int(c["context"]["maximum_step_interval_seconds"])},
            "feasibility":{"minimum_supported_target_events":int(c["feasibility"]["minimum_supported_target_events"])}
        })
        req=max(5,math.ceil(0.70*baseline))
        x["baseline_250m_n"]=baseline
        x["required_n"]=req
        x["retention_fraction"]=x["evaluable_individuals"]/baseline
        x["panel_pass"]=x["evaluable_individuals"]>=req
        results[p]={"source":source,"grid100":x}
        allpass=allpass and x["panel_pass"]

    payload={
      "schema_version":1,
      "study_id":c["study_id"],
      "vertical_values_used":False,
      "panel_results":results,
      "feasible_to_open_100m_vertical_outcome":bool(allpass),
      "stop_rule":c["stop_rule"]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    lines=[
      "# Three-panel 100-m fine-place feasibility preflight v1","",
      "**X-Y-TIME ONLY. No 100-m vertical outcome was opened.**","",
      f"Feasible to open vertical outcome: **{allpass}**","",
      "| panel | 250-m baseline | required | 100-m evaluable | retention |",
      "|---|---:|---:|---:|---:|"
    ]
    for p,r in results.items():
        x=r["grid100"]
        lines.append(f"| {p} | {x['baseline_250m_n']} | {x['required_n']} | {x['evaluable_individuals']} | {x['retention_fraction']:.3f} |")
    lines.append("")
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps({
      "feasible":allpass,
      "counts":{p:results[p]["grid100"]["evaluable_individuals"] for p in c["panels"]},
      "required":{p:results[p]["grid100"]["required_n"] for p in c["panels"]}
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
