# Transparent scalar flight-intensity diagnostic v1

## Status

**POST-PRIMARY INTERPRETABILITY DIAGNOSTIC. NOT CONFIRMATORY.**

Frozen after the latent-dimensionality analysis showed that one training-derived dimension is sufficient for cross-configuration individual identity.

## Question

Can the dominant one-dimensional personal policy be approximated by a transparent, non-fitted scalar rather than a PCA axis?

## Data

Use the exact authoritative environment-standardized Primary-B features for the 45 *Rhinolophus nippon* trajectories.

## Scalar

Define:

`FlightIntensity = mean(z_median_speed, z_p90_speed, z_median_abs_vertical_speed, z_p90_abs_vertical_speed)`.

Equal weights:
0.25 each.

Do not fit weights to identity.

Do not include:
- turning rate;
- path efficiency;
- vertical range;
- pulse features;
- route coordinates.

Higher FlightIntensity means faster movement with stronger vertical velocity on the common within-environment standardized scale.

## Cross-configuration identity test

Use the exact Primary-B leave-one-environment-out architecture:

- target environment held out;
- within each training environment, average FlightIntensity within bat;
- average training-environment bat centroids equally;
- target advantage = mean absolute distance to other-bat centroids minus absolute distance to own-bat centroid;
- equal target -> equal bat -> species statistic.

## Null

Within each environment independently, permute complete bat×environment labels among bat clusters, preserving all scalar values and cluster sizes.

9,999 permutations.

Seed:
`202610042301`.

## Diagnostic support

Call this transparent scalar sufficient if:

- K_scalar > 0;
- one-sided permutation p <= 0.05;
- >=70% evaluable bats have positive individual means.

## Interpretation

If supported:

> much of the portable personal movement-policy signal can be represented by a simple scalar flight-intensity tendency rather than by an opaque high-dimensional signature.

This would not mean all individuality is one-dimensional:
- geometry-only identity already indicates a weaker secondary maneuver component;
- the scalar is a descriptive carrier, not a complete controller.

## Ceiling

Do not interpret FlightIntensity as:
- a physiological trait;
- body size;
- metabolic capacity;
- maximum performance;
- genetic value.

It is an observed behavioural control tendency.
