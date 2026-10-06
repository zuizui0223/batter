# Cross-fitted geometry-family residual identity contract v1

## Status

**POST-PRIMARY EXPLORATORY MECHANISM DIAGNOSTIC.**

Parents:
- `GEOMETRY_ONLY_POLICY_RESULT_V1.md`
- `GEOMETRY_POLICY_FAMILY_ABLATION_RESULT_V1.md`
- `GEOMETRY_POLICY_TARGET_NORMALIZATION_RESULT_V1.md`

The family ablation shows that both:
- global route organization (G);
- horizontal maneuver geometry (H)

carry cross-configuration individual information.

This diagnostic asks a narrower question:

> **Does either family retain portable identity after removing the part linearly predictable from the other family using training environments only?**

It does not test anatomical independence or neural modularity.

## Features

Use exactly the frozen scale-free geometry features.

G:
- path efficiency;
- horizontal displacement ratio;
- absolute vertical displacement ratio;
- vertical range ratio.

H:
- median absolute horizontal turn angle;
- p90 absolute horizontal turn angle.

Vertical-slope family V is excluded from this diagnostic because V-only identity is unsupported.

## Fold transformation

For each held-out environment e:

1. use the other six environments as training;
2. calculate one training-only global mean and SD for all six G+H features;
3. apply those training mean/SD values unchanged to training and held-out trajectories;
4. never use held-out-environment mean or SD.

## R1 — H residual after G

Fit on training trajectories only:

[
H = a + B_G G + epsilon_H.
]

Use ordinary least squares with an intercept.

Apply the frozen training coefficients to:
- training trajectories;
- held-out trajectories.

Identity representation is the 2-D residual:

[
H^{res}=H-widehat H(G).
]

## R2 — G residual after H

Fit on training trajectories only:

[
G = c + B_H H + epsilon_G.
]

Identity representation is the 4-D residual:

[
G^{res}=G-widehat G(H).
]

## Identity estimator

For each held-out environment:
- construct bat × training-environment centroids from residual features;
- average environments equally within bat;
- require >=2 training environments;
- target trajectory own-distance versus equal donor-bat distance;
- equal target trajectories within bat;
- equal bats for the programme statistic.

This is the same biological weighting as the parent portable-policy estimator.

## Null

Within every environment independently permute complete biological bat labels among bat × environment clusters.

Residualization coefficients are label-free and remain unchanged within a permutation.

9,999 permutations.

Seeds:
- H residual after G: `202610061301`
- G residual after H: `202610061302`

Require >=9,500 valid permutations.

## Exploratory support rule

A residual family is called identity-bearing only if:
- K > 0;
- one-sided permutation p <= 0.05;
- >=4/5 bats positive.

## Interpretation

### Both residuals supported

> G and H contain portable individual information that is not removed by a simple linear mapping between the two broad geometry families.

This supports a multi-component coordinative phenotype.

### Only H|G supported

Horizontal maneuver geometry carries incremental identity beyond global route organization.

### Only G|H supported

Global route organization carries incremental identity beyond horizontal maneuver geometry.

### Neither supported

The apparent family-distributed identity may largely reflect a common lower-dimensional geometric axis.

## Ceiling

Do not infer:
- independent motor modules;
- causal motor degeneracy;
- environmental solution abundance;
- nonlinear independence.

A failed residual test is informative and should not be rescued with nonlinear models after outcome opening.
