#!/usr/bin/env python3
"""Synthetic identifiability stress test; NO animal outcomes used.

Implements PR #72's 4-route, 8+8 early/late, alpha=0.5, 20 bat,
five-complete-block, 1024-assignment P1. A constructive short-memory
counterexample can pass P1 without retained individual information.
Also simulate identical R1 forced reset and OPEN re-expression in both
families as a possible, NOT YET AUTHORIZED, extra experiment.
"""
from __future__ import annotations
import json
from itertools import product
from pathlib import Path

import numpy as np
from primary_route_specialization_v1 import family_route_identity_scores

N, BLOCKS, FAMILIES, ROUTES = 20, 5, 2, 4
EARLY, LATE, REOPEN = 8, 8, 8
SMOOTHER, CANONICAL = 0.5, 0
REPLICATES, SEED = 500, 202610081737


def assignments():
    choices = []
    for a in range(2):
        for b in range(2):
            x = np.full(4, -1, dtype=np.int8)
            x[a] = 1
            x[2 + b] = 1
            choices.append(x)
    out = np.vstack([np.concatenate(t) for t in product(choices, repeat=BLOCKS)])
    assert out.shape == (1024, 20)
    assert np.all(out.reshape(-1, BLOCKS, 4).sum(axis=2) == 0)
    return out


LEGAL = assignments()


def draw_markov(rng, stay, length, initial=None):
    # Every individual has exactly the same transition kernel.
    z = np.empty(length, dtype=np.int8)
    z[0] = rng.integers(ROUTES) if initial is None else initial
    for t in range(1, length):
        if rng.random() < stay:
            z[t] = z[t - 1]
        else:
            other = rng.integers(ROUTES - 1)
            z[t] = other if other < z[t - 1] else other + 1
    return z


def simulate(rng, model, assignment):
    probe = np.empty((N, FAMILIES, EARLY + LATE), dtype=np.int8)
    reopen = np.empty((N, FAMILIES, REOPEN), dtype=np.int8)
    for i in range(N):
        for f in range(FAMILIES):
            opened = assignment[i] == (1 if f == 0 else -1)
            if model == "null_both_persistent":
                p = rng.dirichlet(np.full(ROUTES, 0.6))
                probe[i, f] = rng.choice(ROUTES, EARLY + LATE, p=p)
                reopen[i, f] = rng.choice(ROUTES, REOPEN, p=p)
            elif model == "no_personal_markov":
                probe[i, f] = draw_markov(rng, 0.25, EARLY + LATE)
                reopen[i, f] = draw_markov(rng, 0.25, REOPEN, CANONICAL)
            elif model == "acute_markov_only":
                stay = 0.95 if opened else 0.25
                probe[i, f] = draw_markov(rng, stay, EARLY + LATE)
                reopen[i, f] = draw_markov(rng, stay, REOPEN, CANONICAL)
            elif model == "baseline_trait_plus_acute_inertia":
                p = rng.dirichlet(np.full(ROUTES, 0.35))
                if opened:
                    initial = int(rng.choice(ROUTES, p=p))
                    probe[i, f] = draw_markov(rng, 0.95, EARLY + LATE, initial)
                else:
                    probe[i, f] = rng.choice(ROUTES, EARLY + LATE, p=p)
                reopen[i, f] = rng.choice(ROUTES, REOPEN, p=p)
            elif model == "persisting_personal_propensity":
                p = rng.dirichlet(np.full(ROUTES, 0.15 if opened else 4.0))
                probe[i, f] = rng.choice(ROUTES, EARLY + LATE, p=p)
                reopen[i, f] = rng.choice(ROUTES, REOPEN, p=p)
            else:
                raise ValueError(model)
    return probe, reopen


def log_history(probe):
    counts = np.stack([(probe[:, :, :EARLY] == k).sum(axis=2)
                       for k in range(ROUTES)], axis=2)
    return np.log((counts + SMOOTHER) / (EARLY + ROUTES * SMOOTHER))


def score_with_history(probe, targets):
    own = log_history(probe)
    donor = (own.sum(axis=0, keepdims=True) - own) / (N - 1)
    contrast = own - donor
    return np.take_along_axis(contrast, targets, axis=2).mean(axis=2)


