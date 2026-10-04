# Cross-fitted route-conditioned pulse identity contract v1

## Status

**POST-PRIMARY MECHANISM ROBUSTNESS DIAGNOSTIC. NOT CONFIRMATORY.**

Frozen after C3/C4 route-conditioned pulse diagnostics.

C4 remained positive in all five bats and passed its frozen permutation rule, but used an in-sample nuisance projection with a relatively high-dimensional predictor space. The present diagnostic removes target-environment information from nuisance-model fitting.

## Question

Does individual pulse-timing identity remain after movement, scale-free geometry and absolute lane effects are predicted **out of environment**?

## Data

Same 45 authoritative *Rhinolophus nippon* trajectories.

Response:
the exact six pulse features.

Predictors:
- exact eight movement-policy features;
- exact eight scale-free geometry features;
- exact three route-centroid coordinates.

No feature selection based on pulse identity.

## Stage 1 — environment standardization

For every raw pulse feature and every predictor feature:

- within each environment, subtract that environment mean;
- divide by that environment sample SD;
- require finite positive SD.

This step uses no bat identity and only removes configuration scale/location.

## Stage 2 — leave-one-environment-out nuisance regression

For each target environment e separately:

1. training set = all trajectories from environments other than e;
2. target set = all trajectories from e;
3. construct `X_train = intercept + 19 standardized predictors`;
4. fit the six standardized pulse responses jointly by ordinary least squares / Moore-Penrose least squares;
5. require:
   - numerical rank >= 2;
   - training residual degrees of freedom `n_train - rank(X_train) >= 10`;
6. predict standardized pulse features for the held-out target environment;
7. target residual = observed standardized pulse - predicted pulse.

No target-environment pulse response enters the fitted nuisance coefficients for its own residual.

Record rank, condition number and residual df for every fold.

## Stage 3 — residual feature support

After all seven target environments have out-of-environment residuals:

- within each target environment and residual pulse feature, subtract residual mean and divide by residual sample SD;
- if any environment has zero/nonfinite SD for one residual feature, drop that feature species-wide;
- require >=4 of the original six residual pulse features.

## Stage 4 — cross-configuration identity

Use the exact frozen pulse leave-one-environment-out identity estimator on these cross-fitted residual pulse features.

Identity null:
- independently within every environment, permute complete bat × environment cluster labels among the residual feature vectors;
- preserve environment and cluster sizes;
- break cross-environment individual correspondence.

Permutations: **9,999**  
Seed: `202610042281`  
Minimum valid: **9,500**

## Diagnostic support

Supported only if:
- residual identity statistic > 0;
- one-sided permutation p <= 0.05;
- >=70% evaluable bats positive.

## Interpretation

If supported:

> portable pulse-timing individuality cannot be explained by a nuisance relation between pulse timing and measured movement, scale-free route geometry and absolute route placement that generalizes across environments.

This is stronger than in-sample C4, but still does not identify the origin of the residual sensing component.

If unsupported:

Treat C4 as fragile to nuisance-model generalization and lower the mechanism claim accordingly.

## Ceiling

Even support does not distinguish:
- stable physiology/morphology;
- developmental history;
- long-lived learned sensing style;
- genetic constraints.

It only separates the sensing signature from the measured movement/route covariates.
