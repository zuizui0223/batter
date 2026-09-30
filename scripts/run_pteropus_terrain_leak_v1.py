#!/usr/bin/env python3
from __future__ import annotations

import gzip
import hashlib
import io
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from batter.analysis import Event, z_bin
import scripts.run_cross_panel_estimator_calibration as cal

CONTRACT = ROOT / "post_freeze_extensions/PTEROPUS_TERRAIN_LEAK_CONTRACT_V1.md"
RECEIPT = ROOT / "post_freeze_extensions/small_panel_generality/height_opening_receipt_v1.json"
SMALL_RESULT = ROOT / "post_freeze_extensions/small_panel_generality/primary_result_v1.json"
OUT_JSON = ROOT / "post_freeze_extensions/PTEROPUS_TERRAIN_LEAK_RESULT_V1.json"
OUT_MD = ROOT / "post_freeze_extensions/PTEROPUS_TERRAIN_LEAK_RESULT_V1.md"

SOURCE_URL = "https://datarepository.movebank.org/server/api/core/bitstreams/792122ca-c534-4607-81d4-1154cb7a5196/content"
EXPECTED_SOURCE_SHA256 = "13829a97110f3eff191c9066fd5bf7d20f5d1c7e26e152e6c733079fb4e179dc"
SOURCE_ID = "pteropus_poliocephalus_5bd6pq55"
EDGES = (-math.inf, -400.0, -200.0, -100.0, -50.0, 0.0, 50.0, 100.0, 200.0, 400.0, math.inf)
K = len(EDGES) - 1
GRID_M = 5000.0
MIN_TARGET = 50
UA = {"User-Agent": "batter-pteropus-terrain-leak-v1/1.0"}

MSL_B = 9999
MSL_SEED = 20260930162
TERRAIN_REL_B = 9999
TERRAIN_REL_SEED = 20261001071
TERRAIN_ONLY_B = 9999
TERRAIN_ONLY_SEED = 20261001072

def norm(x: str) -> str:
    return "_".join(str(x).strip().lower().replace("-", "_").replace(" ", "_").replace(".", "_").split("_"))

def present(s: pd.Series) -> pd.Series:
    txt = s.astype(str).str.strip()
    return s.notna() & txt.ne("") & ~txt.str.lower().isin({"na","nan","null","none"})

def boolish(x):
    s = str(x).strip().lower()
    if s in {"true","t","1","yes","y"}: return True
    if s in {"false","f","0","no","n"}: return False
    return None

def download_bytes(url: str, timeout=300) -> bytes:
    r = requests.get(url, headers=UA, timeout=timeout)
    r.raise_for_status()
    return r.content

def frozen_session_set(receipt: dict) -> set[str]:
    src = receipt["sources"][SOURCE_ID]
    return {
        str(z["session"])
        for rows in src["training_sessions"].values()
        for z in rows
    }

def frozen_target_counts(receipt: dict) -> dict[str, int]:
    src = receipt["sources"][SOURCE_ID]
    out = {}
    for rows in src["frozen_vertical_target_sessions"].values():
        for x in rows:
            out[str(x["session"])] = int(x["supported_events"])
    return out

