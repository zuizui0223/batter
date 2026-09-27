#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
import sys

import numpy as np
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from batter.analysis import Event, z_bin
import scripts.run_cross_panel_estimator_calibration as cal
import scripts.run_new_species_replications as core
import scripts.run_eidolon_independent_replication as eid

CONTRACT = Path("contract/cross_panel_endpoint_exclusion_v1.json")
BASELINE = Path("results/calibrated_vertical_identity_effect_input_v1.csv")
TOL = 1e-12
CELL_SIZE = 5000.0
MIN_SESSION = 50
PRIMARY_RADIUS = 1000
SENSITIVITY_RADII = {500, 2000}


def load_contract():
    cfg = json.loads(CONTRACT.read_text(encoding="utf-8"))
    return cfg, {p["id"]: p for p in cfg["panels"]}


def baseline_targets():
    import csv
    with BASELINE.open(newline="", encoding="utf-8") as fh:
        return {
            r["panel_id"]: float(r["common_cell_marginal"])
            for r in csv.DictReader(fh)
        }


def adjusted_source_contract(panel_id: str, spec: dict) -> dict:
    c = json.loads(Path(spec["contract"]).read_text(encoding="utf-8"))
    if panel_id == "phyllostomus_2016":
        out = copy.deepcopy(c)
        out["vertical"] = {
            "field": c["vertical"]["primary_field"],
            "primary_edges_m": c["vertical"]["edges_m"],
        }
        return out
    return c


def load_raw_panel(panel_id: str):
    cfg, panels = load_contract()
    spec = panels[panel_id]

    if panel_id == "eidolon":
        source_contract = json.loads(Path(spec["contract"]).read_text(encoding="utf-8"))
        gps = eid.get(eid.GPS_URL, eid.GPS_MD5, eid.GPS_SIZE)
        ref = eid.get(eid.REF_URL, eid.REF_MD5)
        rows = eid.read_csv(gps)
        refs = eid.read_csv(ref)
        pre = eid.build_pre_numeric(rows, refs)
        height_field = eid.HEIGHT_FIELD
        edges = tuple(eid.EDGES)
        finite_float = eid.finite_float
        parse_time = eid.parse_time
        source = {
            "gps_md5": eid.GPS_MD5,
            "reference_md5": eid.REF_MD5,
            "gps_rows": len(rows),
        }
    else:
        source_contract = adjusted_source_contract(panel_id, spec)
        ua = "batter-cross-panel-endpoint-exclusion-v1/1.0"
        gps = core.get(source_contract["source"]["gps"], ua)
        ref = core.get(source_contract["source"]["reference"], ua)
        rows, headers = core.read_csv(gps)
        refs, _ = core.read_csv(ref)
        pre = core.build_pre_numeric(rows, headers, refs, source_contract)
        height_field = source_contract["vertical"]["field"]
        edges = core.parse_edges(source_contract["vertical"]["primary_edges_m"])
        finite_float = core.finite_float
        parse_time = core.parse_time
        source = {
            "gps_md5": source_contract["source"]["gps"]["md5"],
            "reference_md5": source_contract["source"]["reference"]["md5"],
            "gps_rows": len(rows),
        }

    transformers = {
        cohort: Transformer.from_crs(
            "EPSG:4326", f"EPSG:{proj['epsg']}", always_xy=True
        )
        for cohort, proj in pre["projections"].items()
    }

    records = []
    numeric_height_failures = 0
    for idx, row in enumerate(rows):
        sid = pre["session_for_row"].get(idx)
        if sid is None:
            continue
        sm = pre["session_meta"][sid]
        cohort = sm["cohort"]
        if cohort not in pre["admitted_cohorts"]:
            continue
        lon = finite_float(row.get("location_long"))
        lat = finite_float(row.get("location_lat"))
        if lon is None or lat is None:
            continue
        try:
            t = parse_time(row.get("timestamp", ""))
        except Exception:
            continue
        x, y = transformers[cohort].transform(lon, lat)
        h = finite_float(row.get(height_field))
        zb = None
        if h is None:
            numeric_height_failures += 1
        else:
            zb = z_bin(h, edges=edges)
        records.append(
            {
                "cohort": cohort,
                "iid": sm["individual"],
                "session": sid,
                "t": t,
                "x": float(x),
                "y": float(y),
                "zbin": zb,
            }
        )

    return spec, records, len(edges) - 1, source, pre, numeric_height_failures


