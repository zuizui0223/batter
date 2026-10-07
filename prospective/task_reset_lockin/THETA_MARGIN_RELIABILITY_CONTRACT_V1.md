# Rhino theta margin-reliability diagnostic v1

## Status

**POST-PRIMARY MATHEMATICAL-STRUCTURE DIAGNOSTIC. NOT CONFIRMATORY.**

Frozen after:
- one-dimensional Rhino identity sufficiency;
- FlightIntensity scalar support;
- held-out pairwise magnitude calibration;
- rapid theta convergence;
- descriptive full-data pairwise rank stability.

No held-out margin-reliability result has been calculated under this contract.

## Question

If a stable scalar personal parameter `theta_i` is expressed with environment-specific noise, then pairwise rank reversals should concentrate among individuals whose training-only theta estimates are close together.

The prediction is:

> the larger the absolute training-only predicted pair difference, the more reliable the held-out ordering should be.

## Data and prediction architecture

Reuse exactly the *Rhinolophus nippon* FlightIntensity scalar and leave-one-environment-out pairwise calibration architecture from:
- `ONE_PARAMETER_CALIBRATION_CONTRACT_V1.md`;
- authoritative workflow run 37243890343.

For every eligible target environment e and unordered pair (i,j):

[
x_{ije}=hat\theta_{i,-e}-hat\theta_{j,-e}
]

is estimated only from non-target environments.

Held-out difference:

[
y_{ije}=y_{ie}-y_{je}.
]

Define:
- margin `m=|x|`;
- correctness `c=1` if sign(x)=sign(y), `0` if signs disagree, and `0.5` for an exact tie.

## Primary statistic

Spearman correlation across pair × environment points between:
- training-only margin `|x|`;
- held-out correctness `c`.

This asks whether larger scalar separation predicts more reliable ordering.

## Fixed descriptive margin thresholds

Also report raw sign accuracy for points with:

- |x| >= 0.25
- |x| >= 0.50
- |x| >= 0.75
- |x| >= 1.00

Thresholds are frozen before opening point-level outcomes under this diagnostic.

For each threshold report:
- number of eligible pair × environment points;
- sign accuracy;
- number of distinct pairs represented.

## Null calibration

Use the exact label-permutation architecture of the one-parameter calibration:

Within every environment independently:
- permute complete bat × environment scalar clusters among bat labels;
- recompute training-only theta;
- recompute held-out pair differences;
- recompute margins and correctness.

9,999 permutations.

Seed: `20261007901`.

For each valid permutation calculate the same Spearman margin-correctness statistic.

One-sided:
[
p=(1+#\{rho_{null}>=rho_{obs}\})/(1+n_{valid}).
]

Require >=9,500 valid permutations.

## Support rule

Call margin reliability supported if:
- rho > 0;
- p <= 0.05.

The threshold table is descriptive and cannot rescue a failed primary statistic.

## Interpretation

Supported:
> environment-specific rank reversals are concentrated among near-tied personal scalar positions, as expected under a stable theta plus context/noise model.

Unsupported:
> scalar separation does not explain where held-out rank reversals occur; theta may identify average differences without behaving as a simple noisy one-dimensional ordering parameter.

## Ceiling

Even a supported result does not prove Gaussian noise, a unique stochastic differential equation, or a physiological scalar.
