#!/usr/bin/env python3
"""Two-hour deer displacement repeatability and seasonal geographic sharing.

No animal identifiers, coordinates or exact tracking dates are serialized.
R is a proper-score contrast conditional on observed common contexts, not a
randomized identity test. X is geographic occupancy overlap, not encounters.
"""
from __future__ import annotations

import argparse
from bisect import bisect_right
import calendar
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import statistics


def mean(values):
    return statistics.fmean(values)


def quantile(values, q):
    values = sorted(values)
    if not values:
        return None
    pos = (len(values) - 1) * q
    low = math.floor(pos)
    high = min(low + 1, len(values) - 1)
    return values[low] + (values[high] - values[low]) * (pos - low)


def distribution_summary(values):
    values = list(values)
    return {"n": len(values), "mean": mean(values) if values else None,
            **{label: quantile(values, q) for label, q in
               [("min", 0), ("q25", .25), ("median", .5), ("q75", .75), ("max", 1)]}}


class WeightedDistribution:
    """Finite empirical distribution with O(log n) exact CRPS queries."""
    __slots__ = ("points", "values", "prefix_w", "prefix_wz", "mean", "dispersion")

    def __init__(self, points):
        masses = defaultdict(float)
        for value, weight in points:
            if not (math.isfinite(value) and math.isfinite(weight)) or weight < 0:
                raise ValueError("Finite values and nonnegative weights required")
            if weight:
                masses[value] += weight
        total = sum(masses.values())
        if total <= 0:
            raise ValueError("A distribution needs positive mass")
        self.points = tuple((z, w / total) for z, w in sorted(masses.items()))
        self.values = tuple(z for z, _ in self.points)
        self.prefix_w, self.prefix_wz = [0.0], [0.0]
        self.dispersion = 0.0
        for z, w in self.points:
            self.dispersion += w * (z * self.prefix_w[-1] - self.prefix_wz[-1])
            self.prefix_w.append(self.prefix_w[-1] + w)
            self.prefix_wz.append(self.prefix_wz[-1] + w * z)
        self.mean = self.prefix_wz[-1]

    @classmethod
    def mixture(cls, components):
        points = []
        for distribution, weight in components:
            if not math.isfinite(weight) or weight < 0:
                raise ValueError("Invalid mixture weight")
            points.extend((z, w * weight) for z, w in distribution.points)
        return cls(points)

    def crps(self, value):
        if not math.isfinite(value):
            raise ValueError("Finite observation required")
        k = bisect_right(self.values, value)
        absolute = (value * (2 * self.prefix_w[k] - 1)
                    + self.mean - 2 * self.prefix_wz[k])
        score = absolute - self.dispersion
        if score < -1e-9:
            raise ArithmeticError("CRPS unexpectedly negative")
        return max(0.0, score)

    def quantile(self, probability):
        if not 0 <= probability <= 1:
            raise ValueError("Probability outside [0,1]")
        for k, (z, _) in enumerate(self.points):
            if self.prefix_w[k + 1] >= probability - 1e-14:
                return z
        return self.values[-1]


def balanced_profile(day_values):
    by_day = defaultdict(list)
    for day, value in day_values:
        by_day[day].append(value)
    if not by_day:
        raise ValueError("Empty day-balanced profile")
    return WeightedDistribution((value, 1 / len(by_day) / len(values))
                                for values in by_day.values() for value in values)


def peer_distribution(profiles, target):
    others = [p for animal, p in profiles.items() if animal != target]
    if not others:
        raise ValueError("No other animal has a supported training profile")
    return WeightedDistribution.mixture([(p, 1 / len(others)) for p in others])


def context(row, width_km, lat_cos, origin):
    return (math.floor(row.lon * 111.32 * lat_cos / width_km + origin[0]),
            math.floor(row.lat * 111.32 / width_km + origin[1]), row.hour_bin)


def outcome(row):
    return math.log1p(row.speed_kmh * 2 / .1)


