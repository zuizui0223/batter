#!/usr/bin/env python3
# Requires final x-y-time encounter receipt and shiftability implementation.
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_new_species_replications as core
import scripts.run_cross_panel_estimator_calibration as cal

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

shift=load_module("couse_shift_v1",ROOT/"post_freeze_extensions/3d_niche_partition/run_couse_shiftability_v1.py")
ep=load_module("couse_endpoint_v1",ROOT/"post_freeze_extensions/3d_niche_partition/run_couse_endpoint_audit_v1.py")
terr=load_module("orig_terrain_v1",ROOT/"post_freeze_extensions/3d_niche_partition/run_original_terrain_geometry_v1.py")

CFG=ROOT/"post_freeze_extensions/3d_niche_partition/couse_vertical_separation_contract_v1.json"
RECEIPT=ROOT/"post_freeze_extensions/3d_niche_partition/couse_primary_encounter_receipt_v1.json"
DEM_RECEIPT=ROOT/"post_freeze_extensions/3d_niche_partition/original_terrain_dem_preflight_receipt_v1.json"
OUTDIR=ROOT/"post_freeze_extensions/3d_niche_partition/couse_vertical_results"

CPATH={
    "hypsignathus":"contract/hypsignathus_replication_v1.json",
    "phyllostomus_2022":"contract/phyllostomus_replication_v1.json",
    "phyllostomus_2023":"contract/phyllostomus_2023_replication_v1.json",
    "phyllostomus_2016":"contract/phyllostomus_2016_dry_architecture_v1.json",
}


def source_contract(panel):
    base=json.loads((ROOT/CPATH[panel]).read_text(encoding="utf-8"))
    if panel=="phyllostomus_2016":
        c=copy.deepcopy(base)
        c["vertical"]={
            "field":base["vertical"]["primary_field"],
            "primary_edges_m":base["vertical"]["edges_m"],
        }
        return c
    return base


def target_sessions(panel):
    sessions,_=shift.pre.geom.build_session_distributions(panel)
    return {(cohort,s["session"]) for cohort,rows in sessions.items() for s in rows}


def load_panel_records(panel):
    contract=source_contract(panel)
    ua="batter-couse-vertical-separation-v1/1.0"
    gps=core.get(contract["source"]["gps"],ua)
    ref=core.get(contract["source"]["reference"],ua)
    rows,headers=core.read_csv(gps)
    refs,_=core.read_csv(ref)
    pre=core.build_pre_numeric(rows,headers,refs,contract)
    targets=target_sessions(panel)
    hfield=contract["vertical"]["field"]

    transformers={
        cohort:Transformer.from_crs("EPSG:4326",f"EPSG:{meta['epsg']}",always_xy=True)
        for cohort,meta in pre["projections"].items()
    }

    rec=[]
    seen=set()
    for idx,row in enumerate(rows):
        sid=pre["session_for_row"].get(idx)
        if sid is None:
            continue
        sm=pre["session_meta"][sid]
        cohort=sm["cohort"]
        if cohort not in pre["admitted_cohorts"] or (cohort,sid) not in targets:
            continue
        lon=core.finite_float(row.get("location_long"))
        lat=core.finite_float(row.get("location_lat"))
        h=core.finite_float(row.get(hfield))
        if lon is None or lat is None or h is None:
            continue
        try:
            t=core.parse_time(row.get("timestamp",""))
        except Exception:
            continue
        x,y=transformers[cohort].transform(lon,lat)
        rec.append({
            "cohort":str(cohort),
            "iid":str(sm["individual"]),
            "session":str(sid),
            "t":t,
            "x":float(x),"y":float(y),
            "lon":float(lon),"lat":float(lat),
            "native_h":float(h),
        })
        seen.add((cohort,sid))

    if seen!=targets:
        missing=sorted(targets-seen)
        extra=sorted(seen-targets)
        raise RuntimeError(f"{panel}: target-session mismatch missing={missing[:5]} extra={extra[:5]}")
    return rec,contract


