# Rhino configuration-expression alpha diagnostic v1

## Status

POST-OUTCOME mechanism diagnostic. The descriptive per-environment slopes were inspected before this null calibration; therefore this is not independent confirmation.

## Question

Can the portable scalar individual coordinate be represented as

[
y_{ie}=mu_e+alpha_e	heta_i+epsilon_{ie}
]

across obstacle configurations, with the same (	heta_i) estimated from other environments?

## Estimator

Use the existing FlightIntensity scalar and bat×environment centroids.

For each target environment e:
- estimate (	heta_{i,-e}) as the equal-environment mean over all other environments for bat i;
- require at least two training environments for bat i;
- retain target environments with at least three eligible bats;
- fit OLS with intercept:
  `y_ie = intercept_e + alpha_e * theta_i,-e`.

Report each alpha_e and Pearson r.

Programme summaries:
- equal-environment mean alpha;
- median alpha;
- number/fraction alpha > 0.

## Null

Within each environment independently permute complete bat labels among bat×environment scalar centroids, preserving the observed centroid values and environment structure.

For each permutation:
- rebuild all cross-environment theta estimates;
- refit every eligible target environment;
- require the same number of evaluable target environments as observed;
- compute equal-environment mean alpha and number positive.

B = 9,999
Seed = 20261007901

Primary calibrated statistic:
equal-environment mean alpha, one-sided.

Secondary:
number of positive alpha values, one-sided.

## Interpretation

Supported positive mean alpha means the portable scalar is expressed in the same direction across novel obstacle configurations, although its gain can vary.

It does not imply alpha=1, exact linearity, or causal invariance.
