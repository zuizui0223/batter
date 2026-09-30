#!/usr/bin/env python3
from __future__ import annotations

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

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from batter.analysis import Event, z_bin
import scripts.run_cross_panel_estimator_calibration as cal

CONTRACT = ROOT / "post_freeze_extensions/nyctalus_eligibility_robustness/contract_v1.json"
OUT_JSON = ROOT / "post_freeze_extensions/nyctalus_eligibility_robustness/result_v1.json"
OUT_MD = ROOT / "post_freeze_extensions/nyctalus_eligibility_robustness/RESULT_V1.md"
UA = {"User-Agent": "batter-nyctalus-eligibility-robustness-v1/1.0"}
EDGES = (-math.inf, -400.0, -200.0, -100.0, -50.0, 0.0, 50.0, 100.0, 200.0, 400.0, math.inf)
K = len(EDGES) - 1


def present(s: pd.Series) -> pd.Series:
    txt = s.astype(str).str.strip()
    return s.notna() & txt.ne("") & ~txt.str.lower().isin({"na", "nan", "null", "none"})


def fetch_source(c):
    meta = requests.get(
        f"https://zenodo.org/api/records/{c['source']['record_id']}",
        headers=UA,
        timeout=90,
    )
    meta.raise_for_status()
    rec = meta.json()
    target = None
    for f in rec.get("files", []):
        if (f.get("key") or f.get("filename")) == c["source"]["file"]:
            target = f
            break
    if target is None:
        raise RuntimeError("frozen source file not found")
    url = (target.get("links") or {}).get("content") or (target.get("links") or {}).get("self")
    r = requests.get(url, headers=UA, timeout=180)
    r.raise_for_status()
    data = r.content
    sha = hashlib.sha256(data).hexdigest()
    if sha != c["source"]["sha256"]:
        raise RuntimeError(f"source SHA mismatch: {sha}")
    return pd.read_csv(io.BytesIO(data), dtype=str, low_memory=False), sha, len(data)


def prepare_rows(df: pd.DataFrame) -> pd.DataFrame:
    req = ["bat_id", "trackid", "utc", "x", "y", "Height", "Year", "field_period"]
    missing = [x for x in req if x not in df.columns]
    if missing:
        raise RuntimeError(f"missing frozen fields: {missing}")

    mask = pd.Series(True, index=df.index)
    for col in req:
        mask &= present(df[col])
    d = df.loc[mask, req].copy()

    d["x_num"] = pd.to_numeric(d["x"], errors="coerce")
    d["y_num"] = pd.to_numeric(d["y"], errors="coerce")
    d["height_num"] = pd.to_numeric(d["Height"], errors="coerce")
    d["t"] = pd.to_datetime(d["utc"], errors="coerce", utc=True)

    bad = (
        d["x_num"].isna()
        | d["y_num"].isna()
        | d["height_num"].isna()
        | d["t"].isna()
    )
    if bad.any():
        raise RuntimeError(f"parse failures among frozen presence-qualified rows: {int(bad.sum())}")
    h = d["height_num"].to_numpy(dtype=float)
    if not np.isfinite(h).all():
        raise RuntimeError("non-finite Height values")

    d["bat_id"] = d["bat_id"].astype(str)
    d["trackid"] = d["trackid"].astype(str)
    d["cohort"] = d["Year"].astype(str).str.strip() + "::" + d["field_period"].astype(str).str.strip()
    return d


def filter_sessions(d: pd.DataFrame, minimum_fixes: int) -> pd.DataFrame:
    if minimum_fixes <= 0:
        return d.copy()
    counts = (
        d.groupby(["cohort", "bat_id", "trackid"], sort=True)
        .size()
        .rename("n")
        .reset_index()
    )
    keep = counts[counts["n"] >= int(minimum_fixes)]
    keys = set(zip(keep["cohort"], keep["bat_id"], keep["trackid"]))
    idx = [
        (cohort, iid, sid) in keys
        for cohort, iid, sid in zip(d["cohort"], d["bat_id"], d["trackid"])
    ]
    return d.loc[idx].copy()


