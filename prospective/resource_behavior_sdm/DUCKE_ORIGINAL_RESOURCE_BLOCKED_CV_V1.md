# Ducke measured resources × bat guild — original ZIP / exploratory blocked prediction

Research-only, 2026-11-20. Source: user-provided Dryad ZIP, DOI https://doi.org/10.5061/dryad.9rb48c5, pinned ZIP SHA256 55c784e2f7b37987e3657d3ba3d5cf6a41bb3554a11904969d1376c977bcdbce, extracted XLSX SHA256 1fad327f61de4f144a44d1d889726ee8743d4edaf1eae87cdc2d5e2bc86bb9a6. Source file was parsed using artifact_tool; no animal IDs, original site coordinates or original XLSX are committed.

## Source qualification and unexpected data issues

Original 8 worksheets: bat table 1189 rows, two Night_without_capture placeholders, 51 actual species-name labels (publication reports 1138 bats and 52 species), 309 plant rows, 49 insect/terrain plots. 42 bat-table rows dated 2015–2030, including one noncapture placeholder; another 45 rows are March 2014 despite paper's original October 2013–February 2014 collection window. Source dates not repaired. Site label aliases L versus LO and PO1 versus PO_01 are unique one-to-one: 49/49 bat-insect-terrain joins; fruit records available for 48/49 plots. Missing fruit source rows are not zero plants. Paper had 12 potential bat-food genera from Figure 4 but raw plant sheet includes 22 genera. Source vegetation clutter field used by original SEM is not present in uploaded XLSX.

## Strict matched-input design

Use exactly same plot and literal same day 2013-10-01 to 2014-02-28, exclude noncapture markers; retained 46 plots, 103 source plot-nights and 810 captures (573 frugivores). Target is the within-source captured-frugivore guild proportion per plot, not true occupancy. Predictor is the equal-night mean recorded fruiting plants in the 12 original-paper candidate genera; insect mass measured per plot. Site-balanced fractional binomial logistic with L2=0.15, training-only standardization. Baseline terrain elevation + added-riparian sampling-frame indicator (not complete riparian classification) + number of matched nights. Seven full source spatial/design blocks L3–L8 plus PO held out separately; leave-plot-out reported only as sensitivity.

## Executed original-data prediction

Seven-block equal-fold score increments in natural log units: +12 candidate food genera +0.016085 (5/7 blocks positive), +all 22 fruit genera −0.002263, +10 remaining genera +0.012974, +insect mass −0.000442, +food+insect +0.014979. Leave-plot-out food increase +0.007130. Added raw source longitude/latitude controls gives +0.014601 block mean. Removing 459 Carollia captures leaves +0.008523 with 44 sites. Each one-block deletion retains positive overall food effect. 7-block bootstrap descriptive 95% values [0.003578,0.027996] are NOT externally independent confidence intervals.

399 within-block plot-level fruit reassignments yield null mean −0.000267, upper 95th percentile +0.009732 and exploratory Monte Carlo fraction >= observed 0.0225 (+1 correction). This is a source-opened exploratory diagnostic, not a preregistered confirmatory test. The remaining 10 genera also offer some predictive gain, so strict trophic specificity is NOT established. In a separate site-last-day temporal test 36 sites, food gain is +0.004047 with 20/36 positive plots; this does not demonstrate rapid behavioral state switching.

## Claim boundary and next step

Original paper Capaverde et al. 2018, https://doi.org/10.1111/btp.12546, already found elevation and food related to bat assemblage structure. Our addition is source-internal out-of-block prediction, NOT discovery of the food relation, external validation, occupancy SDM, prey choice, 3D height or causal selection. Absence of vegetation clutter in source is an important confound. The independent 5/5 speed-turn within-state identity result from batter remains a distinct original source. A resource-conditional 5D model still requires same-individual resource-time and raw 3D height joins; M3–M1 from NeoBat remains NOT ESTIMATED.

Code: ducke_guild_cv_engine_v1.py is a pure-stdlib plotting-block and leave-one-site-out prediction engine with missing-resource, denominator and data-grain STOPs. Source-derived plot tables and original observation rows are NOT stored in the repo; the uploaded original must be re-imported, IDs canonicalized, exact dates joined, and audited against the frozen SHA before calling the engine.
