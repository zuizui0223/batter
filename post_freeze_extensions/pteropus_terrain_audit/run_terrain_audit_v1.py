#!/usr/bin/env python3
from __future__ import annotations

import gzip
import hashlib
import io
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from batter.analysis import Event, z_bin
import scripts.run_cross_panel_estimator_calibration as cal

CONTRACT = ROOT / "post_freeze_extensions/pteropus_terrain_audit/contract_v1.json"
DEM_RECEIPT = ROOT / "post_freeze_extensions/pteropus_terrain_audit/dem_preflight_receipt_v1.json"
SMALL_RECEIPT = ROOT / "post_freeze_extensions/small_panel_generality/height_opening_receipt_v1.json"
SMALL_PRIMARY = ROOT / "post_freeze_extensions/small_panel_generality/primary_result_v1.json"
OUT = ROOT / "post_freeze_extensions/pteropus_terrain_audit/terrain_audit_result_v1.json"
OUT_MD = ROOT / "post_freeze_extensions/pteropus_terrain_audit/TERRAIN_AUDIT_RESULT_V1.md"
UA = {"User-Agent": "batter-pteropus-terrain-audit-v1/1.0"}
EDGES = (-math.inf, -400.0, -200.0, -100.0, -50.0, 0.0, 50.0, 100.0, 200.0, 400.0, math.inf)
K = len(EDGES) - 1

def norm(x):
    return "_".join(str(x).strip().lower().replace("-", "_").replace(" ", "_").replace(".", "_").split("_"))

def present(s):
    txt = s.astype(str).str.strip()
    return s.notna() & txt.ne("") & ~txt.str.lower().isin({"na", "nan", "null", "none"})

def boolish(x):
    s = str(x).strip().lower()
    if s in {"true", "t", "1", "yes", "y"}: return True
    if s in {"false", "f", "0", "no", "n"}: return False
    return None

def tile_id(lat, lon):
    lat_sw = math.floor(float(lat)); lon_sw = math.floor(float(lon))
    lat_tag = ("N" if lat_sw >= 0 else "S") + f"{abs(lat_sw):02d}"
    lon_tag = ("E" if lon_sw >= 0 else "W") + f"{abs(lon_sw):03d}"
    return lat_tag + lon_tag

def parse_tile_sw(tile):
    lat = int(tile[1:3]) * (1 if tile[0] == "N" else -1)
    lon = int(tile[4:7]) * (1 if tile[3] == "E" else -1)
    return lat, lon

def load_hgt_tiles(receipt):
    grids = {}
    for info in receipt["dem_tiles"]:
        rr = requests.get(info["url"], headers=UA, timeout=300)
        rr.raise_for_status()
        blob = rr.content
        if hashlib.sha256(blob).hexdigest() != info["gzip_sha256"]:
            raise RuntimeError(f"{info['tile']}: DEM gzip SHA mismatch")
        raw = gzip.decompress(blob)
        if len(raw) != int(info["uncompressed_bytes"]):
            raise RuntimeError(f"{info['tile']}: DEM uncompressed byte count mismatch")
        n = int(info["grid_n"])
        grids[info["tile"]] = np.frombuffer(raw, dtype=">i2").reshape((n, n))
    return grids

def bilinear_hgt(grids, lat, lon, void_value=-32768):
    tile = tile_id(lat, lon)
    if tile not in grids:
        raise RuntimeError(f"no pinned DEM tile for {lat},{lon} -> {tile}")
    arr = grids[tile]; n = arr.shape[0]
    lat0, lon0 = parse_tile_sw(tile)
    row = (lat0 + 1.0 - float(lat)) * (n - 1)
    col = (float(lon) - lon0) * (n - 1)
    if not (0 <= row <= n - 1 and 0 <= col <= n - 1):
        raise RuntimeError(f"{tile}: coordinate outside tile row={row} col={col}")
    r0 = int(math.floor(row)); c0 = int(math.floor(col))
    r1 = min(r0 + 1, n - 1); c1 = min(c0 + 1, n - 1)
    vals = np.array([arr[r0, c0], arr[r0, c1], arr[r1, c0], arr[r1, c1]], dtype=float)
    if np.any(vals == void_value):
        raise RuntimeError(f"{tile}: DEM void touched by interpolation at lat={lat} lon={lon}")
    dr = row - r0; dc = col - c0
    v00, v01, v10, v11 = vals
    return v00*(1-dr)*(1-dc) + v01*(1-dr)*dc + v10*dr*(1-dc) + v11*dr*dc

