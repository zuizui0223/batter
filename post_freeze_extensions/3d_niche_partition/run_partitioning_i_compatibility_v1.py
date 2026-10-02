#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"post_freeze_extensions/3d_niche_partition"
CFG=json.loads((BASE/"partitioning_calibration_contract_v1.json").read_text())
PANELS=CFG["panels"]
def run(panel):
    src=BASE/"couse_vertical_results"/f"{panel}_couse_vertical_result_v1.json"
    x=json.loads(src.read_text())
    meds=np.array([d["observed_median_separation_m"] for d in x["observed"]["dyads"]],dtype=float)
    null_mean=float(x["permutation"]["primary_separation"]["mean"])
    obs=float(np.mean(meds)); excess=obs-null_mean
    B=int(CFG["i_compatibility"]["B"]); seed=int(CFG["i_compatibility"]["seeds"][panel])
    rng=np.random.default_rng(seed)
    boot=np.empty(B)
    n=len(meds)
    for b in range(B):
        boot[b]=float(np.mean(rng.choice(meds,size=n,replace=True)))-null_mean
    q=np.quantile(boot,[.025,.5,.975])
    out={"panel":panel,"classification":"post-outcome compatibility calibration","dyads":n,
         "observed_equal_dyad_mean_m":obs,"phase_null_mean_m":null_mean,"observed_excess_m":excess,
         "dyad_bootstrap":{"B":B,"seed":seed,"q025_m":float(q[0]),"q50_m":float(q[1]),"q975_m":float(q[2])},
         "interpretation":{"positive_excess_upper_compatibility_bound_m":float(q[2])},
         "claim_boundary":"percentile dyad-bootstrap compatibility interval; not post-hoc power or formal equivalence"}
    od=BASE/"partitioning_calibration_results"; od.mkdir(exist_ok=True)
    (od/f"{panel}_i_compatibility_v1.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,sort_keys=True))
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--panel",choices=PANELS); a=ap.parse_args()
    if a.panel: run(a.panel)
    else:
        for p in PANELS: run(p)