def endpoint_centers(records):
    by_session = defaultdict(list)
    for r in records:
        by_session[(r["cohort"], r["session"])].append(r)

    endpoint_rows = defaultdict(list)
    for (cohort, _sid), vals in by_session.items():
        vals = sorted(vals, key=lambda r: r["t"])
        for r in vals[:5] + vals[-5:]:
            endpoint_rows[(cohort, r["iid"])].append((r["x"], r["y"]))

    centers = {}
    spread = {}
    for key, pts in sorted(endpoint_rows.items()):
        arr = np.asarray(pts, dtype=float)
        if len(arr) == 0:
            continue
        d = np.sqrt(((arr[:, None, :] - arr[None, :, :]) ** 2).sum(axis=2))
        idx = int(np.argmin(d.sum(axis=1)))
        center = arr[idx]
        centers[key] = (float(center[0]), float(center[1]))
        dist = np.sqrt(((arr - center) ** 2).sum(axis=1))
        spread[f"{key[0]}::{key[1]}"] = {
            "endpoint_count": int(len(arr)),
            "median_distance_to_proxy_m": float(np.median(dist)),
            "q90_distance_to_proxy_m": float(np.quantile(dist, 0.9)),
        }
    return centers, spread


def events_after_exclusion(records, radius_m):
    centers, spread = endpoint_centers(records)
    numeric = [r for r in records if r["zbin"] is not None]

    kept = []
    excluded = 0
    missing_center = 0
    for r in numeric:
        center = centers.get((r["cohort"], r["iid"]))
        if center is None:
            missing_center += 1
            continue
        d = math.hypot(r["x"] - center[0], r["y"] - center[1])
        if d < radius_m:
            excluded += 1
        else:
            kept.append(r)

    post_counts = Counter((r["cohort"], r["session"]) for r in kept)
    retained_sessions = {
        key for key, n in post_counts.items() if n >= MIN_SESSION
    }
    kept = [
        r for r in kept if (r["cohort"], r["session"]) in retained_sessions
    ]

    events_by_cohort = defaultdict(list)
    for r in kept:
        cell = (
            math.floor(r["x"] / CELL_SIZE),
            math.floor(r["y"] / CELL_SIZE),
        )
        events_by_cohort[r["cohort"]].append(
            Event(r["iid"], r["t"], cell, int(r["zbin"]), r["session"])
        )

    qc = {
        "proxy_coordinate_scope": "individual within admitted cohort",
        "proxy_coordinates_written": False,
        "proxy_count": len(centers),
        "proxy_endpoint_spread": spread,
        "numeric_events_before_exclusion": len(numeric),
        "events_excluded_within_radius": excluded,
        "events_missing_proxy_center": missing_center,
        "events_after_exclusion_and_session_reeligibility": len(kept),
        "surviving_sessions": len(retained_sessions),
        "surviving_sessions_by_cohort": dict(
            sorted(Counter(cohort for cohort, _ in retained_sessions).items())
        ),
        "post_exclusion_session_counts": {
            f"{cohort}::{sid}": int(post_counts[(cohort, sid)])
            for cohort, sid in sorted(retained_sessions)
        },
    }
    return events_by_cohort, qc


