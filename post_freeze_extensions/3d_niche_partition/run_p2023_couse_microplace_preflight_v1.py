#!/usr/bin/env python3
from __future__ import annotations

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

CFG=ROOT/"post_freeze_extensions/3d_niche_partition/p2023_couse_microplace_contract_v1.json"
COUSE_CFG=ROOT/"post_freeze_extensions/3d_niche_partition/couse_vertical_separation_contract_v1.json"
RECEIPT=ROOT/"post_freeze_extensions/3d_niche_partition/couse_shiftability_receipt_v1.json"
OUT=ROOT/"post_freeze_extensions/3d_niche_partition/p2023_couse_microplace_preflight_v1.json"
PANEL="phyllostomus_2023"

def endpoint_key(m,side):
    if side=="a":
        return (m["cohort"],m["a"],m["a_session"],m["a_t"].isoformat(),tuple(m["cell"]))
    return (m["cohort"],m["b"],m["b_session"],m["b_t"].isoformat(),tuple(m["cell"]))

def make_lookup(records):
    out={}
    for r in records:
        cell500=(math.floor(r["x"]/500.0),math.floor(r["y"]/500.0))
        key=(r["cohort"],r["iid"],r["session"],r["t"].isoformat(),cell500)
        if key in out:
            raise RuntimeError(f"duplicate endpoint key {key}")
        out[key]=r
    return out

def scale_support(records,encounters,scale,cfg):
    group_n=defaultdict(int)
    for r in records:
        cell500=(math.floor(r["x"]/500.0),math.floor(r["y"]/500.0))
        micro=(math.floor(r["x"]/scale),math.floor(r["y"]/scale))
        key=(r["cohort"],r["iid"],r["session"],cell500,micro)
        group_n[key]+=1

    lookup=make_lookup(records)
    total_ep=0; shift_ep=0
    by_dyad=defaultdict(lambda:{"endpoints":0,"shiftable_endpoints":0,"fully_shiftable_encounters":0,"encounters":0})
    endpoint_group_sizes=[]
    for m in encounters:
        d=(m["cohort"],m["a"],m["b"])
        ka=endpoint_key(m,"a"); kb=endpoint_key(m,"b")
        a=lookup[ka]; b=lookup[kb]
        c500=tuple(m["cell"])
        ma=(math.floor(a["x"]/scale),math.floor(a["y"]/scale))
        mb=(math.floor(b["x"]/scale),math.floor(b["y"]/scale))
        ga=(m["cohort"],m["a"],m["a_session"],c500,ma)
        gb=(m["cohort"],m["b"],m["b_session"],c500,mb)
        na=group_n[ga]; nb=group_n[gb]
        sa=na>=2; sb=nb>=2
        endpoint_group_sizes.extend([na,nb])
        total_ep+=2
        shift_ep+=int(sa)+int(sb)
        by_dyad[d]["endpoints"]+=2
        by_dyad[d]["shiftable_endpoints"]+=int(sa)+int(sb)
        by_dyad[d]["encounters"]+=1
        by_dyad[d]["fully_shiftable_encounters"]+=int(sa and sb)

    pf=cfg["preflight"]
    dyad_rows=[]
    every_dyad_fraction=True
    dyads_ge5=0
    for d in sorted(by_dyad):
        x=by_dyad[d]
        frac=x["shiftable_endpoints"]/x["endpoints"] if x["endpoints"] else 0.0
        ok_frac=frac>=float(pf["per_dyad_endpoint_shiftable_fraction_min"])
        every_dyad_fraction &= ok_frac
        if x["fully_shiftable_encounters"]>=int(pf["dyad_min_fully_shiftable_encounters"]):
            dyads_ge5+=1
        dyad_rows.append({
            "cohort":d[0],"individual_a":d[1],"individual_b":d[2],
            "encounters":int(x["encounters"]),
            "endpoint_shiftable_fraction":float(frac),
            "fully_shiftable_encounters":int(x["fully_shiftable_encounters"]),
            "per_dyad_fraction_gate_met":bool(ok_frac),
        })

    overall=shift_ep/total_ep if total_ep else 0.0
    passed=(
        overall>=float(pf["endpoint_shiftable_fraction_min"]) and
        every_dyad_fraction and
        dyads_ge5>=int(pf["dyads_with_both_endpoints_shiftable_min"])
    )
    arr=np.asarray(endpoint_group_sizes,dtype=float)
    return {
        "scale_m":int(scale),
        "endpoint_shiftable_fraction":float(overall),
        "shiftable_endpoints":int(shift_ep),
        "total_endpoints":int(total_ep),
        "all_dyads_meet_endpoint_fraction_gate":bool(every_dyad_fraction),
        "dyads_with_min_fully_shiftable_encounters":int(dyads_ge5),
        "required_dyads_with_min_fully_shiftable_encounters":int(pf["dyads_with_both_endpoints_shiftable_min"]),
        "group_size_at_encounter_endpoints":{
            "median":float(np.median(arr)),
            "q025":float(np.quantile(arr,0.025)),
            "q975":float(np.quantile(arr,0.975)),
            "min":int(np.min(arr)),
            "max":int(np.max(arr)),
        },
        "dyads":dyad_rows,
        "passed":bool(passed),
    }

def main():
    cfg=json.loads(CFG.read_text())
    couse=json.loads(COUSE_CFG.read_text())
    receipt=json.loads(RECEIPT.read_text())
    frozen=cfg["frozen_primary"]

    xy=shift.pre.load_xy_time(PANEL)
    rr,encounters,dyads,inds,esha,_=vert.reconstruct_primary(PANEL,xy,couse,receipt)
    if esha!=frozen["encounter_sha256"]:
        raise RuntimeError(f"encounter SHA mismatch {esha}")
    if len(encounters)!=int(frozen["encounters"]) or len(dyads)!=int(frozen["dyads"]):
        raise RuntimeError("frozen encounter count mismatch")

    results=[scale_support(rr,encounters,float(scale),cfg) for scale in cfg["candidate_microplace_m"]]
    selected=next((x for x in results if x["passed"]),None)

    payload={
        "schema_version":1,
        "study_id":cfg["study_id"],
        "vertical_values_used":False,
        "encounter_sha256":esha,
        "frozen_encounters":len(encounters),
        "frozen_dyads":len(dyads),
        "frozen_individuals":len(inds),
        "candidate_results":results,
        "selected_microplace_m":selected["scale_m"] if selected else None,
        "microplace_null_may_open":selected is not None,
        "selection_rule":cfg["preflight"]["selection_rule"],
    }
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "encounters":len(encounters),
        "selected_microplace_m":payload["selected_microplace_m"],
        "microplace_null_may_open":payload["microplace_null_may_open"],
        "candidates":[{
            "scale_m":x["scale_m"],
            "endpoint_shiftable_fraction":x["endpoint_shiftable_fraction"],
            "dyads_ge5":x["dyads_with_min_fully_shiftable_encounters"],
            "all_dyads_fraction_gate":x["all_dyads_meet_endpoint_fraction_gate"],
            "passed":x["passed"],
        } for x in results]
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