def load_source(receipt: dict) -> tuple[pd.DataFrame, dict]:
    raw = download_bytes(SOURCE_URL)
    sha = hashlib.sha256(raw).hexdigest()
    if sha != EXPECTED_SOURCE_SHA256:
        raise RuntimeError(f"source SHA mismatch {sha}")

    hdr = pd.read_csv(io.BytesIO(raw), nrows=0)
    cmap = {norm(c): c for c in hdr.columns}
    required = ["timestamp","location_long","location_lat","individual_local_identifier","height_above_msl"]
    missing = [q for q in required if q not in cmap]
    if missing:
        raise RuntimeError(f"missing fields {missing}")

    use = [cmap[q] for q in required]
    for q in ["visible","algorithm_marked_outlier","manually_marked_outlier","import_marked_outlier"]:
        if q in cmap:
            use.append(cmap[q])
    use = list(dict.fromkeys(use))
    d = pd.read_csv(io.BytesIO(raw), dtype=str, usecols=use, low_memory=False)

    tcol, loncol, latcol = cmap["timestamp"], cmap["location_long"], cmap["location_lat"]
    iidcol, hcol = cmap["individual_local_identifier"], cmap["height_above_msl"]

    mask = present(d[tcol]) & present(d[loncol]) & present(d[latcol]) & present(d[iidcol]) & present(d[hcol])
    d = d.loc[mask].copy()

    if "visible" in cmap and cmap["visible"] in d:
        keep = []
        for x in d[cmap["visible"]]:
            b = boolish(x)
            keep.append(True if b is None else b)
        d = d.loc[keep].copy()

    for q in ["algorithm_marked_outlier","manually_marked_outlier","import_marked_outlier"]:
        if q in cmap and cmap[q] in d:
            keep = []
            for x in d[cmap[q]]:
                b = boolish(x)
                keep.append(True if b is None else (not b))
            d = d.loc[keep].copy()

    d["iid"] = d[iidcol].astype(str).str.strip()
    d["t"] = pd.to_datetime(d[tcol], errors="coerce", utc=True, format="mixed")
    d["lon"] = pd.to_numeric(d[loncol], errors="coerce")
    d["lat"] = pd.to_numeric(d[latcol], errors="coerce")
    d["height_msl"] = pd.to_numeric(d[hcol], errors="coerce")

    bad = d[["t","lon","lat","height_msl"]].isna().any(axis=1)
    d = d.loc[~bad].sort_values(["iid","t"]).copy()
    for c in ["lon","lat","height_msl"]:
        if not np.isfinite(d[c].to_numpy(dtype=float)).all():
            raise RuntimeError(f"nonfinite source column {c}")

    d["sess_num"] = -1
    for iid, g in d.groupby("iid", sort=True):
        vals, k, prev = [], 0, None
        for t in g["t"]:
            if prev is not None and (t-prev) > pd.Timedelta(hours=4):
                k += 1
            vals.append(k)
            prev = t
        d.loc[g.index, "sess_num"] = vals
    d["session"] = d["iid"] + "::" + d["sess_num"].astype(int).astype(str)

    frozen = frozen_session_set(receipt)
    d = d[d["session"].isin(frozen)].copy()
    if set(d["session"].unique()) != frozen:
        raise RuntimeError("frozen session universe mismatch")

    epsg = int(receipt["sources"][SOURCE_ID]["projection_epsg"])
    tr = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)
    e, n = tr.transform(d["lon"].to_numpy(float), d["lat"].to_numpy(float))
    d["cx"] = np.floor(np.asarray(e) / GRID_M).astype(int)
    d["cy"] = np.floor(np.asarray(n) / GRID_M).astype(int)

    return d, {
        "source_url": SOURCE_URL,
        "raw_sha256": sha,
        "rows_after_frozen_filters": int(len(d)),
        "frozen_sessions": int(d["session"].nunique()),
        "frozen_individuals": sorted(d["iid"].unique().tolist()),
        "projection_epsg": epsg,
    }

def tile_name(lat: float, lon: float) -> tuple[str, str]:
    south = math.floor(lat)
    west = math.floor(lon)
    ns = "N" if south >= 0 else "S"
    ew = "E" if west >= 0 else "W"
    latpart = f"{ns}{abs(south):02d}"
    tile = f"{latpart}{ew}{abs(west):03d}"
    return latpart, tile

