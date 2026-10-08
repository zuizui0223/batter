#!/usr/bin/env python3
"""Post-outcome audit of target-excluded peer-reference scaling.

Scientific contract:
RHINO_PEER_ONLY_STANDARDIZATION_CONTRACT_V1.md

Never use this diagnostic to change the frozen JAE results or claim an
independently pre-registered inference.
"""
from __future__ import annotations

import argparse
import collections
import importlib.util
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "rhino_configuration_identity_primary_v1.py"
N_PERM = 19_999
NULL_SEED = 20261008121
BOOT_REPS = 9_999
BOOT_SEED = 20261008122
N_FEATURES = 4
EXPECTED_CELLS = {"A": 5, "B": 4, "C": 5, "D": 6, "E": 5}
PREVIOUS = {"G": 0.293072, "MSE_zero": 0.633974, "MSE_self": 0.340902}


def source_clusters():
    """Return physical bat x environment trial arrays, before standardization."""
    spec = importlib.util.spec_from_file_location("rhino_source_v1", SOURCE)
    source = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(source)
    trajectories = source.load_rhino()
    if len(trajectories) != 45 or sum(bool(r["feature_valid"]) for r in trajectories) != 45:
        raise RuntimeError("STOP_SOURCE_DRIFT: expected exactly 45 valid source trajectories")
    sets = collections.defaultdict(list)
    for r in trajectories:
        arr = np.asarray(r["features"], dtype=float)
        if arr.shape != (8,) or not np.all(np.isfinite(arr)):
            raise RuntimeError("STOP_FEATURE_DRIFT")
        sets[(str(r["bat"]), int(r["env"]))].append(arr)
    clusters = {key: np.vstack(v) for key, v in sets.items()}
    count = collections.Counter(b for b, e in clusters)
    if dict(sorted(count.items())) != EXPECTED_CELLS:
        raise RuntimeError("STOP_INCIDENCE_DRIFT: " + repr(dict(count)))
    if set(e for b, e in clusters) != set(range(1, 8)):
        raise RuntimeError("STOP_ENVIRONMENT_DRIFT")
    return clusters


def reference_stats(x):
    """Original sample-SD convention, using first four physical movement features."""
    x = np.asarray(x, dtype=float)[:, :N_FEATURES]
    if len(x) < 2:
        raise RuntimeError("STOP_PEER_SAMPLE_SIZE")
    center = x.mean(axis=0)
    scale = x.std(axis=0, ddof=1)
    if np.any(~np.isfinite(center)) or np.any(~np.isfinite(scale)) or np.any(scale <= 0):
        raise RuntimeError("STOP_REFERENCE_SCALE_NONPOSITIVE")
    return center, scale


def build_tables(clusters):
    """Fully inclusive all-env reference and target-excluded eligible reference."""
    envs = sorted({e for b, e in clusters})
    inclusive = collections.defaultdict(dict)
    peer_only = collections.defaultdict(dict)
    peer_sd_min = float("inf")
    peer_abs_max = 0.0
    peer_counts = {}
    membership = {}

    for e in envs:
        bats = sorted(b for b, ee in clusters if ee == e)
        membership[e] = bats
        all_trials = np.vstack([clusters[(b, e)] for b in bats])
        all_mu, all_sd = reference_stats(all_trials)
        for b in bats:
            own = clusters[(b, e)][:, :N_FEATURES]
            z_all = ((own - all_mu) / all_sd).mean(axis=1)
            inclusive[b][e] = float(z_all.mean())

    eligible = [e for e, bats in sorted(membership.items()) if len(bats) >= 3]
    for e in eligible:
        for b in membership[e]:
            others = [bb for bb in membership[e] if bb != b]
            if len(others) < 2:
                raise RuntimeError(f"STOP_PEER_BATS: e={e} b={b}")
            reference = np.vstack([clusters[(other, e)] for other in others])
            if len(reference) < 2:
                raise RuntimeError(f"STOP_PEER_TRIALS: e={e} b={b}")
            try:
                mu, sd = reference_stats(reference)
            except RuntimeError as exc:
                raise RuntimeError(f"{exc} e={e} b={b}") from exc
            own = clusters[(b, e)][:, :N_FEATURES]
            z = (own - mu) / sd
            if np.any(~np.isfinite(z)):
                raise RuntimeError(f"STOP_FOCAL_Z_NONFINITE e={e} b={b}")
            peer_only[b][e] = float(z.mean(axis=1).mean())
            peer_sd_min = min(peer_sd_min, float(sd.min()))
            peer_abs_max = max(peer_abs_max, float(np.max(np.abs(z))))
            peer_counts[f"{e}:{b}"] = {
                "n_other_bats": len(others),
                "n_other_trials": len(reference),
                "n_focal_trials": len(own)
            }

    all_bats = sorted(inclusive)
    if all_bats != sorted(EXPECTED_CELLS) or sorted(peer_only) != all_bats:
        raise RuntimeError("STOP_BAT_IDENTITY_DRIFT")
    if sum(map(len, peer_only.values())) < 18:
        raise RuntimeError("STOP_TOO_FEW_PEER_ONLY_CELLS")
    if any(len(peer_only[b]) < 3 for b in all_bats):
        raise RuntimeError("STOP_TOO_FEW_PEER_ONLY_ENVIRONMENTS_FOR_A_BAT")
    matched = {b: {e: inclusive[b][e] for e in peer_only[b]} for b in all_bats}
    return (
        {b: dict(inclusive[b]) for b in all_bats}, matched,
        {b: dict(peer_only[b]) for b in all_bats},
        {"eligible_environments": eligible,
         "excluded_environments": [e for e in envs if e not in eligible],
         "members_per_environment": {str(e): membership[e] for e in envs},
         "trial_support": peer_counts,
         "number_of_peer_only_cells": sum(map(len, peer_only.values())),
         "minimum_peer_feature_sd": peer_sd_min,
         "maximum_absolute_peer_z_feature": peer_abs_max}
    )