def add_terrain_relative_z(panel,records,contract):
    dr=json.loads(DEM_RECEIPT.read_text(encoding="utf-8"))
    if dr.get("status")!="DEM_MAY_OPEN":
        raise RuntimeError("DEM receipt does not permit opening")
    prec=dr["panels"][panel]
    if len(records)!=int(prec["coordinate_row_count"]):
        raise RuntimeError(f"{panel}: coordinate row count {len(records)} != frozen {prec['coordinate_row_count']}")
    grids=terr.load_tiles(prec,-32768)
    terrain=np.array([
        terr.bilinear_hgt(grids,r["lat"],r["lon"],-32768)
        for r in records
    ],dtype=float)
    if not np.isfinite(terrain).all():
        raise RuntimeError(f"{panel}: nonfinite terrain")

    rel=np.array([r["native_h"] for r in records],dtype=float)-terrain
    by_session=defaultdict(list)
    for i,r in enumerate(records):
        by_session[(r["cohort"],r["session"])].append(i)
    med={}
    for key,ix in by_session.items():
        med[key]=float(np.median(rel[ix]))
    for i,r in enumerate(records):
        r["terrain_m"]=float(terrain[i])
        r["z_rel"]=float(rel[i]-med[(r["cohort"],r["session"])])
    return {
        "terrain_min_m":float(np.min(terrain)),
        "terrain_median_m":float(np.median(terrain)),
        "terrain_max_m":float(np.max(terrain)),
    }


def make_record_lookup(records):
    # Exact GPS source streams should have unique iid/session/timestamp/cell records
    # for encounter endpoints. Abort if not.
    out={}
    for r in records:
        cell=(math.floor(r["x"]/500.0),math.floor(r["y"]/500.0))
        key=(r["cohort"],r["iid"],r["session"],r["t"].isoformat(),cell)
        if key in out:
            raise RuntimeError(f"duplicate encounter endpoint key {key}")
        out[key]=r
    return out


def reconstruct_primary(panel,records,cfg,receipt):
    p=receipt["panels"][panel]
    tol=int(p["tolerance_s"])
    scope=str(p["primary_scope"])
    centers,_=ep.endpoint_centers(records)
    radius=float(cfg["endpoint_exclusion"]["radius_m"])

    # Authoritative frozen encounter ordering:
    # full shiftable x-y-time universe -> mutual-nearest matching ->
    # endpoint encounter filter (when applicable) -> support gates.
    rr_full,_,_=shift.shiftable_records(records,tol)
    encounters,dyads,inds=shift.build_primary_encounters(
        rr_full,tol,cfg,scope,centers,radius
    )
    desc=sorted(shift.canonical_encounter(m) for m in encounters)
    sha=hashlib.sha256(("\n".join(desc)+"\n").encode()).hexdigest()
    if sha!=p["primary_encounter_set_sha256"]:
        raise RuntimeError(f"{panel}: encounter SHA {sha} != frozen {p['primary_encounter_set_sha256']}")
    if len(encounters)!=int(p["encounters"]) or len(dyads)!=int(p["usable_dyads"]):
        raise RuntimeError(f"{panel}: encounter/dyad count mismatch")

    # The z-phase null uses only the primary-scope fix universe.
    phase_rr=(
        [r for r in rr_full if ep.is_away(r,centers,radius)]
        if scope=="endpoint_excluded" else rr_full
    )
    return phase_rr,encounters,dyads,inds,sha


def encounter_endpoint_key(m,side):
    if side=="a":
        return (m["cohort"],m["a"],m["a_session"],m["a_t"].isoformat(),tuple(m["cell"]))
    return (m["cohort"],m["b"],m["b_session"],m["b_t"].isoformat(),tuple(m["cell"]))


