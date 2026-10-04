# Cross-environment latent-policy dimensionality contract v1

## Status

**POST-PRIMARY MECHANISM DIAGNOSTIC. NOT CONFIRMATORY.**

Frozen after:
- cross-configuration movement-policy identity was supported;
- performance-only, steering-only and geometry-only diagnostics were evaluated;
- pulse individuality was shown not to survive the stricter cross-fitted movement/route nuisance control.

No latent-dimensionality result has yet been calculated.

## Question

Can the transferable individual movement policy be represented by a small linear latent state, or does identity require most of the eight measured movement dimensions?

This is a compression question, not a new test of whether individuality exists.

## Data

Use exactly the 45 authoritative *Rhinolophus nippon* trajectories and the exact eight Primary-B features:

1. median 3-D speed;
2. p90 3-D speed;
3. median absolute vertical speed;
4. p90 absolute vertical speed;
5. median absolute horizontal turning rate;
6. p90 absolute horizontal turning rate;
7. path efficiency;
8. vertical range.

Use the exact authoritative environment-wise standardization from Primary B:
- within each environment × feature subtract the environment mean;
- divide by the environment sample SD.

No pulse variable and no absolute route coordinate enters this diagnostic.

## Fold structure

Use leave-one-environment-out folds for Env1–Env7.

For target environment e:

- training data = all trajectories from environments other than e;
- target data = trajectories in e;
- all dimensional-reduction parameters must be fit from training data only.

The target environment is never used to choose a latent axis.

---

# D1 — unsupervised PCA compression

Within each fold:

1. concatenate the eight standardized movement features from the six training environments;
2. because every feature was already standardized within environment, fit ordinary PCA by SVD with no further feature scaling;
3. order components by training variance;
4. project both training and held-out target trajectories onto the training PCA basis.

Evaluate dimensions:

`d = 1,2,3,4,5,6,7,8`.

For each d, use only the first d PC scores and compute the exact Primary-B identity advantage:
- within each training environment, average trajectories within bat;
- average training-environment centroids equally within bat;
- target K = mean distance to other-bat centroids minus distance to own-bat centroid;
- equal target -> equal bat -> species statistic.

## PCA variance report

For every fold report training explained-variance ratio by PC.

Across folds report:
- median cumulative variance explained at each d;
- range across folds.

No variance threshold is used to select d.

---

# D2 — training-only identity subspace

This supervised diagnostic asks for the dimensionality of the stable between-individual component directly.

Within each held-out environment fold:

1. from training environments only, compute each bat's centroid separately within each environment;
2. average those environment centroids equally to obtain one 8-D training centroid per bat;
3. center the five bat centroids by their grand mean;
4. compute SVD of the 5×8 centered bat-centroid matrix;
5. retain the first d right-singular vectors.

Because there are five bats, evaluate only:

`d = 1,2,3,4`.

Project:
- all training trajectories;
- held-out target trajectories

onto the training-only identity subspace.

Then compute the exact leave-one-environment-out K architecture in that projected space.

This asks whether one, two, three or four linear between-individual axes are sufficient to transfer identity to an unseen obstacle configuration.

---

# Null calibration

For D1 and D2 separately:

Within every environment independently, permute complete bat labels among bat×environment trajectory clusters, preserving:
- all feature vectors;
- environment membership;
- trajectory counts per bat within each environment.

Break only cross-environment identity correspondence.

For D1:
- PCA bases are label-free and may be reused for each permutation.

For D2:
- the identity subspace **must be recomputed from the permuted training labels within every fold and permutation**.

Permutations per d:
**9,999**

Seeds:
- D1 PCA: `202610042281 + d`
- D2 identity subspace: `202610042291 + d`

One-sided descriptive p:
`(1 + #null >= observed)/(1 + n_valid)`.

Require >=9,500 valid permutations.

## Diagnostic support rule

For each d report:
- species K_d;
- individual means;
- positive fraction;
- null 95% interval;
- one-sided p.

A dimension d is called **sufficient in this diagnostic** if:
- K_d > 0;
- p <= 0.05;
- >=70% of evaluable bats have positive mean K.

The **minimal sufficient d** is the smallest d satisfying all three.

This is a descriptive mechanism quantity, not a preregistered population parameter.

---

# Axis interpretation

For PCA:
- report squared loadings for each fold;
- summarize median squared loading of every original feature on PC1–PC3.

For the identity subspace:
- report squared loadings of identity axes 1–4 by fold;
- summarize median squared loading across folds.

Signs are not interpreted because SVD/PCA signs are arbitrary.

No post hoc rotation is allowed.

---

# Interpretation

## One dimension sufficient

A strong result:

> the portable individual flight policy can be compressed to approximately one dominant linear control axis across obstacle configurations.

This would make the system much closer to a low-dimensional latent control parameter than to an irreducibly complex trajectory fingerprint.

## Two dimensions sufficient, one fails

> at least two coupled control axes are needed to carry cross-configuration individuality.

Possible ecological interpretations include:
- performance scale × steering style;
- horizontal maneuvering × vertical strategy.

The loadings, not intuition, determine the descriptive labels.

## Three to four dimensions required

The policy is still low-dimensional relative to the raw trajectory but not reducible to a single scalar tendency.

## PCA requires many dimensions but identity subspace requires few

Identity lives in low-variance directions not captured by the dominant axes of overall flight variation.

## Neither compresses well

The measured policy signature is distributed across many features, or is nonlinear.

This does **not** imply that no mathematical rule exists.

## Ceiling

This diagnostic establishes only linear latent dimensionality of the measured policy summaries.

It does not establish:
- a unique dynamical equation;
- a neural control variable;
- an attractor;
- genetic or learned origin;
- nonlinear intrinsic dimensionality.
