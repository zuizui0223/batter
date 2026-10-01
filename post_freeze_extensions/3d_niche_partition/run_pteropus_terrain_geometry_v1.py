#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

ext=load_module("external_geom_v1",ROOT/"post_freeze_extensions/3d_niche_partition/run_external_geometry_v1.py")
fast=load_module("external_geom_fast_v1",ROOT/"post_freeze_extensions/3d_niche_partition/run_external_geometry_fast_equivalence_v1.py")
terr=load_module("terrain_audit_v1",ROOT/"post_freeze_extensions/pteropus_terrain_audit/run_terrain_audit_v1.py")

CFG=ROOT/"post_freeze_extensions/3d_niche_partition/external_geometry_prediction_contract_v1.json"
TERRAIN_CONTRACT=ROOT/"post_freeze_extensions/pteropus_terrain_audit/contract_v1.json"
DEM_RECEIPT=ROOT/"post_freeze_extensions/pteropus_terrain_audit/dem_preflight_receipt_v1.json"
SMALL_RECEIPT=ROOT/"post_freeze_extensions/small_panel_generality/height_opening_receipt_v1.json"
NATIVE_SUMMARY=ROOT/"post_freeze_extensions/3d_niche_partition/external_geometry_interim_v1.json"
OUT=ROOT/"post_freeze_extensions/3d_niche_partition/pteropus_terrain_geometry_result_v1.json"


def main():
    cfg=json.loads(CFG.read_text())
    tc=json.loads(TERRAIN_CONTRACT.read_text())
    dem=json.loads(DEM_RECEIPT.read_text())
    small=json.loads(SMALL_RECEIPT.read_text())
    native=json.loads(NATIVE_SUMMARY.read_text())["pteropus_poliocephalus"]

    sec=cfg["sources"]["pteropus_poliocephalus"]["terrain_secondary"]
    srcid=tc["source"]["source_id"]
    small_rec=small["sources"][srcid]

    if dem.get("status")!="DEM_MAY_OPEN":
        raise RuntimeError(f"DEM receipt status {dem.get('status')}")
    if hashlib.sha256(TERRAIN_CONTRACT.read_bytes()).hexdigest()!=dem["contract_sha256"]:
        raise RuntimeError("terrain contract SHA mismatch")

    d,source_sha=terr.load_source(tc,small_rec)
    targets={str(x["session"]) for rows in small_rec["frozen_vertical_target_sessions"].values() for x in rows}
    d=d[d["session"].isin(targets)].copy()
    if set(d["session"].unique())!=targets:
        raise RuntimeError("Pteropus target-session universe changed")

    grids=terr.load_hgt_tiles(dem)
    terrain=np.array([
        terr.bilinear_hgt(grids,lat,lon,int(tc["terrain_sampling"]["void_value"]))
        for lat,lon in zip(d["lat"],d["lon"])
    ],dtype=float)
    if not np.isfinite(terrain).all():
        raise RuntimeError("nonfinite terrain")

    d["agl_proxy"]=d["height_msl"].to_numpy(dtype=float)-terrain

    tr=Transformer.from_crs("EPSG:4326",f"EPSG:{int(tc['source']['projection_epsg'])}",always_xy=True)
    x,y=tr.transform(d["lon"].to_numpy(dtype=float),d["lat"].to_numpy(dtype=float))

    import pandas as pd
    q=pd.DataFrame({
        "cohort":srcid,
        "iid":d["iid"].astype(str).to_numpy(),
        "session":d["session"].astype(str).to_numpy(),
        "x":np.asarray(x,dtype=float),
        "y":np.asarray(y,dtype=float),
        "h":d["agl_proxy"].to_numpy(dtype=float),
    })

    sessions=ext.build_sessions(q,float(cfg["primary_grid_m"]),float(cfg["alpha"]))
    cohort=next(iter(sessions))
    ss=sessions[cohort]
    mats,pair_count=ext.metric_matrices(ss,int(cfg["pair_shared_fix_min_each"]))
    labels_raw=np.array([s["individual"] for s in ss],dtype=object)

    observed,per_ind,rows=ext.evaluate_generic(sessions,{cohort:mats},{cohort:labels_raw})
    labels_int,_=fast.encode_labels(labels_raw)
    d_fast,n_fast=fast.fast_primary(mats["ozxy"],labels_int)
    if n_fast!=observed["eligible_individuals"] or not np.isclose(d_fast,observed["d_panel"],rtol=0,atol=1e-15):
        raise RuntimeError("terrain fast/slow observed mismatch")
    if observed["eligible_individuals"]!=4:
        raise RuntimeError(f"terrain geometry eligible n {observed['eligible_individuals']} != 4")

    B=int(sec["B"]); seed=int(sec["seed"])
    rng=np.random.default_rng(seed)
    null=[]; null_n=[]; invalid=0
    for _ in range(B):
        lp=rng.permutation(labels_int)
        dv,n=fast.fast_primary(mats["ozxy"],lp)
        if dv is None or n<4:
            invalid+=1
            continue
        null.append(float(dv));null_n.append(int(n))

    cal=ext.cal.tail_summary(null,float(observed["d_panel"]))
    supported=cal["observed_minus_null_mean"]>0 and cal["p_null_ge_observed"]<=0.05

    H=float(observed["d_oxy"])
    V=float(observed["d_ozxy"])
    S=float(observed["other_r3d"]-observed["self_r3d"])
    payload={
      "study_id":"batter-pteropus-terrain-relative-3d-geometry-v1",
      "classification":"secondary diagnostic; native-MSL geometry remains primary",
      "source_raw_sha256":source_sha,
      "dem_contract_sha256":dem["contract_sha256"],
      "session_count":len(ss),
      "pair_count":pair_count,
      "observed":{**observed,"individual_results":per_ind,"session_results":rows},
      "geometry":{"H":H,"V":V,"S":S},
      "permutation":{
        "B_requested":B,"seed":seed,
        "valid_replicates":len(null),"invalid_replicates":invalid,
        "eligible_individuals_null":{"mean":float(np.mean(null_n)),"min":int(np.min(null_n)),"max":int(np.max(null_n))},
        "primary_d_panel":cal,
      },
      "supported":bool(supported),
      "native_msl_comparison":{
        "H_native":native["H"],"V_native":native["V"],"S_native":native["S"],
        "H_ratio":H/native["H"] if native["H"] else None,
        "V_ratio":V/native["V"] if native["V"] else None,
        "S_ratio":S/native["S"] if native["S"] else None,
      },
      "claim_boundary":[
        "DEM-derived MSL-minus-terrain is a terrain-relative proxy, not true measured AGL",
        "secondary diagnostic cannot overwrite native-MSL primary geometry",
        "does not identify competition or resource partitioning"
      ]
    }
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "eligible_individuals":observed["eligible_individuals"],
      "H":H,"V":V,"S":S,
      "self_ozxy":observed["self_ozxy"],"other_ozxy":observed["other_ozxy"],
      "self_r3d":observed["self_r3d"],"other_r3d":observed["other_r3d"],
      "calibrated_excess":cal["observed_minus_null_mean"],
      "p_upper":cal["p_null_ge_observed"],
      "supported":bool(supported),
      "native_V":native["V"],"V_ratio":V/native["V"]
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
