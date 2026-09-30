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

CONTRACT_MD = ROOT / "post_freeze_extensions/PTEROPUS_TERRAIN_LEAK_CONTRACT_V1.md"
SMALL_CONTRACT = ROOT / "post_freeze_extensions/small_panel_generality/contract_v1.json"
RECEIPT = ROOT / "post_freeze_extensions/small_panel_generality/height_opening_receipt_v1.json"
SMALL_RESULT = ROOT / "post_freeze_extensions/small_panel_generality/primary_result_v1.json"
OUT = ROOT / "post_freeze_extensions/pteropus_terrain_leak/result_v1.json"
OUT_MD = ROOT / "post_freeze_extensions/pteropus_terrain_leak/RESULT_V1.md"

SOURCE_ID = "pteropus_poliocephalus_5bd6pq55"
EXPECTED_RAW_SHA256 = "13829a97110f3eff191c9066fd5bf7d20f5d1c7e26e152e6c733079fb4e179dc"
EDGES = (-math.inf, -400.0, -200.0, -100.0, -50.0, 0.0, 50.0, 100.0, 200.0, 400.0, math.inf)
K = len(EDGES) - 1
UA = {"User-Agent": "batter-pteropus-terrain-leak-v1/1.0"}
B = 9999
MSL_SEED = 20260930162
AGL_SEED = 20261001071
TERRAIN_SEED = 20261001072
GRID_M = 5000.0
HGT_N = 3601
HGT_VOID = -32768


def norm(x):
    return "_".join(
        str(x).strip().lower().replace("-", "_").replace(" ", "_").replace(".", "_").split("_")
    )


def present(s):
    txt = s.astype(str).str.strip()
    return s.notna() & txt.ne("") & ~txt.str.lower().isin({"na", "nan", "null", "none"})


def boolish(x):
    s = str(x).strip().lower()
    if s in {"true", "t", "1", "yes", "y"}:
        return True
    if s in {"false", "f", "0", "no", "n"}:
        return False
    return None


def source_spec():
    c = json.loads(SMALL_CONTRACT.read_text())
    specs = {x["source_id"]: x for x in c["closed_source_set"]}
    return specs[SOURCE_ID]


def frozen_receipt():
    r = json.loads(RECEIPT.read_text())
    return r["sources"][SOURCE_ID]


def load_frozen_dataframe():
    src = source_spec()
    rec = frozen_receipt()
    response = requests.get(src["event_url"], headers=UA, timeout=300)
    response.raise_for_status()
    raw = response.content
    sha = hashlib.sha256(raw).hexdigest()
    if sha != EXPECTED_RAW_SHA256 or sha != rec["raw_sha256"]:
        raise RuntimeError(f"raw SHA mismatch: {sha}")

    hdr = pd.read_csv(io.BytesIO(raw), nrows=0)
    cmap = {norm(x): x for x in hdr.columns}
    hkey = norm(src["vertical_field"])
    req = ["timestamp", "location_long", "location_lat", "individual_local_identifier", hkey]
    missing = [x for x in req if x not in cmap]
    if missing:
        raise RuntimeError(f"missing fields: {missing}")
    use = [cmap[x] for x in req]
    for q in ["visible", "algorithm_marked_outlier", "manually_marked_outlier", "import_marked_outlier"]:
        if q in cmap:
            use.append(cmap[q])
    use = list(dict.fromkeys(use))
    df = pd.read_csv(io.BytesIO(raw), dtype=str, usecols=use, low_memory=False)

    tcol, loncol, latcol = cmap["timestamp"], cmap["location_long"], cmap["location_lat"]
    iidcol, hcol = cmap["individual_local_identifier"], cmap[hkey]

    mask = present(df[tcol]) & present(df[loncol]) & present(df[latcol]) & present(df[iidcol]) & present(df[hcol])
    d = df.loc[mask].copy()

    if "visible" in cmap and cmap["visible"] in d:
        keep = []
        for x in d[cmap["visible"]]:
            b = boolish(x)
            keep.append(True if b is None else b)
        d = d.loc[keep].copy()

    for q in ["algorithm_marked_outlier", "manually_marked_outlier", "import_marked_outlier"]:
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
    bad = d["t"].isna() | d["lon"].isna() | d["lat"].isna() | d["height_msl"].isna()
    d = d.loc[~bad].copy()
    arr = d[["lon", "lat", "height_msl"]].to_numpy(dtype=float)
    if not np.isfinite(arr).all():
        raise RuntimeError("nonfinite coordinate/height after parse")
    d = d.sort_values(["iid", "t"]).copy()

    d["sess_num"] = -1
    for iid, g in d.groupby("iid", sort=True):
        vals, k, prev = [], 0, None
        for t in g["t"]:
            if prev is not None and (t - prev) > pd.Timedelta(hours=4):
                k += 1
            vals.append(k)
            prev = t
        d.loc[g.index, "sess_num"] = vals
    d["session"] = d["iid"] + "::" + d["sess_num"].astype(int).astype(str)

    frozen_sessions = {
        z["session"] for rows in rec["training_sessions"].values() for z in rows
    }
    d = d[d["session"].isin(frozen_sessions)].copy()
    if set(d["session"].unique()) != frozen_sessions:
        missing = sorted(frozen_sessions - set(d["session"].unique()))
        raise RuntimeError(f"frozen sessions missing: {missing[:10]}")

    tr = Transformer.from_crs("EPSG:4326", f"EPSG:{int(rec['projection_epsg'])}", always_xy=True)
    e, n = tr.transform(d["lon"].to_numpy(dtype=float), d["lat"].to_numpy(dtype=float))
    d["cx"] = np.floor(np.asarray(e) / GRID_M).astype(int)
    d["cy"] = np.floor(np.asarray(n) / GRID_M).astype(int)
    return d.reset_index(drop=True), sha


