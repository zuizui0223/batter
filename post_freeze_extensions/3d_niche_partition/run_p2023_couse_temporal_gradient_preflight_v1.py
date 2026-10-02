#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

shift=load_module("couse_shift_v1",ROOT/"post_freeze_extensions/3d_niche_partition/run_couse_shiftability_v1.py")
vert=load_module("couse_vert_v1",ROOT/"post_freeze_extensions/3d_niche_partition/run_couse_vertical_separation_v1.py")

CFG=ROOT/"post_freeze_extensions/3d_niche_partition/p2023_couse_temporal_gradient_contract_v1.json"
COUSE_CFG=ROOT/"post_freeze_extensions/3d_niche_partition/couse_vertical_separation_contract_v1.json"
RECEIPT=ROOT/"post_freeze_extensions/3d_niche_partition/couse_shiftability_receipt_v1.json"
OUT=ROOT/"post_freeze_extensions/3d_niche_partition/p2023_couse_temporal_gradient_preflight_v1.json"

PANEL="phyllostomus_2023"

def canonical_encounter(m):
    return shift.canonical_encounter(m)

def main():
    cfg=json.loads(CFG.read_text())
    couse=json.loads(COUSE_CFG.read_text())
    receipt=json.loads(RECEIPT.read_text())
    frozen=cfg["frozen_primary"]

    xy=shift.pre.load_xy_time(PANEL)
    _,encounters,dyads,inds,esha,_=vert.reconstruct_primary(
        PANEL,xy,couse,receipt
    )
    if esha!=frozen["encounter_sha256"]:
        raise RuntimeError(f"encounter SHA mismatch {esha}")
    if len(encounters)!=int(frozen["encounters"]) or len(dyads)!=int(frozen["dyads"]):
        raise RuntimeError("frozen encounter/dyad count mismatch")

    by_dyad=defaultdict(list)
    all_dt=[]
    for m in encounters:
        d=(m["cohort"],m["a"],m["b"])
        dt=float(m["dt_s"])
        by_dyad[d].append(dt)
        all_dt.append(dt)

    pf=cfg["slope_preflight"]
    rows=[]
    evaluable=[]
    for d in sorted(by_dyad):
        x=np.asarray(by_dyad[d],dtype=float)
        rounded=np.rint(x).astype(int)
        ok=(
            len(x)>=int(pf["min_encounters_per_dyad"]) and
            len(np.unique(rounded))>=int(pf["min_distinct_rounded_dt_s"]) and
            float(np.std(x,ddof=0))>float(pf["min_dt_sd_s_exclusive"])
        )
        row={
            "cohort":d[0],
            "individual_a":d[1],
            "individual_b":d[2],
            "encounters":int(len(x)),
            "dt_min_s":float(np.min(x)),
            "dt_median_s":float(np.median(x)),
            "dt_mean_s":float(np.mean(x)),
            "dt_max_s":float(np.max(x)),
            "dt_sd_s":float(np.std(x,ddof=0)),
            "distinct_rounded_dt_s":int(len(np.unique(rounded))),
            "slope_evaluable":bool(ok),
        }
        rows.append(row)
        if ok:
            evaluable.append(d)

    bands=[]
    for lo,hi in cfg["descriptive_bands_s"]:
        if lo==0:
            sel=[m for m in encounters if 0<=float(m["dt_s"])<=hi]
            label=f"0-{hi}"
        else:
            sel=[m for m in encounters if lo<float(m["dt_s"])<=hi]
            label=f">{lo}-{hi}"
        ds=defaultdict(int)
        for m in sel:
            ds[(m["cohort"],m["a"],m["b"])]+=1
        bands.append({
            "label_s":label,
            "encounters":len(sel),
            "represented_dyads":len(ds),
            "dyads_with_at_least_3_encounters":sum(int(n>=3) for n in ds.values()),
            "dyad_counts":{f"{d[0]}|||{d[1]}|||{d[2]}":int(n) for d,n in sorted(ds.items())},
        })

    cumul=[]
    for hi in cfg["descriptive_cumulative_upper_s"]:
        sel=[m for m in encounters if float(m["dt_s"])<=hi]
        ds=defaultdict(int)
        for m in sel:
            ds[(m["cohort"],m["a"],m["b"])]+=1
        cumul.append({
            "upper_s":int(hi),
            "encounters":len(sel),
            "represented_dyads":len(ds),
            "dyads_with_at_least_3_encounters":sum(int(n>=3) for n in ds.values()),
        })

    proceed=len(evaluable)>=int(pf["panel_min_slope_evaluable_dyads"])
    encounter_desc=sorted(canonical_encounter(m) for m in encounters)
    digest=hashlib.sha256(("\n".join(encounter_desc)+"\n").encode()).hexdigest()

    payload={
        "schema_version":1,
        "study_id":cfg["study_id"],
        "vertical_values_used":False,
        "encounter_sha256":digest,
        "frozen_encounters":len(encounters),
        "frozen_dyads":len(dyads),
        "frozen_individuals":len(inds),
        "dt_overall":{
            "min_s":float(np.min(all_dt)),
            "median_s":float(np.median(all_dt)),
            "mean_s":float(np.mean(all_dt)),
            "max_s":float(np.max(all_dt)),
            "sd_s":float(np.std(all_dt,ddof=0)),
        },
        "dyads":rows,
        "slope_evaluable_dyads":[f"{d[0]}|||{d[1]}|||{d[2]}" for d in evaluable],
        "slope_evaluable_dyad_count":len(evaluable),
        "panel_gate_required":int(pf["panel_min_slope_evaluable_dyads"]),
        "temporal_gradient_may_open":bool(proceed),
        "descriptive_bands":bands,
        "descriptive_cumulative":cumul,
    }
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "encounters":len(encounters),
        "dyads":len(dyads),
        "slope_evaluable_dyads":len(evaluable),
        "may_open":proceed,
        "dt_overall":payload["dt_overall"],
        "bands":[{k:x[k] for k in ("label_s","encounters","represented_dyads","dyads_with_at_least_3_encounters")} for x in bands],
        "cumulative":cumul,
        "encounter_sha256":digest,
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
