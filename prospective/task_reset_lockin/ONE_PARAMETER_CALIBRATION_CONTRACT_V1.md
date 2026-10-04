# One-parameter flight-intensity magnitude calibration contract v1

## Status

**POST-PRIMARY MATHEMATICAL-STRUCTURE DIAGNOSTIC.**

Frozen after:
- one-dimensional Rhino PCA1 was sufficient;
- transparent FlightIntensity was supported;
- pairwise rank ordering was stable across environments;
- speed and vertical-speed components were each supported, while relative verticality was not.

No magnitude-calibration result has yet been calculated.

## Question

Does a bat's scalar policy position estimated from other obstacle configurations predict not only rank but the **magnitude of pairwise differences** in a held-out configuration?

If yes, the dominant personal policy is closer to a transferable scalar parameter `theta_i` than to a generic classification embedding.

## Scalar

Use exactly:

`FlightIntensity = mean(z_median_speed, z_p90_speed, z_median_abs_vertical_speed, z_p90_abs_vertical_speed)`.

Use the authoritative within-environment standardization from the existing scalar programme.

## Bat × environment centroid

Within each environment e and bat i:
- average all FlightIntensity trajectories for that bat;
- call this `y_ie`.

## Held-out training parameter

For target environment e:

`theta_i,-e = equal-environment mean of y_i,e' over all other environments e' where bat i is observed`.

Require at least 2 training environments for each bat.

## Pairwise calibration points

For every target environment e and every unordered bat pair (i,j) satisfying support:

Predicted difference:
`x_ije = theta_i,-e - theta_j,-e`.

Observed held-out difference:
`y_ije = y_ie - y_je`.

Exact zero x values are retained.

## Primary descriptive statistics

Across all eligible pair × environment points report:

1. **through-origin calibration slope**
   `beta = sum(x*y)/sum(x^2)`;

2. **Pearson correlation**
   between x and y;

3. **sign accuracy**
   for nonzero x and y, with ties scored 0.5.

Also report the same quantities after equal-pair weighting:
- first compute each metric contribution/summary within pair where mathematically defined;
- for sign accuracy use equal-pair mean;
- for slope and correlation the programme-level primary remains the raw pair×environment calibration because these quantities are not separable additive statistics.

The pair-equal sign accuracy is a link to the existing rank-stability result.

## Null

Within every environment independently:
- permute complete bat × environment scalar clusters among bat labels;
- preserve the observed scalar centroids, environment membership and cluster sizes;
- recompute both training theta and held-out pair differences.

9,999 permutations.

Seed:
`202610042341`.

For slope and correlation use one-sided positive calibration p-values.

## Calibration interpretation

A transferable scalar-parameter pattern requires:
- beta > 0;
- Pearson r > 0;
- both permutation p <= 0.05.

A slope near 1 would indicate approximate magnitude calibration on the standardized scale, but no equivalence interval is predeclared; therefore do not call beta "equal to one".

## Ceiling

Even strong magnitude calibration means only:

> one scalar behavioural control tendency predicts relative individual differences across these obstacle configurations.

It does not establish:
- a unique dynamical equation;
- a physiological parameter;
- a neural state;
- genetic determination;
- universality across species.
