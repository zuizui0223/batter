#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_new_species_replications as core

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

geom=load_module("geom3d_v1",ROOT/"post_freeze_extensions/3d_niche_partition/run_v1.py")
ext=load_module("external_geom_v1",ROOT/"post_freeze_extensions/3d_niche_partition/run_external_geometry_v1.py")

CONTRACT=ROOT/"post_freeze_extensions/3d_niche_partition/original_terrain_geometry_contract_v1.json"
RECEIPT=ROOT/"post_freeze_extensions/3d_niche_partition/original_terrain_dem_preflight_receipt_v1.json"
NATIVE=ROOT/"post_freeze_extensions/3d_niche_partition/summary_v1.json"
OUTDIR=ROOT/"post_freeze_extensions/3d_niche_partition/original_terrain_results"
UA={"User-Agent":"batter-original-terrain-geometry-v1/1.0"}

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
    sessions,_=geom.build_session_distributions(panel)
    return {(c,s["session"]) for c,rows in sessions.items() for s in rows}


def load_panel_df(panel):
    contract=source_contract(panel)
    ua="batter-original-terrain-geometry-v1/1.0"
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
        x,y=transformers[cohort].transform(lon,lat)
        rec.append({
            "cohort":str(cohort),
            "iid":str(sm["individual"]),
            "session":str(sid),
            "x":float(x),
            "y":float(y),
            "lon":float(lon),
            "lat":float(lat),
            "native_h":float(h),
        })
        seen.add((cohort,sid))

    if seen!=targets:
        missing=sorted(targets-seen)
        extra=sorted(seen-targets)
        raise RuntimeError(f"{panel}: target-session mismatch missing={missing[:5]} extra={extra[:5]}")
    return pd.DataFrame(rec),contract


def parse_tile_sw(tile):
    lat=int(tile[1:3])*(1 if tile[0]=="N" else -1)
    lon=int(tile[4:7])*(1 if tile[3]=="E" else -1)
    return lat,lon


def tile_id(lat,lon):
    lat_sw=math.floor(float(lat)); lon_sw=math.floor(float(lon))
    return ("N" if lat_sw>=0 else "S")+f"{abs(lat_sw):02d}"+("E" if lon_sw>=0 else "W")+f"{abs(lon_sw):03d}"


def load_tiles(panel_receipt,void_value):
    grids={}
    for info in panel_receipt["tiles"]:
        rr=requests.get(info["url"],headers=UA,timeout=300)
        rr.raise_for_status()
        blob=rr.content
        if hashlib.sha256(blob).hexdigest()!=info["gzip_sha256"]:
            raise RuntimeError(f"{info['tile']}: gzip SHA mismatch")
        raw=gzip.decompress(blob)
        n=int(info["grid_n"])
        if len(raw)!=n*n*2:
            raise RuntimeError(f"{info['tile']}: uncompressed bytes {len(raw)} != {n*n*2}")
        arr=np.frombuffer(raw,dtype=">i2").reshape((n,n))
        grids[info["tile"]]=arr
    return grids


def bilinear_hgt(grids,lat,lon,void_value):
    tile=tile_id(lat,lon)
    if tile not in grids:
        raise RuntimeError(f"missing pinned tile {tile}")
    arr=grids[tile];n=arr.shape[0]
    lat0,lon0=parse_tile_sw(tile)
    row=(lat0+1.0-float(lat))*(n-1)
    col=(float(lon)-lon0)*(n-1)
    if not (0<=row<=n-1 and 0<=col<=n-1):
        raise RuntimeError(f"{tile}: point outside tile")
    r0=int(math.floor(row));c0=int(math.floor(col))
    r1=min(r0+1,n-1);c1=min(c0+1,n-1)
    vals=np.array([arr[r0,c0],arr[r0,c1],arr[r1,c0],arr[r1,c1]],dtype=float)
    if np.any(vals==void_value):
        raise RuntimeError(f"{tile}: DEM void touched")
    dr=row-r0;dc=col-c0
    v00,v01,v10,v11=vals
    return float(v00*(1-dr)*(1-dc)+v01*(1-dr)*dc+v10*dr*(1-dc)+v11*dr*dc)


