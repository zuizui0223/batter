# Ducke source v4 — same-complexity plant-label partition challenge

**2026-11-20 | source-open exploratory negative-control analysis; not an independent replication or a registered p-value.** The null design was recorded in [frozen v4 protocol](DUCKE_EQUAL_COMPLEXITY_PLANT_PARTITION_V4_FROZEN.md) at commit `9c35ebf09945ea138c239917291d5b333c3765d3` prior to this v4 output, after v1–v3 outcomes were already known. Original user-supplied Ducke Dryad DOI `10.5061/dryad.9rb48c5`, ZIP SHA256 `55c784e2f7b37987e3657d3ba3d5cf6a41bb3554a11904969d1376c977bcdbce`.

## What was held fixed

Original 46 source-qualified sites, 103 plot×date-matched nights, captured **four-guild** response (809 bats in four major guilds out of 810 captures), 7 complete spatial/design heldout source blocks, identical plot-equal multinomial predictive log score and L2 penalty 0.15. No site coordinates, original capture rows or individual IDs were committed.

For each qualifying site the recorded number of fruiting plants was assembled from each original **plot×same-date fruit survey** into a site×plant-label matrix, averaging source survey nights equally. The original 12 literature candidate-food labels plus ten remaining labels reproduce `fruit_batfood_12`, `fruit_other`, and `fruit_all` in the v3 source input. Important corrected wording: **22 source plant-label categories = 21 named genera + one `Not_identified` category, NOT 22 botanically identified genera**. The unidentified category accounts for **52/661 (7.87%) of summed fruiting-plant counts** (source `Amount` values) across matched nights, contributed by **12 original source rows**. These are not 52 independent plant survey records.

The source-frozen observed model has two source resource axes `log1p(F12)` and `log1p(other10)`, compared with `log1p(total22 categories)`, all other training/scoring unchanged. An independent vectorized SciPy source replay gives **+0.02610671 nats per local plot-guild-composition score**, versus the original v3 +0.02610666 (difference ~5.1×10⁻⁸). A separate pure-stdlib full-Hessian implementation reproduces the source-defined split and one predetermined null partition to within **1.7×10⁻⁸ nats**; GitHub source-free tests pass across Python 3.10, 3.11, 3.12 (Actions #44748952410).

## Fixed same-dimensional-label counterfactuals

Both comparison families have **exactly two resource regressors** (a 12-label sum and its 10-label complement), the same original animal outcomes, and the same measured site environment and heldout blocks. Labels are randomly assigned across plant categories, **not across site/animal rows**. Null models preserve all actual source category-by-plot records; these are *partition-label counterfactuals*, not ecological field interventions.

| Metric | Original F12 vs O10 | Unrestricted 12/10 random labels | Abundance-quartile-matched random labels |
|---|---:|---:|---:|
| Seven-block improvement over one pooled fruit variable | **+0.0261067** | null mean **−0.0027006** | null mean **+0.0012464** |
| Original ≥ random fits | — | **4 / 199** random fits ≥ original | **10 / 199** random fits ≥ original |
| +1-corrected upper-tail proportion | — | **0.025** | **0.055** |
| Random split gain 5–95% range | — | −0.020763 to +0.021933 | −0.014925 to +0.025911 |
| Count matched by plant source abundance | — | no | yes (four original-count quartiles; food-label counts **[4,2,2,4]**) |

Random seeds are `202611201` and `202611202`. Each randomization has 199 draws. Abundance matching fixes the candidate-food label count inside four source-count-ranked quartiles; this makes source counts more comparable but still does not control plant traits, lineage, spatial niche or observer effects. The two nulls are not statistically independent studies and the plus-one fractions are **exploratory ranks, not preregistered confirmatory p values**.

## Sensitivity to unknown plant category and sampling frame

- Drop `Not_identified` (52 entries) rather than guessing a genus, so **21 named genera = 12 candidate food + 9 others**. With the same seven full source block splits, the separated axes still beat one *named-genera-only* total by **+0.0281590**. Thus the composition contrast does not depend solely on unidentified plant entries.
- Remove all 17 added PO-design sites, retain 29 original L3–L8 sites, refit and hold out six full source bands. The original 12-vs-10 split beats one total22 score by **+0.0137782**, less than the full-source +0.0261067; and its baseline-relative gain is **+0.0228782**. This is a different source subpopulation, not a rescued external validation.

## Ecological verdict

**Retain as source-local prediction:** measured fruiting-plant **composition** provides information about the captured four-guild assemblage that is not captured by a single pooled fruit count.

**Do not promote:** the original 12 published food-candidate genera as a uniquely causally relevant nutritional partition. Label specificity is suggestive against completely unconstrained random partitions, but **the abundance-matched partition comparison (10/199, plus-one 0.055) does not strongly separate the original label choice**. The alternative ten categories include unknown plants and do not constitute a measured “not eaten by bats” negative control. Count/identity/flexibility, forest structure and detection effort can all contribute.

Sampling issues and causal ceilings are unchanged: 2015–2030 date anomalies in original raw bat table, incomplete author-reported count reconciliation, missing independent vegetation-clutter covariate, and no directly observed individual plant feeding. The Ducke source contains no same-individual GPS-height records. This does **not** validate a 3D/5D resource-conditioned bat distribution. The NeoBat original ecological M3−M1/N1 is not estimated. This addition stays on draft batter PR #102; frozen JAE/BE and `main` unchanged.

Audit inputs: [v4 frozen protocol](DUCKE_EQUAL_COMPLEXITY_PLANT_PARTITION_V4_FROZEN.md), [source-free code](ducke_plant_partition_v4.py), [aggregate v4 result](ducke_plant_partition_v4_aggregate.json). Full source input, raw original plant-by-site data, and individual null-replicate score vectors stay outside GitHub.