def load_source(c, small_rec):
    src = c["source"]
    rr = requests.get(src["event_url"], headers=UA, timeout=300)
    rr.raise_for_status()
    raw = rr.content
    sha = hashlib.sha256(raw).hexdigest()
    if sha != src["raw_sha256"]:
        raise RuntimeError("source raw SHA mismatch")

    hdr = pd.read_csv(io.BytesIO(raw), nrows=0)
    cmap = {norm(x): x for x in hdr.columns}
    hnorm = norm(src["native_vertical_field"])
    req = ["timestamp", "location_long", "location_lat", "individual_local_identifier", hnorm]
    missing = [x for x in req if x not in cmap]
    if missing: raise RuntimeError(f"missing source fields {missing}")
    use = [cmap[x] for x in req]
    for q in ["visible", "algorithm_marked_outlier", "manually_marked_outlier", "import_marked_outlier"]:
        if q in cmap: use.append(cmap[q])
    use = list(dict.fromkeys(use))
    df = pd.read_csv(io.BytesIO(raw), dtype=str, usecols=use, low_memory=False)

    tcol = cmap["timestamp"]; loncol = cmap["location_long"]; latcol = cmap["location_lat"]
    iidcol = cmap["individual_local_identifier"]; hcol = cmap[hnorm]
    mask = present(df[tcol]) & present(df[loncol]) & present(df[latcol]) & present(df[iidcol]) & present(df[hcol])
    d = df.loc[mask].copy()

    if "visible" in cmap and cmap["visible"] in d:
        keep = []
        for x in d[cmap["visible"]]:
            b = boolish(x); keep.append(True if b is None else b)
        d = d.loc[keep].copy()
    for q in ["algorithm_marked_outlier", "manually_marked_outlier", "import_marked_outlier"]:
        if q in cmap and cmap[q] in d:
            keep = []
            for x in d[cmap[q]]:
                b = boolish(x); keep.append(True if b is None else (not b))
            d = d.loc[keep].copy()

    d["iid"] = d[iidcol].astype(str).str.strip()
    d["t"] = pd.to_datetime(d[tcol], errors="coerce", utc=True, format="mixed")
    d["lon"] = pd.to_numeric(d[loncol], errors="coerce")
    d["lat"] = pd.to_numeric(d[latcol], errors="coerce")
    d["height_msl"] = pd.to_numeric(d[hcol], errors="coerce")
    bad = d["t"].isna() | d["lon"].isna() | d["lat"].isna() | d["height_msl"].isna()
    d = d.loc[~bad].sort_values(["iid", "t"]).copy()
    if not np.isfinite(d["height_msl"].to_numpy(dtype=float)).all():
        raise RuntimeError("nonfinite source MSL height")

    d["sess_num"] = -1
    for iid, g in d.groupby("iid", sort=True):
        vals=[]; k=0; prev=None
        for t in g["t"]:
            if prev is not None and (t-prev) > pd.Timedelta(hours=4): k += 1
            vals.append(k); prev=t
        d.loc[g.index, "sess_num"] = vals
    d["session"] = d["iid"] + "::" + d["sess_num"].astype(int).astype(str)
    frozen = {z["session"] for rows in small_rec["training_sessions"].values() for z in rows}
    d = d[d["session"].isin(frozen)].copy()
    if set(d["session"].unique()) != frozen:
        raise RuntimeError("frozen source session set mismatch")

    tr = Transformer.from_crs("EPSG:4326", f"EPSG:{int(c['source']['projection_epsg'])}", always_xy=True)
    e, n = tr.transform(d["lon"].to_numpy(dtype=float), d["lat"].to_numpy(dtype=float))
    d["cx"] = np.floor(np.asarray(e)/5000.0).astype(int)
    d["cy"] = np.floor(np.asarray(n)/5000.0).astype(int)
    return d, sha

def make_events(d, column):
    med = d.groupby("session")[column].transform("median")
    resid = d[column] - med
    events=[]
    for iid,t,cx,cy,z,session in zip(d["iid"],d["t"],d["cx"],d["cy"],resid,d["session"]):
        events.append(Event(individual=str(iid),timestamp=t.to_pydatetime(),cell=(int(cx),int(cy)),zbin=z_bin(float(z),edges=EDGES),session=str(session)))
    return events

