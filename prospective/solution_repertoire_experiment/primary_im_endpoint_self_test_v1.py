#!/usr/bin/env python3
"""Synthetic self-test for frozen P2 I/M endpoint v1."""

import numpy as np

from primary_im_endpoint_v1 import (
    FEATURE_NAMES,
    family_im_identity_scores,
    fit_acquisition_scalers,
    route_features,
    treatment_delta,
)


def synthetic_trajectory(scale=1.0, zscale=0.2, n=120):
    t = np.linspace(0.0, 2.0, n)
    x = scale * t
    y = 0.1 * np.sin(4 * np.pi * t)
    z = zscale * np.sin(2 * np.pi * t)
    return np.column_stack([t, x, y, z])


def main():
    feat = route_features(
        synthetic_trajectory(),
        min_rows=100,
        min_positive_dt_intervals=50,
    )
    assert feat is not None
    assert feat.shape == (8,)
    assert len(FEATURE_NAMES) == 8

    animals = ["b1", "b2", "b3", "b4"]

    acquisition = []
    for ai, animal in enumerate(animals):
        for family_i, family in enumerate(("A", "B")):
            for trial in range(1, 5):
                # Treatment labels are deliberately absent.
                acquisition.append({
                    "animal_id": animal,
                    "family": family,
                    "features": np.array([
                        1.0 + 0.10 * ai + 0.02 * trial,
                        1.2 + 0.12 * ai + 0.03 * trial,
                        0.20 + 0.03 * ai + 0.01 * trial,
                        0.30 + 0.03 * ai + 0.01 * trial,
                        0.40 + 0.04 * ai + 0.02 * trial,
                        0.60 + 0.05 * ai + 0.02 * trial,
                        0.80 - 0.02 * ai + 0.005 * trial,
                        0.50 + 0.06 * ai + 0.01 * trial,
                    ]) + family_i * 0.01,
                })

    scalers = fit_acquisition_scalers(acquisition)
    assert set(scalers) == {"A", "B"}

    probe = []
    for ai, animal in enumerate(animals):
        for family_i, family in enumerate(("A", "B")):
            for trial in range(1, 5):
                base = np.array([
                    1.1 + 0.10 * ai,
                    1.3 + 0.12 * ai,
                    0.25 + 0.03 * ai,
                    0.35 + 0.03 * ai,
                    0.45 + 0.04 * ai,
                    0.65 + 0.05 * ai,
                    0.78 - 0.02 * ai,
                    0.55 + 0.06 * ai,
                ])
                probe.append({
                    "animal_id": animal,
                    "family": family,
                    "probe_order": trial,
                    "features": base + family_i * 0.01 + trial * 0.001,
                })

    scores = family_im_identity_scores(acquisition, probe, 4)
    assert len(scores) == 8
    assert all(np.isfinite(v) for v in scores.values())
    assert all(v > 0 for v in scores.values())

    open_map = {"b1": "A", "b2": "B", "b3": "A", "b4": "B"}
    delta, individual = treatment_delta(scores, open_map)
    assert np.isfinite(delta)
    assert len(individual) == 4

    print("PASS: P2 transparent I/M endpoint v1")


if __name__ == "__main__":
    main()
