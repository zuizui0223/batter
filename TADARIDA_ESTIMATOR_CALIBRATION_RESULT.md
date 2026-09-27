# Tadarida estimator calibration v1 — result

Date: 2026-09-27

Status: **post-freeze diagnostic calibration**. The algorithm was frozen in
`contract/tadarida_estimator_calibration_v1.json` before this output was opened.

Authoritative workflow:
- run `36291669628`
- head `56a6ba8ac0e6c73c964a235237665faa02716d5b`
- artifact `10922168504`
- artifact digest `sha256:06426a59951bc6b5ed849dd12ffeb4a9d5b0e6da512f61a7c2472210ca9bf7ac`

## 1. Frozen paper score reproduced exactly

The calibration implementation reproduced the paper-facing 5-km MSL *Tadarida* values to
the frozen 1e-12 tolerance:

| Metric | Observed |
|---|---:|
| Conditional identity | +0.428041 |
| Ordinary marginal identity | +0.052484 |
| Ordinary conditional advantage | +0.375556 |
| Evaluable individuals | 6 |

So the calibration targets the actual manuscript estimand rather than an approximate reanalysis.

## 2. The zero-null assumption is false

Under 9,999 whole-session label permutations preserving session x-y-z structure, fix counts,
coverage and the exact session-count vector per individual label:

| Metric | Null mean | Null 2.5–97.5% | Observed | Obs − null mean | P(null >= obs) |
|---|---:|---:|---:|---:|---:|
| Conditional identity | -0.456 | -1.113 to +0.106 | +0.428 | +0.884 | 0.0003 |
| Marginal identity | -0.139 | -0.442 to +0.137 | +0.052 | +0.192 | 0.0777 |
| Conditional advantage | **-0.317** | -0.961 to +0.211 | **+0.376** | **+0.693** | **0.0058** |

Therefore `G_adv = 0` is not the finite-sample exchangeability baseline for this dataset.
The bias concern is confirmed, and it is larger here than in the motivating synthetic example.

At the same time, the observed conditional score and ordinary G_adv are far above their
pipeline-specific permutation nulls. The focal individuality signal is not explained away by
Jeffreys/cell-sparsity bias alone.

The permutation null had fewer evaluable pseudo-individuals on average (mean 4.80; median 5;
2.5–97.5% = 3–6) than the observed six. This means the permutation calibration is a calibration
of the **whole prediction pipeline**, including the horizontal-overlap/evaluability structure;
it must not be interpreted as a pure vertical-mechanism test.

## 3. Common-cell reweighting changes the biological decomposition

When both self and other conditional vertical profiles are integrated using the **same self cell-use
weights**:

| Metric | Observed |
|---|---:|
| Common-cell-weighted marginal identity | **+0.379306** |
| Conditional identity | +0.428041 |
| Common-cell-weighted conditional advantage | **+0.048735** |

Thus common spatial weighting moves marginal identity from +0.052 to +0.379 and reduces the raw
conditional advantage from +0.376 to +0.049.

The change is exactly 0.326822 nats/fix in opposite directions:

- ordinary marginal − common-cell marginal = -0.326822;
- ordinary advantage − common-cell advantage = +0.326822.

This shows that the original marginal/conditional decomposition is strongly affected by how
horizontal cell use is integrated.

## 4. Individual-level uncertainty

Percentile 95% individual-bootstrap intervals (20,000 resamples):

| Metric | Estimate | 95% bootstrap interval |
|---|---:|---:|
| Conditional identity | +0.428 | +0.142 to +0.691 |
| Ordinary marginal identity | +0.052 | -0.318 to +0.485 |
| Ordinary conditional advantage | +0.376 | +0.043 to +0.691 |
| Common-cell marginal identity | **+0.379** | **+0.122 to +0.621** |
| Common-cell conditional advantage | +0.049 | **-0.042 to +0.203** |

Only **2 of 6** evaluable individuals have positive common-cell conditional advantage.
By contrast, common-cell marginal identity is positive for 5 of 6 individuals.

The common-cell advantage is nevertheless above its negatively shifted permutation null
(null mean -0.233; observed-minus-null +0.282; one-sided permutation tail 0.0127).
These two facts are not contradictory: the estimator's finite-sample null is itself negative,
while the raw across-individual increment is small and heterogeneous.

## 5. Ecological conclusion after calibration

The focal result that survives strongly is:

> **European free-tailed bats carry repeatable individual information in vertical airspace use
> across nights, including after horizontal cell-use differences are standardized.**

The stronger statement does **not** currently survive in its simple form:

> “Tadarida vertical identity is primarily conditional on horizontal place.”

After common-cell standardization, most of the original conditional-versus-marginal gap
disappears. The focal system is better described provisionally as having **strong repeatable
vertical identity with only a modest additional raw conditional increment**, while the
pipeline-calibrated conditional increment remains above exchangeability expectation.

## 6. Consequence for the paper

The four-panel “conditional-dominant versus marginal-dominant” classification must now be placed
on **submission hold** until every panel is evaluated with the same two corrections:

1. panel-specific whole-session permutation calibration;
2. common-cell-weighted marginal identity.

The existing v0.3 primary values remain frozen historical endpoints. This diagnostic does not
erase them, but it invalidates using their uncalibrated zero/sign as a directly comparable
cross-panel biological classifier.

The next analysis must be frozen before opening any non-*Tadarida* calibration output.