def exact_treatment_test(family_scores, assignment):
    family_difference = family_scores[:, 0] - family_scores[:, 1]
    observed = float(assignment @ family_difference / N)
    null = LEGAL @ family_difference / N
    p = float(np.mean(null >= observed - 1e-12))
    return observed, p


def open_only_reexpression(probe, reopened, assignment):
    # Descriptive OPEN-only signal: susceptible to pre-existing traits.
    lp = log_history(probe)
    vals = []
    for f in range(FAMILIES):
        group = np.where(assignment == (1 if f == 0 else -1))[0]
        for i in group:
            peers = group[group != i]
            others = lp[peers, f, :].mean(axis=0)
            targets = reopened[i, f]
            vals.append(float(np.mean(lp[i, f, targets] - others[targets])))
    return float(np.mean(vals))


def check_original_p1_formula():
    # One independent frozen-source implementation agreement test.
    rng = np.random.default_rng(7)
    a = LEGAL[7]
    seq, _ = simulate(rng, "null_both_persistent", a)
    ours = score_with_history(seq, seq[:, :, EARLY:])
    rows = [{"animal_id": f"bat{i:02d}", "family": "AB"[f],
             "probe_order": t + 1, "route": f"R{int(seq[i,f,t]) + 1}"}
            for i in range(N) for f in range(FAMILIES)
            for t in range(EARLY + LATE)]
    theirs = family_route_identity_scores(rows, EARLY + LATE)
    assert len(theirs) == N * FAMILIES
    err = max(abs(ours[i,f] - theirs[(f"bat{i:02d}", "AB"[f])])
              for i in range(N) for f in range(FAMILIES))
    if err > 1e-12:
        raise AssertionError(f"P1 estimator drift: max error {err}")
    return float(err)


def main():
    agreement = check_original_p1_formula()
    rng = np.random.default_rng(SEED)
    names = [
        "null_both_persistent", "no_personal_markov", "acute_markov_only",
        "baseline_trait_plus_acute_inertia", "persisting_personal_propensity"
    ]
    result = {
        "tier": "SYNTHETIC_IDENTIFIABILITY_AUDIT_NOT_BAT_DATA",
        "seed": SEED, "replicates": REPLICATES,
        "exact_assignments": len(LEGAL),
        "P1_agrees_with_original_pr72_estimator_to_max_abs_error": agreement,
        "reopening_design": "BOTH families forced to R1; 8 reopened trials in both",
        "scenarios": {}
    }
    for name in names:
        p1_effect, p1_p, memory_signal, delayed_effect, delayed_p = [], [], [], [], []
        for _ in range(REPLICATES):
            assignment = LEGAL[rng.integers(len(LEGAL))]
            seq, reopened = simulate(rng, name, assignment)
            d, p = exact_treatment_test(score_with_history(seq, seq[:, :, EARLY:]),
                                        assignment)
            ddelayed, pdelayed = exact_treatment_test(
                score_with_history(seq, reopened), assignment)
            p1_effect.append(d)
            p1_p.append(p)
            memory_signal.append(open_only_reexpression(seq, reopened, assignment))
            delayed_effect.append(ddelayed)
            delayed_p.append(pdelayed)
        p1_effect = np.asarray(p1_effect)
        p1_p = np.asarray(p1_p)
        memory_signal = np.asarray(memory_signal)
        delayed_effect = np.asarray(delayed_effect)
        delayed_p = np.asarray(delayed_p)
        p1_pass = (p1_effect > 0) & (p1_p <= .05)
        delayed_pass = (delayed_effect > 0) & (delayed_p <= .05)
        result["scenarios"][name] = {
            "P1_pass_fraction": float(p1_pass.mean()),
            "P1_mean_treatment_effect": float(p1_effect.mean()),
            "open_only_reexpression_mean": float(memory_signal.mean()),
            "matched_delayed_treatment_effect_mean": float(delayed_effect.mean()),
            "matched_delayed_pass_fraction": float(delayed_pass.mean()),
            "P1_and_matched_delayed_both_pass_fraction":
                float((p1_pass & delayed_pass).mean()),
        }
    output = Path(__file__).with_name("HISTORY_RESET_IDENTIFIABILITY_SIMULATION_V1.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
