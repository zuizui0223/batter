#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import requests

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

CONTRACT=ROOT/"post_freeze_extensions/3d_niche_partition/original_terrain_geometry_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/3d_niche_partition/original_terrain_dem_preflight_receipt_v1.json"
UA={"User-Agent":"batter-original-terrain-geometry-preflight-v1/1.0"}

CPATH={
    "hypsignathus":"contract/hypsignathus_replication_v1.json",
    "phyllostomus_2022":"contract/phyllostomus_replication_v1.json",
    "phyllostomus_2023":"contract/phyllostomus_2023_replication_v1.json",
    "phyllostomus_2016":"contract/phyllostomus_2016_dry_architecture_v1.json",
}


def tile_id(lat,lon):
    lat_sw=math.floor(float(lat)); lon_sw=math.floor(float(lon))
    lat_tag=("N" if lat_sw>=0 else "S")+f"{abs(lat_sw):02d}"
    lon_tag=("E" if lon_sw>=0 else "W")+f"{abs(lon_sw):03d}"
    return lat_tag+lon_tag


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


def source_coordinates(panel):
    contract=source_contract(panel)
    ua="batter-original-terrain-geometry-preflight-v1/1.0"
    gps=core.get(contract["source"]["gps"],ua)
    ref=core.get(contract["source"]["reference"],ua)
    rows,headers=core.read_csv(gps)
    refs,_=core.read_csv(ref)
    pre=core.build_pre_numeric(rows,headers,refs,contract)
    targets=target_sessions(panel)

    coords=[]
    coord_sessions=set()
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
        if lon is None or lat is None:
            continue
        coords.append((float(lat),float(lon)))
        coord_sessions.add((cohort,sid))

    if coord_sessions!=targets:
        missing=sorted(targets-coord_sessions)
        extra=sorted(coord_sessions-targets)
        raise RuntimeError(f"{panel}: target-session coordinate mismatch missing={missing[:5]} extra={extra[:5]}")
    return coords,targets,contract


def main():
    cfg=json.loads(CONTRACT.read_text(encoding="utf-8"))
    contract_sha=hashlib.sha256(CONTRACT.read_bytes()).hexdigest()
    panels={}
    all_tiles={}

    for panel in cfg["panels"]:
        coords,targets,contract=source_coordinates(panel)
        tiles=sorted({tile_id(lat,lon) for lat,lon in coords})
        if not tiles:
            raise RuntimeError(f"{panel}: no DEM tiles")

        entries=[]
        for tile in tiles:
            band=tile[:3]
            url=cfg["dem"]["url_template"].format(lat_band=band,tile=tile)
            rr=requests.get(url,headers=UA,timeout=300)
            rr.raise_for_status()
            blob=rr.content
            info={
                "tile":tile,
                "url":url,
                "gzip_bytes":len(blob),
                "gzip_sha256":hashlib.sha256(blob).hexdigest(),
                "grid_n":int(cfg["dem"]["grid_n"]),
                "decoded_elevation_values":False,
            }
            entries.append(info)
            if tile in all_tiles and all_tiles[tile]["gzip_sha256"]!=info["gzip_sha256"]:
                raise RuntimeError(f"tile checksum inconsistent {tile}")
            all_tiles[tile]=info

        panels[panel]={
            "target_session_count":len(targets),
            "coordinate_row_count":len(coords),
            "tile_count":len(entries),
            "tiles":entries,
            "source_gps_md5":contract["source"]["gps"]["md5"],
        }

    payload={
        "schema_version":1,
        "study_id":"batter-original-panel-terrain-3d-geometry-dem-preflight-v1",
        "status":"DEM_MAY_OPEN",
        "contract_sha256":contract_sha,
        "numeric_dem_elevation_values_decoded":False,
        "panels":panels,
        "unique_tiles":sorted(all_tiles.values(),key=lambda x:x["tile"]),
        "next_step":"Commit this receipt unchanged before any HGT tile is decoded into elevation values.",
    }
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":payload["status"],
        "panels":{p:{"sessions":x["target_session_count"],"rows":x["coordinate_row_count"],"tiles":[z["tile"] for z in x["tiles"]]} for p,x in panels.items()},
        "unique_tile_count":len(all_tiles),
        "contract_sha256":contract_sha,
        "numeric_dem_elevation_values_decoded":False,
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