def build_events(d: pd.DataFrame, grid_m: int):
    d = d.copy()
    if d.empty:
        return {}, {"rows": 0, "tracks": 0, "individual_cohort_units": 0}

    d["cx"] = np.floor(d["x_num"].astype(float) / float(grid_m)).astype(int)
    d["cy"] = np.floor(d["y_num"].astype(float) / float(grid_m)).astype(int)

    # Center each retained full track exactly as in both Nyctalus analyses.
    d["track_median"] = d.groupby(["cohort", "trackid"])["height_num"].transform("median")
    d["resid_height"] = d["height_num"] - d["track_median"]

    events = defaultdict(list)
    tracks = 0
    units = set()
    for (cohort, iid, sid), g in d.groupby(["cohort", "bat_id", "trackid"], sort=True):
        tracks += 1
        iid_key = f"{cohort}::{iid}"
        sid_key = f"{cohort}::{sid}"
        units.add(iid_key)
        for r in g.itertuples(index=False):
            events[str(cohort)].append(
                Event(
                    individual=iid_key,
                    timestamp=r.t.to_pydatetime(),
                    cell=(int(r.cx), int(r.cy)),
                    zbin=z_bin(float(r.resid_height), edges=EDGES),
                    session=sid_key,
                )
            )
    return dict(events), {
        "rows": int(len(d)),
        "tracks": int(tracks),
        "individual_cohort_units_before_common_support": int(len(units)),
    }


def evaluate_threshold(d, threshold, c):
    grid = int(c["fixed_estimator"]["horizontal_grid_m"])
    q = filter_sessions(d, int(threshold))
    events_by_cohort, structural = build_events(q, grid)
    arrays = {
        cohort: cal.make_cohort_arrays(events, K)
        for cohort, events in sorted(events_by_cohort.items())
        if events
    }
    if not arrays:
        return {
            "threshold": int(threshold),
            "structural": structural,
            "observed": None,
            "permutation": None,
        }

    observed, per_ind, session_rows = cal.observed_eval(arrays)
    obs = observed["common_cell_marginal"]
    if observed["eligible_individuals"] < 1 or obs is None:
        return {
            "threshold": int(threshold),
            "structural": structural,
            "observed": {**observed, "individual_results": per_ind, "session_results": session_rows},
            "permutation": None,
        }

    B = int(c["fixed_estimator"]["B"])
    seed = int(c["fixed_estimator"]["seed"])
    rng = np.random.default_rng(seed)
    null = []
    eligible = []
    invalid = 0
    for _ in range(B):
        p = cal.perm_eval(arrays, rng)
        if p["eligible_individuals"] < 1 or p["common_cell_marginal"] is None:
            invalid += 1
            continue
        null.append(float(p["common_cell_marginal"]))
        eligible.append(int(p["eligible_individuals"]))

    if not null:
        raise RuntimeError(f"threshold {threshold}: no valid permutation replicates")

    summ = cal.tail_summary(null, float(obs))
    return {
        "threshold": int(threshold),
        "structural": structural,
        "observed": {
            **observed,
            "individual_results": per_ind,
            "session_results": session_rows,
        },
        "permutation": {
            "B": B,
            "seed": seed,
            "valid_replicates": len(null),
            "invalid_replicates": invalid,
            "eligible_individual_count_min": int(min(eligible)),
            "eligible_individual_count_max": int(max(eligible)),
            "common_cell_marginal_identity": summ,
        },
    }


