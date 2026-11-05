#!/usr/bin/env python3
"""Calendar-separated, fixed-support fox identity correspondence and matched X.

The enumerated reference is conditional on uniform allowable correspondence.
It is not an experimentally randomized test of biological individuality.
Input animal identifiers and coordinates are used internally, never exported.
"""
from __future__ import annotations

import argparse
import calendar
from collections import Counter, defaultdict
import hashlib
import itertools
import json
import math
from pathlib import Path
import statistics


def day_mean(day_values):
    days = defaultdict(list)
    for day, value in day_values:
        days[day].append(value)
    if not days:
        raise ValueError("No evaluable dates")
    return statistics.fmean(statistics.fmean(values) for values in days.values())


def calendar_split(rows, month):
    year, number = map(int, month.split("-"))
    cut = f"{month}-{calendar.monthrange(year, number)[1] // 2:02d}"
    rows = [r for r in rows if r["month"] == month]
    return [r for r in rows if r["day"] <= cut], [r for r in rows if r["day"] > cut]


def outcome(row, assay):
    if assay == "speed_three":
        speed = row["speed"]
        return 0 if speed < .05 else 1 if speed < .5 else 2
    if assay == "speed_binary":
        return int(row["speed"] >= .5)
    if assay == "activity":
        x, y = row.get("activity_x"), row.get("activity_y")
        if x is None or y is None or not math.isfinite(x) or not math.isfinite(y):
            return None
        return int(x >= 2 and y >= 2)
    raise ValueError("Unknown assay")


def quantile(values, probability):
    values = sorted(values)
    if not values:
        return None
    z = probability * (len(values) - 1)
    i = math.floor(z)
    return values[i] + (values[min(i + 1, len(values) - 1)] - values[i]) * (z - i)


def mapping_reference(scores, allowed):
    """Enumerate every compatible perfect matching, including the true one."""
    n = len(scores)
    if not 1 <= n <= 10 or len(allowed) != n:
        raise ValueError("Exact reference requires 1--10 evaluated animals")
    if any(len(row) != n for row in scores + allowed):
        raise ValueError("Matrices must be square")
    if any(not allowed[i][i] for i in range(n)):
        raise ValueError("True correspondence must have complete donor support")
    candidates = [[j for j in range(n) if allowed[i][j]] for i in range(n)]
    if any(scores[i][j] is None or not math.isfinite(scores[i][j])
           for i in range(n) for j in candidates[i]):
        raise ValueError("An allowed donor must have a finite score on the fixed mask")
    order = sorted(range(n), key=lambda i: (len(candidates[i]), i))
    mapping = [-1] * n
    seen = [set() for _ in range(n)]
    values = []

    def walk(k, used, total):
        if k == n:
            values.append(total / n)
            for i, j in enumerate(mapping):
                seen[i].add(j)
            return
        i = order[k]
        for j in candidates[i]:
            if used & (1 << j):
                continue
            mapping[i] = j
            walk(k + 1, used | (1 << j), total + scores[i][j])

    walk(0, 0, 0.0)
    observed = statistics.fmean(scores[i][i] for i in range(n))
    null_mean = statistics.fmean(values)
    count = len(values)
    tail = sum(v >= observed - 1e-12 for v in values) / count if count > 1 else None
    return {
        "status": "NOT_CALIBRATABLE_IDENTITY_ONLY" if count == 1 else
                  "DESCRIPTIVE_LOW_MAPPING_RESOLUTION" if count < 20 else
                  "CONDITIONAL_MAPPING_REFERENCE_ASSUMPTION_REQUIRED",
        "n_evaluated_animals": n,
        "n_movable_animals": sum(len(s) > 1 for s in seen),
        "n_admissible_maps": count,
        "minimum_attainable_tail_fraction": 1 / count if count > 1 else None,
        "observed_gain": observed,
        "reference_mean_gain": null_mean,
        "excess_over_reference": observed - null_mean,
        "reference_q025": quantile(values, .025),
        "reference_q975": quantile(values, .975),
        "tail_fraction": tail,
        "n_positive_personal_vs_pooled_animals": sum(scores[i][i] > 0 for i in range(n)),
        "individual_gain_range": [min(scores[i][i] for i in range(n)), max(scores[i][i] for i in range(n))],
        "biological_randomization_p_value": None,
    }


def grid(row, width, lat_cos, dx=0.0, dy=0.0):
    return (math.floor((row["lon"] * 111.32 * lat_cos + dx) / width),
            math.floor((row["lat"] * 111.32 + dy) / width))


