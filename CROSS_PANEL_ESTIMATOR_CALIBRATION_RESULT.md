# Cross-panel estimator calibration v1 — result

Date: 2026-09-27

The cross-panel algorithm was frozen before any non-*Tadarida* calibration output was opened.
All five matrix jobs completed successfully in workflow `36292039473`.

The *Tadarida* row comes from the separately frozen focal calibration
(`TADARIDA_ESTIMATOR_CALIBRATION_RESULT.md`).

## Main result

| Panel | n | Original G_adv | Common-cell marginal | Common-cell advantage | Null mean of common-cell advantage | Calibrated advantage | P(null >= obs) | Bootstrap 95% for raw common-cell advantage |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| *Tadarida* | 6 | +0.376 | +0.379 | +0.049 | -0.233 | +0.282 | 0.0127 | -0.042 to +0.203 |
| *Eidolon* | 20 | +0.217 | +0.177 | +0.042 | -0.039 | +0.081 | 0.0060 | +0.003 to +0.090 |
| *Hypsignathus* | 24 | +0.050 | +0.022 | +0.007 | -0.035 | +0.042 | 0.0002 | -0.003 to +0.017 |
| *Phyllostomus* 2022 | 33 | **-0.120** | +0.049 | **+0.0066** | -0.059 | +0.066 | 0.0002 | -0.028 to +0.053 |
| *Phyllostomus* 2023 | 16 | +0.020 | +0.033 | +0.0008 | -0.040 | +0.040 | 0.0144 | -0.013 to +0.016 |
| *Phyllostomus* 2016 | 10 | +0.041 | -0.0039 | +0.061 | -0.160 | +0.222 | 0.0036 | -0.044 to +0.167 |

## 1. The original architecture classes are not robust

The decisive result is *P. hastatus* 2022.

Original decomposition:

- conditional identity = +0.056;
- ordinary marginal identity = +0.176;
- ordinary G_adv = **-0.120**.

This was the sole strong “marginal-dominant” counterexample supporting the manuscript's
multiple-architecture story.

After applying the same horizontal cell weights to self and other vertical profiles:

- common-cell marginal identity = +0.049;
- common-cell advantage = **+0.0066**;
- individual-bootstrap 95% interval = -0.028 to +0.053.

The negative architecture therefore disappears.

The previous “marginal-dominant *Phyllostomus* 2022” interpretation is not robust to horizontal
cell-use standardization.

## 2. The estimator null is negative in every panel

The common-cell conditional-advantage null means are:

- *Tadarida*: -0.233;
- *Eidolon*: -0.039;
- *Hypsignathus*: -0.035;
- *P. hastatus* 2022: -0.059;
- *P. hastatus* 2023: -0.040;
- *P. hastatus* 2016: -0.160.

Thus zero is not the exchangeability expectation for this estimator family.

The size of the bias differs strongly among panels, exactly as expected if sparsity, session
structure and horizontal overlap affect the score.

Raw G_adv signs cannot therefore serve as a cross-panel biological classifier.

## 3. A stronger ecological generality emerges

After horizontal standardization, common-cell marginal identity is above its own panel-specific
permutation null in **all six panels**:

- *Tadarida*: p = 0.0005;
- *Eidolon*: p = 0.0002;
- *Hypsignathus*: p = 0.0002;
- *P. hastatus* 2022: p = 0.0002;
- *P. hastatus* 2023: p = 0.0002;
- *P. hastatus* 2016: p = 0.0422.

This supports a different biological statement:

> **Across six tracking panels from four bat taxa, the same individual carries repeatable
> information about vertical airspace use even after self and other predictors are standardized
> to the same horizontal cell-use distribution.**

This is stronger ecologically than the old architecture classification because it directly
addresses the horizontal-specialization alternative.

## 4. Additional conditional information is small in raw magnitude

Raw common-cell advantages are only about 0.001–0.061 nats/fix across the six panels.

Only *Eidolon* has an individual-bootstrap interval for the raw common-cell advantage that excludes
zero. In the other five panels, individual heterogeneity is broad enough that the raw increment
is not consistently positive across individuals.

However, every panel's observed common-cell advantage lies above its negatively shifted
session-label permutation null under the frozen calibration rule.

This means two distinct statements must be separated:

1. **absolute additional predictive gain from retaining cell identity is small and often
   heterogeneous among individuals;**
2. **the observed gain is consistently larger than expected from the finite-sample exchangeable
   pipeline.**

The second is an estimator-calibrated comparison; it should not be presented as a large
biological effect size.

## 5. Consequence for the manuscript

The current central claim:

> “Individual vertical identity has conditional-dominant and marginal-dominant architectures.”

is **superseded**.

The calibrated evidence does not support qualitative architecture classes. In particular,
the sole strong marginal-dominant panel disappears after horizontal standardization.

A defensible new central claim is:

> **Repeatable individual vertical identity is detectable across bat systems and persists when
> horizontal space use is standardized; pooled three-dimensional airspace therefore contains
> non-exchangeable vertical individual structure that is not reducible to horizontal fidelity.**

A secondary, more cautious result is:

> Horizontal conditioning provides a small additional raw predictive increment, and this increment
> is consistently greater than the negatively biased exchangeability expectation of the fitted
> estimator.

## 6. Submission consequence

The existing JAE v0.3.3 rc2 manuscript is on **scientific submission hold**.

The empirical data freeze remains intact, but the manuscript must be rewritten around calibrated
repeatable vertical identity rather than multiple predictive architectures.

No new dataset search is authorized.
