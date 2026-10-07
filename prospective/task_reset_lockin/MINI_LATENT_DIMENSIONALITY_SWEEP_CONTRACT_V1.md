# Miniopterus latent-dimensionality sweep contract v1

## Status

**POST-PRIMARY EXPLORATORY DIAGNOSTIC WITH FAMILY-WISE CALIBRATION.**

Known before this sweep:
- full 8-D cross-configuration identity primary was unsupported;
- the fixed Rhino scalar and Rhino PC1 were unsupported in Miniopterus;
- a Miniopterus-specific training-only PCA1 was unsupported.

Unknown before this sweep:
- PCA dimensions 2–7;
- training-only supervised identity-subspace dimensions 1–3.

Because the intermediate dimensions are being examined after endpoint failures are known, all dimensions are opened together and calibrated with a max-statistic null. No dimension may be selected using an unadjusted p-value.

## Question

Does *Miniopterus fuliginosus* contain a stable cross-configuration individual signal that becomes visible only after low-rank regularization at an intermediate dimension?

This distinguishes:
- no stable individual carrier in the current archive;
- from a stable carrier that is neither 1-D nor well estimated by the raw full 8-D distance.

## Data and standardization

Use exactly the same 19 feature-valid Miniopterus trajectories and the same eight movement features as the already-opened cross-species programme.

Use exactly the frozen Mini standardization:
- within every environment subtract the feature mean;
- divide by the species-wide pooled residual SD.

No pulse or absolute-route coordinate enters.

## D1 — training-only unsupervised PCA sweep

For every held-out environment:
1. fit ordinary PCA on all other environments only;
2. project training and target trajectories onto the training basis;
3. evaluate d = 1,2,3,4,5,6,7,8;
4. calculate the same equal-target -> equal-bat cross-configuration identity advantage K_d.

The d=1 and d=8 outcomes are retained even though related results are already known; they are part of the family-wise sweep.

## D2 — training-only supervised identity subspace

Within each held-out environment:
1. compute bat centroids separately within each training environment;
2. average training-environment centroids equally within bat;
3. center the available bat centroids by their grand mean;
4. fit SVD to the between-bat centroid matrix;
5. evaluate d = 1,2,3, the maximum nontrivial rank for four candidate bats.

Project held-out trajectories onto the training-only identity basis and calculate the same K_d.

## Structural support

For a target trajectory:
- its assigned bat must have >=2 training environments;
- at least two other candidate bats must have >=2 training environments.

Require >=3 evaluable biological bats programme-wide.

## Null

Within each environment independently permute complete bat×environment clusters among bat labels.

B = 9,999.
Seed = 20261007801.

For every permutation:
- preserve all feature vectors, environments and cluster sizes;
- recompute D2 identity bases under permuted training labels;
- compute K_d for every dimension.

### Family-wise calibration

For D1:
- for each permutation take max(K_1,...,K_8);
- adjusted p_d = (1 + # max-null >= observed K_d)/(B+1).

For D2:
- separately take max(K_1,K_2,K_3);
- use the analogous adjusted p.

No unadjusted p can define support.

## Support rule

A dimension is called supported only if:
- K_d > 0;
- family-wise adjusted p_d <= 0.05;
- >=3/4 evaluable bats have positive mean K.

The minimal supported dimension is the smallest d meeting all three.

## Interpretation

If an intermediate dimension is supported:
> Miniopterus contains a regularized low-dimensional individual carrier, but it is more complex than the Rhino one-parameter axis.

If none is supported in D1 or D2:
> the current Miniopterus archive does not support a stable cross-configuration individual parameter even after low-rank regularization.

This does not prove mathematical non-existence. With only 19 trajectories, weak individual parameters can remain below detection.

## Claim ceiling

This sweep is exploratory and was motivated after d=1 and d=8 failures were known.
It cannot be promoted as independent confirmation or as proof that Miniopterus behaviour is intrinsically high-dimensional.