def tile_name(lat0: int, lon0: int) -> str:
    ns = "N" if lat0 >= 0 else "S"
    ew = "E" if lon0 >= 0 else "W"
    return f"{ns}{abs(lat0):02d}{ew}{abs(lon0):03d}"


def tile_url(lat0: int, lon0: int) -> str:
    name = tile_name(lat0, lon0)
    band = name[:3]
    return f"https://s3.amazonaws.com/elevation-tiles-prod/skadi/{band}/{name}.hgt.gz"


def download_hgt(lat0: int, lon0: int):
    url = tile_url(lat0, lon0)
    r = requests.get(url, headers=UA, timeout=300)
    r.raise_for_status()
    gz = r.content
    raw = gzip.decompress(gz)
    expected = HGT_N * HGT_N * 2
    if len(raw) != expected:
        raise RuntimeError(f"{tile_name(lat0, lon0)} unexpected HGT bytes {len(raw)} != {expected}")
    a = np.frombuffer(raw, dtype=">i2").reshape((HGT_N, HGT_N))
    meta = {
        "tile": tile_name(lat0, lon0),
        "url": url,
        "gzip_bytes": len(gz),
        "raw_bytes": len(raw),
        "gzip_sha256": hashlib.sha256(gz).hexdigest(),
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
    }
    return a, meta


def nearest_finite(a, rowf, colf):
    rr = int(round(rowf))
    cc = int(round(colf))
    best = None
    for r in range(max(0, rr - 3), min(HGT_N, rr + 4)):
        for c in range(max(0, cc - 3), min(HGT_N, cc + 4)):
            v = int(a[r, c])
            if v == HGT_VOID:
                continue
            d2 = (r - rowf) ** 2 + (c - colf) ** 2
            cand = (d2, r, c, float(v))
            if best is None or cand < best:
                best = cand
    if best is None:
        raise RuntimeError("no finite SRTM sample in frozen 7x7 fallback window")
    return best[3], True


