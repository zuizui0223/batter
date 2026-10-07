# Miniopterus latent-policy dimensionality scan v1

## Status

**POST-PRIMARY EXPLORATORY DIMENSIONALITY DIAGNOSTIC.**

Frozen after all of the following were already known:

- the full 8-D *Miniopterus fuliginosus* cross-configuration identity primary was unsupported;
- the fixed *Rhinolophus* FlightIntensity axis was unsupported in Miniopterus;
- the fixed Rhino PC1 axis was unsupported in Miniopterus;
- a Miniopterus-specific leave-one-environment-out PC1 was unsupported.

No result for dimensions 2–7 or for a Mini-specific supervised identity subspace has been calculated before this contract.

## Question

Does Miniopterus lack a stable cross-environment personal policy altogether, or is its individual signal carried by an intermediate-dimensional subspace missed by both the 1-D and full 8-D endpoints?

This closes the dimensionality gap rather than selecting a dimension post hoc.

## Data

Use exactly the same 19 already-opened *Miniopterus fuliginosus* trajectories and the same eight movement features used in the prior Mini diagnostics:

1. median 3-D speed;
2. p90 3-D speed;
3. median absolute vertical speed;
4. p90 absolute vertical speed;
5. median absolute horizontal turning rate;
6. p90 absolute horizontal turning rate;
7. path efficiency;
8. vertical range.

Standardization is inherited exactly from `mini_standardized()` in `cross_species_policy_axis_v1.py`:

- subtract each environment's feature mean;
- divide all environment-centered residuals by the species-wide pooled residual SD;
- no individual label enters standardization.

## D1 — unsupervised training-only PCA

Leave one environment out.

For each target environment:

1. fit PCA only on trajectories from all other environments;
2. project both training and target trajectories using that training basis;
3. evaluate cumulative dimensions
   `d = 1,2,3,4,5,6,7,8`.

At each d use the exact multivariate Euclidean identity architecture:

- average projected training trajectories within bat × environment;
- average training-environment centroids equally within bat;
- for each held-out target trajectory compute

[
K = mean(distance to other bat centroids)-distance to own centroid;
]

- aggregate equal target → equal bat → species.

This D1 scan contains the already-opened d=1 result but does not alter it.

## D2 — training-only supervised identity subspace

For each target environment:

1. from training environments only, compute one equal-environment centroid per bat in the original standardized 8-D feature space;
2. center those bat centroids by their grand mean;
3. SVD the centered bat-centroid matrix;
4. retain the first d right-singular vectors.

With four candidate bats, evaluate only

`d = 1,2,3`.

Project training and held-out target trajectories into the training-only subspace and calculate the same held-out K.

This asks whether stable individual information lives in low-variance directions that unsupervised PCA misses.

## Null calibration

Within every environment independently, permute complete bat × environment clusters among bat labels.

Preserve:
- feature vectors;
- environment membership;
- within-cluster trajectory count;
- exact label multiplicities.

Break only cross-environment identity correspondence.

For D1:
- PCA is label-free and can be reused within each dimension.

For D2:
- recompute the training-only identity subspace for every permutation and fold.

Permutations:
- 9,999 per dimension.

Seeds:
- D1: `20261007800 + d`;
- D2: `20261007820 + d`.

Require at least 9,500 valid permutations.

## Support rule

A dimension is **sufficient** only if all are true:

- species K > 0;
- one-sided p <= 0.05;
- at least 3/4 evaluable bats have positive K;
- >=9,500 valid permutations.

Minimal sufficient dimension is the smallest d passing.

No dimension can be selected by effect size alone after opening.

## Interpretation

### Any d sufficient

Miniopterus does possess a finite linear personal-policy subspace, but its dimensionality differs from the Rhino one-dimensional architecture.

### D2 succeeds while D1 fails

Stable individual information is low-dimensional but lies outside dominant behavioural-variance axes.

### Neither D1 nor D2 succeeds

Under the current 19-trajectory archive, there is no calibrated evidence for a portable linear individual policy even after scanning the full permissible linear dimensionality.

That outcome does **not** imply infinite mathematical dimensionality. It can also reflect:
- weak individual stability;
- nonlinear structure;
- insufficient repeated environments/trajectories;
- greater within-individual plasticity.

## Claim ceiling

This diagnostic tests only linear finite-dimensional compression of the measured eight-feature movement policy.

It does not establish:
- nonlinear intrinsic dimension;
- impossibility of a mathematical rule;
- absence of individual differences within a single environment;
- universality of the Rhino/Mini contrast.
