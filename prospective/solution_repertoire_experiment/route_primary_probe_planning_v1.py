#!/usr/bin/env python3
"""Prospective stress test for P1 route-specialization probe trial count.

This is NOT a power claim about the real experiment.
It compares 8, 12 and 16 total common-OPEN probe trials per family under
illustrative four-route generative scenarios.

P1 architecture:
- first half estimates individual route distribution;
- second half is held out;
- Dirichlet alpha = 0.5;
- same-family all-individual donor reference;
- n = 20, five complete restricted-randomization blocks;
- exact 1,024-assignment randomization test.
"""

import itertools
import numpy as np

SEED = 20261006
REPS = 600
ALPHA = 0.5
N = 20
TOTALS = (8, 12, 16)
SCENARIOS = (
    ("strong", 4.0, 40.0),
    ("moderate", 6.0, 30.0),
    ("mild", 8.0, 30.0),
)


def allowed_assignments():
    block_options = []
    for _ in range(N // 4):
        opts = []
        for a_pick in (0, 1):
            for b_pick in (0, 1):
                x = np.zeros(4, dtype=bool)
                x[a_pick] = True
                x[2 + b_pick] = True
                opts.append(x)
        block_options.append(opts)
    return np.array([
        np.concatenate(combo)
        for combo in itertools.product(*block_options)
    ])


ASSIGNMENTS = allowed_assignments()
OBSERVED_A_OPEN = np.tile(np.array([True, False, True, False]), N // 4)


def route_identity(early_counts, late_routes):
    probs = (early_counts + ALPHA) / (
        early_counts.sum(axis=1, keepdims=True) + 4 * ALPHA
    )
    logp = np.log(probs)
    donor_mean = (logp.sum(axis=0)[None, :] - logp) / (N - 1)
    out = []
    for i in range(N):
        rr = late_routes[i]
        out.append(np.mean(logp[i, rr] - donor_mean[i, rr]))
    return np.asarray(out)


def one_rep(rng, half_trials, k_open, k_constrained):
    p_a, p_b = [], []
    for i in range(N):
        p_a.append(rng.dirichlet(
            np.ones(4) * ((k_open if OBSERVED_A_OPEN[i] else k_constrained) / 4)
        ))
        p_b.append(rng.dirichlet(
            np.ones(4) * ((k_constrained if OBSERVED_A_OPEN[i] else k_open) / 4)
        ))
    p_a = np.asarray(p_a)
    p_b = np.asarray(p_b)

    early_a = np.array([rng.multinomial(half_trials, p) for p in p_a])
    early_b = np.array([rng.multinomial(half_trials, p) for p in p_b])
    late_a = np.array([rng.choice(4, size=half_trials, p=p) for p in p_a])
    late_b = np.array([rng.choice(4, size=half_trials, p=p) for p in p_b])

    r_a = route_identity(early_a, late_a)
    r_b = route_identity(early_b, late_b)
    diff = r_a - r_b

    observed = np.mean(np.where(OBSERVED_A_OPEN, diff, -diff))
    null = np.mean(
        np.where(ASSIGNMENTS, diff[None, :], -diff[None, :]),
        axis=1,
    )
    p = np.mean(null >= observed - 1e-15)
    return observed, p


def main():
    rng = np.random.default_rng(SEED)
    print("scenario,total_probe,half_probe,rejection_fraction,mean_delta,median_p")
    for name, k_open, k_con in SCENARIOS:
        for total in TOTALS:
            vals = [
                one_rep(rng, total // 2, k_open, k_con)
                for _ in range(REPS)
            ]
            obs = np.array([v[0] for v in vals])
            ps = np.array([v[1] for v in vals])
            print(
                f"{name},{total},{total//2},"
                f"{np.mean(ps <= 0.05):.4f},{np.mean(obs):.4f},{np.median(ps):.6f}"
            )


if __name__ == "__main__":
    main()
