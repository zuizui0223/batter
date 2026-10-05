# Sequential policy-subspace ablation contract v1

## Status

**POST-PRIMARY DIMENSIONALITY FALSIFICATION DIAGNOSTIC.**

Frozen after:
- 1-D cross-environment identity was sufficient;
- rank-one held-out reconstruction was supported;
- removing PC1 alone left significant residual identity (K=0.389, 5/5 positive, p=0.0031).

No sequential multi-axis ablation result has yet been calculated.

## Question

How many dominant, label-free movement-policy axes must be removed before transferable individual identity is no longer detectable?

This distinguishes:
- one dominant axis plus meaningful secondary individual axes;
- a genuinely low-rank individual policy;
- broadly distributed high-dimensional identity.

## Data

Use exactly the 45 authoritative *Rhinolophus nippon* trajectories and the exact eight Primary-B environment-standardized movement features.

## Leave-one-environment-out PCA basis

For every target environment e:

1. use only trajectories from the other six environments;
2. fit ordinary PCA by SVD on the eight standardized movement features;
3. retain the full ordered 8-D orthonormal loading matrix `V_-e`.

No bat identity is used to fit the basis.

## Sequential ablation

For each:

`k = 0,1,2,3,4,5,6,7`

remove the first k training PCA directions from every training and target vector in that fold:

`r_k = z - V_k V_k^T z`.

Where:
- k=0 = the full 8-D reference;
- k=1 = the already-run PC1-complement concept;
- k=7 leaves only training PC8.

Do not re-standardize or rotate the residual after ablation.

## Cross-environment identity statistic

Use the exact Primary-B leave-one-environment-out architecture on the residual vectors:

- average trajectories within bat × training environment;
- average training environments equally within bat;
- compare held-out target vector to own vs other bat training centroids;
- equal target -> equal bat.

For each k report:
- K_k;
- five bat means where evaluable;
- positive fraction.

## Null

For each k independently:

- within every environment, permute complete bat × environment trajectory clusters among labels;
- preserve residual feature vectors, environment membership and cluster sizes;
- break only cross-environment identity correspondence.

PCA bases are label-free and remain fixed.

9,999 permutations per k.

Seed:
`202610050930 + k`.

One-sided p for K_k > 0.

Require >=9,500 valid permutations.

## Descriptive carrier profile

Report:
- K_k / K_0 for every k;
- cumulative training variance removed by the first k PCs, median across folds;
- smallest k such that the residual identity diagnostic is unsupported:
  K_k <= 0, or p > 0.05, or positive fraction < 0.70.

Call this the **first unsupported complement k**, not the true intrinsic dimensionality.

## Axis loadings

For PC1–PC4, report median squared feature loadings across the seven training folds.

This is descriptive and used to name candidate policy dimensions only after the ablation profile is known.

## Interpretation

### Residual identity disappears after k=2

A compact approximately two-axis individual policy.

### After k=3 or 4

Still low-dimensional relative to raw trajectories, but not scalar.

### Persists through k>=5

Individual information is broadly distributed across the eight measured summaries.

## Ceiling

An unsupported residual at some k is not proof that no information exists beyond k; n=5 individuals limits power.

This programme estimates the dimensional concentration of the measured transferable signal, not a unique neural or biomechanical state dimension.
