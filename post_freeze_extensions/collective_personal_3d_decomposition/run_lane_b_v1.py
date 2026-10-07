#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from post_freeze_extensions.collective_personal_3d_decomposition.run_v1 import cfg, build_sessions, run_laneB

OUT=ROOT/"post_freeze_extensions/collective_personal_3d_decomposition/lane_b_result_v1.json"

def main():
    c=cfg()
    panels=c["lane_B_cross_individual_prediction"]["included_panels"]
    out={}
    for p in panels:
        sessions,_=build_sessions(p,c)
        out[p]=run_laneB(p,sessions,c)
    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "lane":"B_cross_individual_prediction",
        "contract_unchanged":True,
        "panels":out,
        "headline":{p:{
            "classification":v["classification"],
            "shared_group_gain":v["bootstrap"]["shared_group_gain"],
            "personal_increment":v["bootstrap"]["personal_increment"],
            "total_personal_history_gain":v["bootstrap"]["total_personal_history_gain"]
        } for p,v in out.items()}
    }
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(payload["headline"],sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