def terrain_at(a, lat0, lon0, lat, lon):
    rowf = (lat0 + 1.0 - lat) * 3600.0
    colf = (lon - lon0) * 3600.0
    if rowf < -1e-8 or rowf > 3600.0 + 1e-8 or colf < -1e-8 or colf > 3600.0 + 1e-8:
        raise RuntimeError("coordinate outside derived HGT tile")
    rowf = min(3600.0, max(0.0, rowf))
    colf = min(3600.0, max(0.0, colf))
    r0 = min(3599, int(math.floor(rowf)))
    c0 = min(3599, int(math.floor(colf)))
    fr = rowf - r0
    fc = colf - c0
    vals = [
        int(a[r0, c0]),
        int(a[r0, c0 + 1]),
        int(a[r0 + 1, c0]),
        int(a[r0 + 1, c0 + 1]),
    ]
    if any(v == HGT_VOID for v in vals):
        return nearest_finite(a, rowf, colf)
    v00, v01, v10, v11 = [float(v) for v in vals]
    value = (
        v00 * (1 - fr) * (1 - fc)
        + v01 * (1 - fr) * fc
        + v10 * fr * (1 - fc)
        + v11 * fr * fc
    )
    return value, False


def attach_terrain(d):
    keys = sorted({(math.floor(float(lat)), math.floor(float(lon))) for lat, lon in d[["lat", "lon"]].to_numpy()})
    tiles, meta = {}, []
    for lat0, lon0 in keys:
        a, m = download_hgt(lat0, lon0)
        tiles[(lat0, lon0)] = a
        meta.append(m)

    vals, fallbacks = [], 0
    for lat, lon in d[["lat", "lon"]].to_numpy(dtype=float):
        key = (math.floor(lat), math.floor(lon))
        v, fb = terrain_at(tiles[key], key[0], key[1], lat, lon)
        if fb:
            fallbacks += 1
        vals.append(v)
    d = d.copy()
    d["terrain_m"] = np.asarray(vals, dtype=float)
    if not np.isfinite(d["terrain_m"].to_numpy()).all():
        raise RuntimeError("nonfinite terrain values")
    d["terrain_relative_m"] = d["height_msl"] - d["terrain_m"]
    return d, meta, fallbacks


def events_for_response(d, response_col):
    med = d.groupby("session")[response_col].transform("median")
    resid = d[response_col] - med
    events = []
    for row, z in zip(d.itertuples(index=False), resid.to_numpy(dtype=float)):
        events.append(
            Event(
                individual=str(row.iid),
                timestamp=row.t.to_pydatetime(),
                cell=(int(row.cx), int(row.cy)),
                zbin=z_bin(float(z), edges=EDGES),
                session=str(row.session),
            )
        )
    return events


def expected_frozen_targets():
    rec = frozen_receipt()
    out = {}
    for iid, rows in rec["frozen_vertical_target_sessions"].items():
        for x in rows:
            out[str(x["session"])] = {
                "iid": str(iid),
                "supported_events": int(x["supported_events"]),
                "target_events": int(x["target_events"]),
            }
    return out


def validate_session_rows(session_rows):
    frozen = expected_frozen_targets()
    got = {str(x["session"]): x for x in session_rows}
    if set(got) != set(frozen):
        raise RuntimeError(
            f"target-session set mismatch; missing={sorted(set(frozen)-set(got))[:10]}, "
            f"extra={sorted(set(got)-set(frozen))[:10]}"
        )
    for sid, fx in frozen.items():
        if int(got[sid]["scored_fixes"]) != fx["supported_events"]:
            raise RuntimeError(
                f"supported-event mismatch {sid}: {got[sid]['scored_fixes']} != {fx['supported_events']}"
            )


def run_endpoint(events, seed):
    arrays = {SOURCE_ID: cal.make_cohort_arrays(events, K)}
    observed, per_ind, session_rows = cal.observed_eval(arrays)
    if int(observed["eligible_individuals"]) != 4:
        raise RuntimeError(f"eligible n={observed['eligible_individuals']} != 4")
    validate_session_rows(session_rows)
    metric = "common_cell_marginal"
    obs = float(observed[metric])
    rng = np.random.default_rng(seed)
    null, eligible, invalid = [], [], 0
    for _ in range(B):
        p = cal.perm_eval(arrays, rng)
        if p["eligible_individuals"] < 1 or p[metric] is None:
            invalid += 1
            continue
        null.append(float(p[metric]))
        eligible.append(int(p["eligible_individuals"]))
    if not null:
        raise RuntimeError("no valid permutations")
    summ = cal.tail_summary(null, obs)
    passed = bool(summ["observed_minus_null_mean"] > 0 and summ["p_null_ge_observed"] <= 0.05)
    return {
        "observed": observed,
        "individual_results": per_ind,
        "session_results": session_rows,
        "permutation": {
            "B": B,
            "seed": seed,
            "valid_replicates": len(null),
            "invalid_replicates": invalid,
            "eligible_individual_count": {
                "observed": 4,
                "min": int(min(eligible)),
                "max": int(max(eligible)),
                "mean": float(np.mean(eligible)),
            },
            "calibration": summ,
        },
        "pass": passed,
    }