def _fold_support(train, test, width_km, lat_cos, origin):
    by_animal_context = defaultdict(list)
    for row in train:
        by_animal_context[(row.animal, context(row, width_km, lat_cos, origin))].append(row)
    qualified = {key: rows for key, rows in by_animal_context.items()
                 if len(rows) >= 15 and len({r.day for r in rows}) >= 3}
    donors = defaultdict(set)
    for animal, ctx in qualified:
        donors[ctx].add(animal)
    common = {ctx for ctx, animals in donors.items() if len(animals) >= 2}
    test_by = defaultdict(list)
    for row in test:
        ctx = context(row, width_km, lat_cos, origin)
        if ctx in common and (row.animal, ctx) in qualified:
            test_by[row.animal].append((row, ctx))
    evaluated = {a: rows for a, rows in test_by.items()
                 if len(rows) >= 15 and len({r.day for r, _ in rows}) >= 3}
    return {"qualified": qualified, "donors": donors, "common": common,
            "evaluated": evaluated, "train_dates": {r.day for r in train},
            "test_dates": {r.day for r in test}}


def analyze_month_r(steps, year, month, lat_cos, width_km=5, origin=(0, 0)):
    rows = [r for r in steps if r.year == year and r.month == month]
    by_animal = defaultdict(list)
    for r in rows:
        by_animal[r.animal].append(r)
    initial = {a for a, seq in by_animal.items()
               if len(seq) >= 80 and len({r.day for r in seq}) >= 10}
    eligible = [r for r in rows if r.animal in initial]
    split = calendar.monthrange(year, month)[1] // 2
    first = [r for r in eligible if r.dt.day <= split]
    second = [r for r in eligible if r.dt.day > split]
    folds = [_fold_support(first, second, width_km, lat_cos, origin),
             _fold_support(second, first, width_km, lat_cos, origin)]
    for fold in folds:
        if fold['train_dates'] & fold['test_dates']:
            raise AssertionError("Training and test dates overlap")
    animals = set(folds[0]['evaluated']) & set(folds[1]['evaluated'])
    report = {
        "year": year, "month": month, "context_km": width_km,
        "origin_x_fraction": origin[0], "origin_y_fraction": origin[1],
        "n_source_step_animals": len(by_animal), "n_initial_animals": len(initial),
        "n_evaluated_animals": len(animals), "all_source_month_steps": len(rows),
        "initial_eligible_steps": len(eligible), "calendar_separation_verified": True,
        "fold_support": [{"n_qualified_training_animals": len({a for a, _ in f['qualified']}),
                          "n_common_contexts": len(f['common']),
                          "n_evaluation_eligible_animals": len(f['evaluated'])} for f in folds],
        "status": "DESCRIPTIVE_CROSSFIT_DISPLACEMENT_R" if len(animals) >= 2 else
                  "NOT_ESTIMABLE_BOTH_FOLDS_COMMON_CONTEXT_SUPPORT",
        "R_gain": None, "peer_CRPS": None, "personal_CRPS": None,
        "relative_CRPS_reduction": None, "heldout_steps": 0,
        "heldout_animal_days": 0,
    }
    internal = {"animals": animals, "animal_gain": {}}
    if len(animals) < 2:
        return report, internal
    # This cohort and every score mask are determined before movement scores.
    daily_scores = defaultdict(lambda: defaultdict(list))
    raw_displacement = defaultdict(lambda: defaultdict(list))
    peer_counts = []
    for fold in folds:
        profiles = defaultdict(dict)
        days = {}
        for (animal, ctx), seq in fold['qualified'].items():
            if ctx in fold['common']:
                profiles[ctx][animal] = balanced_profile((r.day, outcome(r)) for r in seq)
                days[(animal, ctx)] = len({r.day for r in seq})
        model_cache = {}
        for animal in sorted(animals):
            for row, ctx in fold['evaluated'][animal]:
                key = (animal, ctx)
                if key not in model_cache:
                    peer = peer_distribution(profiles[ctx], animal)
                    alpha = days[key] / (days[key] + 5)
                    personal = WeightedDistribution.mixture(
                        [(peer, 1 - alpha), (profiles[ctx][animal], alpha)])
                    model_cache[key] = (peer, personal)
                peer, personal = model_cache[key]
                y = outcome(row)
                daily_scores[animal][row.day].append((peer.crps(y), personal.crps(y)))
                raw_displacement[animal][row.day].append(row.speed_kmh * 2)
                peer_counts.append(len(profiles[ctx]) - 1)
    animal_peer, animal_personal = {}, {}
    for animal, daily in daily_scores.items():
        animal_peer[animal] = mean(mean(s[0] for s in seq) for seq in daily.values())
        animal_personal[animal] = mean(mean(s[1] for s in seq) for seq in daily.values())
    gains = {a: animal_peer[a] - animal_personal[a] for a in sorted(animals)}
    displacement = WeightedDistribution(
        (value, 1 / len(animals) / len(daily) / len(values))
        for daily in raw_displacement.values() for values in daily.values() for value in values)
    peer_score, personal_score = mean(animal_peer.values()), mean(animal_personal.values())
    report.update({
        "R_gain": mean(gains.values()), "peer_CRPS": peer_score,
        "personal_CRPS": personal_score,
        "relative_CRPS_reduction": mean(gains.values()) / peer_score if peer_score > 0 else None,
        "heldout_steps": sum(len(seq) for daily in daily_scores.values() for seq in daily.values()),
        "heldout_animal_days": sum(len(daily) for daily in daily_scores.values()),
        "all_steps_from_final_animals": sum(len(by_animal[a]) for a in animals),
        "individual_gain_distribution": distribution_summary(gains.values()),
        "fraction_animals_positive_gain": sum(v > 0 for v in gains.values()) / len(gains),
        "other_training_animals_per_scored_step": distribution_summary(peer_counts),
        "standardized_2h_displacement_km_equal_animal_day": {
            "mean": displacement.mean,
            **{label: displacement.quantile(q) for label, q in [('q25', .25), ('median', .5), ('q75', .75)]}},
    })
    report['heldout_step_fraction_final_animals'] = report['heldout_steps'] / report['all_steps_from_final_animals']
    internal['animal_gain'] = gains
    return report, internal


