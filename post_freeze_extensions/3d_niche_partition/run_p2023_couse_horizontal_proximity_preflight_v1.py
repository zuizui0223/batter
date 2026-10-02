#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
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

CFG=ROOT/"post_freeze_extensions/3d_niche_partition/p2023_couse_horizontal_proximity_contract_v1.json"
COUSE_CFG=ROOT/"post_freeze_extensions/3d_niche_partition/couse_vertical_separation_contract_v1.json"
RECEIPT=ROOT/"post_freeze_extensions/3d_niche_partition/couse_shiftability_receipt_v1.json"
OUT=ROOT/"post_freeze_extensions/3d_niche_partition/p2023_couse_horizontal_proximity_preflight_v1.json"
PANEL="phyllostomus_2023"


def endpoint_key(m,side):
    if side=="a":
        return (m["cohort"],m["a"],m["a_session"],m["a_t"].isoformat(),tuple(m["cell"]))
    return (m["cohort"],m["b"],m["b_session"],m["b_t"].isoformat(),tuple(m["cell"]))


def make_lookup(records):
    out={}
    for r in records:
        cell=(math.floor(r["x"]/500.0),math.floor(r["y"]/500.0))
        key=(r["cohort"],r["iid"],r["session"],r["t"].isoformat(),cell)
        if key in out:
            raise RuntimeError(f"duplicate endpoint key {key}")
        out[key]=r
    return out


def main():
    cfg=json.loads(CFG.read_text())
    couse=json.loads(COUSE_CFG.read_text())
    receipt=json.loads(RECEIPT.read_text())
    frozen=cfg["frozen_primary"]

    xy=shift.pre.load_xy_time(PANEL)
    rr,encounters,dyads,inds,esha,_=vert.reconstruct_primary(
        PANEL,xy,couse,receipt
    )
    if esha!=frozen["encounter_sha256"]:
        raise RuntimeError("frozen encounter SHA mismatch")
    if len(encounters)!=int(frozen["encounters"]) or len(dyads)!=int(frozen["dyads"]):
        raise RuntimeError("frozen geometry count mismatch")

    lookup=make_lookup(rr)
    by_dyad=defaultdict(list)
    distances=[]
    for m in encounters:
        ka=endpoint_key(m,"a")
        kb=endpoint_key(m,"b")
        if ka not in lookup or kb not in lookup:
            raise RuntimeError("encounter endpoint missing from x-y lookup")
        a=lookup[ka]; b=lookup[kb]
        dist=float(math.hypot(a["x"]-b["x"],a["y"]-b["y"]))
        d=(m["cohort"],m["a"],m["b"])
        by_dyad[d].append(dist)
        distances.append(dist)

    pf=cfg["preflight"]
    rows=[]; evaluable=[]
    for d in sorted(by_dyad):
        x=np.asarray(by_dyad[d],dtype=float)
        rounded=np.rint(x).astype(int)
        ok=(
            len(x)>=int(pf["min_encounters_per_dyad"]) and
            len(np.unique(rounded))>=int(pf["min_distinct_rounded_distance_m"]) and
            float(np.std(x,ddof=0))>float(pf["min_distance_sd_m_exclusive"])
        )
        rows.append({
            "cohort":d[0],"individual_a":d[1],"individual_b":d[2],
            "encounters":int(len(x)),
            "distance_min_m":float(np.min(x)),
            "distance_median_m":float(np.median(x)),
            "distance_mean_m":float(np.mean(x)),
            "distance_max_m":float(np.max(x)),
            "distance_sd_m":float(np.std(x,ddof=0)),
            "distinct_rounded_distance_m":int(len(np.unique(rounded))),
            "slope_evaluable":bool(ok),
        })
        if ok: evaluable.append(d)

    bands=[]
    for lo,hi in cfg["descriptive_bands_m"]:
        if lo==0:
            sel=[(m,d) for m,d in zip(encounters,distances) if 0<=d<=hi]
            label=f"0-{hi}"
        else:
            sel=[(m,d) for m,d in zip(encounters,distances) if lo<d<=hi]
            label=f">{lo}-{hi}"
        dc=defaultdict(int)
        for m,_ in sel:
            dc[(m["cohort"],m["a"],m["b"])]+=1
        bands.append({
            "label_m":label,
            "encounters":len(sel),
            "represented_dyads":len(dc),
            "dyads_with_at_least_3_encounters":sum(int(n>=3) for n in dc.values()),
            "dyad_counts":{f"{d[0]}|||{d[1]}|||{d[2]}":int(n) for d,n in sorted(dc.items())},
        })

    cumul=[]
    for hi in cfg["descriptive_cumulative_upper_m"]:
        sel=[(m,d) for m,d in zip(encounters,distances) if d<=hi]
        dc=defaultdict(int)
        for m,_ in sel:
            dc[(m["cohort"],m["a"],m["b"])]+=1
        cumul.append({
            "upper_m":int(hi),
            "encounters":len(sel),
            "represented_dyads":len(dc),
            "dyads_with_at_least_3_encounters":sum(int(n>=3) for n in dc.values()),
        })

    desc=sorted(shift.canonical_encounter(m) for m in encounters)
    digest=hashlib.sha256(("\n".join(desc)+"\n").encode()).hexdigest()
    proceed=len(evaluable)>=int(pf["panel_min_evaluable_dyads"])

    payload={
        "schema_version":1,
        "study_id":cfg["study_id"],
        "vertical_values_used":False,
        "encounter_sha256":digest,
        "frozen_encounters":len(encounters),
        "frozen_dyads":len(dyads),
        "frozen_individuals":len(inds),
        "distance_overall":{
            "min_m":float(np.min(distances)),
            "median_m":float(np.median(distances)),
            "mean_m":float(np.mean(distances)),
            "max_m":float(np.max(distances)),
            "sd_m":float(np.std(distances,ddof=0)),
        },
        "dyads":rows,
        "slope_evaluable_dyads":[f"{d[0]}|||{d[1]}|||{d[2]}" for d in evaluable],
        "slope_evaluable_dyad_count":len(evaluable),
        "panel_gate_required":int(pf["panel_min_evaluable_dyads"]),
        "horizontal_proximity_may_open":bool(proceed),
        "descriptive_bands":bands,
        "descriptive_cumulative":cumul,
    }
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "encounters":len(encounters),"dyads":len(dyads),
        "slope_evaluable_dyads":len(evaluable),"may_open":proceed,
        "distance_overall":payload["distance_overall"],
        "bands":[{k:x[k] for k in ("label_m","encounters","represented_dyads","dyads_with_at_least_3_encounters")} for x in bands],
        "cumulative":cumul,"encounter_sha256":digest
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