def validate_msl_replay(msl):
    old = json.loads(SMALL_RESULT.read_text())["sources"][SOURCE_ID]
    oldc = old["permutation"]["calibration"]
    newc = msl["permutation"]["calibration"]
    fields = ["observed", "mean", "observed_minus_null_mean", "p_null_ge_observed"]
    for f in fields:
        if not math.isclose(float(oldc[f]), float(newc[f]), rel_tol=0.0, abs_tol=1e-12):
            raise RuntimeError(f"MSL replay mismatch {f}: {newc[f]} != {oldc[f]}")
    if bool(old["primary_pass"]) != bool(msl["pass"]):
        raise RuntimeError("MSL replay PASS mismatch")


def interpretation(agl_pass, terrain_pass):
    if agl_pass and not terrain_pass:
        return {
            "code": "ROBUST_TERRAIN_RELATIVE_ONLY",
            "text": "Pteropus replication is robust to the tested terrain pathway; terrain distribution alone is not supported as carrying the identity signal.",
            "robust_terrain_independent_replication": True,
        }
    if agl_pass and terrain_pass:
        return {
            "code": "ROBUST_WITH_TERRAIN_IDENTITY",
            "text": "Pteropus retains centered terrain-relative individuality while terrain use is also individually repeatable; the replication remains robust but horizontal-terrain organization is an additional axis.",
            "robust_terrain_independent_replication": True,
        }
    if (not agl_pass) and terrain_pass:
        return {
            "code": "COMPATIBLE_WITH_TERRAIN_LEAK",
            "text": "The original MSL-centered PASS is compatible with fine-scale terrain leakage and is not robust evidence of terrain-independent centered vertical individuality.",
            "robust_terrain_independent_replication": False,
        }
    return {
        "code": "UNRESOLVED_AFTER_TERRAIN_ADJUSTMENT",
        "text": "The MSL-centered PASS is not robust to terrain adjustment, while terrain-only identity is unsupported; terrain is not identified as the cause and Pteropus is removed from the robust-replication count.",
        "robust_terrain_independent_replication": False,
    }


def endpoint_brief(x):
    c = x["permutation"]["calibration"]
    return {
        "observed": c["observed"],
        "null_mean": c["mean"],
        "calibrated_excess": c["observed_minus_null_mean"],
        "p_upper": c["p_null_ge_observed"],
        "null_standardized_deviation": c["null_standardized_deviation"],
        "pass": x["pass"],
    }