def select_constant_cohort(events, year):
    counts, days = Counter(), defaultdict(set)
    for row in events:
        if row.year == year:
            counts[(row.animal, row.month)] += 1
            days[(row.animal, row.month)].add(row.day)
    return {animal for animal, _ in counts if all(
        counts[(animal, m)] >= 80 and len(days[(animal, m)]) >= 10 for m in range(1, 13))}


def seasonal_pair_contrast(monthly_pair_scores):
    winter, summer = defaultdict(list), defaultdict(list)
    for month, scores in monthly_pair_scores.items():
        target = winter if month in (12, 1, 2) else summer if month in (6, 7, 8) else None
        if target is not None:
            for pair, score in scores.items():
                target[pair].append(score)
    pairs = [p for p in winter.keys() & summer.keys() if len(winter[p]) >= 2 and len(summer[p]) >= 2]
    w = [mean(winter[p]) for p in pairs]
    s = [mean(summer[p]) for p in pairs]
    d = [a - b for a, b in zip(w, s)]
    return {"n_pairs": len(pairs), "n_animals": len({a for p in pairs for a in p}),
            "winter_mean": mean(w) if w else None,
            "summer_mean": mean(s) if s else None,
            "winter_minus_summer_mean": mean(d) if d else None,
            "pair_difference_distribution": distribution_summary(d),
            "fraction_pairs_winter_greater": sum(v > 0 for v in d) / len(d) if d else None}