def score(table):
    """Equal target configurations within each bat, then equal bats."""
    per_bat = {}
    for b, obs in sorted(table.items()):
        z = []
        s = []
        for e, y in sorted(obs.items()):
            train = [other_y for ee, other_y in obs.items() if ee != e]
            if len(train) < 2:
                raise RuntimeError("STOP_HISTORY_SUPPORT")
            pred = float(np.mean(train))
            z.append(float(y**2))
            s.append(float((y - pred)**2))
        mse0 = float(np.mean(z))
        mses = float(np.mean(s))
        per_bat[b] = {
            "number_of_environments": len(obs),
            "MSE_zero": mse0,
            "MSE_self": mses,
            "G": mse0 - mses,
            "R2_vs_zero": 1.0 - mses / mse0 if mse0 > 0 else None,
        }
    mse0 = float(np.mean([x["MSE_zero"] for x in per_bat.values()]))
    mses = float(np.mean([x["MSE_self"] for x in per_bat.values()]))
    return {
        "G": mse0 - mses,
        "MSE_zero": mse0,
        "MSE_self": mses,
        "R2_vs_zero": 1.0 - mses / mse0 if mse0 > 0 else None,
        "n_bats": len(per_bat),
        "n_cells": sum(map(len, table.values())),
        "per_bat": per_bat,
    }


def shuffled_correspondence(table, rng):
    """Permute source bundles among observed labels, within configurations."""
    envs = sorted({e for row in table.values() for e in row})
    shuffled = {b: {} for b in table}
    for e in envs:
        labels = sorted(b for b in table if e in table[b])
        values = [table[b][e] for b in labels]
        perm = rng.permutation(len(labels))
        for j, label in enumerate(labels):
            shuffled[label][e] = values[int(perm[j])]
    return shuffled


