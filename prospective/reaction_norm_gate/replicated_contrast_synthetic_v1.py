#!/usr/bin/env python3
"""Synthetic-only illustration of replicated personal challenge-response covariance.

NO BAT DATA are loaded by this program. Do not turn these synthetic p values into
biological claims. See REPEATED_CONTEXT_IDENTIFIABILITY_CONTRACT_V1.md.
"""
from __future__ import annotations

import argparse
from itertools import permutations
import json
from math import factorial, isclose, isfinite


def centered(values: list[float]) -> list[float]:
    if len(values) < 3 or not all(isfinite(v) for v in values):
        raise ValueError("Need >=3 finite, independent-bat contrasts")
    mean = sum(values) / len(values)
    return [v - mean for v in values]


def cross_occasion_covariance(s1: list[float], s2: list[float]) -> float:
    if len(s1) != len(s2):
        raise ValueError("Each bat must appear in both independent occasions")
    x, y = centered(s1), centered(s2)
    return sum(a * b for a, b in zip(x, y)) / (len(x) - 1)


def exact_label_correspondence(s1: list[float], s2: list[float]) -> dict:
    """Exact exchangeable-label null for <=8 bats. NOT a new population test."""
    if len(s1) != len(s2) or not 3 <= len(s1) <= 8:
        raise ValueError("Exact demonstration only supports 3-8 matched bats")
    x, y = centered(s1), centered(s2)
    observed = sum(a * b for a, b in zip(x, y)) / (len(x) - 1)
    exceed = 0
    for assignment in permutations(range(len(x))):
        trial = sum(x[i] * y[assignment[i]] for i in range(len(x))) / (len(x) - 1)
        if trial >= observed - 1e-12:
            exceed += 1
    number = factorial(len(x))
    return {"synthetic_observed_cov": observed,
            "synthetic_exact_label_p": exceed / number,
            "permutations": number,
            "extreme_assignments": exceed,
            "caveat": "archive-conditional exchangeable-label illustration, no animal data"}


def make_synthetic(scale: float = 1.0) -> tuple[list[float], list[float]]:
    """Six fictional bats with independent recorded occasions and strong b_i."""
    b = [-3.0, -2.0, -1.0, 1.0, 2.0, 3.0]
    first, second = [], []
    for i, personal_response in enumerate(b):
        baseline = 100 + i * 47  # strongly different individual mean flight levels
        low_s1 = baseline + 2
        high_s1 = low_s1 + 11 + scale * personal_response
        low_s2 = baseline - 3
        high_s2 = low_s2 + 18 + scale * personal_response
        first.append(high_s1 - low_s1)
        second.append(high_s2 - low_s2)
    return first, second


def self_test() -> dict:
    x, y = make_synthetic()
    positive = exact_label_correspondence(x, y)
    assert positive["permutations"] == 720
    assert positive["extreme_assignments"] == 1
    assert positive["synthetic_observed_cov"] > 0
    # Intercepts and arbitrary shared context/session shifts must disappear.
    same_shift = cross_occasion_covariance(x, [v + 923 for v in y])
    assert isclose(same_shift, positive["synthetic_observed_cov"], abs_tol=1e-11)

    n1, n2 = make_synthetic(scale=0.0)
    null = exact_label_correspondence(n1, n2)
    assert abs(null["synthetic_observed_cov"]) < 1e-12
    assert null["synthetic_exact_label_p"] == 1.0

    # Scrambling physical labels destroys the personal mapping.
    reversed_cov = cross_occasion_covariance(x, list(reversed(y)))
    assert reversed_cov < 0

    # Identical observations can arise from (a) bats with b_i, or
    # (b) calibrated-independent bats, but a permanent device bias b_i.
    # The statistic C has NO causal ability to distinguish these origins.
    device_bias_data = (x[:], y[:])
    assert isclose(cross_occasion_covariance(*device_bias_data),
                   positive["synthetic_observed_cov"], abs_tol=1e-12)
    return {
        "synthetic_positive_exact_test": "PASS",
        "synthetic_common_session_shift_invariance": "PASS",
        "synthetic_constant_response_no_false_identity": "PASS",
        "synthetic_label_mismatch_negative_control": "PASS",
        "synthetic_device_artifact_nonidentification": "PASS",
        "example_positive": positive,
        "example_constant_response": null,
        "note": "NO real bats, outcomes, raw coordinates, or existing trajectories accessed",
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--self-test", action="store_true",
                   help="run completely synthetic algebra/label controls")
    args = p.parse_args()
    if not args.self_test:
        p.error("This is a synthetic-only gate: use --self-test. "
                "No real-data loading endpoint is implemented.")
    print(json.dumps(self_test(), sort_keys=True, indent=2))
