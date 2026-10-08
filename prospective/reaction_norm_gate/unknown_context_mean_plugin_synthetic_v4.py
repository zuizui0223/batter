#!/usr/bin/env python3
"""Standalone, synthetic-only test of sign flips about a sample-fitted context mean.

NEVER retrieves bat observations. The exact algebraic non-invariance is the
primary result; Monte Carlo error rates are only illustrative.
"""
from __future__ import annotations
import argparse
import json
import math
import random

from whole_cell_signflip_synthetic_v1 import (
    BATS, CELLS, ENVS, RHO, SD_EQUAL, SD_UNEQUAL,
    fabricate, shared_environment, to_raw, score, p_label
)
from rhino_four_feature_synthetic_null_v1 import folds_from_raw, gain, identity_mapping

N_ARCHIVES=120
N_RANDOMIZATIONS=99
SEED=202610082238


def estimated_context_means(cells):
    """Unweighted observed-bat centroid means; NOT independent mu."""
    mu={}
    for e in ENVS:
        matching=[cells[(ee,b)] for ee,b in CELLS if ee==e]
        if len(matching)<2:
            raise ValueError("no co-observed peers")
        mu[e]=tuple(sum(v[f] for v in matching)/len(matching) for f in range(4))
    return mu


def sign_transform(cells,mu,rng):
    out={}
    for e,b in CELLS:
        s=1 if rng.getrandbits(1) else -1
        out[(e,b)] = tuple(
            mu[e][f] + s*(cells[(e,b)][f]-mu[e][f])
            for f in range(4)
        )
    return out


def p_sign(cells,mu,observed,rng):
    extreme=1
    for _ in range(N_RANDOMIZATIONS):
        fake=sign_transform(cells,mu,rng)
        if score(fake)>=observed-1e-12:
            extreme+=1
    return extreme/(N_RANDOMIZATIONS+1)


def original_perm_p(cells,observed,rng):
    from rhino_four_feature_synthetic_null_v1 import shuffled_mapping
    folds=folds_from_raw(to_raw(cells),cells)
    hits=1
    for _ in range(N_RANDOMIZATIONS):
        if gain(folds,shuffled_mapping(rng))>=observed-1e-12:
            hits+=1
    return hits/(N_RANDOMIZATIONS+1)


def explicit_noninvariance():
    # A one-dimensional face of the 4D construction. Bat values 1,3,5.
    # Fit mu=3 => residuals -2,0,+2; flip only first => +2,0,+2.
    raw=(1.,3.,5.)
    mu=sum(raw)/len(raw)
    r=[x-mu for x in raw]
    transformed=[-r[0],r[1],r[2]]
    assert sum(r)==0
    assert sum(transformed)==4
    # Additionally demonstrate this occurs in a genuine 4D fabricated cell panel.
    c=fabricate(random.Random(107),SD_UNEQUAL,"gaussian")
    fitted=estimated_context_means(c)
    for e in ENVS:
        members=[b for ee,b in CELLS if ee==e]
        for f in range(4):
            assert abs(sum(c[(e,b)][f]-fitted[e][f] for b in members))<1e-10
    target=next(e for e in ENVS if len([b for ee,b in CELLS if ee==e])>=2)
    members=[b for ee,b in CELLS if ee==target]
    flipped=dict(c)
    first=members[0]
    flipped[(target,first)]=tuple(2*fitted[target][f]-c[(target,first)][f] for f in range(4))
    post=[sum(flipped[(target,b)][f]-fitted[target][f] for b in members) for f in range(4)]
    assert any(abs(v)>1e-6 for v in post)
    return {"equal_weight_fitted_residual_sum_before":0.,
            "explicit_3bat_sign_flipped_residual_sum":4.,
            "whole_4d_bat_context_constraint_violated":True}


def scenario(sigmas,seed):
    rng=random.Random(seed)
    counts={"oracle":0,"plugin":0,"label":0}
    means={"oracle":0.,"plugin":0.,"label":0.}
    for _ in range(N_ARCHIVES):
        c=fabricate(rng,sigmas,"gaussian")
        observed=score(c)
        known={e:shared_environment(e) for e in ENVS}
        fitted=estimated_context_means(c)
        pvals={
            "oracle":p_sign(c,known,observed,rng),
            "plugin":p_sign(c,fitted,observed,rng),
            "label":original_perm_p(c,observed,rng)
        }
        for k,p in pvals.items():
            counts[k]+=int(p<=.05)
            means[k]+=p
    return {
        "fabricated_archives":N_ARCHIVES,
        "null_randomizations_per_archive":N_RANDOMIZATIONS,
        "rejection_counts_005":counts,
        "rejection_fractions_005":{k:counts[k]/N_ARCHIVES for k in counts},
        "mean_null_p":{k:means[k]/N_ARCHIVES for k in means},
        "bat_residual_sd":sigmas
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if not args.self_test:
        p.error("synthetic-only; no bat recordings or real datasets supported")
    algebra=explicit_noninvariance()
    r={
       "status":"SYNTHETIC_ONLY",
       "frozen_contract":"UNKNOWN_ENVIRONMENT_MEAN_PLUGIN_NO_GO_CONTRACT_V4.md",
       "structural_proof":algebra,
       "scenarios":{
          "equal_gaussian":scenario(SD_EQUAL,SEED),
          "unequal_gaussian":scenario(SD_UNEQUAL,SEED+1)
       },
       "restriction":"The known-mu oracle needs independent means; fitted-mu signs lack invariance, whatever Monte Carlo rates say",
       "animal_data_opened":False,
    }
    assert all(0<=z<=N_ARCHIVES for x in r["scenarios"].values()
               for z in x["rejection_counts_005"].values())
    print(json.dumps(r,sort_keys=True,indent=2))


if __name__=="__main__":
    main()
