# Transparent two-parameter policy law contract v1

## Status

**POST-PRIMARY MATHEMATICAL-STRUCTURE DIAGNOSTIC.**

Frozen after:
- transparent FlightIntensity was supported;
- transparent ManeuveringExtent was supported;
- their 2-D span captured calibrated cross-configuration identity;
- calibrated residual identity outside that span was unsupported.

No held-out two-parameter prediction result has yet been calculated.

## Question

Can each *Rhinolophus nippon* individual be represented by a stable 2-D behavioural coordinate

`theta_i = (theta_I,i, theta_M,i)`

that predicts its position in a completely held-out obstacle configuration without refitting coefficients?

## Transparent axes

Use exactly:

`I = mean(z1,z2,z3,z4)`

where z1–z4 are:
- median speed;
- p90 speed;
- median absolute vertical speed;
- p90 absolute vertical speed.

Use exactly:

`M = mean(-z1,z5,z6,z7,z8)`

where z5–z8 are:
- median absolute horizontal turning rate;
- p90 absolute horizontal turning rate;
- path efficiency;
- vertical range.

All z values use the authoritative within-environment standardization.

## Bat × environment centroid

For every bat i in environment e:

`y_ie = (mean I, mean M)`

averaging repeated trajectories equally.

## Held-out personal parameter

For target environment e:

`theta_i,-e`

is the equal-environment mean of the 2-D centroids from all other environments where bat i is observed.

Require >=2 training environments.

No target-environment data enter theta.

---

# P1 — no-refit held-out 2-D prediction

Prediction:

`yhat_ie = theta_i,-e`.

Zero baseline:

`yhat0_ie = (0,0)`

because both transparent coordinates are constructed from environment-standardized features.

Across all eligible held-out bat × environment centroids define:

`R2_2D = 1 - sum ||y_ie-yhat_ie||^2 / sum ||y_ie||^2`.

Also report:
- RMSE in the 2-D transparent policy space;
- median Euclidean prediction error;
- median cosine similarity between y and yhat where both norms are positive.

## P2 — axis-specific no-refit R²

Separately calculate the same zero-baseline no-refit R² for:
- FlightIntensity coordinate I;
- ManeuveringExtent coordinate M.

No coefficient fitting.

## P3 — pairwise displacement-vector prediction

For every target environment and eligible unordered bat pair (i,j):

Predicted 2-D difference:

`delta_hat = theta_i,-e - theta_j,-e`.

Observed held-out difference:

`delta_obs = y_ie - y_je`.

Report across all pair × environment points:
- vector no-refit R²:
  `1 - sum ||delta_obs-delta_hat||² / sum ||delta_obs||²`;
- median cosine similarity between predicted and observed pair-difference vectors;
- fraction with positive cosine;
- Pearson correlation between predicted and observed pairwise Euclidean separation magnitudes.

This asks whether not only individual coordinates, but the **geometry among individuals**, transfers across configurations.

---

# Null

Within every environment independently:
- permute complete bat labels among bat × environment centroids;
- preserve observed 2-D centroids and support;
- break only cross-environment individual correspondence.

For every permutation recompute:
- theta;
- held-out predictions;
- P1, P2, P3.

9,999 permutations.

Seeds:
- P1: `202610051001`
- P2-I: `202610051002`
- P2-M: `202610051003`
- P3 vector R²: `202610051004`

One-sided p:
`(1 + #null >= observed)/(1+n_valid)`.

Require >=9,500 valid permutations.

## Support interpretation

A strong two-parameter law requires:
- P1 R2_2D > 0 and p <= 0.05;
- both axis-specific R² positive;
- P3 vector R² > 0 and p <= 0.05.

This would support:

> each individual occupies a reproducible point in a two-dimensional movement-policy space that predicts its relative behavioural position in unseen obstacle configurations.

## Ceiling

This is an approximate statistical control law.

It does not establish:
- a deterministic dynamical system;
- a neural state variable;
- physiological identity of either coordinate;
- universality beyond this species and experiment.