def build_phase_groups(rr,lookup,encounters):
    groups=defaultdict(list)
    for r in rr:
        cell=(math.floor(r["x"]/500.0),math.floor(r["y"]/500.0))
        key=(r["cohort"],r["iid"],r["session"],cell)
        groups[key].append(r)

    group_data={}
    record_pos={}
    for gid,(key,vals) in enumerate(sorted(groups.items(),key=lambda kv:str(kv[0]))):
        vals=sorted(vals,key=lambda r:r["t"])
        z=np.array([r["z_rel"] for r in vals],dtype=float)
        group_data[gid]={"key":key,"z":z,"n":len(z)}
        for pos,r in enumerate(vals):
            cell=key[3]
            rk=(r["cohort"],r["iid"],r["session"],r["t"].isoformat(),cell)
            if rk in record_pos:
                raise RuntimeError(f"duplicate phase record key {rk}")
            record_pos[rk]=(gid,pos)

    ga=[];pa=[];gb=[];pb=[];dyad_keys=[]
    for m in encounters:
        ka=encounter_endpoint_key(m,"a")
        kb=encounter_endpoint_key(m,"b")
        if ka not in record_pos or kb not in record_pos:
            raise RuntimeError("encounter endpoint absent from primary phase universe")
        a=record_pos[ka]; b=record_pos[kb]
        ga.append(a[0]);pa.append(a[1]);gb.append(b[0]);pb.append(b[1])
        dyad_keys.append((m["cohort"],m["a"],m["b"]))

    uniq_dyads=sorted(set(dyad_keys))
    didx={d:i for i,d in enumerate(uniq_dyads)}
    di=np.array([didx[d] for d in dyad_keys],dtype=np.int16)

    return group_data,np.array(ga,dtype=np.int32),np.array(pa,dtype=np.int32),np.array(gb,dtype=np.int32),np.array(pb,dtype=np.int32),di,uniq_dyads


def observed_endpoint_values(group_data,g,p):
    out=np.empty(len(g),dtype=float)
    for gid in np.unique(g):
        mask=(g==gid)
        out[mask]=group_data[int(gid)]["z"][p[mask]]
    return out


def panel_stat(sep,di,n_dyads):
    meds=np.empty(n_dyads,dtype=float)
    for d in range(n_dyads):
        vals=sep[di==d]
        if len(vals)==0:
            raise RuntimeError("empty frozen dyad")
        meds[d]=float(np.median(vals))
    return float(np.mean(meds)),meds


def permuted_endpoint_values(group_data,g,p,rng):
    out=np.empty(len(g),dtype=float)
    for gid in np.unique(g):
        mask=(g==gid)
        gd=group_data[int(gid)]
        n=int(gd["n"])
        if n>=2:
            sh=int(rng.integers(1,n))
            out[mask]=gd["z"][(p[mask]+sh)%n]
        else:
            out[mask]=gd["z"][p[mask]]
    return out