def shared_context(row, width, lat_cos):
    return grid(row, width, lat_cos) + (row["dt"].hour // 6,)


def occupancy(rows, width, lat_cos, dx=0.0, dy=0.0):
    days = defaultdict(list)
    for row in rows:
        days[row["day"]].append(row)
    histogram = defaultdict(float)
    for values in days.values():
        w = 1 / (len(days) * len(values))
        for row in values:
            histogram[grid(row, width, lat_cos, dx, dy)] += w
    return histogram


def overlap(a, b):
    return sum(min(p, b.get(cell, 0.0)) for cell, p in a.items())


def matched_x(events, animals, month, lat_cos):
    _, test_events = calendar_split(events, month)
    grouped = {animal: [] for animal in animals}
    for row in test_events:
        if row["animal"] in grouped:
            grouped[row["animal"]].append(row)
    days = {a: {r["day"] for r in seq} for a, seq in grouped.items()}
    pairs = [(a, b) for a, b in itertools.combinations(animals, 2) if len(days[a] & days[b]) >= 3]
    answer = {
        "n_animals": len(animals), "heldout_qc_fixes": sum(map(len, grouped.values())),
        "n_supported_dependent_dyads": len(pairs),
        "n_dyads_missing_shared_date_support": math.comb(len(animals), 2) - len(pairs),
        "axis": "X_2D_GEOGRAPHIC_OVERLAP_NOT_RESOURCE_OR_SYNCHRONOUS_ENCOUNTERS",
        "uses_full_qc_geography_not_selected_R_contexts": True,
        "scales": [],
    }
    for width in (.5, 1.0, 2.0):
        shifts = []
        original = []
        for dx, dy in ((0, 0), (width / 2, 0), (0, width / 2), (width / 2, width / 2)):
            hist = {a: occupancy(seq, width, lat_cos, dx, dy) for a, seq in grouped.items()}
            values = [overlap(hist[a], hist[b]) for a, b in pairs]
            if values:
                shifts.append(statistics.fmean(values))
            if dx == dy == 0:
                original = values
        answer["scales"].append({
            "grid_km": width,
            "mean_overlap": statistics.fmean(original) if original else None,
            "median_overlap": statistics.median(original) if original else None,
            "n_zero_overlap_dyads": sum(v == 0 for v in original),
            "origin_shift_mean_range": [min(shifts), max(shifts)] if shifts else None,
        })
    return answer


def cohort_analysis(all_steps, events, site, year, month, width, lat_cos):
    rows = [r for r in all_steps if r["site"] == site and r["year"] == year and r["month"] == month]
    initial = defaultdict(list)
    for row in rows:
        initial[row["animal"]].append(row)
    eligible = {a for a, seq in initial.items() if len(seq) >= 80 and len({r["day"] for r in seq}) >= 6}
    rows = [r for r in rows if r["animal"] in eligible]
    train, test = calendar_split(rows, month)
    assert not ({r["day"] for r in train} & {r["day"] for r in test})
    train_by = defaultdict(list)
    for row in train:
        train_by[(row["animal"], shared_context(row, width, lat_cos))].append(row)
    supported = {key for key, seq in train_by.items() if len(seq) >= 15 and len({r["day"] for r in seq}) >= 2}
    donors = defaultdict(set)
    for animal, ctx in supported:
        donors[ctx].add(animal)
    common = {ctx for ctx, values in donors.items() if len(values) >= 2}
    eval_by = defaultdict(list)
    for row in test:
        ctx = shared_context(row, width, lat_cos)
        if ctx in common and (row["animal"], ctx) in supported:
            eval_by[row["animal"]].append(row)
    eval_by = {a: seq for a, seq in eval_by.items() if len(seq) >= 15 and len({r["day"] for r in seq}) >= 3}
    animals = sorted(eval_by)
    contexts = {a: {shared_context(r, width, lat_cos) for r in seq} for a, seq in eval_by.items()}
    report = {
        "site": site, "reference_deployment_year": year, "month": month,
        "grid_km": width, "clock_bin_hours": 6,
        "n_source_month_animals": len(initial),
        "n_source_month_eligible_animals": len(eligible),
        "training_steps": len(train), "all_eligible_heldout_steps": len(test),
        "n_common_training_contexts": len(common),
        "n_evaluated_animals": len(animals),
        "heldout_shared_context_steps": sum(map(len, eval_by.values())),
        "heldout_animal_days": sum(len({r["day"] for r in seq}) for seq in eval_by.values()),
        "no_train_test_calendar_date_overlap": True,
        "status": "EXPLORATORY_MATCHED_R_X" if len(animals) >= 2 else "NOT_ESTIMABLE_SHARED_HOLDOUT_SUPPORT",
        "assays": {},
    }
    if len(animals) < 2:
        return report
    allowed = [[all((donor, ctx) in supported for ctx in contexts[target])
                for donor in animals] for target in animals]
    # The digest contains only array dimensions / counts, not identifiers/locations.
    report["allowed_matrix_sha256"] = hashlib.sha256(json.dumps(allowed).encode()).hexdigest()
    report["n_supported_target_donor_entries"] = sum(map(sum, allowed))
    report["n_targets_with_some_allowed_other_donor"] = sum(any(allowed[i][j] for j in range(len(animals)) if j != i) for i in range(len(animals)))

    for assay, nclasses in (("speed_three", 3), ("speed_binary", 2), ("activity", 2)):
        relevant_train = [r for (a, ctx), seq in train_by.items() if (a, ctx) in supported and ctx in common for r in seq]
        relevant_test = [r for seq in eval_by.values() for r in seq]
        missing_train = sum(outcome(r, assay) is None for r in relevant_train)
        missing_test = sum(outcome(r, assay) is None for r in relevant_test)
        if missing_train or missing_test:
            report["assays"][assay] = {"status": "NOT_ESTIMABLE_MATCHED_ASSAY_MISSING",
                                        "missing_training": missing_train, "missing_test": missing_test}
            continue
        counts = {(a, ctx): Counter(outcome(r, assay) for r in seq)
                  for (a, ctx), seq in train_by.items() if (a, ctx) in supported and ctx in common}
        pooled = {}
        personal = {}
        for ctx in common:
            total = Counter()
            for donor in donors[ctx]:
                total.update(counts[(donor, ctx)])
            denominator = sum(total.values()) + .5 * nclasses
            pooled[ctx] = [(total[k] + .5) / denominator for k in range(nclasses)]
            for donor in donors[ctx]:
                own = counts[(donor, ctx)]
                size = sum(own.values())
                personal[(donor, ctx)] = [(own[k] + 15 * pooled[ctx][k]) / (size + 15) for k in range(nclasses)]
        scores = [[None] * len(animals) for _ in animals]
        for i, target in enumerate(animals):
            for j, donor in enumerate(animals):
                if not allowed[i][j]:
                    continue
                weighted = []
                for row in eval_by[target]:
                    ctx, value = shared_context(row, width, lat_cos), outcome(row, assay)
                    weighted.append((row["day"], math.log(personal[(donor, ctx)][value] / pooled[ctx][value])))
                scores[i][j] = day_mean(weighted)
        ref = mapping_reference(scores, allowed)
        fractions = [[day_mean((r["day"], float(outcome(r, assay) == k)) for r in eval_by[a])
                      for k in range(nclasses)] for a in animals]
        ref["heldout_class_fraction_equal_animal_day"] = [statistics.fmean(v[k] for v in fractions) for k in range(nclasses)]
        ref["heldout_last_class_fraction_individual_range"] = [min(v[-1] for v in fractions), max(v[-1] for v in fractions)]
        report["assays"][assay] = ref
    cohort_events = [r for r in events if r["site"] == site and r["year"] == year]
    report["matched_X"] = matched_x(cohort_events, animals, month, lat_cos)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    from fox_source_pipeline_v1 import load_source, make_steps, source_lat_cos
    events, qc, receipts = load_source(args.events, args.reference)
    steps, step_audit = make_steps(events)
    lat_cos = source_lat_cos(events)
    root = Path(__file__).resolve().parent
    old = json.loads((root / "FOX_COMMON_PLACE_HELDOUT_R_PILOT_2026_10_19.json").read_text())
    results = []
    for row in old["results"]:
        for width in (1.0, 2.0):
            result = cohort_analysis(steps, events, row["source_site"], row["source_reference_deploy_year"], row["month"], width, lat_cos)
            results.append(result)
            assay = result.get("assays", {}).get("speed_three", {})
            print(json.dumps({"site": result["site"], "month": result["month"], "grid_km": width,
                              "n": result["n_evaluated_animals"], "B": assay.get("observed_gain"),
                              "maps": assay.get("n_admissible_maps"), "tail": assay.get("tail_fraction")}))
    out = {
        "schema_version": 1, "date": "2026-10-20", "source_doi": "10.5441/001/1.304",
        "design": "FOX_MATCHED_CORRESPONDENCE_DESIGN_2026_10_20.md",
        "evidence_status": "EXPLORATORY_SOURCE_TEMPORAL_CORRESPONDENCE_AND_MATCHED_GEOGRAPHIC_X",
        "source_receipts": receipts, "observation_audit": qc, "step_audit": step_audit,
        "n_preselected_cohort_months": len(old["results"]), "n_spatial_scenarios": 2,
        "source_positions_exported": False, "individual_identifiers_exported": False,
        "biological_randomization_p_values_reported": False,
        "results": results,
        "limitations": [
            "Uniform support-compatible identity correspondence is an explicit observational reference assumption, not an established randomized biological null.",
            "The three assays use the same instruments and dates and are not independent replications.",
            "Ten source-months reuse animals within four deployment cohorts at two sites; animals were not permanently marked between years.",
            "GPS error, collar fit, duty cycle, sex, reproductive state and fine-scale geography remain possible identity carriers.",
            "Shared 1-km/6-hour contexts do not establish identical microhabitat or realized encounters.",
            "X is geographic overlap and is scale-sensitive. Resource exposure, diet, competition and cross-taxon mechanisms remain unmeasured.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