def synthetic_self_checks():
    """Use synthetic features; this does not open any study outcome."""
    base = {
        ("A", 1): np.array([[2, 3, 4, 5, 0, 0, 0, 0]], float),
        ("B", 1): np.array([[4, 6, 5, 7, 0, 0, 0, 0],
                              [5, 7, 7, 9, 0, 0, 0, 0]], float),
        ("C", 1): np.array([[9, 12, 10, 14, 0, 0, 0, 0]], float),
    }
    peer_x = np.vstack((base[("B", 1)], base[("C", 1)]))
    mu0, sd0 = reference_stats(peer_x)
    changed = dict(base)
    changed[("A", 1)] = base[("A", 1)] * 100
    mu1, sd1 = reference_stats(np.vstack((changed[("B", 1)], changed[("C", 1)])))
    if not (np.array_equal(mu0, mu1) and np.array_equal(sd0, sd1)):
        raise AssertionError("focal bat leaked into peer-only normalization")
    if not np.all(sd0 > 0):
        raise AssertionError("synthetic reference invalid")

    toy = {
        "A": {1: 1.0, 2: 1.2, 3: 0.8},
        "B": {1: -1.0, 2: -1.2, 3: -0.8},
        "C": {1: 0.0, 2: 0.1, 3: -0.1},
    }
    obs = score(toy)
    if abs(obs["G"] - (obs["MSE_zero"] - obs["MSE_self"])) > 1e-12:
        raise AssertionError("MSE gain decomposition invalid")
    rng = np.random.default_rng(123)
    p = shuffled_correspondence(toy, rng)
    for e in (1, 2, 3):
        if sorted(p[b][e] for b in p) != sorted(toy[b][e] for b in toy):
            raise AssertionError("within-configuration permutation changed source values")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out", default="rhino_peer_only_standardization_result_v1.json"
    )
    args = parser.parse_args()
    synthetic_self_checks()
    clusters = source_clusters()
    full, matched, peer, support = build_tables(clusters)
    old = score(full)
    for k, expected in PREVIOUS.items():
        if not math.isclose(old[k], expected, rel_tol=0.0, abs_tol=2e-5):
            raise RuntimeError(
                f"STOP_UPSTREAM_REPRODUCTION: {k}={old[k]} expected={expected}"
            )

    paired = score(matched)
    observed = score(peer)
    rng = np.random.default_rng(NULL_SEED)
    null = np.empty(N_PERM, dtype=float)
    for k in range(N_PERM):
        null[k] = score(shuffled_correspondence(peer, rng))["G"]
    p_one = float((1 + np.count_nonzero(null >= observed["G"] - 1e-15))
                  / (N_PERM + 1))

    bats = sorted(peer)
    gains = np.array([observed["per_bat"][b]["G"] for b in bats])
    rboot = np.random.default_rng(BOOT_SEED)
    draws = rboot.integers(0, len(bats), size=(BOOT_REPS, len(bats)))
    samples = gains[draws].mean(axis=1)
    leave_one = {
        b: float(np.mean([observed["per_bat"][bb]["G"]
                          for bb in bats if bb != b]))
        for b in bats
    }
    out = {
        "status": "POST_OUTCOME_TARGET_LEAKAGE_SENSITIVITY_NOT_CONFIRMATORY",
        "contract": "RHINO_PEER_ONLY_STANDARDIZATION_CONTRACT_V1.md",
        "source": "Figshare 29209493; frozen Rhinolophus 45-trajectory loader",
        "n_source_trajectories": sum(len(a) for a in clusters.values()),
        "A_original_inclusive_25_cell_reproduction": old,
        "B_inclusive_reference_on_peer_eligible_matched_support": paired,
        "C_target_excluded_peer_only_reference": observed,
        "structural_support": support,
        "conditional_permutation": {
            "n": N_PERM,
            "seed": NULL_SEED,
            "null_mean": float(np.mean(null)),
            "null_95_percentile": [float(v) for v in np.quantile(null, [0.025, 0.975])],
            "p_one_sided": p_one,
        },
        "bat_cluster_bootstrap": {
            "n": BOOT_REPS, "seed": BOOT_SEED,
            "G_95_percentile": [float(v) for v in np.quantile(samples, [0.025, 0.975])]
        },
        "leave_one_bat_out_aggregate_G_not_renormalized": leave_one,
        "peer_only_verdict": (
            "SUPPORTED_WITH_PEER_REFERENCE"
            if observed["G"] > 0 and p_one <= .05
            else "UNSUPPORTED_WITH_PEER_REFERENCE"
        ),
        "interpretation_ceiling": (
            "Requires current-environment peer trials for normalization; "
            "not a no-peer future-configuration forecast. "
            "Five bats and post-outcome design; not population confirmation."
        ),
    }
    Path(args.out).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n",
                              encoding="utf-8")
    print(json.dumps({
        "old_reproduction_G": old["G"],
        "support": support,
        "inclusive_matched": {k: paired[k] for k in ("G", "MSE_zero", "MSE_self", "R2_vs_zero")},
        "peer_only": {k: observed[k] for k in ("G", "MSE_zero", "MSE_self", "R2_vs_zero")},
        "peer_individual_gains": {b: observed["per_bat"][b]["G"] for b in bats},
        "permutation_p": p_one,
        "permutation_null_95": out["conditional_permutation"]["null_95_percentile"],
        "bat_bootstrap_G_95": out["bat_cluster_bootstrap"]["G_95_percentile"],
        "verdict": out["peer_only_verdict"],
    }, indent=2))


if __name__ == "__main__":
    main()
