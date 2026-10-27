#!/usr/bin/env python3
"""Audit original-source GPS near-time *distance bands* from pinned aggregate outputs.

The source GPS originals were previously verified against publisher MD5,
SHA256, original reference joins and independently reconstructed time/position
multisets. This is a POST-INSPECTION algebraic transformation of already
committed ORIGINAL-SOURCE AGGREGATE outcomes, NOT a fresh raw GPS analysis,
ecological encounter inference, social-network observation, or p-value.

Only source/year/season/gap/radius/seed aggregates are processed or emitted.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parent
PINS = {
    "turkey": ("13008932046ad79cdde16e3cbd8b7aacb253668953ac2de34580abc71c99d938",
               {2019: (112, 112), 2020: (21, 21)}),
    "black_bear": ("867c9941b472a0781708e71c084ff595cd62f3c78c9d2d404ee48d4d63dd7bc7",
                   {2019: (0, 0), 2020: (38, 47)}),
    "white_tailed_deer": ("919d0786370d0b298d904d13510571e7dfb67c0ffdd6bc32b54bdaddc847bae6",
                           {2019: (55, 55), 2020: (205, 205)}),
}
GAPS = (900, 1800)
RADII = (0.5, 1.0, 2.0)
BANDS = (
    ("[0,0.5] km", 0.0, 0.5),
    ("(0.5,1] km", 0.5, 1.0),
    ("(1,2] km", 1.0, 2.0),
    ("(2,infinity) km", 2.0, None),
)
SEEDS = tuple(range(12))
EPS = 1e-10
SERIALIZED_OUTPUT = "SUBHOUR_DISTANCE_BANDS_2026_10_21.json"


def close(a, b):
    return math.isclose(a, b, rel_tol=1e-10, abs_tol=EPS)


def _check_number(x, *, bounded=False):
    if isinstance(x, bool) or not isinstance(x, (float, int)) or not math.isfinite(x):
        raise AssertionError("Unexpected nonfinite or nonnumeric source aggregate")
    if bounded and not -EPS <= x <= 1 + EPS:
        raise AssertionError("Original probability is outside [0,1]")
    return float(x)


def signed(values):
    c = Counter(1 if v > 1e-12 else -1 if v < -1e-12 else 0 for v in values)
    return {"positive": c[1], "negative": c[-1], "near_zero": c[0]}


def _observed_seed_bands(index, seed, n_pairs):
    """Return exactly four disjoint distance-band observations for one seed."""
    cumulative = {radius: index[(seed, radius)] for radius in RADII}
    denom = None
    previous_gap = None
    for r in RADII:
        row = cumulative[r]
        if row["seed"] != seed or row["radius_km"] != r:
            raise AssertionError("Original seed-radius keys moved")
        if row["n_matched_dyads"] != n_pairs:
            raise AssertionError("Dyad sample changed across distances")
        if row["n_selected_dyad_dates"] != n_pairs * 28:
            raise AssertionError("Matched dyad-date denominator differs from 28")
        if row["n_selected_direct_fix_pairs"] != n_pairs * 84:
            raise AssertionError("Three original matching fix pairs/date missing")
        current = (row["n_selected_dyad_dates"], row["n_selected_direct_fix_pairs"])
        if denom is not None and denom != current:
            raise AssertionError("Radius changed source GPS observation support")
        denom = current
        gap = (row["winter_mean_abs_recording_gap_seconds"],
               row["summer_mean_abs_recording_gap_seconds"])
        if previous_gap is not None and gap != previous_gap:
            raise AssertionError("Radius changed original GPS observation times")
        previous_gap = gap
        for season in ("winter", "summer"):
            o = _check_number(row[season]["O"], bounded=True)
            n = _check_number(row[season]["N"], bounded=True)
            d = _check_number(row[season]["D"])
            if not close(o - n, d):
                raise AssertionError("Source cumulative O-N=D did not reconcile")
            for key in ("O", "N", "D"):
                if not close(row["winter"][key] - row["summer"][key],
                             row["winter_minus_summer"][key]):
                    raise AssertionError("Original source seasonal difference does not reconcile")
    for season in ("winter", "summer"):
        for variable in ("O", "N"):
            prev = 0.0
            for radius in RADII:
                value = float(cumulative[radius][season][variable])
                if value < prev - EPS:
                    raise AssertionError("Cumulative original spatial proximity is not monotone")
                prev = value

    output = []
    for idx, (label, lower, upper) in enumerate(BANDS):
        season_values = {}
        for season in ("winter", "summer"):
            metrics = {}
            for metric in ("O", "N"):
                lower_value = cumulative[lower][season][metric] if lower else 0.0
                upper_value = cumulative[upper][season][metric] if upper else 1.0
                band_probability = _check_number(upper_value - lower_value)
                if band_probability < -EPS or band_probability > 1 + EPS:
                    raise AssertionError("Disjoint distance-band probability invalid")
                metrics[metric] = max(0.0, min(1.0, band_probability))
            metrics["D"] = metrics["O"] - metrics["N"]
            # Independent reference: consecutive differences of cumulative D.
            low_d = cumulative[lower][season]["D"] if lower else 0.0
            high_d = cumulative[upper][season]["D"] if upper else 0.0
            expected_d = high_d - low_d if upper is not None else -low_d
            if not close(metrics["D"], expected_d):
                raise AssertionError("Band surplus differs from cumulative difference")
            season_values[season] = metrics
        output.append({
            "seed": seed,
            "band": label,
            "winter": season_values["winter"],
            "summer": season_values["summer"],
            "winter_minus_summer_D": (season_values["winter"]["D"]
                                      - season_values["summer"]["D"]),
        })
    for season in ("winter", "summer"):
        for metric, target in (("O", 1.0), ("N", 1.0), ("D", 0.0)):
            if not close(math.fsum(x[season][metric] for x in output), target):
                raise AssertionError("Four distance bands do not form a partition")
    if not close(math.fsum(x["winter_minus_summer_D"] for x in output), 0.0):
        raise AssertionError("All-band seasonal surplus contrasts do not cancel")
    return output


def _summary(seed_rows, label):
    rows = [r for r in seed_rows if r["band"] == label]
    if len(rows) != 12 or {r["seed"] for r in rows} != set(SEEDS):
        raise AssertionError("Declared 12 original source subsamples missing")
    result = {"band": label, "n_seeds": len(rows)}
    for season in ("winter", "summer"):
        result[season] = {metric: statistics.fmean(r[season][metric] for r in rows)
                          for metric in ("O", "N", "D")}
        result[season + "_D_min_max"] = [
            min(r[season]["D"] for r in rows),
            max(r[season]["D"] for r in rows),
        ]
    differences = [r["winter_minus_summer_D"] for r in rows]
    result["winter_minus_summer_D"] = statistics.fmean(differences)
    result["delta_D_seed_signs"] = signed(differences)
    result["winter_D_seed_signs"] = signed([r["winter"]["D"] for r in rows])
    result["summer_D_seed_signs"] = signed([r["summer"]["D"] for r in rows])
    result["delta_D_min_max"] = [min(differences), max(differences)]
    if not close(result["winter"]["D"] - result["summer"]["D"],
                 result["winter_minus_summer_D"]):
        raise AssertionError("Band summary temporal contrast not additive")
    return result


def source_file(root, source):
    path = root / ("SUBHOUR_GEODESIC_" + source.upper() + "_2026_10_20.json")
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != PINS[source][0]:
        raise AssertionError("Pinned original-GPS source output bytes changed")
    obj = json.loads(data)
    if (obj["source"] != source or obj["n_seeds"] != 12
            or obj["timestamp_tolerances_seconds"] != [900, 1800]
            or set(obj["geodesic_radii_km"]) != set(RADII)
            or not obj["complete_original_MD5_SHA256_replay_verified"]
            or not obj["independent_original_native_timestamp_to_position_QC_verified"]
            or obj["GPS_location_error_quantified"]
            or obj["native_clock_absolute_UTC_offset_verified"]
            or obj["source_specific_population_membership_verified"]):
        raise AssertionError("Original-source data provenance/eligibility claim changed")
    return obj


def derive(root=ROOT):
    result = {
        "schema_version": 1,
        "as_of": "2026-10-21",
        "status": "POST_INSPECTION_SOURCE_AGGREGATE_DISTANCE_BAND_REANALYSIS",
        "fixed_design": "DISTANCE_BAND_CLOCK_ALIGNMENT_DESIGN_2026_10_21.md",
        "source_original_verified": "Earlier original publisher MD5 and pinned SHA256; this is secondary aggregate-only derivation",
        "source_input_SHA256": {s: PINS[s][0] for s in PINS},
        "source_DOIs": {
            "turkey": "10.5441/001/1.671",
            "black_bear": "10.5441/001/1.706",
            "white_tailed_deer": "10.5441/001/1.718",
        },
        "tolerances_seconds": list(GAPS),
        "sample_seeds": list(SEEDS),
        "cumulative_input_radii_km": list(RADII),
        "distance_bands": [
            {"label": label, "lower_km_exclusive": lower if lower else None,
             "upper_km_inclusive": upper}
            for label, lower, upper in BANDS
        ],
        "source_years": [],
        "n_valid_source_year_tolerance_groups": 0,
        "n_stopped_source_year_tolerance_groups": 0,
        "n_seed_band_records": 0,
        "n_summary_band_records": 0,
        "caveats": [
            "Same-time GPS distance means recorded near-position proxy, not observed animal interaction",
            "Negative surplus in a distance band is not evidence for biological avoidance",
            "The four per-season distance bands sum to zero surplus by algebra, not by biological selection",
            "Source animal populations, absolute GPS clock basis and tag location accuracy unverified",
            "Repeated animals, dyads and the 12 seed samplings are dependent; no population p-values or confidence intervals",
            "Post-inspection selection of 500m and 1–2km contrasts is disclosed; no cross-taxon generality inferred",
        ],
    }
    for source in PINS:
        obj = source_file(Path(root), source)
        if obj["source_doi"] != result["source_DOIs"][source]:
            raise AssertionError("Published source DOI mismatch")
        groups = {g["year"]: g for g in obj["year_results"]}
        if set(groups) != {2019, 2020}:
            raise AssertionError("A source year is absent from original aggregate")
        for year in (2019, 2020):
            timed = {r["max_abs_timestamp_gap_seconds"]: r
                     for r in groups[year]["time_tolerance_results"]}
            if set(timed) != set(GAPS):
                raise AssertionError("Original 15/30-minute GPS data incomplete")
            for gap in GAPS:
                row = timed[gap]
                expected_n = PINS[source][1][year][GAPS.index(gap)]
                if row["n_clock_matched_dyads"] != expected_n:
                    raise AssertionError("Source time-match dyad risk set changed")
                out = {
                    "source": source,
                    "year": year,
                    "max_abs_timestamp_gap_seconds": gap,
                    "n_source_dyads": groups[year]["n_original_source_geographic_dyads"],
                    "n_matched_dyads": expected_n,
                    "status": row["status"],
                    "seed_band_records": [],
                    "band_summary": [],
                }
                if expected_n < 8:
                    if (row["status"] != "STOP_SMALL_TIMESTAMP_MATCHED_OPPORTUNITY"
                            or row["grid_free_geodesic_seed_results"]):
                        raise AssertionError("Ineligible cohort was coded as zero effect")
                    result["n_stopped_source_year_tolerance_groups"] += 1
                else:
                    if row["status"] != "DESCRIPTIVE_NEAR_SYNCHRONOUS_GPS_NEARBY_PROXY":
                        raise AssertionError("Expected source-year geographic proxy not computed")
                    items = row["grid_free_geodesic_seed_results"]
                    idx = {(r["seed"], r["radius_km"]): r for r in items}
                    if (len(items) != 36 or set(idx) != {(seed, radius)
                        for seed in SEEDS for radius in RADII}):
                        raise AssertionError("Missing/duplicate original radius/seed entries")
                    for seed in SEEDS:
                        out["seed_band_records"].extend(_observed_seed_bands(idx, seed, expected_n))
                    out["band_summary"] = [_summary(out["seed_band_records"], band[0])
                                           for band in BANDS]
                    result["n_valid_source_year_tolerance_groups"] += 1
                    result["n_seed_band_records"] += len(out["seed_band_records"])
                    result["n_summary_band_records"] += len(out["band_summary"])
                result["source_years"].append(out)
    if (result["n_valid_source_year_tolerance_groups"] != 10
            or result["n_stopped_source_year_tolerance_groups"] != 2
            or result["n_seed_band_records"] != 480
            or result["n_summary_band_records"] != 40):
        raise AssertionError("Incomplete set of exploratory source comparisons")
    return result


def _recursive_check(actual, expected, path="root"):
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or actual.keys() != expected.keys():
            raise AssertionError("Derived JSON fields differ at " + path)
        for key in expected:
            _recursive_check(actual[key], expected[key], path + "." + str(key))
    elif isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            raise AssertionError("Derived JSON array shape differs at " + path)
        for index, (got, want) in enumerate(zip(actual, expected)):
            _recursive_check(got, want, path + "[" + str(index) + "]")
    elif isinstance(expected, float) or isinstance(actual, float):
        if not close(_check_number(actual), _check_number(expected)):
            raise AssertionError("Derived float mismatch at " + path)
    elif actual != expected:
        raise AssertionError("Derived reference value mismatch at " + path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify-published", type=Path)
    args = parser.parse_args()
    derived = derive(args.input_dir)
    if args.verify_published:
        stored = json.loads(args.verify_published.read_text())
        _recursive_check(stored, derived)
    if args.output:
        args.output.write_text(json.dumps(derived, indent=2, sort_keys=True,
                                          allow_nan=False) + "\n")
    print(json.dumps({
        "status": "PASS_DISTANCE_BAND_ORIGINAL_SOURCE_AGGREGATE_VERIFIED",
        "n_groups": derived["n_valid_source_year_tolerance_groups"],
        "n_stop": derived["n_stopped_source_year_tolerance_groups"],
        "n_seed_band_records": derived["n_seed_band_records"],
        "n_summary_rows": derived["n_summary_band_records"],
        "published_reconciled": bool(args.verify_published),
    }))


if __name__ == "__main__":
    main()
