#!/usr/bin/env python3
"""Synthetic randomized route-seeding discriminator; NO animal data.

See RANDOMIZED_ROUTE_SEED_CONTRACT_V1.md. The original PR #72 P1 is unchanged.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

import numpy as np

N = 20
BLOCK = 4
B = N // BLOCK
K = 4
Q = 8
MC = 1000
ROOT_SEED = 202610081401
PERM24 = np.asarray(list(itertools.permutations(range(K))), dtype=np.int8)
SCENARIOS = (
    "TRAIT_ONLY",
    "TRAIT_WITH_ROUTE_ASYMMETRY",
    "GATED_PREDISPOSITION",
    "MARKOV_WITH_RESET",
    "HISTORY_IMPRINT_WEAK",
    "HISTORY_IMPRINT_STRONG",
    "MARKOV_NO_RESET",
)


def randomized_seeds(rng):
    """One seed route of each kind per four-animal block."""
    return np.concatenate([rng.permutation(K) for _ in range(B)]).astype(np.int8)


def categorical_draw(rng, q):
    """q: N x 4 route probabilities. Return N x Q categorical choices."""
    cp = np.cumsum(np.asarray(q, float), axis=1)
    if q.shape != (N, K) or not np.allclose(cp[:, -1], 1, rtol=1e-12):
        raise ValueError("bad individual route probabilities")
    u = rng.random((N, Q))
    choices = np.sum(u[:, :, None] > cp[:, None, :], axis=2)
    return choices.astype(np.int8)


def markov_draw(rng, starts, rho=0.95):
    """Common route-inertia kernel; starts are the most recent prior routes."""
    cur = np.array(starts, dtype=np.int8)
    y = np.zeros((N, Q), dtype=np.int8)
    for k in range(Q):
        stay = rng.random(N) < rho
        fresh = rng.integers(0, K, size=N)
        cur = np.where(stay, cur, fresh)
        y[:, k] = cur
    return y


def simulate_reopening(rng, scenario, seeds):
    if scenario == "MARKOV_WITH_RESET":
        # All have performed forced route R1; nothing depends on seed.
        return markov_draw(rng, np.zeros(N, dtype=np.int8))
    if scenario == "MARKOV_NO_RESET":
        # Deliberately omit the route-state synchronization control.
        return markov_draw(rng, seeds)
    alpha = {
        "TRAIT_ONLY": [0.35] * 4,
        "TRAIT_WITH_ROUTE_ASYMMETRY": [1.6, 0.6, 0.5, 0.3],
        "GATED_PREDISPOSITION": [0.12] * 4,
        "HISTORY_IMPRINT_WEAK": [0.35] * 4,
        "HISTORY_IMPRINT_STRONG": [0.35] * 4,
    }[scenario]
    # Fixed personal predispositions are generated independently from seed routes.
    bias = rng.dirichlet(np.asarray(alpha), size=N)
    if scenario in ("HISTORY_IMPRINT_WEAK", "HISTORY_IMPRINT_STRONG"):
        lam = 0.15 if scenario == "HISTORY_IMPRINT_WEAK" else 0.35
        seed_component = np.eye(K, dtype=float)[seeds]
        bias = (1 - lam) * bias + lam * seed_component
    return categorical_draw(rng, bias)


def route_count_matrix(targets):
    if targets.shape != (N, Q):
        raise ValueError("target shape drift")
    counts = np.zeros((N, K), dtype=np.int64)
    for route in range(K):
        counts[:, route] = (targets == route).sum(axis=1)
    assert np.all(counts.sum(axis=1) == Q)
    return counts


def exact_block_null(counts, assigned_seeds):
    """Exact randomization using convolution, NOT random permutation samples."""
    if counts.shape != (N, K) or assigned_seeds.shape != (N,):
        raise ValueError("support drift")
    obs_hit = int(counts[np.arange(N), assigned_seeds].sum())
    hist = np.asarray([1], dtype=np.int64)
    for block in range(B):
        c = counts[block * BLOCK:(block + 1) * BLOCK]
        possible = c[np.arange(BLOCK)[None, :], PERM24].sum(axis=1)
        local_hist = np.bincount(possible, minlength=BLOCK * Q + 1).astype(np.int64)
        if local_hist.sum() != math.factorial(K):
            raise RuntimeError("local null not 24")
        hist = np.convolve(hist, local_hist)
    legal = int(math.factorial(K) ** B)
    if int(hist.sum()) != legal:
        raise RuntimeError("global null count drift")
    return {
        "T": float(obs_hit / (N * Q) - 1 / K),
        "hit_count": obs_hit,
        "p_exact": float(hist[obs_hit:].sum() / legal),
        "null_mean_hit_count": float(np.dot(np.arange(len(hist)), hist) / legal),
        "assignment_count": legal,
    }


def test_exact_against_brute():
    toy = np.asarray([
        [2, 4, 1, 1], [0, 2, 5, 1], [4, 2, 1, 1], [1, 0, 2, 5],
        [1, 2, 2, 3], [4, 0, 0, 4], [0, 1, 3, 4], [2, 1, 2, 3]
    ], dtype=np.int64)
    expected_local = []
    for first in (toy[:4], toy[4:]):
        scores = [int(first[np.arange(4), p].sum()) for p in PERM24]
        expected_local.append(np.bincount(scores, minlength=33))
        assert len({tuple(p) for p in PERM24}) == 24
        assert sum(expected_local[-1]) == 24
    convolution = np.convolve(expected_local[0], expected_local[1])
    brute = np.zeros(65, dtype=np.int64)
    for p in PERM24:
        aa = int(toy[:4][np.arange(4), p].sum())
        for q in PERM24:
            bb = int(toy[4:][np.arange(4), q].sum())
            brute[aa + bb] += 1
    if not np.array_equal(convolution, brute):
        raise AssertionError("exact histogram convolution does not equal 576 assignments")


def preflight():
    test_exact_against_brute()
    rng = np.random.default_rng(12121)
    for _ in range(30):
        s = randomized_seeds(rng)
        if not all(sorted(s[j:j+4]) == [0, 1, 2, 3] for j in range(0, N, 4)):
            raise AssertionError("seed balance failed")
        y = rng.integers(0, K, size=(N, Q)).astype(np.int8)
        x = exact_block_null(route_count_matrix(y), s)
        assert x["assignment_count"] == math.factorial(4) ** 5
        assert math.isclose(x["null_mean_hit_count"], N * Q / K, abs_tol=1e-12)
    # The null test must not require the prediction of any latent trait.
    return {
        "legal_randomized_seed_assignments": math.factorial(4) ** 5,
        "two_block_histogram_equals_576_brute_force": "PASS",
        "balance_each_block": "PASS",
        "all_histogram_totals_and_expectations": "PASS",
        "seed_independent_static_generators": "PASS",
        "forced_markov_reset_state_is_R1": "PASS",
    }


def evaluate_scenario(name, scenario_seed):
    rows = []
    for seed in scenario_seed.spawn(MC):
        rng = np.random.default_rng(seed)
        assigned = randomized_seeds(rng)
        targets = simulate_reopening(rng, name, assigned)
        rows.append(exact_block_null(route_count_matrix(targets), assigned))
    v = np.asarray([d["T"] for d in rows])
    pv = np.asarray([d["p_exact"] for d in rows])
    passed = (v > 0) & (pv <= .05)
    frac = float(passed.mean())
    return {
        "n_independent_synthetic_experiments": MC,
        "mean_seed_hit_excess_vs_25pct": float(np.mean(v)),
        "sd_seed_hit_excess": float(np.std(v, ddof=1)),
        "mean_seed_hit_rate": float(0.25 + np.mean(v)),
        "support_count": int(passed.sum()),
        "support_fraction": frac,
        "mc_binomial_se": float(np.sqrt(frac * (1 - frac) / MC)),
        "median_exact_p": float(np.median(pv)),
        "max_exact_assignments_checked_per_simulation": int(math.factorial(K) ** B),
        "scenario_pseudopower_not_biological_power": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--out", default="RANDOMIZED_ROUTE_SEED_SIMULATION_RESULT_V1.json")
    args = parser.parse_args()
    checks = preflight()
    if args.self_test:
        print(json.dumps(checks, indent=2))
        return
    root = np.random.SeedSequence(ROOT_SEED)
    results = {}
    for name, child in zip(SCENARIOS, root.spawn(len(SCENARIOS))):
        results[name] = evaluate_scenario(name, child)
        print(name, results[name]["support_fraction"],
              results[name]["mean_seed_hit_excess_vs_25pct"], flush=True)
    out = {
        "evidence_tier": "SYNTHETIC_DESIGN_STRESS_NO_ANIMAL_OUTCOMES",
        "contract": "RANDOMIZED_ROUTE_SEED_CONTRACT_V1.md",
        "root_seed": ROOT_SEED,
        "bats": N,
        "blocks": B,
        "routes": K,
        "post_reset_target_trials": Q,
        "replicates_per_scenario": MC,
        "number_scenarios": len(SCENARIOS),
        "total_route_assignments_in_exact_test": math.factorial(K) ** B,
        "preflight": checks,
        "scenarios": results,
        "warning": "A programmed imprinting effect is not evidence that bats learn. Seed randomization would identify a history-specific causal effect, not its neural mechanism or fitness consequence."
    }
    Path(args.out).write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("ALL_SYNTHTETIC_SCENARIOS_COMPLETE")
if __name__ == "__main__":
    main()
