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

CONTRACT=ROOT/"post_freeze_extensions/behavioural_mixture/preflight_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/behavioural_mixture/preflight_result_v1.json"

def q(x,p):
    return float(np.quantile(np.asarray(x,dtype=float),p)) if x else None

def panel(panel):
    records,_=shape.panel_raw(panel)
    by=defaultdict(list)
    inds=set()
    for r in records:
        by[(r["cohort"],r["session"])].append(r)
        inds.add(r["iid"])
    dts=[]; dists=[]
    for vals in by.values():
        vals=sorted(vals,key=lambda r:r["t"])
        for a,b in zip(vals[:-1],vals[1:]):
            dt=(b["t"]-a["t"]).total_seconds()
            if dt<=0: continue
            dx=float(b["x"]-a["x"]); dy=float(b["y"]-a["y"])
            dts.append(float(dt))
            dists.append(math.hypot(dx,dy))
    return {
      "panel":panel,
      "sessions":len(by),
      "individuals":len(inds),
      "positive_dt_steps":len(dts),
      "dt_seconds":{"q10":q(dts,.10),"q50":q(dts,.50),"q90":q(dts,.90),"q95":q(dts,.95),"q99":q(dts,.99),"max":max(dts) if dts else None},
      "distance_m":{"q50":q(dists,.50),"q90":q(dists,.90),"q95":q(dists,.95),"q99":q(dists,.99)},
      "proportion_dt_le":{str(c):float(np.mean(np.asarray(dts)<=c)) if dts else None for c in [60,300,600,1800]},
      "vertical_values_summarized":False
    }

def main():
    c=json.loads(CONTRACT.read_text())
    out={p:panel(p) for p in c["panels"]}
    payload={"study_id":c["study_id"],"contract":str(CONTRACT.relative_to(ROOT)),"panels":out,"vertical_values_summarized":False}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps({p:{"steps":v["positive_dt_steps"],"dt":v["dt_seconds"],"prop":v["proportion_dt_le"]} for p,v in out.items()},sort_keys=True))
if __name__=="__main__":
    main()
