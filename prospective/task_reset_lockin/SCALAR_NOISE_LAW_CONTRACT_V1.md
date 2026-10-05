# One-parameter scalar-noise law diagnostic v1

## Status

**POST-PRIMARY MATHEMATICAL-STRUCTURE DIAGNOSTIC.**

Frozen after:
- one-dimensional Rhino policy identity was supported;
- transparent FlightIntensity was supported;
- held-out pairwise magnitude calibration was supported;
- observed pairwise sign errors were noted but not yet analysed as a function of held-out training separation.

No margin/error-concentration result has yet been calculated.

## Question

If personal flight policy is approximately a scalar parameter with environmental noise,

`y_ie = theta_i + epsilon_ie`,

then two predictions follow:

1. held-out pairwise differences should be quantitatively predicted by the training-only scalar difference;
2. sign reversals should concentrate among pairs with small `|Delta theta|`.

This diagnostic tests those predictions without changing the scalar.

## Source scalar

Use exactly the transparent scalar:

`FlightIntensity = mean(z_median_speed, z_p90_speed, z_median_abs_vertical_speed, z_p90_abs_vertical_speed)`.

Use the exact bat × environment centroids and leave-one-environment-out training parameters from
`ONE_PARAMETER_CALIBRATION_CONTRACT_V1.md`.

For every eligible pair × target-environment point:

- predicted difference `x = theta_i,-e - theta_j,-e`;
- held-out observed difference `y = y_ie - y_je`;
- prediction error `r = y - x`;
- sign correctness `c = 1` if x and y have same non-zero sign, `0` if signs differ, and `0.5` for a tie.

No global theta estimate may replace the leave-one-environment-out value.

---

# N1 — no-refit pairwise predictive R²

Use the identity-slope prediction:

`y_hat = x`.

No coefficient is fitted.

Define:

`R2_zero = 1 - sum((y-x)^2) / sum(y^2)`.

The denominator is prediction by zero pair difference.

Also report:
- RMSE of `y-x`;
- MAE;
- Pearson r already defined in the calibration programme.

Positive `R2_zero` means the training-only one-parameter magnitude predicts held-out pair differences better than predicting no individual difference.

## Null

Use the same within-environment complete-label permutation architecture as the magnitude-calibration programme.

For every permutation:
- recompute leave-one-environment-out theta;
- recompute x and y;
- calculate R2_zero.

9,999 permutations.

Seed:
`202610050901`.

One-sided p:
`#null >= observed`.

---

# N2 — error concentration near the scalar boundary

Exclude tie points for this subtest.

Let:
- correct points = sign(x) == sign(y);
- error points = sign(x) != sign(y);
- margin = `|x|`.

Primary margin statistic:

`M = mean(margin_correct) - mean(margin_error)`.

Prediction:
`M > 0`.

Also report:
- median margin correct vs error;
- fraction of all sign errors occurring in the lowest 50% of observed margins;
- fraction of errors occurring in the lowest 25% of observed margins.

## Null

Use the same 9,999 environment-wise label permutations.

For each permutation recompute the complete calibration point set and M.

Seed:
`202610050902`.

One-sided p for M.

If a permutation has no correct points or no errors, it is invalid for M.
Require >=9,500 valid permutations.

---

# N3 — monotone margin-confidence relationship

Use all non-tie points.

Fit the simple descriptive logistic regression:

`logit Pr(correct=1) = alpha + gamma * |x|`.

No additional predictors.

Report:
- gamma;
- predicted correctness at observed margin quartiles.

Because point independence is imperfect, do not use asymptotic regression p-values.

Calibrate gamma only by the same environment-wise label permutation null.

9,999 permutations.

Seed:
`202610050903`.

Require >=9,500 valid permutations.

---

# Diagnostic interpretation

## N1 supported + N2/N3 supported

Strong scalar-noise pattern:

> a single transferable individual parameter predicts both the magnitude of held-out individual differences and where environment-dependent rank reversals occur.

This is substantially stronger than classification identity.

## N1 supported but margins unsupported

The scalar predicts average magnitude but sign errors are not localized near scalar boundaries; environmental interactions are more structured than simple additive noise.

## N1 unsupported

The previous positive slope/correlation should be interpreted as association rather than a useful no-refit generative approximation.

## Ceiling

Even full support establishes only an approximate behavioural scalar law for this species and experiment.

It does not establish:
- a physiological constant;
- deterministic dynamics;
- a universal bat parameter;
- irreducible exactness analogous to a mathematical constant.
