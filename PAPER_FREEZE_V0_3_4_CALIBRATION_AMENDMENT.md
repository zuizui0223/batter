# batter v0.3.4 estimator-calibration claim amendment

Date: 2026-09-27

This amendment follows a post-freeze estimator audit. It does **not** alter any frozen primary
dataset, endpoint, source-admission rule, grid, vertical bin, smoothing constant, or retained
negative result.

It changes the paper-level interpretation because the original conditional-versus-marginal
architecture classes were not robust to estimator calibration.

## Trigger

A diagnostic audit identified that:

1. the finite-sample exchangeability expectation of
   `G_adv = G_cond - G_marg` is not zero;
2. ordinary marginal identity mixes vertical identity with differences in horizontal cell-use
   weighting.

The focal calibration was frozen before its output was opened. After that output showed a
material effect, a second cross-panel calibration contract was frozen before any non-*Tadarida*
calibration output was opened.

## Result

Across all six panels, the permutation null of common-cell conditional advantage is negative.

After integrating self and other conditional vertical profiles under the same self cell-use
weights, the original architecture contrast changes substantially.

Most importantly, *Phyllostomus hastatus* 2022 changes from:

- ordinary conditional advantage = **-0.120**

to:

- common-cell conditional advantage = **+0.0066**.

Its prior “marginal-dominant” classification therefore does not survive horizontal
standardization.

## Superseded claim

Do not use:

> Individual vertical identity has conditional-dominant and marginal-dominant architectures.

The raw sign of uncalibrated G_adv is not a valid cross-panel biological classifier.

## New central claim

> **Across six tracking panels from four bat taxa, individual identity predicts vertical airspace
> use across sessions even after self and other predictors are standardized to the same
> horizontal cell-use distribution. Repeatable vertical individuality is therefore not reducible
> to horizontal space-use fidelity.**

A secondary calibrated result is:

> **Retaining horizontal cell identity provides a small additional raw predictive increment, and
> that increment is consistently greater than the negatively biased exchangeability expectation
> of the estimator.**

The second statement concerns estimator-calibrated evidence; it is not a claim of a large
cell-specific biological effect.

## Quantitative summary

| Panel | Common-cell marginal | Raw common-cell advantage | Null mean of advantage | Calibrated advantage | P(null >= observed) |
|---|---:|---:|---:|---:|---:|
| *Tadarida* | +0.379 | +0.049 | -0.233 | +0.282 | 0.0127 |
| *Eidolon* | +0.177 | +0.042 | -0.039 | +0.081 | 0.0060 |
| *Hypsignathus* | +0.022 | +0.007 | -0.035 | +0.042 | 0.0002 |
| *P. hastatus* 2022 | +0.049 | +0.0066 | -0.059 | +0.066 | 0.0002 |
| *P. hastatus* 2023 | +0.033 | +0.0008 | -0.040 | +0.040 | 0.0144 |
| *P. hastatus* 2016 | -0.0039 | +0.061 | -0.160 | +0.222 | 0.0036 |

Common-cell marginal identity is above its panel-specific permutation null in all six panels.

## Submission status

JAE v0.3.3 rc2 is **scientifically superseded and must not be submitted**.

The source/data freeze remains closed. The next manuscript version must be reframed around
repeatable vertical identity beyond horizontal fidelity, not multiple predictive architecture
classes.

## Claim boundary retained

Still not established:

- stable individual-specific cell × height maps;
- fixed learned routes;
- personality;
- adaptation or optimality;
- validated foraging specialization;
- a universal environmental mechanism.
