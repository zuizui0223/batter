# Non-tautological held-out personal-policy transfer test v1

## Status

POST-OUTCOME MATHEMATICAL AUDIT / NEW DIAGNOSTIC, NOT CONFIRMATORY. Frozen after the 1D and transparent two-axis results and after the finite-sample convergence identity was proved, but **before opening this test's permutation outcomes**.

## Question

Do true bat identities allow portable personal scalars to predict an unseen obstacle configuration better than null identity correspondences, **without** treating the mechanical reduction of subset variance as an inference?

## Source

Use the same 45 *Rhinolophus nippon* trajectories and eight feature summaries that fed the frozen cross-configuration policy primary.

- seven obstacle environments;
- five identified bats A–E;
- per-environment eight-feature means and sample SDs are fixed label-free, exactly as in `latent_policy_dimensionality_v1.standardized_rows()`;
- no pulse or absolute route coordinates.

This uses the original label-free environment-wise z-scoring (a *transductive* comparison); no new normalization tuning.

## Two transparent axes

For each trajectory with frozen eight-element standardized vector `z`:

```
I = mean(z[0],z[1],z[2],z[3])
M = mean(-z[0],z[4],z[5],z[6],z[7])
```

I is movement intensity; M is maneuvering extent.

For each bat × environment, average trials within that cluster.

## Target and prediction

For every bat×environment centroid as a held-out target:

- exclude the entire target environment from training;
- retain only targets with at least 3 other environments observed for that same identity;
- no results-driven changes in the eligible target set;
- expected: 25 targets covering all five bats.

For axis a in {I,M}, target y, and the N non-target same-individual historical centroids x:

```
MSE_m = (y - mean(x))^2 + (1/m - 1/N) * sample_variance(x)
```

for m in 1,2,3. This is exactly equal to enumeration of all m-subsets, verified by a toy self-test.

Define baseline `MSE_zero = y²` (the original within-environment standardized group-center prediction).

Primary meaningful gain:

```
G_{a,m} = MSE_zero - MSE_m
```

M=3 primary; full available history and m=1,2 secondary.

Aggregate equal target environment within bat, then equal bat.

Each gain answers whether the scalar personal history beats the label-free environmental center, **not** whether subset averaging mechanically reduces variance.

For a joint two-axis descriptive gain, use the mean of the axis-wise gains divided by their pre-permutation observed zero-baseline MSEs, with those normalizers held fixed in every permutation.

## Null

Within each environment independently permute complete bat × environment centroid clusters among the bat labels, retaining the exact environment-wise set of labels and the cluster centroids. Recompute every held-out same-label history and every target error.

Permutation count: 9,999.
Seed: 202610081011.
One-sided p for positive gain = `(1 + #null_gain >= observed_gain)/(1+9999)`.

For each axis and the joint metric report:
- observed m=3 and full gains;
- R² compared with own zero baseline;
- permutation null 95% interval and p-value;
- number of bats with positive m=3 gain.

Call supported only if:
1. observed m=3 gain >0;
2. one-sided permutation p <=.05;
3. >=4/5 bats have positive m=3 gain.

## Bootstrap

Optional descriptive biological-bat bootstrap of the observed m=3 gain:
- 4,999 resamples;
- seed 202610081012;
- percentile 95% intervals;
- not a replacement for the identity-permutation calibration.

## Claim ceiling

A supported scalar is a portable **predictive individual coordinate in these measured features**, not a unique equation of motion or proof of a stationary neural parameter.

A second supported M gain would show additive portable information in the transparent maneuvering scalar; it would not prove exact intrinsic dimension 2.

No outcome-specific model tuning, source exclusions, missing-cell imputations or metric revisions are permitted. Do not promote this post-outcome diagnostic to an independent replication.