class HGTStore:
    def __init__(self):
        self.arrays = {}
        self.meta = {}

    def load(self, lat: float, lon: float):
        latpart, tile = tile_name(lat, lon)
        if tile in self.arrays:
            return tile, self.arrays[tile]

        url = f"https://s3.amazonaws.com/elevation-tiles-prod/skadi/{latpart}/{tile}.hgt.gz"
        gz = download_bytes(url)
        raw = gzip.decompress(gz)
        n = int(round(math.sqrt(len(raw) / 2)))
        if n * n * 2 != len(raw) or n < 2:
            raise RuntimeError(f"invalid HGT tile size for {tile}: {len(raw)} bytes")
        arr = np.frombuffer(raw, dtype=">i2").reshape((n,n))
        self.arrays[tile] = arr
        self.meta[tile] = {
            "url": url,
            "gzip_bytes": len(gz),
            "raw_bytes": len(raw),
            "gzip_sha256": hashlib.sha256(gz).hexdigest(),
            "raw_sha256": hashlib.sha256(raw).hexdigest(),
            "samples_per_side": n,
        }
        return tile, arr

    @staticmethod
    def nearest_finite(arr, row: int, col: int):
        n = arr.shape[0]
        for radius in range(0,4):
            r0, r1 = max(0,row-radius), min(n-1,row+radius)
            c0, c1 = max(0,col-radius), min(n-1,col+radius)
            best = None
            bestd = None
            for rr in range(r0,r1+1):
                for cc in range(c0,c1+1):
                    v = int(arr[rr,cc])
                    if v == -32768:
                        continue
                    dd = (rr-row)**2 + (cc-col)**2
                    if bestd is None or dd < bestd:
                        bestd, best = dd, float(v)
            if best is not None:
                return best
        raise RuntimeError("no finite terrain sample in frozen 7x7 window")

    def elevation(self, lat: float, lon: float) -> float:
        _, tile = tile_name(lat, lon)
        south = math.floor(lat)
        west = math.floor(lon)
        _, arr = self.load(lat, lon)
        n = arr.shape[0]
        intervals = n - 1

        # HGT rows run north -> south; columns west -> east.
        x = (lon - west) * intervals
        y = ((south + 1) - lat) * intervals
        x = min(max(x, 0.0), float(intervals))
        y = min(max(y, 0.0), float(intervals))
        c0 = int(math.floor(x)); r0 = int(math.floor(y))
        c1 = min(c0 + 1, intervals); r1 = min(r0 + 1, intervals)
        dx = x - c0; dy = y - r0

        vals = [int(arr[r0,c0]), int(arr[r0,c1]), int(arr[r1,c0]), int(arr[r1,c1])]
        if any(v == -32768 for v in vals):
            return self.nearest_finite(arr, int(round(y)), int(round(x)))

        v00, v01, v10, v11 = map(float, vals)
        top = v00 * (1-dx) + v01 * dx
        bot = v10 * (1-dx) + v11 * dx
        return top * (1-dy) + bot * dy

