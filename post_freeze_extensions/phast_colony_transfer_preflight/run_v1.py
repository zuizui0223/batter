#!/usr/bin/env python3
from __future__ import annotations
import json, re, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import scripts.run_tag_altitude_bias_shape as shape

OUT=ROOT/"post_freeze_extensions/phast_colony_transfer_preflight/result_v1.json"
PANELS=["phyllostomus_2016","phyllostomus_2022","phyllostomus_2023"]

def main():
    out={"schema_version":1,"vertical_outcome_opened":False,"panels":{}}
    for p in PANELS:
        rec,_=shape.panel_raw(p)
        by=defaultdict(list)
        for r in rec: by[str(r["cohort"])].append(r)
        cs={}
        for c,rows in sorted(by.items()):
            cs[c]={
                "individuals":len({str(r["iid"]) for r in rows}),
                "sessions":len({str(r["session"]) for r in rows}),
                "rows":len(rows),
                "min_timestamp":min(r["t"] for r in rows).isoformat(),
                "max_timestamp":max(r["t"] for r in rows).isoformat(),
                "x_min":float(min(r["x"] for r in rows)),
                "x_max":float(max(r["x"] for r in rows)),
                "y_min":float(min(r["y"] for r in rows)),
                "y_max":float(max(r["y"] for r in rows))
            }
        out["panels"][p]={"cohorts":cs}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
