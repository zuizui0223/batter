#!/usr/bin/env python3
"""Frozen P1 route-choice individual-specialization endpoint v1."""

from __future__ import annotations

import math
from typing import Dict, Mapping, Sequence, Tuple

ROUTES = ("R1", "R2", "R3", "R4")
ALPHA = 0.5


def endpoint_eligible_animals(rows: Sequence[dict], planned_probe_count: int):
    if planned_probe_count <= 0 or planned_probe_count % 2 != 0:
        raise ValueError("planned_probe_count must be positive and even")

    families = sorted({row["family"] for row in rows})
    if families != ["A", "B"]:
        raise ValueError("expected matched families A and B")

    animals = sorted({row["animal_id"] for row in rows})
    eligible = []

    for animal in animals:
        ok = True
        for family in families:
            rr = [
                row for row in rows
                if row["animal_id"] == animal and row["family"] == family
            ]
            if len(rr) != planned_probe_count:
                ok = False
                break
            orders = sorted(int(row["probe_order"]) for row in rr)
            if orders != list(range(1, planned_probe_count + 1)):
                ok = False
                break
            if any(row["route"] not in ROUTES for row in rr):
                ok = False
                break
        if ok:
            eligible.append(animal)

    return eligible


def smoothed_route_distribution(early_rows: Sequence[dict]) -> Dict[str, float]:
    counts = {route: 0 for route in ROUTES}
    for row in early_rows:
        route = row["route"]
        if route not in counts:
            raise ValueError(f"unknown route {route}")
        counts[route] += 1

    n = len(early_rows)
    denom = n + ALPHA * len(ROUTES)
    return {
        route: (counts[route] + ALPHA) / denom
        for route in ROUTES
    }


def family_route_identity_scores(
    rows: Sequence[dict],
    planned_probe_count: int,
) -> Dict[Tuple[str, str], float]:
    """Return treatment-blind R_(animal,family) scores."""
    eligible = endpoint_eligible_animals(rows, planned_probe_count)
    if len(eligible) < 4:
        raise ValueError("P1 requires at least four endpoint-eligible animals")

    half = planned_probe_count // 2
    families = ("A", "B")
    scores = {}

    for family in families:
        early_p = {}

        for animal in eligible:
            early = [
                row for row in rows
                if row["animal_id"] == animal
                and row["family"] == family
                and int(row["probe_order"]) <= half
            ]
            if len(early) != half:
                raise ValueError("early probe support drift")
            early_p[animal] = smoothed_route_distribution(early)

        for animal in eligible:
            late = [
                row for row in rows
                if row["animal_id"] == animal
                and row["family"] == family
                and int(row["probe_order"]) > half
            ]
            if len(late) != half:
                raise ValueError("late probe support drift")

            donors = [x for x in eligible if x != animal]
            if len(donors) < 3:
                raise ValueError("P1 requires at least three donors")

            vals = []
            for row in late:
                route = row["route"]
                own = math.log(early_p[animal][route])
                donor = sum(math.log(early_p[j][route]) for j in donors) / len(donors)
                vals.append(own - donor)

            scores[(animal, family)] = sum(vals) / len(vals)

    return scores


def treatment_delta(
    family_scores: Mapping[Tuple[str, str], float],
    open_family_map: Mapping[str, str],
):
    score_animals = sorted({animal for animal, family in family_scores})
    individual = {}

    for animal in score_animals:
        if animal not in open_family_map:
            raise ValueError(f"missing treatment assignment for {animal}")
        if (animal, "A") not in family_scores or (animal, "B") not in family_scores:
            raise ValueError(f"animal {animal} lacks paired family scores")

        open_family = open_family_map[animal]
        constrained_family = "B" if open_family == "A" else "A"
        individual[animal] = (
            family_scores[(animal, open_family)]
            - family_scores[(animal, constrained_family)]
        )

    if not individual:
        raise ValueError("no paired route scores")

    return sum(individual.values()) / len(individual), individual


def score_bound(planned_probe_count: int) -> float:
    """Maximum absolute family-specific R_i,f implied by alpha=.5 and 4 routes."""
    if planned_probe_count <= 0 or planned_probe_count % 2 != 0:
        raise ValueError("planned_probe_count must be positive and even")
    m = planned_probe_count // 2
    p_min = ALPHA / (m + ALPHA * len(ROUTES))
    p_max = (m + ALPHA) / (m + ALPHA * len(ROUTES))
    return math.log(p_max / p_min)
