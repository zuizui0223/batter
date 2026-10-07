# Rhino theta convergence contract v1

## Status

**POST-PRIMARY MATHEMATICAL-STRUCTURE DIAGNOSTIC. NOT CONFIRMATORY.**

Frozen after the following were already known for *Rhinolophus nippon*:

- full 8-D cross-configuration individual-policy transfer is supported;
- one training-only PCA dimension is sufficient;
- one training-only supervised identity dimension is sufficient;
- an interpretable FlightIntensity scalar is supported;
- cross-environment pairwise rank stability is supported;
- held-out pairwise magnitude calibration is supported.

No theta-learning-curve result has been calculated before this contract.

## Question

Does the one-dimensional personal parameter become increasingly recoverable as more independent obstacle configurations are observed?

This is the direct convergence test behind the informal question:

> is there a finite scalar `theta_i` to estimate, or does every new environment require a new independent behavioural degree of freedom?

## Fixed scalar

Use exactly the already-defined transparent scalar:

[
FlightIntensity =
[z(v_{med})+z(v_{90})+z(|v_z|_{med})+z(|v_z|_{90})]/4.
]

The z-scores are the authoritative within-environment standardization already used in the scalar programme.

For bat i in environment e, let `y_ie` be the bat×environment mean FlightIntensity.

## Held-out prediction

For each target bat×environment observation `y_ie`:

- remove target environment e;
- let the remaining observed environments for bat i be the training environment set;
- retain targets with at least **3** training environments.

For training-set size `m = 1,2,3`:

- enumerate **all** size-m subsets of the available training environments;
- estimate `theta_hat_i,S = mean(y_i,e')` over subset S;
- predict the held-out target `y_ie` by `theta_hat_i,S`;
- average squared error equally over all subsets S for that target.

Use the **same target set** for m=1,2,3.

## Full-training reference

For each retained target, also estimate:

[
theta_{i,-e}^{full} = mean(y_{i,e'})
]

over **all** available non-target environments.

This is not treated as truth. It is the lowest-variance estimator available from the archive and is used only as a finite-data reference for the learning curve.

## Aggregation

For every m:

1. average subset prediction error within target bat×environment;
2. average target environments equally within bat;
3. average bats equally.

Primary quantities:

- `MSE_m`;
- `MAE_m`;
- `MSE_full`;
- zero-baseline MSE, where the prediction is 0 after within-environment standardization;
- `R2_m = 1 - MSE_m / MSE_zero`;
- `excess_m = MSE_m - MSE_full`.

## Convergence quantities

Primary convergence contrast:

[
Delta_{1to3}=MSE_1-MSE_3.
]

Estimate uncertainty by cluster bootstrap of biological individuals.

Also report:

[
fraction_to_full(m)
= 1 - rac{MSE_m-MSE_{full}}{MSE_1-MSE_{full}},
]

when the denominator is positive.

This equals 0 at m=1 and approaches 1 as subset estimation approaches the full-training estimator.

Descriptive **rapid-convergence threshold**:

- m=3 is called rapid convergence if `fraction_to_full(3) >= 0.80`.

This 80% threshold is frozen before the learning curve is opened and is descriptive rather than a biological constant.

## Individual theta spread

For each retained target and m, report the SD across all subset estimates `theta_hat_i,S`.

Aggregate with the same equal-target/equal-bat weighting.

This is an estimator-stability quantity. Its decline with m is expected for a finite stable parameter and is not independently inferential.

## Bootstrap

Cluster unit: biological bat.

B = 9,999.

Seed = 20261007601.

Report percentile 95% CIs for:

- MSE_1, MSE_2, MSE_3;
- R2_1, R2_2, R2_3;
- Delta_1to3;
- fraction_to_full(2), fraction_to_full(3).

A positive convergence contrast is supported if the 95% lower bound of `Delta_1to3` is > 0.

## Interpretation

### Strong scalar-convergence pattern

If:

- full-training prediction beats the zero baseline;
- Delta_1to3 > 0 with bootstrap support;
- and fraction_to_full(3) >= 0.80;

then the archive is consistent with a finite recoverable scalar personal parameter whose estimation stabilizes with repeated environments.

### Weak/no convergence

If additional environments do not reduce held-out error, then one-dimensional identity sufficiency should be interpreted as a discriminative embedding rather than a convergent personal parameter.

### Ceiling

Even strong convergence does not establish:

- a unique dynamical equation;
- a neural scalar;
- genetic determination;
- stationarity over the lifetime;
- universality across bat species.

It only tests whether a one-dimensional cross-configuration behavioural parameter behaves like an estimable finite parameter over the observed environment range.
