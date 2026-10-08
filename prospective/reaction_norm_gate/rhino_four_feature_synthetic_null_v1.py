#!/usr/bin/env python3
"""Synthetic-only four-feature target-blind Rhino estimator calibration.

Replicates the estimation logic, 5-bat/7-environment/25-cell support and
45 trial-file count of the previous archive, but does NOT read that archive.
Environment membership and replicate placement here are deliberately
SCHEMATIC, NOT CLAIMED TO MATCH THE ORIGINAL file manifests.
No external network, no measurements, no biological effect estimate.
"""
from __future__ import annotations
from collections import defaultdict
import argparse
import json
import math
import random

SUPPORT = {
    "A": (1, 2, 3, 5, 7),
    "B": (1, 3, 5, 7),
    "C": (1, 2, 4, 6, 7),
    "D": (1, 2, 3, 4, 6, 7),
    "E": (1, 2, 3, 5, 6),
}
BATS = tuple(SUPPORT)
ENVS = tuple(range(1, 8))
SINGLETONS = {(7,"A"), (7,"B"), (7,"C"), (7,"D"), (6,"E")}
CELLS = tuple((e, b) for e in ENVS for b in BATS if e in SUPPORT[b])
N_NULL_PERM = 199
N_REPLICATES = 280
SEED = 202610082041

def check_structure():
    assert len(CELLS) == 25 and len(BATS) == 5 and len(ENVS) == 7
    assert {b: sum(e in SUPPORT[b] for e in ENVS) for b in BATS} == {
        "A": 5, "B": 4, "C": 5, "D": 6, "E": 5}
    assert len(SINGLETONS) == 5
    assert all(k in CELLS for k in SINGLETONS)
    assert sum(1 if k in SINGLETONS else 2 for k in CELLS) == 45

def fabricate(rng: random.Random, sigmas: dict[str,float],
              rho: float = 0.6):
    """One independent 4D random centroid per cell, duplicated to 45 records.

    The exact duplicates are a deliberate artificial device for a faithful
    trial-count reference without making centroid precision depend on n=1/2.
    It is not a realistic model of within-trajectory measurement error.
    There is NO personal mean identity, learned trait, or bat x env reaction.
    """
    raw=[]
    cellvec={}
    for e,b in CELLS:
        z_common=rng.gauss(0,1)
        vals=[sigmas[b]*(math.sqrt(rho)*z_common+
                        math.sqrt(1-rho)*rng.gauss(0,1))
              + 0.35*math.sin(e+f*0.55)
              for f in range(4)]
        cellvec[(e,b)]=tuple(vals)
        for _ in range(1 if (e,b) in SINGLETONS else 2):
            raw.append((e,b,tuple(vals)))
    assert len(raw)==45
    return raw,cellvec

def folds_from_raw(raw,cellvec):
    folds={}
    for held in ENVS:
        # Fit four training-only means and unbiased SD, as in #79.
        prior=[vec for e,b,vec in raw if e!=held]
        n=len(prior)
        mu=[sum(v[f] for v in prior)/n for f in range(4)]
        sd=[math.sqrt(sum((v[f]-mu[f])**2 for v in prior)/(n-1))
            for f in range(4)]
        assert min(sd)>0
        folds[held]={key:sum((vec[f]-mu[f])/sd[f]
                            for f in range(4))/4.0
                     for key,vec in cellvec.items()}
    return folds

def identity_mapping():
    return {key:key[1] for key in CELLS}

def shuffled_mapping(rng:random.Random):
    out={}
    for e in ENVS:
        members=[b for ee,b in CELLS if ee==e]
        shuffled=members[:]
        rng.shuffle(shuffled)
        for original,label in zip(members,shuffled):
            out[(e,original)]=label
    return out

def gain(folds,mapping):
    history={b:[] for b in BATS}
    for key,label in mapping.items():
        history[label].append(key)
    perbat=defaultdict(list)
    for (e,b), label in mapping.items():
        other=[folds[e][key] for key in history[label]
               if key[0]!=e]
        assert len(other)>=3
        y=folds[e][(e,b)]
        pred=sum(other)/len(other)
        perbat[label].append(y*y-(y-pred)**2)
    return sum(sum(perbat[b])/len(perbat[b]) for b in BATS)/len(BATS)

def run_scenario(sigmas, seed, repetitions=N_REPLICATES):
    rng=random.Random(seed)
    rejected_005=0
    rejected_001=0
    mean_gain=0
    for _ in range(repetitions):
        raw, cells=fabricate(rng,sigmas)
        folds=folds_from_raw(raw,cells)
        observed=gain(folds,identity_mapping())
        hits=1
        for _ in range(N_NULL_PERM):
            if gain(folds,shuffled_mapping(rng))>=observed-1e-12:
                hits+=1
        p=hits/(N_NULL_PERM+1)
        if p<=.05: rejected_005+=1
        if p<=.01: rejected_001+=1
        mean_gain+=observed
    return {
       "fabricated_draws":repetitions,
       "per_draw_label_shuffles":N_NULL_PERM,
       "false_positive_rate_005":rejected_005/repetitions,
       "false_positive_rate_001":rejected_001/repetitions,
       "mean_null_gain":mean_gain/repetitions,
       "bat_sd":sigmas,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    opts=p.parse_args()
    if not opts.self_test:
        p.error("synthetic-only code; no live/raw/empirical dataset access implemented")
    check_structure()
    # Independently seeded scenarios: same support, common environmental
    # offset and within-cell four-feature correlation; only stable sigma differs.
    equal=run_scenario({b:1.0 for b in BATS},SEED)
    heterogeneous=run_scenario(
        dict(zip(BATS,(.3,.6,1.2,2.5,5.0))), SEED+1)
    assert equal["fabricated_draws"]==N_REPLICATES
    assert heterogeneous["fabricated_draws"]==N_REPLICATES
    assert math.isfinite(equal["mean_null_gain"])
    assert math.isfinite(heterogeneous["mean_null_gain"])
    print(json.dumps({
       "source":"NO animal data; every 4D feature synthetically generated",
       "design":"SCHEMATIC 45 trials / 25 bat-environment cells / 5 bats / 7 environments, original forecast scalar and label-permutation logic",
       "original_exact_filename_membership_used":False,
       "four_feature_correlation":0.6,
       "result_equal_noise":equal,
       "result_unequal_noise":heterogeneous,
       "evidence_status":"SYNTHETIC_NULL_STRESS_ONLY",
       "warning":"Not a correction to original PR #79 p=.0003; does not model source-specific variance or exactly reproduce source occupancy",
    },sort_keys=True,indent=2))

if __name__=="__main__":
    main()
