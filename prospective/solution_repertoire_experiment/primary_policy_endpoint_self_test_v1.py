#!/usr/bin/env python3
"""Synthetic self-test for the frozen primary I/M endpoint."""

import numpy as np

from primary_policy_endpoint_v1 import (
    FEATURE_NAMES,
    family_identity_scores,
    route_features,
    standardize_probe_rows,
    treatment_delta,
)


def synthetic_trajectory(scale=1.0, zscale=0.2, n=120):
    t = np.linspace(0.0, 2.0, n)
    x = scale * t
    y = 0.1 * np.sin(4 * np.pi * t)
    z = zscale * np.sin(2 * np.pi * t)
    return np.column_stack([t, x, y, z])


def main():
    feat = route_features(synthetic_trajectory())
    assert feat is not None
    assert feat.shape == (8,)
    assert np.all(np.isfinite(feat))
    assert len(FEATURE_NAMES) == 8

    # Build a fully balanced treatment-blind common-OPEN probe:
    # 4 animals x 2 families x 4 probe flights.
    rows = []
    animals = ["b1", "b2", "b3", "b4"]

    for ai, animal in enumerate(animals):
        for family_i, family in enumerate(["A", "B"]):
            for trial in range(1, 5):
                base = np.array([
                    1.0 + 0.10 * ai,
                    1.2 + 0.12 * ai,
                    0.20 + 0.03 * ai,
                    0.30 + 0.03 * ai,
                    0.40 + 0.04 * ai,
                    0.60 + 0.05 * ai,
                    0.80 - 0.02 * ai,
                    0.50 + 0.06 * ai,
                ])
                # Tiny deterministic family/trial offsets preserve individual ordering.
                features = base + family_i * 0.01 + trial * 0.001
                rows.append({
                    "animal_id": animal,
                    "family": family,
                    "probe_order": trial,
                    "features": features,
                })

    standardized = standardize_probe_rows(rows)
    assert len(standardized) == len(rows)
    assert all("I" in row and "M" in row for row in standardized)

    scores = family_identity_scores(rows, planned_probe_count=4)
    assert len(scores) == 8
    assert all(np.isfinite(v) for v in scores.values())
    assert all(v > 0 for v in scores.values())

    open_map = {"b1": "A", "b2": "B", "b3": "A", "b4": "B"}
    delta, individual = treatment_delta(scores, open_map)
    assert np.isfinite(delta)
    assert len(individual) == 4

    print("PASS: primary policy endpoint v1")


if __name__ == "__main__":
    main()
