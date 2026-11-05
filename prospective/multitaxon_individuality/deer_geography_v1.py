#!/usr/bin/env python3
"""Pair-date-balanced occupancy overlap for one source calendar month.

This module accepts validated source ``Event`` objects and an already selected
cohort. It neither selects animals by overlap nor reads source files. Original
identities, dates, positions, and grid cells stay internal. The first return
value is an aggregate, JSON-safe report; the second deliberately contains
internal pair identities for matched-cohort comparisons and MUST NOT be
serialized into public artifacts.

For each animal-date, GPS-fix counts define a probability distribution over
grid cells. For each pair with at least seven shared dates, each animal's
daily distributions are averaged over exactly that pair's shared dates. The
overlap is the sum of the minimum probability masses across cells. Dates and
pairs receive equal weight at their respective averaging stages. This is
monthly geographic occupancy overlap, not simultaneous proximity, association,
resource use, competition, or biological niche overlap.
"""
from __future__ import annotations

import math
from collections import Counter, defaultdict
from itertools import combinations

DEFAULT_SCALES_KM = (1.0, 2.0, 5.0, 10.0)
DEFAULT_ORIGINS = ((0.0, 0.0), (0.5, 0.0), (0.0, 0.5), (0.5, 0.5))
KM_PER_DEGREE = 111.32


def _quantile(sorted_values, probability):
    """Linear interpolation at (n - 1) * probability; null for no values."""
    if not sorted_values:
        return None
    position = (len(sorted_values) - 1) * probability
    lo = math.floor(position)
    hi = math.ceil(position)
    fraction = position - lo
    return float(sorted_values[lo] * (1 - fraction) + sorted_values[hi] * fraction)


def _day_summary(values):
    ordered = sorted(values)
    return {"n": len(ordered), "min": ordered[0] if ordered else None,
            "q25": _quantile(ordered, 0.25), "median": _quantile(ordered, 0.5),
            "q75": _quantile(ordered, 0.75), "p95": _quantile(ordered, 0.95),
            "max": ordered[-1] if ordered else None}


def _overlap_summary(values):
    ordered = sorted(values)
    return {"mean": math.fsum(ordered) / len(ordered) if ordered else None,
            "median": _quantile(ordered, 0.5), "q25": _quantile(ordered, 0.25),
            "q75": _quantile(ordered, 0.75),
            "zero_fraction": sum(value == 0 for value in ordered) / len(ordered) if ordered else None}


