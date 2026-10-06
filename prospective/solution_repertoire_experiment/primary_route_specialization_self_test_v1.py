#!/usr/bin/env python3
"""Synthetic self-test for P1 route specialization endpoint v1."""

import math

from primary_route_specialization_v1 import (
    family_route_identity_scores,
    score_bound,
    treatment_delta,
)


def main():
    # Four animals with distinct stable route preferences in each family.
    animals = ["b1", "b2", "b3", "b4"]
    preferred = {"b1": "R1", "b2": "R2", "b3": "R3", "b4": "R4"}
    rows = []

    for animal in animals:
        for family in ("A", "B"):
            for trial in range(1, 13):
                rows.append({
                    "animal_id": animal,
                    "family": family,
                    "probe_order": trial,
                    "route": preferred[animal],
                })

    scores = family_route_identity_scores(rows, 12)
    assert len(scores) == 8
    assert all(value > 0 for value in scores.values())

    open_map = {"b1": "A", "b2": "B", "b3": "A", "b4": "B"}
    delta, individual = treatment_delta(scores, open_map)

    # Families are identical in this synthetic construction.
    assert abs(delta) < 1e-12
    assert all(abs(value) < 1e-12 for value in individual.values())

    # Closed-form score bound for 6 early trials:
    # pmax/pmin = (6.5)/(0.5) = 13.
    assert abs(score_bound(12) - math.log(13.0)) < 1e-12

    print("PASS: P1 route specialization endpoint v1")


if __name__ == "__main__":
    main()
