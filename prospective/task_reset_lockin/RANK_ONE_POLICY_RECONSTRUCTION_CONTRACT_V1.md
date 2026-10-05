# Rank-one policy reconstruction contract v1

## Status

**POST-PRIMARY MATHEMATICAL-STRUCTURE DIAGNOSTIC.**

Frozen after:
- full 8-D cross-configuration movement identity was supported;
- one-dimensional leave-one-environment-out PCA identity was sufficient;
- a transparent FlightIntensity scalar and pairwise one-parameter magnitude calibration were supported.

No held-out multivariate reconstruction result has yet been calculated.

## Question

Is the one-dimensional result merely enough for classification, or can one latent individual parameter reconstruct the **multivariate movement-policy vector** in an unseen obstacle configuration?

## Data

Use exactly the authoritative 45 *Rhinolophus nippon* trajectories and the exact eight Primary-B movement features.

Use the same environment-wise standardization as Primary B:

`z_q = (x_q - mean_e(x)) / sd_e(x)`.

This removes configuration-level mean and scale.

## Biological unit for reconstruction

Within each environment e and bat i:

- average standardized trajectory vectors equally;
- call the resulting 8-D bat × environment centroid `m_ie`.

The reconstruction target is `m_ie`, not individual trajectory noise.

## Leave-one-environment-out rank-one model

For target environment e:

### Training loading vector

From all **trajectory-level standardized vectors** in the other six environments:

1. concatenate training trajectories;
2. fit ordinary PCA by SVD without additional scaling;
3. retain the first right-singular vector `lambda_-e`.

The sign is arbitrary and has no biological interpretation.

### Individual latent parameter

For every bat i:

- project each available training-environment bat centroid onto `lambda_-e`;
- average projected values equally across training environments;
- call this `theta_i,-e`.

Require >=2 training environments for a bat.

### Held-out prediction

For a target bat × environment centroid:

`mhat_ie = lambda_-e * theta_i,-e`.

No target-label information enters lambda or theta.

## R1 — held-out multivariate reconstruction R²

Across all eligible target bat × environment centroids:

`SSE_rank1 = sum ||m_ie - mhat_ie||^2`.

Null reconstruction:

`mhat0_ie = 0`,

because the target environment has already been centered feature-wise.

`SSE_zero = sum ||m_ie||^2`.

Define:

`R2_rank1 = 1 - SSE_rank1/SSE_zero`.

Report also:
- RMSE per feature dimension;
- cosine similarity between observed and predicted centroid where both norms are positive;
- median cosine similarity.

## R2 — rank-two comparison

Repeat the identical procedure using the first two training PCA vectors.

For each bat:
- estimate two latent coordinates by equal-environment averaging of training projections;
- reconstruct held-out centroid from the two-axis loading matrix.

Report:

`R2_rank2`.

Define incremental gain:

`DeltaR2_2minus1 = R2_rank2 - R2_rank1`.

This is descriptive; no threshold is predeclared for declaring rank 1 "exact".

## Identity permutation null

Within each environment independently:
- permute complete bat × environment labels among bat centroids;
- preserve all standardized vectors and environment membership;
- break only cross-environment identity correspondence.

For each permutation:
- PCA loading vectors remain feature-derived and label-free;
- recompute theta from permuted training labels;
- predict permuted held-out labels;
- calculate R2_rank1 and R2_rank2.

9,999 permutations.

Seeds:
- rank 1: `202610050911`;
- rank 2: `202610050912`.

One-sided p for positive reconstruction R².
Require >=9,500 valid permutations.

## Interpretation

### Rank-1 R² > 0 and calibrated beyond null

> one latent individual parameter carries enough information to reconstruct a non-zero fraction of the held-out 8-D movement-policy vector.

This is stronger than identification alone.

### Rank 2 greatly improves reconstruction

Individual identity may be one-dimensional for discrimination but multivariate policy magnitude still needs at least two axes.

### Rank-1 reconstruction unsupported despite one-axis identity

The one-dimensional coordinate is a discriminative signature, not an adequate generative approximation of the full measured policy.

## Ceiling

Even a supported rank-one reconstruction is an approximate statistical factor model, not a deterministic equation of flight.

It does not identify whether theta is:
- morphology;
- physiology;
- learned motor style;
- developmental history;
- a neural control variable.
