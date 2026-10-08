#!/usr/bin/env python3
"""Fabricated-data-only comparison: bat-label permutations vs known-mu whole-cell signs.

No external API, no Figshare observations, no animal telemetry or task outcomes.
The null is conditional on externally known environment means and independent,
jointly centrally symmetric four-feature bat×environment residual vectors.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import json
import math
import random

from rhino_four_feature_synthetic_null_v1 import (
    CELLS, SINGLETONS, BATS, ENVS, check_structure,
    folds_from_raw, gain, identity_mapping, shuffled_mapping
)

N_SIM = 160
B = 199
SEED = 202610082151
RHO = .6
SD_EQUAL = {bat:1.0 for bat in BATS}
SD_UNEQUAL = dict(zip(BATS, (.3,.6,1.2,2.5,5.0)))


def shared_environment(e):
    return tuple(.35 * math.sin(e + f*.55) for f in range(4))


def noise(rng, kind):
    if kind == "gaussian":
        return rng.gauss(0, 1)
    if kind == "skewed":
        return rng.expovariate(1) - 1
    raise ValueError("Unknown simulation mode")


def fabricate(rng, sigmas, kind):
    cells = {}
    for e,b in CELLS:
        mu = shared_environment(e)
        common = noise(rng, kind)
        cells[(e,b)] = tuple(
            mu[f] + sigmas[b] * (
                math.sqrt(RHO)*common + math.sqrt(1-RHO)*noise(rng,kind))
            for f in range(4)
        )
    return cells


def to_raw(cells):
    raw=[]
    for e,b in CELLS:
        for rep in range(1 if (e,b) in SINGLETONS else 2):
            raw.append((e,b,cells[(e,b)]))
    assert len(raw) == 45
    return raw


def flip_complete_vectors(cells, rng):
    transformed={}
    for e,b in CELLS:
        sign = 1 if rng.getrandbits(1) else -1
        mu = shared_environment(e)
        old = cells[(e,b)]
        transformed[(e,b)] = tuple(
            mu[f] + sign*(old[f]-mu[f]) for f in range(4)
        )
    return transformed


def score(cells):
    raw=to_raw(cells)
    return gain(folds_from_raw(raw,cells),identity_mapping())


def p_label(cells, observed, rng):
    # Old reference: fold centering/scaling held constant; bat labels remapped.
    folds=folds_from_raw(to_raw(cells),cells)
    count=1
    for _ in range(B):
        if gain(folds,shuffled_mapping(rng)) >= observed - 1e-12:
            count+=1
    return count/(B+1)


def p_sign(cells, observed, rng):
    # Proposed oracle: preserve each *whole* 4D cell residual and bat amplitude.
    # Recompute all 7 training-only references for EVERY randomized draw.
    count=1
    for _ in range(B):
        other=flip_complete_vectors(cells,rng)
        if score(other) >= observed - 1e-12:
            count+=1
    return count/(B+1)


def scenario(kind, sigmas, seed):
    rng=random.Random(seed)
    n_old=n_new=n_old_strict=n_new_strict=0
    obs_total=0.0
    for _ in range(N_SIM):
        cells=fabricate(rng,sigmas,kind)
        obs=score(cells)
        label=p_label(cells,obs,rng)
        sign=p_sign(cells,obs,rng)
        n_old+=(label <= .05)
        n_new+=(sign <= .05)
        n_old_strict+=(label <= .01)
        n_new_strict+=(sign <= .01)
        obs_total+=obs
    return {
        "bat_sd":sigmas,"residual_distribution":kind,
        "simulated_archives":N_SIM,
        "null_draws_per_archive":B,
        "mean_observed_gain":obs_total/N_SIM,
        "label_false_positive_at_005":n_old/N_SIM,
        "whole_vector_sign_false_positive_at_005":n_new/N_SIM,
        "label_false_positive_at_001":n_old_strict/N_SIM,
        "whole_vector_sign_false_positive_at_001":n_new_strict/N_SIM,
        "label_rejections_005":n_old,
        "sign_rejections_005":n_new,
    }


def test_invariances():
    check_structure()
    rng=random.Random(37)
    c=fabricate(rng,SD_UNEQUAL,"gaussian")
    assert len(c)==25
    before=score(c)
    after=flip_complete_vectors(c,random.Random(97))
    assert len(to_raw(after)) == 45
    for e,b in CELLS:
        mu=shared_environment(e)
        original=[c[(e,b)][f]-mu[f] for f in range(4)]
        flipped=[after[(e,b)][f]-mu[f] for f in range(4)]
        assert all(abs(abs(original[f])-abs(flipped[f]))<1e-11 for f in range(4))
        if abs(original[0]) > 1e-10:
            s=flipped[0]/original[0]
            assert abs(abs(s)-1)<1e-10
            assert all(abs(flipped[f]-s*original[f])<1e-10 for f in range(4))
    assert math.isfinite(before) and math.isfinite(score(after))
    return "PASS"


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    opt=parser.parse_args()
    if not opt.self_test:
        parser.error("synthetic-only. Real data opening or re-fitting not implemented.")
    gates=test_invariances()
    cases={
        "equal_gaussian":scenario("gaussian",SD_EQUAL,SEED),
        "hetero_gaussian":scenario("gaussian",SD_UNEQUAL,SEED+1),
        "hetero_asymmetric":scenario("skewed",SD_UNEQUAL,SEED+2),
    }
    print(json.dumps({
        "status":"SYNTHETIC_KNOWN_MEAN_SIGNFLIP_STRESS_ONLY",
        "source":"ALL numerical observations fabricated. No bats.",
        "fixed_before_results":"CELLWISE_SIGNFLIP_KNOWN_ENVIRONMENT_CONTRACT_V1.md",
        "within_vector_correlation":RHO,
        "n_4d_cells":len(CELLS),
        "n_artificial_trial_rows":45,
        "self_test":gates,
        "independent_environment_center_known":True,
        "caveat":"sign symmetry + external mu unavailable in real bat archive",
        "scenarios":cases,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