def main():
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    df, sha, size = fetch_source(c)
    d = prepare_rows(df)

    thresholds = [int(x) for x in c["only_varied_parameter"]["thresholds"]]
    results = [evaluate_threshold(d, t, c) for t in thresholds]

    # Regression anchors: these verify that one code path reproduces the two already-opened analyses.
    by_t = {r["threshold"]: r for r in results}
    anchor_checks = {}
    for t, key in [(0, "threshold_0"), (50, "threshold_50")]:
        anchor = c["known_anchor_runs"][key]
        r = by_t[t]
        got_n = r["observed"]["eligible_individuals"]
        got_x = r["permutation"]["common_cell_marginal_identity"]["observed_minus_null_mean"]
        got_p = r["permutation"]["common_cell_marginal_identity"]["p_null_ge_observed"]
        anchor_checks[str(t)] = {
            "n_expected": int(anchor["expected_n"]),
            "n_observed": int(got_n),
            "n_match": int(got_n) == int(anchor["expected_n"]),
            "reported_calibrated_excess": float(anchor["reported_calibrated_excess"]),
            "recomputed_calibrated_excess": float(got_x),
            "absolute_excess_difference": abs(float(got_x) - float(anchor["reported_calibrated_excess"])),
            "reported_p": float(anchor["reported_p"]),
            "recomputed_p": float(got_p),
            "absolute_p_difference": abs(float(got_p) - float(anchor["reported_p"])),
        }
    if not all(x["n_match"] for x in anchor_checks.values()):
        raise RuntimeError(f"anchor n mismatch: {anchor_checks}")

    curve = []
    for r in results:
        if r["permutation"] is None:
            curve.append({
                "threshold": r["threshold"],
                "n": r["observed"]["eligible_individuals"] if r["observed"] else 0,
                "observed": None,
                "null_mean": None,
                "null_sd": None,
                "calibrated_excess": None,
                "p_upper": None,
            })
            continue
        s = r["permutation"]["common_cell_marginal_identity"]
        curve.append({
            "threshold": r["threshold"],
            "n": int(r["observed"]["eligible_individuals"]),
            "observed": float(s["observed"]),
            "null_mean": float(s["mean"]),
            "null_sd": float(s["sd"]),
            "calibrated_excess": float(s["observed_minus_null_mean"]),
            "p_upper": float(s["p_null_ge_observed"]),
        })

    finite = [x for x in curve if x["calibrated_excess"] is not None]
    effects = np.array([x["calibrated_excess"] for x in finite], dtype=float)
    synthesis = {
        "thresholds_evaluated": len(finite),
        "positive_excess_count": int(np.sum(effects > 0)),
        "all_excesses_positive": bool(np.all(effects > 0)),
        "calibrated_excess_min": float(effects.min()),
        "calibrated_excess_median": float(np.median(effects)),
        "calibrated_excess_max": float(effects.max()),
        "n_min": int(min(x["n"] for x in finite)),
        "n_max": int(max(x["n"] for x in finite)),
        "inferential_status": "post-outcome sensitivity only; no threshold is promoted to confirmatory status",
    }

    payload = {
        "schema_version": 1,
        "study_id": c["study_id"],
        "source_sha256": sha,
        "source_size_bytes": size,
        "row_count": int(len(d)),
        "contract": c,
        "anchor_checks": anchor_checks,
        "curve": curve,
        "synthesis": synthesis,
        "details": results,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Nyctalus eligibility robustness diagnostic v1",
        "",
        "**POST-OUTCOME SENSITIVITY DIAGNOSTIC. This cannot restore prospective status to the revised eligibility analysis.**",
        "",
        "Only the minimum presence-qualified fixes per source track is varied. All estimator, target-support, vertical-bin, horizontal-grid and permutation settings are fixed.",
        "",
        "| min fixes / track | evaluable n | observed identity | null mean | calibrated excess | null SD | p(null >= observed) |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for x in curve:
        if x["calibrated_excess"] is None:
            lines.append(f"| {x['threshold']} | {x['n']} | — | — | — | — | — |")
        else:
            lines.append(
                f"| {x['threshold']} | {x['n']} | {x['observed']:+.5f} | {x['null_mean']:+.5f} | "
                f"**{x['calibrated_excess']:+.5f}** | {x['null_sd']:.5f} | {x['p_upper']:.4f} |"
            )
    lines += [
        "",
        "## Frozen interpretation",
        "",
        f"- positive calibrated excess: **{synthesis['positive_excess_count']}/{synthesis['thresholds_evaluated']} thresholds**",
        f"- effect range: **{synthesis['calibrated_excess_min']:+.5f} to {synthesis['calibrated_excess_max']:+.5f}**",
        f"- median calibrated excess: **{synthesis['calibrated_excess_median']:+.5f}**",
        f"- evaluable n range: **{synthesis['n_min']} to {synthesis['n_max']}**",
        "",
        "The original >=50-fix analysis remains the prospective primary external test. The curve above is used only to diagnose whether effect direction and magnitude are fragile to the session-length eligibility rule; p-values are displayed descriptively and no threshold is selected because it is significant.",
        "",
        "## Anchor reproduction",
        "",
        f"- threshold 0: n match = **{anchor_checks['0']['n_match']}**, recomputed excess = {anchor_checks['0']['recomputed_calibrated_excess']:+.6f}, p = {anchor_checks['0']['recomputed_p']:.4f}",
        f"- threshold 50: n match = **{anchor_checks['50']['n_match']}**, recomputed excess = {anchor_checks['50']['recomputed_calibrated_excess']:+.6f}, p = {anchor_checks['50']['recomputed_p']:.4f}",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"curve": curve, "synthesis": synthesis, "anchor_checks": anchor_checks}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
