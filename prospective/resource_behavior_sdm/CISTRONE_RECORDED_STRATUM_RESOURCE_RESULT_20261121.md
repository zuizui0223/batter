# Cistrone original supplements: recorded-stratum resource prediction

## Result and decision

**Neither of the two frozen resource variants improved the macro-averaged
held-out-plot score.** Adding total raw insect catch changed the mean by
**-0.015784010 nats**; adding separate Lepidoptera and Diptera
catch contrasts changed it by **-0.015870293 nats**.
The two comparisons are closed. No plot was dropped, model retuned, species
subset selected or split changed after these results.

These are exploratory, same-study predictions of **recorded ground/canopy pass
allocation**, pooling two nights and all acoustic groups. They do not estimate
individual flight height, observed feeding, ecological absence of a resource
association, or a resource-conditioned regional SDM. All seven strict
individual-resource-height/SDM ledger fields remain null.

## What the upload established

The uploaded ScienceDirect ZIP contains S1 and S2 for Cistrone et al., DOI
[10.1016/j.foreco.2026.124382](https://doi.org/10.1016/j.foreco.2026.124382).
The publisher issue is dated 2027-01-01; the source audit and analysis were
performed on 2026-11-21. The three pinned source checksums and full design are
in the [frozen protocol](CISTRONE_RECORDED_STRATUM_RESOURCE_FROZEN_20261121.md).
Source bytes come from the user's upload; a separate publisher-download identity
check was not performed.

| Original data | Verified scope |
| --- | --- |
| S1 insects | 20 plots × ground/canopy, 40 samples, 23 taxa, 1,123 individuals |
| S2 acoustics | 20 plots × two strata × two ordinal nights, 80 rows, 17 groups, 1,301 passes |
| Spatial table join | All 40 `(Plot, Stratum)` keys match, with exactly two S2 nights per S1 sample |
| Arithmetic | All taxon sums agree; all 80 cached acoustic total formulas reconcile |
| Valid zero counts | One insect sample has zero catch; six recorder-night rows have zero passes |
| Conditional-score coverage | 19 positive-pass plots retain all 1,301 passes; one entire zero-pass plot remains in coverage only |

There are no missing count fields or duplicate source keys. Both adapters
independently reconstructed the same source units. Source zeros were preserved;
the zero-pass plot was not converted into a ground-only observation or an
artificial zero score.

## Fixed prediction comparison

On each fold, both nights and both strata of one positive-pass plot are held out.
Training uses the other 18 positive-pass plots. The five environmental predictors
are canopy-minus-ground openness, the unweighted two-night mean regional station
minimum temperature, stand basal area, DBH and mean tree height. Training-only
means and population SDs standardize the predictors.

All three models use the same logistic intercept and ridge penalties: 0.01 for
the intercept and 0.15 for each slope, with the penalty written as one half the
weighted sum of squared coefficients. The objective gives each training plot
equal weight. The primary variant adds the canopy-minus-ground difference in
`log1p(total insect catch)`; the secondary replaces that added total contrast
with two fixed order-specific contrasts. Neither is a calibrated prey-density
measurement. See the frozen protocol for the exact taxon columns.

The held-out plot score is its observed canopy fraction times log predicted
canopy probability, plus its ground fraction times log predicted ground
probability. Scores are **nats per recorded pass within plot, macro-averaged
across plots**: choose a positive-pass plot uniformly, then a recorded pass
within it. A plot with many passes therefore does not dominate through sample
count alone. Passes are not treated as independent bats or inferential replicates.

| Model | Mean held-out score | Gain over reference | Positive plot gains | Plot gain range |
| --- | ---: | ---: | ---: | ---: |
| Environmental reference | -0.712750882 | — | — | — |
| Total raw catch, primary | -0.728534892 | -0.015784010 | 11 / 19 | -0.333283 to +0.018522 |
| Lepidoptera + Diptera, secondary | -0.728621175 | -0.015870293 | 3 / 19 | -0.060393 to +0.007224 |

The primary mean is sensitive to one substantially negative plot difference
(-0.333283), while 11 other plot differences are positive.
That held-out failure remains in the prespecified result. The secondary has
negative differences in 16 of 19 plots. The similar mean losses consequently
hide different distributions of prediction errors. Positive-fold counts are
descriptive and are not significance tests. This analysis does not test the
published stratum-level associations or establish their absence.

## Metadata and inference that remain unresolved

| Missing or limited information | Consequence |
| --- | --- |
| No calendar dates or insect sampling window | The plot/stratum join does not verify same-night prey and acoustic observations. `Night` is ordinal within plot. |
| One trap and two nominal nights, but no trap-hours or recorder-hours | Raw catches and recorded pass allocation cannot be interpreted as effort-standardized prey availability or activity rates. |
| Recorder heights only in the legend | Ground recorders are described at 1.3 m and canopy recorders at 6.3–15.8 m, but no plot-level recorder height column exists. |
| Trap heights differ from recorder heights | S1 trap ranges are 1.00–1.31 m and 8.61–11.80 m. They cannot substitute for detector positions or actual flight height. |
| No detector calibration, deployment geometry or detection volumes | Differences in detection remain part of the recorded outcome. |
| No individual IDs, tracks or feeding marks | No observed individual behavior or resource-to-flight-height mechanism is identified. |
| All species/acoustic groups pooled | Prediction may reflect community composition; no within-species diet response is estimated. |
| No coordinates, stand IDs or deployment dates | Whole-plot withholding does not certify independent spatial or temporal transfer. Eleven repeated stand-covariate profiles do not define verified spatial blocks. |

S1 canopy cover and openness complement within 0.01 percentage point. Their
values differ between strata in all plots; the model uses the supplied openness
contrast literally. Photograph geometry and the reason for those paired
differences require original methods metadata. Source spellings in insect
headers are preserved; the order grouping does not verify specimen identification
or consumption by bats.

## Numerical and implementation verification

The design was committed before the first new source fit:
[`0f7b9a6972f81203f95c6eaf7d161c768946eacf`](https://github.com/zuizui0223/batter/commit/0f7b9a6972f81203f95c6eaf7d161c768946eacf).
Independent source and methods review preceded fitting. The production Newton
implementation has 57 fitted fold models; every maximum absolute gradient is
below 1e-10. The largest is 8.43414e-11.

A separate implementation independently reads the original ZIP with openpyxl,
constructs all features, and fits the objective with NumPy/SciPy BFGS. It imports
neither production adapter nor model. All 57 fits pass the fixed gradient gate
below 1e-8, with maximum 7.527998e-9. SciPy reported 21 successful exits and 36
precision-loss warnings; those warning fits are accepted only because their
gradients and independent predictive comparisons pass the frozen gates.

All 114 log probabilities, 57 fold scores and 38 paired plot gains agree within
1e-7. Maximum discrepancies are **3.819032e-8** for log probabilities,
**8.536398e-9** for plot scores and **8.152776e-9** for paired gains. Mean gain
discrepancy is at most **7.263632e-10**; positive-plot counts agree exactly.
The detailed aggregate comparison and script/output checksums are stored in the
[result receipt](cistrone_recorded_stratum_resource_receipt_20261121.json).

**48 new synthetic tests pass:** 28 source-adapter tests and 20 model tests.
These cover source joins and totals, observed zero versus missing data, retained
zero-pass coverage, known signal and constant-resource worlds, whole-plot
response exclusion, training-only transformations, count-weight invariance,
stratum reversal and valid probability scoring. A targeted XML decimal-precision
guard was fixed after a failing synthetic regression; every actual source model
and score remained **exactly unchanged** after the fix. The original ZIP hash
was rechecked unchanged. No unresolved material review finding remains.

## Reproduce without publishing source data

Run from a checkout containing this directory, using the user's original ZIP:

```bash
python prospective/resource_behavior_sdm/cistrone_resource_stratum_v1.py \
  --archive /private/path/ScienceDirect_files_21Nov2026_14-08-21.113.zip \
  --receipt /private/path/recomputed_aggregate.json \
  --private-details /private/path/recomputed_folds.json
python -m unittest discover -s prospective/resource_behavior_sdm -p 'test_cistrone*.py' -v
```

The main analysis requires only Python's standard library. Independent checking
uses the optional `verify_cistrone_scipy_independent_v1.py`; tested versions are
Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0 and openpyxl 3.1.5. Its keyed outputs
must remain private. The public receipt adds review and independent-verification
provenance to the directly recomputable production analysis.

The original spreadsheets, source rows, plot IDs, coordinates and private fitted
details are not included in the repository. Only code, protocol, aggregate
results and scope-qualified evidence are added. Earlier evidence entries and
strict null fields are preserved. PR #102 remains Draft and unmerged.

## Complete unkeyed plot-gain distribution

Each number is a **paired resource-model minus environmental-reference score**
for one held-out plot. Each column is independently sorted in increasing order;
the two entries on a rank row do **not** identify the same source plot. Keyed
fold alignment was checked privately. These are descriptive cross-validation
differences with overlapping training sets, not independent-study replicates.

| Rank within each column | Total catch, primary | Lepidoptera + Diptera, secondary |
| --- | ---: | ---: |
| 1 | -0.333283223035 | -0.060392520745 |
| 2 | -0.019464340899 | -0.042775985605 |
| 3 | -0.013350685490 | -0.038550065994 |
| 4 | -0.010916974626 | -0.036647590066 |
| 5 | -0.008524069533 | -0.034021135806 |
| 6 | -0.008029550672 | -0.024352753864 |
| 7 | -0.001432471138 | -0.018838423153 |
| 8 | -0.001356168620 | -0.011183664774 |
| 9 | +0.000137845560 | -0.010769119940 |
| 10 | +0.004487662529 | -0.009290192964 |
| 11 | +0.004764582061 | -0.005731514654 |
| 12 | +0.005598832804 | -0.005692661608 |
| 13 | +0.009038960218 | -0.004990656728 |
| 14 | +0.009319272755 | -0.004210682306 |
| 15 | +0.009803176717 | -0.002288213229 |
| 16 | +0.010164658929 | -0.000588894521 |
| 17 | +0.010452740094 | +0.000035630531 |
| 18 | +0.014171724004 | +0.001529129623 |
| 19 | +0.018521842175 | +0.007223748375 |

The present comparison is complete. Further interpretation would require the
original paper methods and deployment metadata for dates, effort, trap/detector
geometry and spatial grouping. That metadata audit must not turn into
post-outcome retuning of these two comparisons.