def fast_panel_d(sessions_by_cohort,mats_by_cohort,labels_by_cohort,min_other=2):
    per_ind=defaultdict(list)
    for cohort,sessions in sessions_by_cohort.items():
        M=mats_by_cohort[cohort]["ozxy"]
        labels=labels_by_cohort[cohort]
        unique=sorted(set(labels.tolist()))
        finite=np.isfinite(M)
        M0=np.nan_to_num(M,nan=0.0)

        mean_by={}
        for lab in unique:
            mask=(labels==lab).astype(float)
            counts=finite @ mask
            sums=M0 @ mask
            a=np.full(len(labels),np.nan,dtype=float)
            ok=counts>0
            a[ok]=sums[ok]/counts[ok]
            mean_by[lab]=a

        for t,lab in enumerate(labels):
            selfv=mean_by[lab][t]
            if not np.isfinite(selfv):
                continue
            others=[]
            for olab in unique:
                if olab==lab:
                    continue
                v=mean_by[olab][t]
                if np.isfinite(v):
                    others.append(float(v))
            if len(others)<min_other:
                continue
            per_ind[str(lab)].append(float(selfv-np.mean(others)))

    vals=[]
    for iid,ds in per_ind.items():
        if ds:
            vals.append(float(np.mean(ds)))
    return (float(np.mean(vals)) if vals else None,len(vals))