def run(panel):
    cfg=json.loads(CFG.read_text(encoding="utf-8"))
    receipt=json.loads(RECEIPT.read_text(encoding="utf-8"))
    if receipt.get("status")!="PRIMARY_ENCOUNTER_SET_MAY_OPEN_VERTICAL":
        raise RuntimeError("primary encounter receipt does not permit vertical opening")

    records,contract=load_panel_records(panel)
    terrain_summary=add_terrain_relative_z(panel,records,contract)
    rr,encounters,dyads,inds,esha=reconstruct_primary(panel,records,cfg,receipt)

    lookup=make_record_lookup(rr)
    group_data,ga,pa,gb,pb,di,dyad_list=build_phase_groups(rr,lookup,encounters)

    za=observed_endpoint_values(group_data,ga,pa)
    zb=observed_endpoint_values(group_data,gb,pb)
    sep=np.abs(za-zb)
    obs,dyad_meds=panel_stat(sep,di,len(dyad_list))

    seed=int(cfg["null"]["seeds"][panel])
    B=int(cfg["null"]["B"])
    rng=np.random.default_rng(seed)
    null=np.empty(B,dtype=float)
    for b in range(B):
        za_p=permuted_endpoint_values(group_data,ga,pa,rng)
        zb_p=permuted_endpoint_values(group_data,gb,pb,rng)
        null[b]=panel_stat(np.abs(za_p-zb_p),di,len(dyad_list))[0]

    calibration=cal.tail_summary(null.tolist(),obs)
    supported=bool(
        calibration["observed_minus_null_mean"]>0 and
        calibration["p_null_ge_observed"]<=0.05
    )

    dyad_rows=[]
    for i,d in enumerate(dyad_list):
        vals=sep[di==i]
        dyad_rows.append({
            "cohort":d[0],"individual_a":d[1],"individual_b":d[2],
            "encounters":int(len(vals)),
            "observed_median_separation_m":float(np.median(vals)),
            "observed_mean_separation_m":float(np.mean(vals)),
        })

    pinfo=receipt["panels"][panel]
    payload={
        "schema_version":1,
        "study_id":cfg["study_id"],
        "panel":panel,
        "classification":"post-outcome synchronous co-use mechanism test",
        "primary_scope":pinfo["primary_scope"],
        "tolerance_s":int(pinfo["tolerance_s"]),
        "encounter_set_sha256":esha,
        "encounters":len(encounters),
        "usable_dyads":len(dyad_list),
        "usable_individuals":len(inds),
        "terrain_relative_proxy":True,
        "terrain_summary_descriptive":terrain_summary,
        "observed":{
            "panel_equal_dyad_median_separation_m":obs,
            "encounter_separation_m":{
                "mean":float(np.mean(sep)),
                "median":float(np.median(sep)),
                "q025":float(np.quantile(sep,0.025)),
                "q975":float(np.quantile(sep,0.975)),
            },
            "dyads":dyad_rows,
        },
        "phase_groups":{
            "count":len(group_data),
            "shiftable_groups":sum(int(x["n"]>=2) for x in group_data.values()),
            "unshiftable_groups":sum(int(x["n"]<2) for x in group_data.values()),
            "frozen_shiftable_endpoint_fraction":float(pinfo["shiftable_endpoint_fraction"]),
        },
        "permutation":{
            "B":B,"seed":seed,
            "primary_separation":calibration,
        },
        "decision":{
            "supported":supported,
            "interpretation":(
                "synchronous local co-use shows additional vertical separation beyond stable site-specific personal strategies"
                if supported else
                "no evidence that synchronous local co-use adds vertical separation beyond stable site-specific personal strategies"
            ),
        },
        "claim_boundary":[
            "co-presence-dependent association is not unique evidence for competition",
            "endpoint proxy is not a verified roost/lek/colony location",
            "terrain-relative height is DEM-derived proxy, not measured AGL",
            "highly localized shared-site encounters are not landscape-wide interactions",
        ],
    }
    OUTDIR.mkdir(parents=True,exist_ok=True)
    out=OUTDIR/f"{panel}_couse_vertical_result_v1.json"
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    print(json.dumps({
        "panel":panel,
        "scope":pinfo["primary_scope"],
        "tolerance_s":pinfo["tolerance_s"],
        "individuals":len(inds),
        "dyads":len(dyad_list),
        "encounters":len(encounters),
        "observed_separation_m":obs,
        "null_mean_m":calibration["mean"],
        "calibrated_excess_m":calibration["observed_minus_null_mean"],
        "p_upper":calibration["p_null_ge_observed"],
        "p_lower":calibration["p_null_le_observed"],
        "supported":supported,
        "encounter_sha256":esha,
    },sort_keys=True))
    return 0


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--panel",required=True,choices=["hypsignathus","phyllostomus_2022","phyllostomus_2023","phyllostomus_2016"])
    args=ap.parse_args()
    return run(args.panel)

if __name__=="__main__":
    raise SystemExit(main())