def main():
    if not CONTRACT_MD.exists():
        raise RuntimeError("missing frozen terrain-leak contract")
    d, raw_sha = load_frozen_dataframe()

    # Hard validation first: reproduce the already-opened MSL endpoint exactly.
    msl = run_endpoint(events_for_response(d, "height_msl"), MSL_SEED)
    validate_msl_replay(msl)

    # Only after successful replay do terrain-derived outcomes open.
    d2, tile_meta, fallback_count = attach_terrain(d)
    agl = run_endpoint(events_for_response(d2, "terrain_relative_m"), AGL_SEED)
    terrain = run_endpoint(events_for_response(d2, "terrain_m"), TERRAIN_SEED)
    interp = interpretation(agl["pass"], terrain["pass"])

    # Descriptive quantities are not decision endpoints.
    tmp = d2.copy()
    tmp["centered_msl"] = tmp["height_msl"] - tmp.groupby("session")["height_msl"].transform("median")
    tmp["centered_terrain"] = tmp["terrain_m"] - tmp.groupby("session")["terrain_m"].transform("median")
    tmp["centered_terrain_relative"] = tmp["terrain_relative_m"] - tmp.groupby("session")["terrain_relative_m"].transform("median")
    corr = float(np.corrcoef(tmp["centered_msl"], tmp["centered_terrain"])[0, 1])

    payload = {
        "schema_version": 1,
        "study_id": "batter-pteropus-terrain-leak-v1",
        "contract": "post_freeze_extensions/PTEROPUS_TERRAIN_LEAK_CONTRACT_V1.md",
        "inferential_class": "post-outcome frozen confound diagnostic",
        "source": {
            "source_id": SOURCE_ID,
            "taxon": "Pteropus poliocephalus",
            "raw_sha256": raw_sha,
            "frozen_event_rows": int(len(d2)),
            "individuals": sorted(d2["iid"].unique().tolist()),
            "sessions": int(d2["session"].nunique()),
        },
        "terrain_source": {
            "product": "Skadi/SRTM1 HGT",
            "reference": "WGS84/EGM96 geoid",
            "nominal_resolution": "1 arc-second",
            "interpolation": "bilinear; frozen 7x7 nearest-finite fallback on void corner",
            "tiles": tile_meta,
            "void_fallback_events": int(fallback_count),
        },
        "validation_msl_replay": endpoint_brief(msl),
        "primary_terrain_relative_proxy": endpoint_brief(agl),
        "secondary_terrain_only": endpoint_brief(terrain),
        "interpretation": interp,
        "descriptive_only": {
            "terrain_m_min": float(d2["terrain_m"].min()),
            "terrain_m_max": float(d2["terrain_m"].max()),
            "terrain_m_sd": float(d2["terrain_m"].std(ddof=1)),
            "centered_msl_vs_centered_terrain_pearson_r": corr,
        },
        "claim_boundary": [
            "This is a post-outcome confound diagnostic, not a prospective external replication.",
            "Terrain-relative height is a DEM-based proxy, not error-free true AGL.",
            "No DEM product, grid, bin, session, individual subset or threshold may be changed to rescue a FAIL.",
            "This diagnostic does not test the post-hoc resource-anchoring hypothesis.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    m = payload["validation_msl_replay"]
    a = payload["primary_terrain_relative_proxy"]
    t = payload["secondary_terrain_only"]
    lines = [
        "# Pteropus terrain-leak diagnostic v1",
        "",
        "**Inferential class:** post-outcome frozen confound diagnostic.",
        "",
        "The original MSL-centered endpoint was first replayed exactly before any terrain-derived outcome was interpreted.",
        "",
        "| endpoint | calibrated excess | p_upper | verdict |",
        "|---|---:|---:|---|",
        f"| source-native centered MSL replay | {m['calibrated_excess']:+.5f} | {m['p_upper']:.4f} | {'PASS' if m['pass'] else 'FAIL'} |",
        f"| centered terrain-relative proxy (primary) | {a['calibrated_excess']:+.5f} | {a['p_upper']:.4f} | {'PASS' if a['pass'] else 'FAIL'} |",
        f"| centered terrain elevation only (secondary) | {t['calibrated_excess']:+.5f} | {t['p_upper']:.4f} | {'PASS' if t['pass'] else 'FAIL'} |",
        "",
        f"**Frozen interpretation:** {interp['text']}",
        "",
        f"Terrain tiles used: {', '.join(x['tile'] for x in tile_meta)}.",
        f"Void-fallback events: {fallback_count}.",
        f"Descriptive centered MSL vs centered terrain correlation: r = {corr:.4f}.",
        "",
        "No alternative terrain product or analysis threshold is opened by this diagnostic.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({
        "msl_replay": endpoint_brief(msl),
        "terrain_relative": endpoint_brief(agl),
        "terrain_only": endpoint_brief(terrain),
        "interpretation": interp,
        "tiles": [x["tile"] for x in tile_meta],
        "void_fallback_events": fallback_count,
        "centered_msl_vs_centered_terrain_r": corr,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