def seasonal_individual_r(monthly_gains):
    winter, summer = defaultdict(list), defaultdict(list)
    for month, gains in monthly_gains.items():
        target = winter if month in (12, 1, 2) else summer if month in (6, 7, 8) else None
        if target is not None:
            for animal, gain in gains.items():
                target[animal].append(gain)
    animals = [a for a in winter.keys() & summer.keys() if len(winter[a]) >= 2 and len(summer[a]) >= 2]
    w, s = [mean(winter[a]) for a in animals], [mean(summer[a]) for a in animals]
    differences = [a - b for a, b in zip(w, s)]
    return {"n_matched_animals": len(animals),
            "winter_mean_R": mean(w) if w else None,
            "summer_mean_R": mean(s) if s else None,
            "winter_minus_summer_R": mean(differences) if differences else None,
            "individual_difference_distribution": distribution_summary(differences),
            "peer_reference_changes_across_months": True}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def run(events_path, reference_path, output, sensitivity_output):
    from deer_source_pipeline_v1 import load_source, make_steps, source_lat_cos, group_steps_by_month
    from deer_geography_v1 import compute_geography_overlap
    events, event_audit, receipts = load_source(events_path, reference_path)
    steps, step_audit = make_steps(events)
    lat_cos = source_lat_cos(events)
    by_steps = group_steps_by_month(steps)
    by_events = defaultdict(list)
    for row in events:
        by_events[(row.year, row.month)].append(row)
    constant = {year: select_constant_cohort(events, year) for year in (2018, 2019, 2020)}
    root = Path(__file__).resolve().parent
    result = {"schema_version": 1, "as_of": "2026-10-20",
        "source_doi": "10.5441/001/1.708", "source_receipts": receipts,
        "event_audit": event_audit, "step_audit": step_audit,
        "design_sha256": hashlib.sha256((root / 'DEER_SEASONAL_RX_DESIGN_2026_10_20.md').read_bytes()).hexdigest(),
        "script_sha256": {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
            for name in ('deer_source_pipeline_v1.py', 'deer_seasonal_rx_v1.py', 'deer_geography_v1.py')},
        "claim_scope": "Exploratory one-source adult-female herd patterns; no cross-taxon inference or causal partitioning claim",
        "R_definition": "Peer-only balanced empirical CRPS minus day-shrunk personal-mixture CRPS for log1p(2h-standardized displacement/0.1km)",
        "uncertainty": "Individual/pair empirical distributions and declared scale/origin sensitivities; no population confidence intervals or biological p-values",
        "source_clock_verified_UTC": False, "T_encounter_estimable": False,
        "E_resource_exposure_estimable": False, "monthly": [],
        "constant_cohort_by_year": {str(y): len(a) for y, a in constant.items()},
        "seasonal_constant_cohort_X": [], "seasonal_paired_R": [],
        "source_step_speed_kmh_diagnostics": {
            "max": max(r.speed_kmh for r in steps),
            "n_above_10_8": sum(r.speed_kmh > 10.8 for r in steps),
            "n_above_20": sum(r.speed_kmh > 20 for r in steps),
            "primary_speed_filter_applied": False},
    }
    sensitivities = {"schema_version": 1, "as_of": "2026-10-20", "monthly_R": []}
    constant_pairs = defaultdict(dict)
    gains = defaultdict(dict)
    for year in (2018, 2019, 2020):
        for month in range(1, 13):
            key = (year, month)
            month_steps, month_events = by_steps.get(key, []), by_events.get(key, [])
            r, internal = analyze_month_r(month_steps, year, month, lat_cos)
            r['matched_X'], _ = compute_geography_overlap(month_events, internal['animals'], lat_cos=lat_cos)
            r['constant_cohort_X'], pairs = compute_geography_overlap(month_events, constant[year], lat_cos=lat_cos)
            constant_pairs[year][month] = pairs
            gains[year][month] = internal['animal_gain']
            result['monthly'].append(r)
            for width, origin in [(10, (0, 0)), (5, (.5, 0)), (5, (0, .5)), (5, (.5, .5))]:
                sr, _ = analyze_month_r(month_steps, year, month, lat_cos, width, origin)
                sensitivities['monthly_R'].append(sr)
            print(json.dumps({"year": year, "month": month, "n_R": r['n_evaluated_animals'],
                              "R_gain": r['R_gain'], "n_constant": len(constant[year])}), flush=True)
    for year in (2018, 2019, 2020):
        keys = sorted(set(k for p in constant_pairs[year].values() for k in p))
        for scale, ox, oy in keys:
            monthly = {m: p.get((scale, ox, oy), {}) for m, p in constant_pairs[year].items()}
            contrast = seasonal_pair_contrast(monthly)
            contrast.update({"year": year, "scale_km": scale, "origin_x_fraction": ox, "origin_y_fraction": oy})
            result['seasonal_constant_cohort_X'].append(contrast)
        contrast = seasonal_individual_r(gains[year])
        contrast['year'] = year
        result['seasonal_paired_R'].append(contrast)
    write_json(output, result)
    write_json(sensitivity_output, sensitivities)
    print(json.dumps({"output": str(output), "sensitivity_output": str(sensitivity_output),
                      "n_months": len(result['monthly']), "n_R_sensitivities": len(sensitivities['monthly_R'])}), flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--events', type=Path, required=True)
    p.add_argument('--reference', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--sensitivity-output', type=Path, required=True)
    args = p.parse_args()
    run(args.events, args.reference, args.output, args.sensitivity_output)


if __name__ == '__main__':
    main()
