# Ducke original source v2 — fixed food-12 vs remaining-10 model discrimination

2026-11-20 | **post-outcome exploratory source-specific sensitivity**, not preregistered or externally replicated. Design/code were committed at `8a19e182514bfb0ba02ccbca7b0aad8d04d5e0a4` **before this v2 output**. Original food-source result, including unusual dates and incomplete vegetation structure adjustment, remains unchanged. Original ZIP SHA-256: `55c784e2f7b37987e3657d3ba3d5cf6a41bb3554a11904969d1376c977bcdbce`.

## Question
Can a two-part measure of actually recorded fruiting plants (12 paper-figure candidate food genera vs 10 other recorded genera) predict the captured bat **guild proportions** beyond (i) elevation + sample frame + matched nights, (ii) each other, and (iii) a single total-fruit score? No species occupancy, absolute feeding or causal intervention is estimated.

Original 46 source-qualified plots, 103 same-day matched plot-nights and 810 bats; seven held-out source layout blocks; fractional-binomial plot-equal heldout log scores with pre-fixed `L2=0.15` and train-only scaling. All five candidate models score **identical test plots** and source group margins. The original source was opened before the v2 design, so no independent test claim.

## Frozen seven-block heldout source results

| Response among captured bats | F alone − baseline | O alone − baseline | F+O − baseline | F contribution after O | O contribution after F | F+O − total fruit |
|---|---:|---:|---:|---:|---:|---:|
| Frugivores | +0.016085 | +0.012974 | **+0.024011** | **+0.011036** (5/7) | +0.007926 (4/7) | **+0.026274** (6/7) |
| Gleaning animalivores | +0.002225 | +0.015543 | **+0.015671** | +0.000127 (4/7) | **+0.013445** (7/7) | +0.015010 (6/7) |
| Nectarivores | +0.005169 | −0.002947 | +0.002517 | +0.005464 (5/7) | **−0.002652** (0/7) | −0.001199 (4/7) |

All values are differences in natural-log predictive scores per heldout *plot-level captured-guild fraction*, not independent bat observations. F = `log1p` of observed fruiting plants from 12 author figure food-candidate genera, O = `log1p` of the remaining 10 genera, and total = `log1p(F fruit count + O fruit count)`. Four of the seven blocks had a positive O-after-F effect for frugivores, so **neither 12 nor 10 genera has an exclusive nutritional interpretation**.

For frugivores, leave-one-plot-out (46 dependent folds) gave F contribution after O **+0.004775**, O after F +0.000391, and F+O versus baseline +0.007521. Restricting the entire analysis and training to the original L3–L8 source layout (29 plots, **six** heldout L blocks, excluding all 17 PO-design plots) gave F after O **+0.005036** (4/6), O after F +0.004197 (3/6), and F+O vs baseline **+0.014733** (5/6). The improved frugivore prediction thus persists in these **source-local, exploratory sensitivity populations** but is weaker in L-only design.

The v1 F-alone seven-block result was independently replayed from the original SHA-pinned source with a second pure-stdlib Newton solver, reproducing **+0.016084661100832526 to within 1.3 × 10⁻⁹ nats** before this v2 model discrimination. The v2 conditional and six-layout contrasts are new *within-source* fits, not independent animals/studies.

## Ecological distinction strengthened — but causal specificity not established

1. A single total-fruiting-plant score was not predictively useful in the v1 original result (−0.002263), whereas **separate resource-composition scores** carry more information (+0.024011 for frugivore fraction and +0.026274 against total fruit on identical folds). This is consistent with environmental filtering depending on resource/habitat composition rather than just total fruit count, but a two-variable model has more flexibility; independent new source transport is required.
2. For **gleaning animalivores**, the remaining 10 genera add more to prediction than the candidate food 12 genera, even with F entered (+0.013445, 7/7 original blocks); this suggests plant composition can proxy non-food structure and guild-specific spatial context. It does **not** prove gleaning bats consume those fruits.
3. Nectarivores show a different weak pattern; under 29 L-only sites the combined model's gain was approximately zero (−0.000148), underscoring context/sample sensitivity.
4. Zero new p-values are generated. Seven spatial/design blocks, source's unresolved capture-year anomalies, unmatched vegetation clutter, uneven 17 added PO sites, missing fruit records for some sites, conditional mist-net detection, multiple target/model comparisons, and source-original paper prior art prevent causality or universal generalization.
5. All three responses are compositional proportions of the same captured community. They must not be treated as independent replicated outcomes. A **joint heldout multinomial guild model** is the natural next methodological test if source size supports it, not a new 5-D bat-flight SDM.

**Source-local conclusion ceiling:** Two fruit-plant composition axes improve within-source heldout prediction of captured fruit-bat guild shares more than total fruits alone, with cross-guild patterns that suggest composition/spatial-structure filtering. No true trophic interaction, bat resource choice, externally transferable species SDM, or resource-conditioned individual GPS altitude has been established. Original NeoBat M3−M1/N1 remains NOT ESTIMATED. No JAE, BE, esdm main or batter main changes.

Reproduce with [fixed v2 code](ducke_resource_specificity_v2.py) and private source-validated aggregate 46-plot data; immutable aggregate output in [v2 receipt](ducke_source_specificity_v2.json). No raw bat, plot, GPS or original coordinates committed.