def add_terrain(d: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    store = HGTStore()
    # Cache repeated coordinate pairs; GPS data often repeat exact fixes.
    cache = {}
    terr = np.empty(len(d), dtype=float)
    for j, (lat, lon) in enumerate(zip(d["lat"].to_numpy(float), d["lon"].to_numpy(float))):
        key = (float(lat), float(lon))
        if key not in cache:
            cache[key] = store.elevation(*key)
        terr[j] = cache[key]
    if not np.isfinite(terr).all():
        raise RuntimeError("nonfinite terrain after frozen void handling")
    d = d.copy()
    d["terrain_m"] = terr
    d["terrain_relative"] = d["height_msl"].to_numpy(float) - terr
    return d, {
        "tile_count": len(store.meta),
        "tiles": store.meta,
        "unique_coordinate_pairs": len(cache),
        "terrain_min_m": float(np.min(terr)),
        "terrain_median_m": float(np.median(terr)),
        "terrain_max_m": float(np.max(terr)),
    }

def events_from_response(d: pd.DataFrame, response_col: str) -> list[Event]:
    x = d.copy()
    med = x.groupby("session")[response_col].transform("median")
    x["centered_response"] = x[response_col].to_numpy(float) - med.to_numpy(float)
    out = []
    for row in x.itertuples(index=False):
        out.append(Event(
            individual=str(row.iid),
            timestamp=row.t.to_pydatetime(),
            cell=(int(row.cx), int(row.cy)),
            zbin=z_bin(float(row.centered_response), edges=EDGES),
            session=str(row.session),
        ))
    return out

def validate_targets(session_rows, receipt: dict):
    frozen = frozen_target_counts(receipt)
    got = {str(x["session"]): int(x["scored_fixes"]) for x in session_rows}
    if set(got) != set(frozen):
        raise RuntimeError(
            f"target session mismatch missing={sorted(set(frozen)-set(got))[:10]} "
            f"extra={sorted(set(got)-set(frozen))[:10]}"
        )
    for sid, expected in frozen.items():
        if got[sid] != expected:
            raise RuntimeError(f"supported-event mismatch {sid}: {got[sid]} != {expected}")

def evaluate(events: list[Event], B: int, seed: int, receipt: dict) -> dict:
    arrays = {SOURCE_ID: cal.make_cohort_arrays(events, K)}
    observed, per_ind, session_rows = cal.observed_eval(arrays)
    if int(observed["eligible_individuals"]) != 4:
        raise RuntimeError(f"eligible individuals changed: {observed['eligible_individuals']}")
    validate_targets(session_rows, receipt)

    metric = "common_cell_marginal"
    obs = float(observed[metric])
    rng = np.random.default_rng(seed)
    null, eligible = [], []
    invalid = 0
    for _ in range(B):
        p = cal.perm_eval(arrays, rng)
        if p["eligible_individuals"] < 1 or p[metric] is None:
            invalid += 1
            continue
        null.append(float(p[metric]))
        eligible.append(int(p["eligible_individuals"]))
    if not null:
        raise RuntimeError("no valid null replicates")
    summ = cal.tail_summary(null, obs)
    return {
        "observed": observed,
        "individual_results": per_ind,
        "session_results": session_rows,
        "B": B,
        "seed": seed,
        "valid_null_replicates": len(null),
        "invalid_null_replicates": invalid,
        "eligible_null_min": int(min(eligible)),
        "eligible_null_max": int(max(eligible)),
        "calibration": summ,
        "pass": bool(summ["observed_minus_null_mean"] > 0 and summ["p_null_ge_observed"] <= 0.05),
    }

def main():
    receipt = json.loads(RECEIPT.read_text())
    old = json.loads(SMALL_RESULT.read_text())
    d, source_meta = load_source(receipt)

    # Hard-gated replay of the already-opened native MSL centered result.
    msl = evaluate(events_from_response(d, "height_msl"), MSL_B, MSL_SEED, receipt)
    oldcal = old["sources"][SOURCE_ID]["permutation"]["calibration"]
    replay_ok = (
        abs(float(msl["calibration"]["observed_minus_null_mean"]) - float(oldcal["observed_minus_null_mean"])) <= 1e-10
        and abs(float(msl["calibration"]["p_null_ge_observed"]) - float(oldcal["p_null_ge_observed"])) <= 1e-12
        and int(msl["observed"]["eligible_individuals"]) == 4
    )
    if not replay_ok:
        raise RuntimeError(
            "hard STOP: original MSL-centered result did not replay exactly; "
            f"new={msl['calibration']} old={oldcal}"
        )

    d, terrain_meta = add_terrain(d)

    terrain_rel = evaluate(events_from_response(d, "terrain_relative"), TERRAIN_REL_B, TERRAIN_REL_SEED, receipt)
    terrain_only = evaluate(events_from_response(d, "terrain_m"), TERRAIN_ONLY_B, TERRAIN_ONLY_SEED, receipt)

    pr = terrain_rel["pass"]
    pt = terrain_only["pass"]
    if pr and not pt:
        label = "ROBUST_NO_TERRAIN_ONLY_SIGNAL"
        interpretation = (
            "Pteropus retains centered terrain-relative individuality and terrain elevation alone does not pass. "
            "The existing replication is robust to the tested terrain-leak pathway."
        )
    elif pr and pt:
        label = "ROBUST_WITH_REPEATABLE_TERRAIN_USE"
        interpretation = (
            "Pteropus retains centered terrain-relative individuality, while terrain elevation itself is also individually repeatable. "
            "The replication is robust to subtraction of terrain, with additional horizontal-terrain organization."
        )
    elif (not pr) and pt:
        label = "COMPATIBLE_WITH_TERRAIN_LEAKAGE"
        interpretation = (
            "The terrain-relative endpoint fails while terrain-only identity passes. "
            "The original MSL-centered PASS is compatible with fine-scale terrain leakage and cannot count as robust terrain-independent replication."
        )
    else:
        label = "NOT_ROBUST_CAUSE_UNRESOLVED"
        interpretation = (
            "The terrain-relative endpoint fails and terrain-only identity also fails. "
            "The original MSL-centered PASS is not robust to terrain adjustment, but terrain is not identified as the cause."
        )

    payload = {
        "schema_version": 1,
        "study_id": "batter-pteropus-terrain-leak-diagnostic-v1",
        "inferential_class": "post-outcome frozen confound diagnostic",
        "contract": str(CONTRACT.relative_to(ROOT)),
        "source": source_meta,
        "terrain": terrain_meta,
        "msl_replay": {"replay_ok": replay_ok, **msl},
        "terrain_relative_primary": terrain_rel,
        "terrain_only_secondary": terrain_only,
        "frozen_interpretation": {
            "label": label,
            "robust_terrain_independent_replication": bool(pr),
            "interpretation": interpretation,
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    mr = msl["calibration"]
    ar = terrain_rel["calibration"]
    tr = terrain_only["calibration"]
    md = [
        "# Pteropus terrain-leak diagnostic result v1",
        "",
        "**Inferential class:** post-outcome frozen confound diagnostic.",
        "",
        "The original native-MSL small-panel result replayed exactly before terrain-derived endpoints were opened.",
        "",
        "| endpoint | calibrated excess | p(null >= observed) | verdict |",
        "|---|---:|---:|---|",
        f"| native MSL centered replay | {mr['observed_minus_null_mean']:+.5f} | {mr['p_null_ge_observed']:.4f} | {'PASS' if msl['pass'] else 'FAIL'} |",
        f"| terrain-relative proxy centered | {ar['observed_minus_null_mean']:+.5f} | {ar['p_null_ge_observed']:.4f} | {'PASS' if terrain_rel['pass'] else 'FAIL'} |",
        f"| terrain-only centered | {tr['observed_minus_null_mean']:+.5f} | {tr['p_null_ge_observed']:.4f} | {'PASS' if terrain_only['pass'] else 'FAIL'} |",
        "",
        f"**Frozen interpretation:** `{label}`",
        "",
        interpretation,
        "",
        f"Terrain tiles used: **{terrain_meta['tile_count']}**; terrain range {terrain_meta['terrain_min_m']:.1f} to {terrain_meta['terrain_max_m']:.1f} m.",
        "",
        "No event, session, individual, grid, bin, DEM product or threshold was changed after terrain-derived outcomes were opened.",
        "",
    ]
    OUT_MD.write_text("\n".join(md), encoding="utf-8")

    print(json.dumps({
        "msl_replay_excess": mr["observed_minus_null_mean"],
        "msl_replay_p": mr["p_null_ge_observed"],
        "terrain_relative_excess": ar["observed_minus_null_mean"],
        "terrain_relative_p": ar["p_null_ge_observed"],
        "terrain_relative_pass": terrain_rel["pass"],
        "terrain_only_excess": tr["observed_minus_null_mean"],
        "terrain_only_p": tr["p_null_ge_observed"],
        "terrain_only_pass": terrain_only["pass"],
        "interpretation_label": label,
        "tile_count": terrain_meta["tile_count"],
    }, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
