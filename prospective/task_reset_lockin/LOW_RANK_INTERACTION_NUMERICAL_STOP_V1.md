# Rhino low-rank interaction — numerical identifiability STOP v1

## Status

**STOP — do not interpret the frozen unregularized low-rank completion as a biological dimensionality result.**

The frozen contract was executed deterministically from the authoritative bat × environment FlightIntensity centroid matrix while the dedicated workflow run 37639641289 remained queued.

## What happened

The additive baseline is numerically stable.

The unregularized rank-1 / rank-2 interaction completion is not.

Examples from held-out folds:

- rank 1, C in Env1: predicted value ≈ **11.79** for an observed value ≈ 0.026;
- rank 2, D in Env6: predicted value ≈ **-476.3** for an observed value ≈ -0.791.

Several ALS fits reach the maximum iteration cap or produce very large missing-cell extrapolations despite low training interaction SSE.

This is the characteristic sparse-matrix identifiability problem: many factor combinations fit the observed cells similarly while implying arbitrarily different values for an unobserved cell.

## Consequence

Do **not** conclude:

- that the biological interaction is high-dimensional;
- that rank 1 or rank 2 is biologically false;
- that the residual is non-convergent.

The correct result is:

> the current sparse 5 × 7 incidence matrix does not identify an **unregularized** low-rank individual × environment completion.

## What remains valid

The already-supported portable scalar theta is unaffected.

The failure localizes the unresolved part to:

[
h_{ie},
]

the task-specific individual realization.

A valid next low-rank test would require:
- training-only regularization / shrinkage;
- or measured environment descriptors;
- or denser bat × environment replication.

No tuning of the frozen unregularized analysis is permitted after this outcome.
