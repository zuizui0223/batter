#!/usr/bin/env python3
from __future__ import annotations

import gzip
import hashlib
import io
import json
import math
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "post_freeze_extensions/pteropus_terrain_audit/contract_v1.json"
SMALL_RECEIPT = ROOT / "post_freeze_extensions/small_panel_generality/height_opening_receipt_v1.json"
OUT = ROOT / "post_freeze_extensions/pteropus_terrain_audit/dem_preflight_receipt_v1.json"
UA = {"User-Agent": "batter-pteropus-terrain-preflight-v1/1.0"}

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
    lat_sw = math.floor(float(lat))
    lon_sw = math.floor(float(lon))
    lat_tag = ("N" if lat_sw >= 0 else "S") + f"{abs(lat_sw):02d}"
    lon_tag = ("E" if lon_sw >= 0 else "W") + f"{abs(lon_sw):03d}"
    return lat_tag + lon_tag

def tile_url(template, tile):
    return template.format(lat_dir=tile[0], lat_abs2=tile[1:3], tile=tile)

def read_source(c, rec):
    src = c["source"]
    r = requests.get(src["event_url"], headers=UA, timeout=300)
    r.raise_for_status()
    raw = r.content
    sha = hashlib.sha256(raw).hexdigest()
    if sha != src["raw_sha256"]:
        raise RuntimeError(f"source raw SHA mismatch: {sha}")

    hdr = pd.read_csv(io.BytesIO(raw), nrows=0)
    cmap = {norm(x): x for x in hdr.columns}
    hnorm = norm(src["native_vertical_field"])
    req = ["timestamp", "location_long", "location_lat", "individual_local_identifier", hnorm]
    missing = [x for x in req if x not in cmap]
    if missing: raise RuntimeError(f"missing fields {missing}")

    use = [cmap[x] for x in req]
    for q in ["visible", "algorithm_marked_outlier", "manually_marked_outlier", "import_marked_outlier"]:
        if q in cmap: use.append(cmap[q])
    use = list(dict.fromkeys(use))
    df = pd.read_csv(io.BytesIO(raw), dtype=str, usecols=use, low_memory=False)

    tcol = cmap["timestamp"]; loncol = cmap["location_long"]; latcol = cmap["location_lat"]
    iidcol = cmap["individual_local_identifier"]; hcol = cmap[hnorm]

    # Vertical magnitude remains unopened here: presence/nonblank only.
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
    d = d.loc[~(d["t"].isna() | d["lon"].isna() | d["lat"].isna())].sort_values(["iid", "t"]).copy()

    d["sess_num"] = -1
    for iid, g in d.groupby("iid", sort=True):
        vals = []; k = 0; prev = None
        for t in g["t"]:
            if prev is not None and (t - prev) > pd.Timedelta(hours=4): k += 1
            vals.append(k); prev = t
        d.loc[g.index, "sess_num"] = vals
    d["session"] = d["iid"] + "::" + d["sess_num"].astype(int).astype(str)

    frozen = {z["session"] for rows in rec["training_sessions"].values() for z in rows}
    d = d[d["session"].isin(frozen)].copy()
    got = set(d["session"].unique())
    if got != frozen:
        raise RuntimeError(f"frozen session mismatch missing={sorted(frozen-got)[:10]} extra={sorted(got-frozen)[:10]}")
    return raw, sha, d

def validate_hgt_gzip(blob, tile):
    gz_sha = hashlib.sha256(blob).hexdigest()
    raw = gzip.decompress(blob)
    if len(raw) % 2: raise RuntimeError(f"{tile}: HGT byte count not divisible by 2")
    samples = len(raw) // 2
    n = math.isqrt(samples)
    if n * n != samples or n not in {1201, 3601}:
        raise RuntimeError(f"{tile}: unexpected HGT grid shape bytes={len(raw)} n={n}")
    return {
        "tile": tile,
        "gzip_bytes": len(blob),
        "gzip_sha256": gz_sha,
        "uncompressed_bytes": len(raw),
        "grid_n": n,
        "decoded_elevation_values": False
    }

def main():
    c = json.loads(CONTRACT.read_text())
    small = json.loads(SMALL_RECEIPT.read_text())
    rec = small["sources"][c["source"]["source_id"]]
    raw, source_sha, d = read_source(c, rec)

    tiles = sorted({tile_id(lat, lon) for lat, lon in zip(d["lat"], d["lon"])})
    rows = []
    for tile in tiles:
        url = tile_url(c["dem_preflight"]["url_template"], tile)
        rr = requests.get(url, headers=UA, timeout=300)
        rr.raise_for_status()
        info = validate_hgt_gzip(rr.content, tile)
        info["url"] = url
        rows.append(info)

    payload = {
        "schema_version": 1,
        "study_id": "batter-pteropus-terrain-dem-preflight-v1",
        "status": "DEM_MAY_OPEN",
        "contract_sha256": hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
        "source_raw_sha256": source_sha,
        "source_bytes": len(raw),
        "source_numeric_vertical_opened_by_this_script": False,
        "dem_elevation_values_decoded_by_this_script": False,
        "frozen_event_universe": {
            "retained_rows": int(len(d)),
            "individuals": sorted(d["iid"].unique().tolist()),
            "session_count": int(d["session"].nunique()),
            "lon_min": float(d["lon"].min()), "lon_max": float(d["lon"].max()),
            "lat_min": float(d["lat"].min()), "lat_max": float(d["lat"].max())
        },
        "dem_tiles": rows,
        "tile_count": len(rows),
        "claim_boundary": [
            "This receipt pins only DEM source bitstreams and coordinate coverage.",
            "No DEM elevation value is decoded and no terrain-adjusted outcome is computed here.",
            "Terrain audit may proceed only if status is DEM_MAY_OPEN and the contract SHA matches."
        ]
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "retained_rows": payload["frozen_event_universe"]["retained_rows"],
        "session_count": payload["frozen_event_universe"]["session_count"],
        "tiles": [{"tile": x["tile"], "grid_n": x["grid_n"], "gzip_sha256": x["gzip_sha256"]} for x in rows]
    }, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