def validate_session_support(session_rows, small_rec):
    frozen={}
    for iid,rows in small_rec["frozen_vertical_target_sessions"].items():
        for x in rows: frozen[str(x["session"])] = int(x["supported_events"])
    got={str(x["session"]):int(x["scored_fixes"]) for x in session_rows}
    if set(got) != set(frozen): raise RuntimeError("target-session set changed under terrain audit")
    bad={s:(got[s],frozen[s]) for s in frozen if got[s] != frozen[s]}
    if bad: raise RuntimeError(f"target supported-event counts changed: {list(bad.items())[:5]}")

def observed_only(events):
    arrays={"pteropus_poliocephalus_5bd6pq55":cal.make_cohort_arrays(events,K)}
    observed,per_ind,session_rows=cal.observed_eval(arrays)
    return arrays,observed,per_ind,session_rows

def calibrated_test(events,B,seed):
    arrays,observed,per_ind,session_rows=observed_only(events)
    if int(observed["eligible_individuals"]) != 4:
        raise RuntimeError(f"eligible individuals changed: {observed['eligible_individuals']}")
    metric="common_cell_marginal"; obs=float(observed[metric])
    rng=np.random.default_rng(int(seed)); null=[]; elig=[]; invalid=0
    for _ in range(int(B)):
        p=cal.perm_eval(arrays,rng)
        if p["eligible_individuals"] < 1 or p[metric] is None:
            invalid += 1; continue
        null.append(float(p[metric])); elig.append(int(p["eligible_individuals"]))
    if not null: raise RuntimeError("no valid permutation replicates")
    summ=cal.tail_summary(null,obs)
    passed=summ["observed_minus_null_mean"] > 0 and summ["p_null_ge_observed"] <= 0.05
    return {
        "observed":observed,"individual_results":per_ind,"session_results":session_rows,
        "permutation":{"B":int(B),"seed":int(seed),"valid_replicates":len(null),"invalid_replicates":invalid,
        "eligible_individual_count":{"observed":4,"min":int(min(elig)),"max":int(max(elig)),"mean":float(np.mean(elig))},
        "calibration":summ},
        "pass":bool(passed)
    }

