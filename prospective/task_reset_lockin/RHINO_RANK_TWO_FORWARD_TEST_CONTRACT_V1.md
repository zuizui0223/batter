# Rhino rank-two forward-prediction test v1

## Status and motivation

**POST-OUTCOME DIAGNOSTIC — NOT AN INDEPENDENT CONFIRMATION.**

This test is frozen after the following results were observed:
- training-only rank-1 PCA / identity axes carry held-out individual identity;
- residual geometry after a one-dimensional intensity coordinate carries held-out individual identity;
- a two-coordinate intensity/maneuvering representation carries identity;
- the previous all-training-subset 91.6% convergence is an algebraic finite-sampling identity, NOT evidence of biological parameter convergence;
- genuine held-out correspondence was supported by label permutations, but personal gain was positive in only 3/5 bats.

The current test is necessary because **classification sufficiency and incremental forecast value are different**. A second identity axis may distinguish bat labels without improving quantitative future prediction once axis 1 is known.

## Question

Does adding one independently trained second personal coordinate improve held-out prediction of the **same 8-dimensional movement feature vector**, compared with the best rank-1 nested predictor?

This is the missing same-endpoint nested prediction test.

## Data, gate and standardization

Use exactly 45 original *Rhinolophus nippon* trajectories, five bats A-E, seven obstacle configurations Env1-Env7, eight Primary-B movement features:
1. median speed,
2. p90 speed,
3. median absolute vertical speed,
4. p90 absolute vertical speed,
5. median absolute horizontal turn rate,
6. p90 absolute horizontal turn rate,
7. path efficiency,
8. vertical range.

Inherit `latent_policy_dimensionality_v1.standardized_rows()` exactly. For each environment-feature, subtract the full environment mean and divide by the environment SD. This is **transductive within-environment normalization**, not a cold-start prediction. Fix the 45-row gate before outcomes.

## Training-only rank-r model

Leave one environment e out.

For each training bat i:
- mean feature vectors within each training bat x environment;
- average these means **equally across available training environments** to obtain an 8D centroid `c_i,-e`;
- retain bat i only if it has >=2 training environments.

Require >=5 eligible training bat centroids per fold. Compute the grand mean of the five centroids `mu_-e`. Fit SVD on their centered 5 x 8 centroid matrix, using **training environments only**.

Define the rank-r prediction for a target bat i in held-out e:

`pred_i,e,r = mu_-e + V_r V_r^T (c_i,-e - mu_-e)`

for r = 0,1,2,3,4, where r=0 predicts the pooled five-bat training centroid mean. No target outcomes enter the basis or centroid.

## Shared held-out loss

At each rank r, use exactly the same 45 held-out target trajectories and the same 8 features. Loss:

`L_r = mean_k=1..8 (z_target,k - pred_i,e,r,k)^2`.

Aggregation:
1. equal target trajectories within bat x held-out environment;
2. equal target environments within biological bat;
3. equal biological bats.

All ranks are evaluated on identical target features and folds.

Primary contrast: `Delta_2_given_1 = L_1 - L_2`.

Secondary contrasts: `Delta_1_given_0 = L_0 - L_1`, `Delta_2_given_0 = L_0 - L_2`.
Descriptive ranks 0..4 retain all values without post-hoc dimensionality selection.

## Frozen correspondence null

Within each environment independently, permute **complete bat x environment trajectory clusters** among the observed bat labels, preserving environment composition, cluster sizes, and all feature values.

For **every** permuted assignment and fold:
- recompute the assigned five training centroids;
- recompute training-only SVD axes;
- score held-out targets using their reassigned labels.

B=9,999; seed=20261008161; require 9,999 valid permutations.

One-sided primary p=(1 + count(Delta_null >= Delta_observed))/(B+1).

## Uncertainty and decision

Cluster bootstrap biological bats with replacement, B=9,999, seed=20261008162.

Report:
- all five observed rank losses;
- primary and secondary mean gains;
- individual primary gains;
- primary bat-cluster percentile 95% CI;
- primary correspondence-null mean, 95% interval, p.

**Call the second coordinate incrementally predictive only if all hold:**
- Delta_2_given_1 > 0;
- one-sided correspondence p<=.05;
- >=4/5 bat-level gains >0;
- bootstrap 95% lower bound >0.

Do not relax after opening.

## Interpretation ceiling

Supported: a second training-only latent identity coordinate improves unseen configuration prediction of the same eight movement features beyond a first coordinate.

Unsupported: a second axis may still carry discriminative information, but positive nested quantitative forecast value is not established.

Neither case establishes a unique two-variable dynamical flight equation, stationary lifelong traits, nonlinear intrinsic dimension, causal learning mechanism, or species universality. The exact earlier 91.6% subset-averaging result remains superseded by its mathematical audit.

No rank, target support, contrast, seed, threshold, aggregation or null may change after opening.
