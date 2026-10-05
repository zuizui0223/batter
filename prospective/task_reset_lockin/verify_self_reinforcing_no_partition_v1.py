#!/usr/bin/env python3
"""Finite-sample verification of self-reinforcing specialization without partition."""
from __future__ import annotations
import json
import numpy as np

SEED=202610051801
N=12000
T=400
PAIR_N=30000
GRID=[(K,a) for K in (2,4,8) for a in (0.1,0.5,1.0,5.0)]

def simulate(K,alpha,rng):
    counts=np.zeros((N,K),dtype=np.int32)
    for t in range(T):
        probs=(counts+alpha)/(K*alpha+t)
        u=rng.random(N)
        cs=np.cumsum(probs,axis=1)
        choice=(u[:,None]>cs).sum(axis=1)
        counts[np.arange(N),choice]+=1
    p=(counts+alpha)/(K*alpha+T)
    h=np.sum(p*p,axis=1)

    i=rng.integers(0,N,size=PAIR_N)
    j=rng.integers(0,N,size=PAIR_N)
    same=i==j
    while np.any(same):
        j[same]=rng.integers(0,N,size=int(same.sum()))
        same=i==j
    overlap=np.sum(p[i]*p[j],axis=1)

    theory_h=(alpha+1)/(K*alpha+1)
    theory_overlap=1/K
    return {
      "K":K,"alpha":alpha,
      "n_individuals":N,"steps":T,"pairs":PAIR_N,
      "empirical_mean_concentration":float(h.mean()),
      "theory_asymptotic_concentration":float(theory_h),
      "uniform_concentration":float(1/K),
      "empirical_excess_concentration":float(h.mean()-1/K),
      "theory_excess_concentration":float((K-1)/(K*(K*alpha+1))),
      "empirical_mean_between_individual_overlap":float(overlap.mean()),
      "theory_between_individual_overlap":float(theory_overlap),
      "overlap_minus_uniform":float(overlap.mean()-1/K),
      "abs_concentration_error":float(abs(h.mean()-theory_h)),
      "abs_overlap_error":float(abs(overlap.mean()-theory_overlap)),
    }

def main():
    rng=np.random.default_rng(SEED)
    rows=[simulate(K,a,rng) for K,a in GRID]
    out={
      "status":"THEORY_IMPLEMENTATION_CHECK",
      "seed":SEED,
      "model":"independent symmetric Polya urns",
      "rows":rows,
      "max_abs_concentration_error":max(x["abs_concentration_error"] for x in rows),
      "max_abs_overlap_error":max(x["abs_overlap_error"] for x in rows),
      "interpretation":"finite-sample simulation should approach excess within-individual concentration with no expected between-individual repulsion"
    }
    print(json.dumps(out,indent=2))

if __name__=="__main__":
    main()
