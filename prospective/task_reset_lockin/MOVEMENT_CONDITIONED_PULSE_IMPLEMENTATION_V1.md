# Movement-conditioned pulse implementation clarification v1

## Status

**FROZEN BEFORE MOVEMENT-CONDITIONED PULSE IDENTITY IS CALCULATED.**

Parent:
`MOVEMENT_CONDITIONED_PULSE_CONTRACT_V1.md`

## Join

Join the 45 authoritative Rhino movement-feature rows and pulse-feature rows by exact CSV filename.

Require a one-to-one 45/45 match.

Any mismatch = STOP.

## First-stage environment standardization

For all 45 rows:

- z-score each of the six pulse features separately within each environment;
- z-score each of the eight movement features separately within each environment;
- use sample SD (ddof=1);
- require finite positive SD for every feature in every environment.

No feature is selected using identity.

## OLS

### C1

Design:
- intercept;
- five frozen performance predictors.

Shape:
45 × 6.

Require full column rank = 6.

### C2

Design:
- intercept;
- all eight frozen movement predictors.

Shape:
45 × 9.

Require full column rank = 9.

For every pulse feature separately, fit ordinary least squares with `numpy.linalg.lstsq`.

No regularization, interaction, polynomial, or bat/environment term is added.

Report:
- design rank;
- 2-norm condition number.

## Residual re-standardization

For each fitted pulse feature:

1. retain OLS residuals;
2. within each environment, subtract the residual environment mean;
3. divide by the residual environment sample SD.

If one pulse feature has zero/nonfinite residual SD in any environment:
- drop that pulse feature for the entire diagnostic.

Require >=4 of 6 residual pulse features.

No feature may be dropped for effect direction or identity performance.

## Identity estimator and null

Use the exact leave-one-environment-out identity estimator and environment-wise whole-cluster label permutation already frozen in `RHINO_PULSE_IDENTITY_CONTRACT_V1.md`.

The OLS and residualization are computed once from the observed movement/pulse values and are not re-fit inside identity permutations because bat identity labels are absent from the regression.

## Permutations

C1:
- 9,999
- seed `202610042251`

C2:
- 9,999
- seed `202610042252`

Minimum valid:
9,500.

## Diagnostic support

For each C1/C2:
- residual P > 0;
- one-sided p <= 0.05;
- >=70% evaluable bats positive.

These remain post-primary sensitivities.