def compute_geography_overlap(events, selected_animals, *, lat_cos,
                              min_shared_days=7, scales_km=DEFAULT_SCALES_KM,
                              origins=DEFAULT_ORIGINS):
    """Return ``(aggregate_report, internal_pair_scores)`` for a single month.

    ``events`` is any iterable exposing ``animal``, ordinal ``day``, ``year``,
    integer ``month``, ``lat``, and ``lon``. Only selected animals contribute.
    ``lat_cos`` is the fixed cosine from the source loader, shared across all
    months, cohorts, grids, and origins; this function never estimates it.

    Projected kilometers are x = lon * 111.32 * lat_cos and y = lat * 111.32.
    Grid indices are floor(x / scale + origin_x_fraction) and likewise for y.
    Origins are positive, dimensionless shifts in [0, 1), matching the fox
    audit convention. No coordinates or cell indices enter the report.

    ``n_animals`` counts distinct selected identities, including any without
    events, while ``n_animals_observed`` counts those with retained events.
    Shared-date summaries include all possible pairs and valid pairs separately.
    Unsupported overlap is null, never zero. Supported pair scores are equally
    weighted in each grid's summary.

    Internal scores have keys ``(scale_km, origin_x_fraction,
    origin_y_fraction)``, then sorted ``(animal_a, animal_b)`` tuples. Pairs
    below the date threshold are absent. These identity-bearing dictionaries
    are for in-memory matched-pair comparisons only.
    """
    if not math.isfinite(lat_cos) or not 0 < lat_cos <= 1:
        raise ValueError("lat_cos must be finite and in (0, 1]")
    if isinstance(min_shared_days, bool) or not isinstance(min_shared_days, int) or min_shared_days < 1:
        raise ValueError("min_shared_days must be a positive integer")
    scales = tuple(float(scale) for scale in scales_km)
    shifts = tuple((float(x), float(y)) for x, y in origins)
    if not scales or any(not math.isfinite(scale) or scale <= 0 for scale in scales):
        raise ValueError("Grid scales must be finite and positive")
    if not shifts or any(not math.isfinite(value) or not 0 <= value < 1
                         for shift in shifts for value in shift):
        raise ValueError("Grid origin fractions must be finite and in [0, 1)")
    if len(set(scales)) != len(scales) or len(set(shifts)) != len(shifts):
        raise ValueError("Grid scales and origins must not contain duplicates")

    animals = tuple(sorted(set(selected_animals)))
    selected = set(animals)
    projected = {animal: defaultdict(list) for animal in animals}
    source_month = None
    for event in events:
        if event.animal not in selected:
            continue
        current_month = (event.year, event.month)
        if source_month is None:
            source_month = current_month
        elif current_month != source_month:
            raise ValueError("Geography input must contain one calendar month")
        if not math.isfinite(event.lat) or not math.isfinite(event.lon):
            raise ValueError("Geography input contains an invalid position")
        projected[event.animal][event.day].append(
            (event.lon * KM_PER_DEGREE * lat_cos, event.lat * KM_PER_DEGREE))

    available_days = {animal: set(by_day) for animal, by_day in projected.items()}
    supported_pairs = []
    all_shared_day_counts = []
    for animal_a, animal_b in combinations(animals, 2):
        shared_days = tuple(sorted(available_days[animal_a] & available_days[animal_b]))
        all_shared_day_counts.append(len(shared_days))
        if len(shared_days) >= min_shared_days:
            supported_pairs.append((animal_a, animal_b, shared_days))

    report = {
        "method": "equal-date pair-shared-calendar-date occupancy intersection",
        "clock": "native_source_calendar",
        "pair_weighting": "equal",
        "quantile_method": "linear interpolation at (n-1)*probability",
        "n_animals": len(animals),
        "n_animals_observed": sum(bool(days) for days in available_days.values()),
        "n_pairs_possible": len(all_shared_day_counts),
        "n_pairs_valid": len(supported_pairs),
        "min_shared_days": min_shared_days,
        "shared_days_all_pairs": _day_summary(all_shared_day_counts),
        "shared_days_valid_pairs": _day_summary([len(days) for _, _, days in supported_pairs]),
        "grids": [],
    }
    pair_scores = {}
    for scale in scales:
        for origin_x, origin_y in shifts:
            daily_probabilities = {}
            for animal, by_day in projected.items():
                daily_probabilities[animal] = {}
                for day, points in by_day.items():
                    counts = Counter((math.floor(x / scale + origin_x),
                                      math.floor(y / scale + origin_y)) for x, y in points)
                    total = len(points)
                    daily_probabilities[animal][day] = {cell: count / total for cell, count in counts.items()}

            # Many pairs share the same date coverage. Reuse their animal UDs
            # within this grid while preserving each exact shared-date tuple.
            occupancy_cache = {}

            def summed_daily_occupancy(animal, days):
                key = (animal, days)
                if key not in occupancy_cache:
                    occupancy = defaultdict(float)
                    for day in days:
                        for cell, probability in daily_probabilities[animal][day].items():
                            occupancy[cell] += probability
                    occupancy_cache[key] = dict(occupancy)
                return occupancy_cache[key]

            scores = {}
            for animal_a, animal_b, shared_days in supported_pairs:
                occupancy_a = summed_daily_occupancy(animal_a, shared_days)
                occupancy_b = summed_daily_occupancy(animal_b, shared_days)
                if len(occupancy_a) > len(occupancy_b):
                    occupancy_a, occupancy_b = occupancy_b, occupancy_a
                overlap = math.fsum(min(probability, occupancy_b.get(cell, 0.0))
                                    for cell, probability in occupancy_a.items()) / len(shared_days)
                # Roundoff can produce 1 + a few ulps for identical UDs.
                scores[(animal_a, animal_b)] = min(1.0, max(0.0, overlap))
            pair_scores[(scale, origin_x, origin_y)] = scores
            report["grids"].append({"scale_km": scale, "origin_x_fraction": origin_x,
                                    "origin_y_fraction": origin_y,
                                    "overlap": _overlap_summary(scores.values())})
    return report, pair_scores
