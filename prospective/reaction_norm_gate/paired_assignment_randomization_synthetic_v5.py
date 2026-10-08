#!/usr/bin/env python3
"""EXCLUSIVELY FABRICATED paired-assignment randomization under Fisher sharp H0.

The example enumerates all 2^15 assignments for fictional 5 bats x 3 matched
pairs and tests the randomization p-value calibration EXACTLY. It does NOT
test repeatability, personal slopes, or wild 3D bat ecology.
"""
from __future__ import annotations
import argparse
from bisect import bisect_left
from itertools import product
from math import isfinite
import json

BATS = "ABCDE"
SESSIONS = 3
N_PAIRS = len(BATS)*SESSIONS
assert N_PAIRS==15
N_ASSIGN = 1 << N_PAIRS


def synthetic_fixed_slots():
    """Potential no-treatment outcomes, arbitrarily different across bats/slots.

    Every outcome is fixed before assigning which slot receives the treatment;
    distributional exchangeability, Gaussian noise and sigma equality are NOT
    assumed. Numbers are intentionally hand-constructed and not observations.
    """
    records=[]
    for i,bat in enumerate(BATS):
        personal_baseline = (i-2)*31.0
        for session in range(SESSIONS):
            shared_night = 400.0 + 13.0*session
            # Different deterministic slot effects and bat x slot noise:
            within_pair = ((i*7+session*3+2)**2 % 43 - 20)/6.0
            y_first = personal_baseline+shared_night + 1.3 + within_pair
            y_second = personal_baseline+shared_night - 0.7 - within_pair/3.0
            records.append((bat,session,y_first,y_second))
    return records


def difference(records):
    return [slot0-slot1 for _bat,_s,slot0,slot1 in records]


def treatment_stat(weights, allocation):
    """+1 when slot 0 is challenged, -1 when slot 1 is challenged.

    Here each bat has three blocks: equal-bat/equal-block mean is 1/15.
    """
    return sum((1.0 if allocation[j] else -1.0)*weights[j]
               for j in range(N_PAIRS))/N_PAIRS


def null_distribution(weights):
    if len(weights)!=N_PAIRS or not all(isfinite(x) for x in weights):
        raise ValueError("Exactly 15 finite paired-slot differences required")
    # Each of the 15 slot assignments is known to have probability one-half.
    # Under Fisher sharp null the outcomes/weights remain fixed for every
    # legal assignment, hence this enumerates the ACTUAL design randomization.
    return sorted(treatment_stat(weights,allocation)
                  for allocation in product((0,1),repeat=N_PAIRS))


def exact_one_sided_p(sorted_null, observed):
    # Exact randomization including observed assignment, NO (+1)/(B+1).
    return (len(sorted_null)-bisect_left(sorted_null,observed-1e-11))/len(sorted_null)


def check():
    records=synthetic_fixed_slots()
    assert len(records)==N_PAIRS
    weights=difference(records)
    distribution=null_distribution(weights)
    assert len(distribution)==32768

    # Every possible allocation is equally likely under sharp H0, so the
    # distribution of its randomization p-value MUST be super-uniform.
    for alpha in (0.01,0.05,0.10):
        n=sum(exact_one_sided_p(distribution,t)<=alpha+1e-12
              for t in distribution)
        assert n/N_ASSIGN <= alpha+1e-12

    # An independently random assignment (deterministically selected here)
    # has an ordinary exact p-value, not evidence of a biological effect.
    fixed_assignment=tuple(int(j%3==0 or j%5==1) for j in range(N_PAIRS))
    observed=treatment_stat(weights,fixed_assignment)
    p=exact_one_sided_p(distribution,observed)

    # Each individual and occasion's arbitrary shared additive baseline
    # cancels in its slot contrast, without knowing or estimating it.
    shifted=[]
    for j,(bat,s,a,b) in enumerate(records):
        unknown_bat_intercept=(ord(bat)-ord("A"))*100000.0
        unknown_occasion_center=(s+1)*10000.0
        add=unknown_bat_intercept+unknown_occasion_center
        shifted.append((bat,s,a+add,b+add))
    weights2=difference(shifted)
    assert all(abs(a-b)<1e-9 for a,b in zip(weights,weights2))
    assert abs(treatment_stat(weights2,fixed_assignment)-observed)<1e-9

    # Crucial COUNTEREXAMPLE: identical positive effect tau for every bat
    # makes the sharp-null test reject; that is NOT heterogeneous policy.
    tau=100.0
    shared_D=[tau + (2*z-1)*w for z,w in zip(fixed_assignment,weights)]
    shared_T=sum(shared_D)/len(shared_D)
    shared_null_p=exact_one_sided_p(distribution,shared_T)
    assert shared_null_p <= 1/N_ASSIGN
    assert len(set(BATS))==5

    rates={}
    for alpha in (0.01,0.05,0.10):
        total=sum(exact_one_sided_p(distribution,t)<=alpha+1e-12
                  for t in distribution)
        rates[str(alpha)]={"rejected":total,"total":N_ASSIGN,
                           "exact_randomization_type_i":total/N_ASSIGN}
    return {
      "result":"PASS_EXACT_DESIGN_BASED_SHARP_NULL_SYNTHETIC",
      "fictional_bats":len(BATS),"fictional_independent_sessions":SESSIONS,
      "matched_bat_session_pairs":N_PAIRS,
      "legal_random_assignments":N_ASSIGN,
      "sharp_null_rejection_fractions":rates,
      "example_random_allocation_p":p,
      "unknown_bat_and_context_intercepts_cancel":"PASS",
      "individual_baselines_and_variances_unconstrained":"PASS_UNDER_FIXED_SHARP_NULL",
      "identical_positive_effect_rejects_sharp_null":{
         "common_effect_per_bat":tau,
         "example_p":shared_null_p,
         "individual_effect_heterogeneity":0.0,
         "warning":"rejecting sharp no-effect does not establish bat-specific slopes"
      },
      "NO_biological_effects_tested":True
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    a=parser.parse_args()
    if not a.self_test:
        parser.error("synthetic-only: NO real animal data reading implemented")
    print(json.dumps(check(),indent=2,sort_keys=True))


if __name__=="__main__":
    main()
