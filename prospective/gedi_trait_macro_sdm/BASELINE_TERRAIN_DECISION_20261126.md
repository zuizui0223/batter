# Baseline-completeness challenge decision — terrain result, 2026-11-26 JST

Original 14-taxon recorded-label pilot V6 preserved. This is a matched post-pilot sensitivity, not an independent biological replication or a calibrated SDM. The original complete DLT + terrain test remains stopped.

## Completed terrain adjustment

Original run 45659440994 terrain job succeeded: all 220 DSM tiles and 1,796 original recorded cells supported, zero missing tiles or excessive overlap. Exact table SHA256 0b24b047ad6ce0209b0de93dc3e8fa3aae4c78078d69d40d9a6991530ed65d43. DLT metadata connection timed out before any numerical values, and the fitted terrain-only report failed JSON serialization. Corrected only NumPy scalar serialization, then reused both original artifacts and re-executed the fixed estimator in run 45713275711. All 31,601 comparisons, 51 original blocks, 14 contributing taxa and original hash-fold assignments preserved. Actual compared endpoints: 1,543 of 1,796 candidate cells; 40 comparison providers. All 20 fitted fold-model optimizers converged. Original baseline and profile scores re-agree with the previous result.

| Baseline family | Without R50 | With R50 | Increment | Positive folds | Positive blocks |
|---|---:|---:|---:|---:|---:|
| B | -0.66629891 | -0.65190104 | 0.01439786 | 5/5 | 37/51 |
| T (B + mean surface elevation and within-cell SD) | -0.66121365 | -0.64837764 | 0.01283601 | 5/5 | 39/51 |

Neutral score −log(2) = −0.69314718. Terrain-only baseline increment T−B = 0.00508526. Matched R50 increment retains 89.15% of its earlier value; descriptive attenuation 10.85%, not a causal mediation estimate. T+R50−B = 0.01792127. T+R50−T conditional test-block bootstrap range 0.00695830 to 0.01933711, delete-one-block mean range 0.01117187 to 0.01373906. These are descriptive conditional ranges, not independent-pair or population-level confidence intervals. The frozen terrain-only screen passes. See BASELINE_TERRAIN_DIAGNOSTIC_RECEIPT_V1.json for all actual scores, folds and checks.

Interpretation: the measured mean DSM elevation and elevation SD do not remove the original predictive R50 increment. They do not exhaust topography, forest composition or observation confounding. DSM includes surface objects, not true bare-earth elevation. Neither the incremental predictor gain nor its attenuation establishes causal vertical habitat filtering.

## Next bounded test

The DLT primary test has zero leaf-supported cells because the original public numeric service timed out, not because the forest-type ecological effect is absent. The alternative 2019 LC100 discrete forest-class sensitivity was frozen before any alternative raster or model outcomes in BASELINE_LC100_ALTERNATIVE_CONTRACT_V1.md. Four classified forest-area fractions (broadleaf, needleleaf, mixed, other), distinct from 10m DLT canopy leaf fractions, are combined with the original two DSM terrain proxies in the same exact paired sample design. Acquisition/fit run 45713474572. Do not replace or mark the DLT primary test as passed if this alternative succeeds. Do not refit old models repeatedly or optimize source selection based on results. Keep V6 immutable; integrate in a new revision only after verified alternative result. No submission, merge, actual altitude inference or original 20-species gate relaxation.
