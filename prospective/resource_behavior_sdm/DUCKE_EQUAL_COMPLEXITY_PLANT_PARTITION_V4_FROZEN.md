# Ducke original source v4 — equal-complexity plant-label partition negative control

2026-11-20, **post-outcome exploratory**, design fixed before executing v4. Original 2018 Ducke Dryad ZIP SHA256 `55c784e2f7b37987e3657d3ba3d5cf6a41bb3554a11904969d1376c977bcdbce`.

### Previously unresolved comparability
V3 compared the baseline + `log1p(12 candidate food taxa) + log1p(remaining 10 source categories)` against baseline + `log1p(total)`. This is a **two-parameter vs one-parameter** comparison. Heldout gains show predictive information under one source, but do not isolate published candidate food labels. Crucially the source's "22 genera" wording includes **21 named genera plus `Not_identified`**, so the ten-category "other" group contains one *unidentified* entry. The matched-night fruit records sum to **661** counts; `Not_identified` contributes **52 (7.87%)**. This must be retained or explicitly omitted according to the sensitivity, never guessed to be a fruit genus.

### Fixed reproducible input
Reopen the user ZIP and validate its SHA. Use source-derived same-plot, same-date 103 nights, 46 plots, guild totals 809 analyzed of 810 captures, same 7 source blocks, 12 named literature food-candidate genera, and all 22 original plant label categories (including one unknown label). Construct one matrix of original source *plant genus categories × matched survey nights*, average equally over each plot's recorded qualifying nights. Assert that sum of fixed 12 and other 10 equals the v3 source plot's F and O **within 1e-12** and original total `fruit_all` exactly.

### One primary exploratory specificity/null test
- Outcome: exactly the frozen v3 one 4-class normalized multinomial distribution, same L2=0.15, same training-only covariate standardization, same 7 whole original source blocks; score identical test plots with equal group weights.
- Compare the observed publisher-defined 12-versus-10 split model's **7-fold mean log predictive score** against **199 fixed random 12-versus-10 divisions of the same 22 source categories**. All randomized splits have identical predictor count, and the original total fruit score is unchanged. Random seed `202611201`. Source category labels shuffled globally, *not per plot*, preserving the measured source spatial, time and within-genus data vectors. Statistic: observed F+O score minus the mean of the 199 random split F+O scores, plus rank and `(1+#random>=observed)/200`.
- A second **abundance-stratified random** split sample of 199 replicates (seed `202611202`), in which 22 plant categories are binned into four approximately equal-count groups by total source matched-night original plant count (ties deterministic); each quartile retains exactly the original number of literature-food genera within that quartile. This controls the gross abundance composition of the random partition without referring to bat responses.
- These are **partition-label specificity diagnostics**, not confirmatory p values or exchangeability proof. All 22 categories remain in random partitions including the unidentified category, so sensitivity is required.

### Frozen sensitivity
1. Exclude exactly `Not_identified` source counts, leaving **21 named genera** split into 12 original literature-food versus the remaining 9. Compare F+O vs one named-only total, using identical 7 original source blocks. This asks if the result depends on unidentified plant entries.
2. Repeat the observed publisher-defined F+O vs pooled-total contrast on **29 L3–L8-only sites/6 whole withheld bands**, no PO sites, but do not change the random partition primary definition or denominator after opening the results.
3. Record model fitting failures as explicit STOP; do not silently replace failed draws or seek extra random seeds. Keep all 199 draws in a local/private audit; publish only summary statistics and original source SHA.

### Claim gating
If arbitrary 12/10 partitions frequently match the publisher 12/10 split, **the composition-vs-total signal may be real within the source, but evidence for the *literature-defined food identity* is not established**. If the published split outperforms random splits, the evidence is still source-internal exploratory; plant category correlates with unmeasured vegetation structure, plot design and mist-net detection. Neither result identifies observed plant consumption, causal selection, external spatial transfer or the real individual bat resource-conditioned height model. 2018 original study prior art must be acknowledged.

### Output
`ducke_plant_partition_randomization_v4.py` for local authorized source run and `test_ducke_plant_partition_randomization_v4.py` source-free synthetic checks; source-only aggregate output `ducke_plant_partition_v4_aggregate.json` after execution. No original geographic coordinates, animal IDs, or per-plot food values committed.