def calibrated_panel(events_by_cohort, k, B, seed):
    arrays = {
        cohort: cal.make_cohort_arrays(events, k)
        for cohort, events in sorted(events_by_cohort.items())
        if events
    }
    if not arrays:
        raise RuntimeError("no surviving cohort events after exclusion")

    observed, per_ind, session_rows = cal.observed_eval(arrays)
    rng = np.random.default_rng(int(seed))
    null_marginal = []
    null_advantage = []
    eligible = []
    invalid = 0

    for _ in range(int(B)):
        s = cal.perm_eval(arrays, rng)
        if (
            s["eligible_individuals"] < 1
            or s["common_cell_marginal"] is None
            or s["common_cell_advantage"] is None
        ):
            invalid += 1
            continue
        eligible.append(s["eligible_individuals"])
        null_marginal.append(s["common_cell_marginal"])
        null_advantage.append(s["common_cell_advantage"])

    if not null_marginal:
        raise RuntimeError("no valid permutation replicates")

    margin_cal = cal.tail_summary(
        null_marginal, observed["common_cell_marginal"]
    )
    adv_cal = cal.tail_summary(
        null_advantage, observed["common_cell_advantage"]
    )
    e = np.asarray(eligible, dtype=float)
    eligible_summary = {
        "valid_permutations": int(len(eligible)),
        "invalid_permutations": int(invalid),
        "observed": int(observed["eligible_individuals"]),
        "mean": float(e.mean()),
        "q025": float(np.quantile(e, 0.025)),
        "q50": float(np.quantile(e, 0.5)),
        "q975": float(np.quantile(e, 0.975)),
        "min": int(e.min()),
        "max": int(e.max()),
    }
    return observed, per_ind, session_rows, margin_cal, adv_cal, eligible_summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", required=True)
    ap.add_argument("--radius", required=True, type=int, choices=[500, 1000, 2000])
    args = ap.parse_args()

    cfg, panels = load_contract()
    if args.panel not in panels:
        raise SystemExit(f"unknown panel {args.panel}")
    spec, records, k, source, pre, numeric_failures = load_raw_panel(args.panel)

    # Two pre-output consistency checks. First reproduce the published no-exclusion
    # common-cell endpoint using the existing calibration loader; then reproduce it
    # from this runner's projected-record path with a zero-radius exclusion.
    _old_spec, old_events, old_k, _old_source, _old_pre, _old_fail = cal.load_panel(args.panel)
    old_arrays = {
        cohort: cal.make_cohort_arrays(events, old_k)
        for cohort, events in sorted(old_events.items())
    }
    old_observed, _, _ = cal.observed_eval(old_arrays)
    expected = baseline_targets()[args.panel]
    if abs(float(old_observed["common_cell_marginal"]) - expected) > TOL:
        raise RuntimeError(
            f"existing calibration baseline mismatch {args.panel}: "
            f"{old_observed['common_cell_marginal']} != {expected}"
        )

    zero_events, zero_qc = events_after_exclusion(records, 0)
    zero_arrays = {
        cohort: cal.make_cohort_arrays(events, k)
        for cohort, events in sorted(zero_events.items())
        if events
    }
    zero_observed, _, _ = cal.observed_eval(zero_arrays)
    if abs(float(zero_observed["common_cell_marginal"]) - expected) > TOL:
        raise RuntimeError(
            f"endpoint-runner reconstruction mismatch {args.panel}: "
            f"{zero_observed['common_cell_marginal']} != {expected}"
        )

    events_by_cohort, qc = events_after_exclusion(records, args.radius)
    if args.radius == PRIMARY_RADIUS:
        B = int(cfg["exclusion_and_scoring"]["primary_permutations_per_panel"])
        seed = int(spec["primary_seed"])
        role = "primary"
    else:
        B = int(cfg["exclusion_and_scoring"]["sensitivity_permutations_per_panel_radius"])
        seed = int(
            spec[
                "sensitivity_seed_500m"
                if args.radius == 500
                else "sensitivity_seed_2000m"
            ]
        )
        role = "descriptive_sensitivity"

    observed, per_ind, session_rows, marg_cal, adv_cal, eligible_null = calibrated_panel(
        events_by_cohort, k, B, seed
    )

    min_n = int(spec["minimum_evaluable_individuals"])
    passes = (
        role == "primary"
        and observed["eligible_individuals"] >= min_n
        and marg_cal["observed_minus_null_mean"] > 0
        and marg_cal["p_null_ge_observed"] <= 0.05
    )

    payload = {
        "study_id": cfg["study_id"],
        "contract": str(CONTRACT),
        "panel_id": args.panel,
        "taxon": spec["taxon"],
        "radius_m": args.radius,
        "analysis_role": role,
        "source": source,
        "original_admitted_cohorts": list(pre["admitted_cohorts"]),
        "numeric_height_parse_failures": numeric_failures,
        "pre_exclusion_consistency": {
            "expected_common_cell_marginal": expected,
            "existing_loader_common_cell_marginal": old_observed["common_cell_marginal"],
            "endpoint_runner_zero_radius_common_cell_marginal": zero_observed["common_cell_marginal"],
            "absolute_tolerance": TOL,
            "zero_radius_qc": zero_qc,
        },
        "qc": qc,
        "observed": {
            **observed,
            "individual_results": per_ind,
            "session_results": session_rows,
        },
        "permutation": {
            "B": B,
            "seed": seed,
            "common_cell_marginal": marg_cal,
            "common_cell_advantage": adv_cal,
            "eligible_individual_count_distribution": eligible_null,
        },
        "primary_pass_rule": {
            "minimum_evaluable_individuals": min_n,
            "calibrated_common_cell_marginal_positive": (
                marg_cal["observed_minus_null_mean"] > 0
            ),
            "upper_tail_le_0_05": (
                marg_cal["p_null_ge_observed"] <= 0.05
            ),
            "passes": passes if role == "primary" else None,
            "sensitivity_cannot_rescue_primary": role != "primary",
        },
        "claim_boundary": {
            "proxy_is_not_verified_roost_colony_or_lek": True,
            "no_new_source_search": True,
            "no_radius_retuning": True,
        },
    }

    out = Path(
        f"results/cross_panel_endpoint_exclusion_{args.panel}_{args.radius}m_v1.json"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "panel": args.panel,
                "radius_m": args.radius,
                "role": role,
                "observed": {
                    "eligible_individuals": observed["eligible_individuals"],
                    "common_cell_marginal": observed["common_cell_marginal"],
                },
                "calibration": marg_cal,
                "passes": payload["primary_pass_rule"]["passes"],
                "qc": {
                    "excluded": qc["events_excluded_within_radius"],
                    "events_after": qc["events_after_exclusion_and_session_reeligibility"],
                    "surviving_sessions": qc["surviving_sessions"],
                },
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
