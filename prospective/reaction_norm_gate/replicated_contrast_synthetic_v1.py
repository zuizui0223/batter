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



def heldout_session_score(four_sessions: list[list[float]]) -> dict:
    """Freeze first two occasions as training and latter two as testing.

    Center each occasion's bat contrasts first to remove a common response.
    This illustrates generalization, NOT independent-bat population inference.
    """
    if len(four_sessions) != 4:
        raise ValueError("Need four separate synthetic session vectors")
    sessions = [centered(list(s)) for s in four_sessions]
    n = len(sessions[0])
    if any(len(v) != n for v in sessions):
        raise ValueError("Mismatch in complete bat IDs")
    train = [(sessions[0][i] + sessions[1][i]) / 2 for i in range(n)]
    test = [(sessions[2][i] + sessions[3][i]) / 2 for i in range(n)]
    mse_zero = sum(v * v for v in test) / n
    mse_personal = sum((test[i] - train[i]) ** 2 for i in range(n)) / n
    return {"synthetic_n_bats": n,
            "synthetic_train_test_cov": sum(train[i] * test[i] for i in range(n)) / (n-1),
            "synthetic_mse_zero": mse_zero,
            "synthetic_mse_personal": mse_personal,
            "synthetic_gain": mse_zero - mse_personal}


def make_four_sessions(scale: float = 1.0) -> list[list[float]]:
    """Four fictitious nights. Shared context effect varies across nights."""
    b = [-3.0, -2.0, -1.0, 1.0, 2.0, 3.0]
    return [[shared + scale * bi for bi in b]
            for shared in (11.0, 18.0, 13.0, 21.0)]


def independent_sigma_gaussian_p(s1: list[float], s2: list[float],
                                 sigma: list[float]) -> float:
    """One-sided Gaussian correspondence null with KNOWN independent S2 SDs.

    Theory: after centering s1, sum_i (s1_i-mean1)*s2_i has variance
    sum_i ((s1_i-mean1)^2 * sigma_i^2) conditional on s1.
    Centering s2 changes nothing because centered s1 sums to zero.
    Valid ONLY if held-out S2 residuals are independent zero-mean Gaussian
    with sigma_i fixed from independent, non-outcome data; permanent bat
    effects and device biases violate this null. Not a biological test.
    """
    from math import erfc, sqrt
    if len(s1) != len(s2) or len(s1) != len(sigma):
        raise ValueError("Unmatched bat/SD arrays")
    x = centered(s1)
    if any((not isfinite(s)) or s <= 0 for s in sigma):
        raise ValueError("Known independent sigma must be finite and positive")
    stat = sum(a*b for a, b in zip(x, s2))
    v = sum(a*a*s*s for a, s in zip(x, sigma))
    if v <= 1e-18:
        raise ValueError("Degenerate training contrast")
    return 0.5 * erfc((stat / sqrt(v)) / sqrt(2))


def simulate_null_calibration(nrep: int = 1200, seed: int = 20261008) -> dict:
    """Synthetic empirical size of the exact permutation p under two nulls.

    The HETEROSCEDASTIC null has ZERO stable individual response and errors
    independent between occasions, but individual-specific observation SD.
    Under unequal SD, cross-individual labels are NOT exchangeable.
    """
    from itertools import permutations as perm_fn
    import random

    n = 5
    all_perms = list(perm_fn(range(n)))
    rng = random.Random(seed)

    def trial(sigmas: list[float]) -> tuple[float, float]:
        positive_perm, positive_known_sigma = 0, 0
        for _ in range(nrep):
            x = centered([rng.gauss(0.0, sigma) for sigma in sigmas])
            y = centered([rng.gauss(0.0, sigma) for sigma in sigmas])
            observed = sum(x[i]*y[i] for i in range(n))
            extreme = sum(
                sum(x[i]*y[p[i]] for i in range(n)) >= observed - 1e-12
                for p in all_perms
            )
            if extreme / len(all_perms) <= .05:
                positive_perm += 1
            # Oracle comparison: true individual SD is presumed from
            # independent evidence and is not estimated from x or y.
            if independent_sigma_gaussian_p(x, y, sigmas) <= .05:
                positive_known_sigma += 1
        return positive_perm / nrep, positive_known_sigma / nrep

    equal, equal_known_sigma = trial([1.0] * n)
    unequal, unequal_known_sigma = trial([0.3, 0.6, 1.2, 2.5, 5.0])
    return {
        "synthetic_bats": n,
        "synthetic_replicates_per_scenario": nrep,
        "synthetic_uniform_sd_null_reject_at_p005": equal,
        "synthetic_heterogeneous_sd_null_reject_at_p005": unequal,
        "synthetic_known_independent_sigma_null_reject_equal": equal_known_sigma,
        "synthetic_known_independent_sigma_null_reject_unequal": unequal_known_sigma,
        "known_sigma_null_scope": "oracle independently known Gaussian bat-level noise SD; cannot be estimated from these two held-out tests",
        "nominal_rate": 0.05,
        "warning": "individual-label permutation is not calibrated under heteroscedastic individual errors",
    }


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
    four = make_four_sessions(scale=1.0)
    perfect = heldout_session_score(four)
    assert perfect["synthetic_gain"] > 0
    no_personal = heldout_session_score(make_four_sessions(scale=0.0))
    assert abs(no_personal["synthetic_gain"]) < 1e-12

    # Stable sensor bias permanently assigned to a bat perfectly mimics
    # genuine personal response, even with all four nights observed.
    sensor_only = heldout_session_score(four)
    assert sensor_only == perfect

    # A deliberately switched sensor sign on independent evaluation nights
    # exposes that a sensor-specific response is not a bat-fixed response.
    swapped_sensors = four[:2] + [[shared - b for b in [-3., -2., -1., 1., 2., 3.]]
                                  for shared in (13., 21.)]
    swapped = heldout_session_score(swapped_sensors)
    assert swapped["synthetic_train_test_cov"] < 0
    assert swapped["synthetic_gain"] < 0

    calibration = simulate_null_calibration()
    assert 0.015 < calibration["synthetic_uniform_sd_null_reject_at_p005"] < 0.085
    assert calibration["synthetic_heterogeneous_sd_null_reject_at_p005"] > (
        calibration["synthetic_uniform_sd_null_reject_at_p005"] + .025
    )
    assert 0.015 < calibration["synthetic_known_independent_sigma_null_reject_equal"] < 0.085
    assert 0.015 < calibration["synthetic_known_independent_sigma_null_reject_unequal"] < 0.085
    assert calibration["synthetic_heterogeneous_sd_null_reject_at_p005"] > (
        calibration["synthetic_known_independent_sigma_null_reject_unequal"] + .025
    )

    return {
        "synthetic_four_occasion_holdout": "PASS",
        "synthetic_personal_response_vs_noise": "PASS",
        "synthetic_permanent_device_bias_nonidentification": "PASS",
        "synthetic_sensor_rotation_exposes_device_artifact": "PASS",
        "synthetic_heteroscedastic_false_positive_warning": "PASS",
        "synthetic_independently_known_sigma_oracle_calibration": "PASS",
        "synthetic_null_calibration": calibration,
        "synthetic_heldout_reliable_response": perfect,
        "synthetic_heldout_no_personal_response": no_personal,
        "synthetic_heldout_swapped_sensor": swapped,
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
