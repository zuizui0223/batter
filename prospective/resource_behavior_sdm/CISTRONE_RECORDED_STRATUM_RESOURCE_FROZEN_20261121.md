# Cistrone uploaded supplements: frozen exploratory recorded-stratum comparison

## Status and scope

Design frozen on 2026-11-21 after inspecting source structure, marginal counts and
published results, but before any new empirical model fit or predictive comparison.
An independent methods reviewer examined the schema and legends without fitting.
This is a **source-open exploratory reanalysis**, not preregistered confirmation.
The protocol commit must precede execution of the source-analysis CLI.

The question is whether measured **raw insect trap-catch contrasts** improve
prediction of the ground/canopy allocation of recorded bat passes at a withheld
plot in the same study. The response pools all species/acoustic groups and two
recording nights. It does not measure individual flight height, feeding behavior,
prey consumption, calibrated bat abundance or regional ecological occupancy.

## Source and structural audit

Paper: Cistrone et al., *Stratification of insects and bats reveals vertical
trophic structuring in beech forests*, DOI
[10.1016/j.foreco.2026.124382](https://doi.org/10.1016/j.foreco.2026.124382),
publisher PII `S0378112726008807`. Its issue date is 2027-01-01; this audit occurs
on 2026-11-21. Source bytes are the user's supplied publisher download, not a
separately downloaded copy independently authenticated against the publisher.

| Object | SHA256 |
| --- | --- |
| Uploaded ScienceDirect ZIP | `3eed7ceeb9c1201a3e8594c6d28115d268a7c64e1c1acdccfb6e5d50da872653` |
| `1-s2.0-S0378112726008807-mmc1.xlsx` | `7220410f012954b82ae12d33a06d0a6ff70abb66aaa7e17a5aaaf874242f9259` |
| `1-s2.0-S0378112726008807-mmc2.xlsx` | `adcfc18635b5f7d804dad496f3f5108f642a86ba4aaec6d90a932c724148531d` |

S1 `Data` contains a header, a DNA-barcoding annotation row, and 40 observations:
20 plots × two strata, 23 insect taxon columns and 1,123 individuals. Each
`(Plot, Stratum)` key is unique. `n_traps=1` throughout. These are raw catch
counts, explicitly not standardized by trapping effort. One sample has zero
insects; it remains a valid measured zero.

S2 `Data` contains 80 observations: 20 plots × two strata × two consecutive
recording nights, 17 species/acoustic group columns and 1,301 bat passes.
`(Plot, Stratum, Night)` is unique, with both nights and strata present per plot.
The 80 cached total formulas must agree with sums of the 17 count fields.
One entire plot has zero recorded passes across both nights and strata. Its
conditional stratum distribution is undefined; retain it in coverage but exclude
it from fitting and scoring. The remaining 19 plots retain all 1,301 passes.
No pseudocount is added to bat responses and no other plot is excluded.

The 40 S1 keys match the S2 `(Plot, Stratum)` keys exactly, one insect sample to
two recorder-night rows. Pool the two bat nights **before** joining/modeling at
plot level. Do not turn duplicated S1 values into independent resource samples.

The supplements contain no calendar dates, insect sampling windows, trap-hours,
recorder-hours, detector failure/calibration logs or plot coordinates. `Night`
is a within-plot ordinal, not a global date. The legend describes ground
recorders at 1.3 m and canopy recorders at 6.3–15.8 m, but `Recorder_height_m`
is absent from S2 `Data`. S1 `Height_m` measures insect traps (ground 1.00–1.31 m,
canopy 8.61–11.80 m); it must not be substituted for recorder height. Matching
strata is not proof of matching dates, effort or exact physical heights.
The regional weather-station value is not measured plot microclimate.

## Estimand and whole-plot validation

For positive-pass plot i, let G_i and C_i be pooled ground and canopy counts,
N_i=G_i+C_i, and y_i=C_i/N_i. Predict p_i, the canopy probability of a recorded
pass within that plot. Score

`s_i = (G_i/N_i) log(1-p_i) + (C_i/N_i) log(p_i)`.

Hold out one entire plot, including both nights and strata, on each of 19 folds.
The training set contains 18 positive-pass plots. Average scores and paired
resource-minus-reference differences equally over held-out plots. This is the
distribution obtained by selecting a positive-pass plot uniformly, then a
recorded pass uniformly within it. Units: **nats per recorded pass within plot,
macro-averaged across plots**. It is not a pass-weighted score over all 1,301
events. Recorded passes and the two nights are not independent replicate animals.

All observations remain conditioned on the study's recording process. Whole-plot
withholding is not independent temporal validation, a verified spatial block
design, or transfer to another forest. No geographic or stand IDs are invented
from row order or repeated stand measurements.

## Exactly three fixed logistic models

All models have a canopy-logit intercept and the same five baseline features:

1. S1 canopy minus ground `Clear_canopy_%`, in percentage points. Do not also
   include its complementary canopy-cover variable.
2. Unweighted arithmetic mean of the two S2 nightly `Temp_min` values. First
   require the two strata to agree for each plot-night. Do not weight by passes.
3. `Mean_basal_area_m2_ha`.
4. `Mean_DBH_cm`.
5. `Mean_tree_height_m`.

The three stand variables must agree across all four recorder-night rows of a
plot. The supplied within-stratum canopy-openness values are used literally;
their photograph geometry cannot be independently verified from the supplements.
No trap height, recorder-height proxy, taxon-derived dietary label, response-based
feature, occurrence total or held-out response enters the predictors.

| Role | Additional features |
| --- | --- |
| Environmental reference (`baseline`) | None |
| **Primary** resource variant (`total`) | `log1p(canopy total insect count) - log1p(ground total insect count)` |
| Prespecified secondary (`orders`) | Separate contrasts of this form for Lepidoptera and Diptera; no total-catch contrast |

Lepidoptera uses these exact 14 source headers: `Agrotis ipsilon`,
`Alcis bastelbergi`, `Amata phegea`, `Arctornis l-nigrum`, `Biston betularia`,
`Lymantria monacha`, `Crambus pascuella`, `Tuta absoluta`, `Eilema caniola`,
`Orgyia antiqua`, `Catocala ilia`, `Pscoparia basistrigalis`, `Eudonia lacustrata`,
and `Tineola bisselliella`. Diptera uses `Scathophaga stercoraria`,
`Brevicornu foliatum`, `Pseudolynchia canariensis`, and `Cylindromyia rufipes`.
Preserve source spellings. Their grouping is fixed before fitting, informed by
the published prey-order discussion; no taxon is selected from a new association.
All 23 taxon counts enter the primary total regardless of order or assumed diet.

Standardize every non-intercept feature using only the training plots' unweighted
mean and **population** SD (denominator 18 for source folds). If SD <= 1e-12,
replace it with 1. Centering still uses the training mean. Apply those training
parameters unchanged to the held-out plot. Do not standardize the response.

Minimize the mean training-plot cross-entropy plus

`0.5 * 0.01 * intercept**2 + 0.5 * 0.15 * sum(slope**2)`.

Use the same penalties in every model/fold. The intercept is penalized; it is
not described as the exact empirical canopy fraction. The slopes have no imposed
sign constraint. There is no hyperparameter search, inner tuning, species subset
search, post-outcome predictor change or alternative split selection.

Use stable logistic log probabilities, Newton iterations with a maximum of 100,
gradient maximum absolute value <1e-10, partial-pivot Hessian solve and Armijo
backtracking (coefficient 1e-4, minimum step 2**-30, objective roundoff allowance
1e-15). Fail explicitly if optimization or source validation fails. An independent
SciPy implementation must reproduce source fold scores/gains to absolute 1e-7
before final reporting; it must construct its own features and objective.

## Reporting, verification and stopping rule

Report both fixed comparisons, keeping `total-baseline` primary regardless of
direction. Include absolute mean scores, mean paired differences, positive-plot
counts, full sorted unkeyed plot differences and their range. Retain keyed
per-fold details privately for independent numerical checking. Do not publish
original records, plot identifiers, coordinates, source spreadsheets or source ZIP.
Fold differences describe this dataset; they are not independent-study evidence,
a p-value or a confidence interval. Pooled results do not identify within-species
effects and may reflect community composition.

Verify synthetic known-signal and constant-resource worlds, zero versus missing
data, source joins, totals, training-only transformations, whole-plot splitting,
score normalization and invariance to multiplying one plot's counts. Run the
repository's existing source-free tests and claim gates. Keep all strict
individual-resource-height/SDM ledger fields null and historical results unchanged.

Close this source/model comparison after these two frozen resource increments,
whether positive, negative or mixed. Further analyses require a new explicitly
motivated question or new measurement metadata, not a search for a positive score.
Keep PR #102 Draft and unmerged; no changes to batter/main, esdm/main or frozen
manuscripts. A positive result would support only measured raw trap-catch
information for same-study recorded-stratum prediction under this model.
