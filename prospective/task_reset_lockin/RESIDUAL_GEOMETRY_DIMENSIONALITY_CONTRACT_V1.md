# Residual-geometry latent dimensionality contract v1

## Status

**POST-PRIMARY MATHEMATICAL-STRUCTURE DIAGNOSTIC.**

Frozen after:
- FlightIntensity theta was shown to be portable and rapidly convergent;
- raw scale-free geometry identity was supported;
- cross-fitted geometry identity remained supported after linear FlightIntensity removal;
- no latent-dimensionality result for the residual geometry component has been calculated.

## Question

Can the portable geometry information that remains after theta removal be compressed to one additional latent coordinate?

This directly tests whether the current minimum personal-policy representation can be approximated as:

[
personal policy approx (	heta_i,phi_i).
]

## Input

Use exactly the 45 authoritative *Rhinolophus nippon* trajectories.

Residual geometry is generated exactly as in `GEOMETRY_BEYOND_THETA_CONTRACT_V1.md`:

- eight scale-free geometry features;
- authoritative within-environment geometry standardization;
- transparent FlightIntensity scalar;
- for each held-out environment, fit geometry ~ intercept + FlightIntensity using non-target environments only;
- apply training-fitted coefficients to training and target trajectories;
- retain the resulting eight-dimensional residual vectors.

No residualization parameter is fit with target-environment outcomes.

## D1 — training-only PCA of residual geometry

For each held-out environment:

1. take residual geometry vectors from training environments only;
2. fit ordinary PCA by SVD;
3. project all training and target residual vectors onto that training basis;
4. evaluate cumulative dimensions d = 1,2,3,4,5,6,7,8.

At each d use the exact cross-environment identity estimator:
- training centroid averages trajectories within bat × environment;
- then averages environments equally;
- target K = mean distance to other-bat centroids − distance to own centroid;
- equal target -> equal bat -> programme.

## D2 — training-only residual-identity subspace

For every held-out environment:

1. compute each bat's equal-environment training centroid in the eight-dimensional residual geometry space;
2. center bat centroids by their grand mean;
3. SVD the centered bat-centroid matrix;
4. retain first d axes.

With five bats evaluate d = 1,2,3,4.

Project training and target residual vectors using training-only axes and compute the same held-out K.

## Null

Within every environment independently permute complete bat × environment trajectory clusters among labels.

Preserve:
- residual geometry vectors;
- FlightIntensity values and residualization;
- environment membership;
- cluster sizes.

Break only cross-environment identity correspondence.

For D1, PCA is label-free and may be reused per permutation.

For D2, recompute the identity subspace for every permutation and fold.

Permutations per d:
9,999.

Seeds:
- D1: 20261007960 + d
- D2: 20261007980 + d

Require >=9,500 valid permutations.

## Support rule

A dimension d is sufficient if:
- K_d > 0;
- one-sided p <= 0.05;
- >=70% evaluable bats have positive K;
- >=9,500 valid permutations.

Minimal sufficient d is the smallest passing dimension.

## Interpretation

### Residual d=1 sufficient

The current data are consistent with a compact two-coordinate personal policy:

[
(	heta_i,phi_i),
]

where theta is movement intensity and phi is a portable geometry coordinate beyond theta.

### Residual d=2 or more required

Portable individuality is still finite-dimensional but needs more than two total coordinates under this linear decomposition.

### No residual dimension sufficient

The supported full residual-geometry identity is distributed in a way not recoverable by these training-only linear compression routes; nonlinear or weak distributed structure remains possible.

## Ceiling

This diagnostic identifies statistical dimensionality, not:
- neural control dimensions;
- causal independence;
- unique coordinates;
- lifetime stationarity;
- cross-species universality.