def run(panel):
    cfg=json.loads(CONTRACT.read_text(encoding="utf-8"))
    receipt=json.loads(RECEIPT.read_text(encoding="utf-8"))
    native=json.loads(NATIVE.read_text(encoding="utf-8"))["panels"][panel]

    if receipt.get("status")!="DEM_MAY_OPEN":
        raise RuntimeError(f"receipt status {receipt.get('status')}")
    if hashlib.sha256(CONTRACT.read_bytes()).hexdigest()!=receipt["contract_sha256"]:
        raise RuntimeError("terrain contract SHA mismatch")

    df,source=load_panel_df(panel)
    prec=receipt["panels"][panel]
    if len(df)!=int(prec["coordinate_row_count"]):
        raise RuntimeError(f"{panel}: coordinate row count changed {len(df)} != {prec['coordinate_row_count']}")

    grids=load_tiles(prec,int(cfg["dem"]["void_value"]))
    terrain=np.array([bilinear_hgt(grids,lat,lon,int(cfg["dem"]["void_value"])) for lat,lon in zip(df["lat"],df["lon"])],dtype=float)
    if not np.isfinite(terrain).all():
        raise RuntimeError(f"{panel}: nonfinite DEM")
    df["h"]=df["native_h"].to_numpy(dtype=float)-terrain

    q=df[["cohort","iid","session","x","y","h"]].copy()
    sessions=ext.build_sessions(q,float(cfg["geometry"]["horizontal_grid_m"]),float(cfg["geometry"]["alpha"]))
    mats={}
    pair_counts={}
    for cohort,ss in sessions.items():
        mats[cohort],pair_counts[cohort]=ext.metric_matrices(ss,int(cfg["geometry"]["pair_common_support_min_fixes_each"]))

    labels={c:np.array([s["individual"] for s in ss],dtype=object) for c,ss in sessions.items()}
    observed,per_ind,rows=ext.evaluate_generic(sessions,mats,labels)

    H=float(observed["d_oxy"]) if observed["d_oxy"] is not None else None
    native_H=float(native["self_oxy"]-native["other_oxy"])
    if H is None or not np.isclose(H,native_H,rtol=0,atol=1e-12):
        raise RuntimeError(f"{panel}: horizontal geometry changed terrain H={H} native H={native_H}")

    gate=int(cfg["geometry"]["panel_min_evaluable_individuals"])
    structural=observed["eligible_individuals"]>=gate
    B=int(cfg["permutation"]["B"])
    seed=int(cfg["permutation"]["seeds"][panel])
    rng=np.random.default_rng(seed)
    null=[];null_s=[];null_n=[];invalid=0

    if structural:
        for _ in range(B):
            plabels={c:rng.permutation(v) for c,v in labels.items()}
            pobj,_,_=ext.evaluate_generic(sessions,mats,plabels)
            dv=pobj["d_ozxy"]
            n=int(pobj["eligible_individuals"])
            ps=(float(pobj["other_r3d"]-pobj["self_r3d"])
                if pobj["other_r3d"] is not None and pobj["self_r3d"] is not None else None)
            if dv is None or ps is None or n<gate:
                invalid+=1
                continue
            null.append(float(dv));null_s.append(float(ps));null_n.append(int(n))

    cal=ext.cal.tail_summary(null,float(observed["d_panel"])) if structural and null else None
    supported=bool(cal and cal["observed_minus_null_mean"]>0 and cal["p_null_ge_observed"]<=0.05)

    V=float(observed["d_ozxy"]) if observed["d_ozxy"] is not None else None
    S=float(observed["other_r3d"]-observed["self_r3d"]) if observed["other_r3d"] is not None else None
    native_V=float(native["d_panel"])
    native_S=float(native["other_r3d"]-native["self_r3d"])
    sarr=np.asarray(null_s,dtype=float)
    smean=float(np.mean(sarr)) if len(sarr) else None
    s_cal=None
    if len(sarr):
        dev=abs(S-smean)
        s_cal={
            "observed":S,
            "null_mean":smean,
            "null_q025":float(np.quantile(sarr,0.025)),
            "null_q50":float(np.quantile(sarr,0.5)),
            "null_q975":float(np.quantile(sarr,0.975)),
            "observed_minus_null_mean":float(S-smean),
            "p_two_sided_about_null_mean":float((1+np.sum(np.abs(sarr-smean)>=dev))/(len(sarr)+1)),
        }

    payload={
        "study_id":cfg["study_id"],
        "panel":panel,
        "classification":"secondary terrain-relative geometry diagnostic",
        "source_gps_md5":source["source"]["gps"]["md5"],
        "dem_tiles":prec["tiles"],
        "observed":{**observed,"individual_results":per_ind,"session_results":rows},
        "geometry":{"H":H,"V_rel":V,"S_rel":S},
        "native_comparison":{
            "H_native":native_H,
            "V_native":native_V,
            "S_native":native_S,
            "V_change":V-native_V if V is not None else None,
            "S_change":S-native_S if S is not None else None,
        },
        "terrain_summary_descriptive":{
            "min_m":float(np.min(terrain)),
            "median_m":float(np.median(terrain)),
            "max_m":float(np.max(terrain)),
        },
        "pair_counts":pair_counts,
        "permutation":{
            "B_requested":B,"seed":seed,
            "valid_replicates":len(null),"invalid_replicates":invalid,
            "eligible_individuals_null":{
                "mean":float(np.mean(null_n)) if null_n else None,
                "min":int(np.min(null_n)) if null_n else None,
                "max":int(np.max(null_n)) if null_n else None,
            },
            "primary_V_rel":cal,
            "secondary_S_rel":s_cal,
        },
        "decision":{"structural_gate_met":structural,"terrain_relative_supported":supported},
        "claim_boundary":[
            "terrain-relative proxy, not measured AGL",
            "ellipsoid-height sources retain unresolved spatial vertical-datum variation",
            "secondary diagnostic cannot overwrite native-space result",
            "does not identify competition or resource partitioning",
        ],
    }
    OUTDIR.mkdir(parents=True,exist_ok=True)
    out=OUTDIR/f"{panel}_terrain_geometry_result_v1.json"
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "panel":panel,
        "eligible_individuals":observed["eligible_individuals"],
        "H":H,
        "V_native":native_V,
        "V_rel":V,
        "S_native":native_S,
        "S_rel":S,
        "calibrated_excess":cal["observed_minus_null_mean"] if cal else None,
        "p_upper":cal["p_null_ge_observed"] if cal else None,
        "structural_gate":structural,
        "terrain_relative_supported":supported,
        "S_calibration":s_cal,
    },sort_keys=True))
    return 0


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--panel",required=True,choices=["hypsignathus","phyllostomus_2022","phyllostomus_2023","phyllostomus_2016"])
    args=ap.parse_args()
    run(args.panel)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
