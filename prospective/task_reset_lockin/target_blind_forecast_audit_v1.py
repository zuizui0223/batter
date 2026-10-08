#!/usr/bin/env python3
"""Post-outcome audit of forecast semantics: target-blind vs peer-conditioned.
Freeze: TARGET_BLIND_FORECAST_AUDIT_CONTRACT_V1.md.
No result from this script is an independent confirmatory biological test.
"""
from __future__ import annotations

import argparse
import collections
import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "rhino_configuration_identity_primary_v1.py"
EXPECTED = {"A": 5, "B": 4, "C": 5, "D": 6, "E": 5}
N_PERM = 9999
PERM_SEED = 202610081319
N_BOOT = 9999
BOOT_SEED = 202610081320


def source_cells():
    spec = importlib.util.spec_from_file_location("rhino_source", SOURCE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    trajectories = module.load_rhino()
    assert len(trajectories) == 45
    assert all(x["feature_valid"] for x in trajectories)
    raw = [(int(x["env"]), str(x["bat"]), np.asarray(x["features"][:4], float))
           for x in trajectories]
    return raw


def make_cells(raw):
    groups = collections.defaultdict(list)
    for e, b, features in raw:
        a = np.asarray(features, float)
        if a.shape != (4,) or not np.isfinite(a).all():
            raise ValueError("Bad four-feature trial")
        groups[(e, b)].append(a)
    return {k: np.mean(np.vstack(v), axis=0) for k, v in groups.items()}


def peer_mean(cells, e, focal):
    peers = [v for (ee, b), v in cells.items() if ee == e and b != focal]
    if len(peers) < 1:
        raise ValueError(f"Unidentifiable peer reference: env={e}, bat={focal}")
    return np.mean(np.vstack(peers), axis=0)


def training_reference(raw, target_env):
    values = np.vstack([v for e, _b, v in raw if e != target_env])
    if len(values) < 2:
        raise ValueError("Not enough training trials")
    mu = np.mean(values, axis=0)
    sd = np.std(values, axis=0, ddof=1)
    if not np.isfinite(sd).all() or np.any(sd <= 0):
        raise ValueError("Bad training-only reference SD")
    return mu, sd


def fold_values(raw, cells, mode):
    envs = sorted(set(e for e, _b in cells))
    folds = {}
    for held in envs:
        mu, sd = training_reference(raw, held)
        values = {}
        for (e, b), v in cells.items():
            if mode == "blind":
                z = (v - mu) / sd
            elif mode == "peer":
                z = (v - peer_mean(cells, e, b)) / sd
            else:
                raise ValueError("Unsupported mode")
            values[(e, b)] = float(np.mean(z))
        folds[held] = values
    return folds


def structure_guard(raw, cells):
    if len(raw) != 45 or len(cells) != 25:
        raise RuntimeError("Rhinolophus archive structural drift")
    per_bat = collections.Counter(b for e, b in cells)
    if dict(per_bat) != EXPECTED:
        raise RuntimeError(f"Bat environment support drift: {dict(per_bat)}")
    per_env = collections.Counter(e for e, b in cells)
    if sorted(per_env) != list(range(1, 8)):
        raise RuntimeError("Expected seven numbered configurations")
    if min(per_env.values()) < 2:
        raise RuntimeError("Some peer target configurations have no other bat")
    return {"n_trajectories": len(raw), "n_bat_environment_cells": len(cells),
            "bat_environments": dict(sorted(per_bat.items())),
            "bats_by_configuration": {str(e): per_env[e] for e in sorted(per_env)}}


def observed_mapping(cells):
    return {key: key[1] for key in cells}


def permuted_mapping(cells, rng):
    result = {}
    for e in sorted(set(x[0] for x in cells)):
        bs = sorted(b for ee, b in cells if ee == e)
        perm = rng.permutation(bs)
        for old, new in zip(bs, perm):
            result[(e, old)] = str(new)
    return result


def score(folds, mapping):
    # Each target has its own scale fitted on other configurations only.
    history = collections.defaultdict(list)
    for (e, original_b), label in mapping.items():
        history[label].append((e, original_b))
    per = collections.defaultdict(list)
    for (target_e, original_b), label in mapping.items():
        other = [folds[target_e][(e, b)] for e, b in history[label] if e != target_e]
        if len(other) < 3:
            raise RuntimeError(f"Unmatched history for {label} target {target_e}")
        y = folds[target_e][(target_e, original_b)]
        pred = float(np.mean(other))
        per[label].append((y * y, (y - pred) ** 2))
    summary = {}
    for bat, records in sorted(per.items()):
        v = np.asarray(records, float)
        mse0, mse_self = np.mean(v, axis=0)
        summary[bat] = {
            "n_targets": len(v), "MSE_zero": float(mse0),
            "MSE_self": float(mse_self),
            "gain": float(mse0 - mse_self),
            "R2": float(1 - mse_self / mse0) if mse0 > 0 else None,
        }
    mse0 = float(np.mean([d["MSE_zero"] for d in summary.values()]))
    mse_self = float(np.mean([d["MSE_self"] for d in summary.values()]))
    return {
        "G": float(mse0 - mse_self), "MSE_zero": mse0,
        "MSE_self": mse_self, "R2": float(1 - mse_self / mse0)
        if mse0 > 0 else None, "per_bat": summary,
    }


def test_invariance():
    # Synthetic features with independent configuration and individual offsets.
    raw = []
    for e in range(1, 5):
        for j, b in enumerate("ABC"):
            for rep in range(2):
                raw.append((e, b, np.array([
                    e * 0.2 + j * 0.9 + rep * 0.05,
                    2 * e + j * 0.3 + rep * 0.02,
                    j * 0.5 + e * 0.1 + rep * 0.06,
                    j * 1.1 + e * 0.8 + rep * 0.01,
                ])))
    cells = make_cells(raw)
    mu, sd = training_reference(raw, 4)
    # All future config-4 raw values may change without changing the forecast reference.
    modified = [(e, b, v + 1e5 if e == 4 else v.copy()) for e, b, v in raw]
    mu2, sd2 = training_reference(modified, 4)
    assert np.array_equal(mu, mu2) and np.array_equal(sd, sd2)
    # Focal A at e=4 must not contribute to its own peer reference.
    peer = peer_mean(cells, 4, "A")
    changed = dict(cells)
    changed[(4, "A")] = changed[(4, "A")] + 1e8
    assert np.array_equal(peer, peer_mean(changed, 4, "A"))
    for mode in ("blind", "peer"):
        folds = fold_values(raw, cells, mode)
        baseline = score(folds, observed_mapping(cells))
        assert np.isfinite(baseline["G"])
        rng = np.random.default_rng(7)
        shuffled = score(folds, permuted_mapping(cells, rng))
        assert np.isfinite(shuffled["G"])
        # Own historical prediction is independent of *all* numeric values in target e.
        changed_folds = fold_values(modified, make_cells(modified), mode)
        # Peer-mode common environment translation cancels in values, blind-mode does not.
        for cell in cells:
            if cell[0] != 4:
                assert np.isclose(folds[4][cell], changed_folds[4][cell])
    return {"synthetic_target_blind_reference": "PASS",
            "synthetic_peer_reference_excludes_focal": "PASS",
            "synthetic_permutation_and_fold_score": "PASS"}


def evaluate(folds, cells):
    observed = score(folds, observed_mapping(cells))
    null = np.empty(N_PERM, float)
    rng = np.random.default_rng(PERM_SEED)
    for k in range(N_PERM):
        null[k] = score(folds, permuted_mapping(cells, rng))["G"]
    p = float((1 + np.count_nonzero(null >= observed["G"] - 1e-15)) / (N_PERM + 1))
    bat_gains = np.asarray([observed["per_bat"][b]["gain"] for b in sorted(EXPECTED)])
    rng_boot = np.random.default_rng(BOOT_SEED)
    draws = rng_boot.integers(0, len(bat_gains), size=(N_BOOT, len(bat_gains)))
    boot = bat_gains[draws].mean(axis=1)
    leave_one = {
        b: float(np.mean([observed["per_bat"][other]["gain"] for other in EXPECTED if other != b]))
        for b in sorted(EXPECTED)
    }
    return {
        "observed": observed,
        "permutation": {
            "B": N_PERM, "seed": PERM_SEED, "p_one_sided": p,
            "null_mean": float(np.mean(null)),
            "null_ci95": [float(np.quantile(null, .025)), float(np.quantile(null, .975))],
        },
        "bat_cluster_bootstrap": {
            "B": N_BOOT, "seed": BOOT_SEED,
            "gain_ci95": [float(np.quantile(boot, .025)), float(np.quantile(boot, .975))],
        },
        "leave_one_bat_out_gains": leave_one,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--out", default="target_blind_forecast_audit_v1.json")
    args = parser.parse_args()
    tests = test_invariance()
    if args.self_test:
        print(json.dumps(tests, sort_keys=True))
        return
    raw = source_cells()
    cells = make_cells(raw)
    structure = structure_guard(raw, cells)
    results = {
        "status": "POST_OUTCOME_PREDICTIVE_SEMANTICS_AUDIT",
        "contract": "TARGET_BLIND_FORECAST_AUDIT_CONTRACT_V1.md",
        "source": "Figshare 29209493 Rhinolophus, frozen 45 trajectories",
        "gate": structure,
        "verification": tests,
        "target_configuration_blind_primary": evaluate(fold_values(raw, cells, "blind"), cells),
        "peer_conditioned_target_bat_blind_secondary":
            evaluate(fold_values(raw, cells, "peer"), cells),
        "claim_limit": (
            "Conditionally shuffled identity correspondence within five observed bats; "
            "not an independent confirmatory test; peer-conditioned requires "
            "contemporaneous target-configuration conspecific observations."
        ),
    }
    Path(args.out).write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for key in ("target_configuration_blind_primary",
                "peer_conditioned_target_bat_blind_secondary"):
        z = results[key]
        print(json.dumps({
            "endpoint": key,
            "G": z["observed"]["G"],
            "R2": z["observed"]["R2"],
            "MSE_zero": z["observed"]["MSE_zero"],
            "MSE_self": z["observed"]["MSE_self"],
            "per_bat_gain": {b: v["gain"] for b, v in z["observed"]["per_bat"].items()},
            "p_one_sided": z["permutation"]["p_one_sided"],
            "null_ci95": z["permutation"]["null_ci95"],
            "bat_bootstrap_ci95": z["bat_cluster_bootstrap"]["gain_ci95"],
        }, sort_keys=True))


if __name__ == "__main__":
    main()