def main():
    c=json.loads(CONTRACT.read_text())
    dem_rec=json.loads(DEM_RECEIPT.read_text())
    small=json.loads(SMALL_RECEIPT.read_text())
    small_primary=json.loads(SMALL_PRIMARY.read_text())
    srcid=c["source"]["source_id"]; small_rec=small["sources"][srcid]; pinned=small_primary["sources"][srcid]

    if dem_rec.get("status") != "DEM_MAY_OPEN":
        raise RuntimeError(f"DEM receipt status {dem_rec.get('status')} prohibits opening")
    if hashlib.sha256(CONTRACT.read_bytes()).hexdigest() != dem_rec["contract_sha256"]:
        raise RuntimeError("terrain contract SHA differs from frozen DEM receipt")

    d,source_sha=load_source(c,small_rec)
    if int(len(d)) != int(dem_rec["frozen_event_universe"]["retained_rows"]):
        raise RuntimeError("retained source rows changed since DEM preflight")

    grids=load_hgt_tiles(dem_rec)
    terrain=np.array([bilinear_hgt(grids,lat,lon,int(c["terrain_sampling"]["void_value"])) for lat,lon in zip(d["lat"],d["lon"])],dtype=float)
    if not np.isfinite(terrain).all(): raise RuntimeError("nonfinite terrain values after interpolation")
    d["terrain_m"]=terrain
    d["agl_proxy_m"]=d["height_msl"].to_numpy(dtype=float)-terrain

    msl_events=make_events(d,"height_msl")
    _,msl_observed,_,msl_sessions=observed_only(msl_events)
    validate_session_support(msl_sessions,small_rec)
    pinned_obs=float(pinned["observed"]["common_cell_marginal"])
    if not math.isclose(float(msl_observed["common_cell_marginal"]),pinned_obs,rel_tol=0.0,abs_tol=1e-12):
        raise RuntimeError(f"MSL reproduction failed: {msl_observed['common_cell_marginal']} != {pinned_obs}")

    agl=calibrated_test(make_events(d,"agl_proxy_m"),c["primary_audit"]["B"],c["primary_audit"]["seed"])
    terrain_test=calibrated_test(make_events(d,"terrain_m"),c["terrain_pathway_diagnostic"]["B"],c["terrain_pathway_diagnostic"]["seed"])
    validate_session_support(agl["session_results"],small_rec)
    validate_session_support(terrain_test["session_results"],small_rec)

    a_pass=bool(agl["pass"]); t_pass=bool(terrain_test["pass"])
    key=f"agl_{'PASS' if a_pass else 'FAIL'}__terrain_{'PASS' if t_pass else 'FAIL'}"
    interpretation=c["interpretation_matrix"][key]
    original_cal=pinned["permutation"]["calibration"]
    agl_cal=agl["permutation"]["calibration"]
    terrain_cal=terrain_test["permutation"]["calibration"]
    ratio=float(agl_cal["observed_minus_null_mean"])/float(original_cal["observed_minus_null_mean"])

    payload={
        "schema_version":1,
        "study_id":"batter-pteropus-terrain-confound-audit-result-v1",
        "classification":c["relationship_to_previous_result"]["classification"],
        "contract_sha256":dem_rec["contract_sha256"],
        "source_raw_sha256":source_sha,
        "dem_receipt":{"tile_count":dem_rec["tile_count"],"tiles":dem_rec["dem_tiles"]},
        "terrain_summary_descriptive":{"min_m":float(np.min(terrain)),"median_m":float(np.median(terrain)),"max_m":float(np.max(terrain))},
        "original_pinned_centered_msl":{"observed":pinned_obs,"calibration":original_cal,"primary_pass":bool(pinned["primary_pass"]),"reproduced_observed_exactly":True},
        "terrain_adjusted_agl_proxy":agl,
        "terrain_only_pathway":terrain_test,
        "descriptive_attenuation":{"agl_to_original_calibrated_excess_ratio":ratio,"original_excess":float(original_cal["observed_minus_null_mean"]),"agl_excess":float(agl_cal["observed_minus_null_mean"])},
        "decision":{"terrain_robust":a_pass,"terrain_pathway_supported":t_pass,"matrix_key":key,"interpretation":interpretation},
        "claim_boundary":c["reporting"]["prohibited"]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    lines=[
      "# Pteropus terrain-confound audit result v1","",
      "**Classification:** post-outcome confound diagnostic; it does not alter the historical prospective MSL verdict.","",
      "| endpoint | observed | null mean | calibrated excess | p(null>=obs) | verdict |",
      "|---|---:|---:|---:|---:|---|",
      f"| original centered MSL (pinned) | {float(original_cal['observed']):+.5f} | {float(original_cal['mean']):+.5f} | {float(original_cal['observed_minus_null_mean']):+.5f} | {float(original_cal['p_null_ge_observed']):.4f} | {'PASS' if pinned['primary_pass'] else 'FAIL'} |",
      f"| centered MSL - DEM | {float(agl_cal['observed']):+.5f} | {float(agl_cal['mean']):+.5f} | {float(agl_cal['observed_minus_null_mean']):+.5f} | {float(agl_cal['p_null_ge_observed']):.4f} | {'PASS' if a_pass else 'FAIL'} |",
      f"| centered DEM terrain | {float(terrain_cal['observed']):+.5f} | {float(terrain_cal['mean']):+.5f} | {float(terrain_cal['observed_minus_null_mean']):+.5f} | {float(terrain_cal['p_null_ge_observed']):.4f} | {'PASS' if t_pass else 'FAIL'} |","",
      f"Terrain-adjusted/original calibrated-excess ratio (descriptive): **{ratio:.3f}**.","",
      f"Frozen interpretation: **{interpretation}**","",
      "The DEM subtraction is a terrain-relative proxy, not a source-measured AGL endpoint. All four individuals, the original session universe, 5-km cells, centered bins and support rules were retained.",""
    ]
    OUT_MD.write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps({"msl_observed_reproduced":float(msl_observed["common_cell_marginal"]),"agl_excess":float(agl_cal["observed_minus_null_mean"]),"agl_p":float(agl_cal["p_null_ge_observed"]),"agl_pass":a_pass,"terrain_excess":float(terrain_cal["observed_minus_null_mean"]),"terrain_p":float(terrain_cal["p_null_ge_observed"]),"terrain_pass":t_pass,"ratio":ratio,"matrix_key":key},sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
