# Supplement S5. Matched baseline-completeness sensitivity

26 November 2026 JST. Post-pilot challenge frozen before new covariate model scores, not independent biological replication. The original DLT (10 m dominant leaf type) test stopped before acquisition; the 100 m LC100 forest-class analysis is a distinct alternative, not a successful DLT test. No new biological responses or change to the original 20-species SDM admission rule.

## Sources and exact matching

Copernicus GLO-30 surface elevation (public DSM): 220/220 tiles, 1,796/1,796 candidate cells; no missing tile or excess native-area overlap. Two covariates are area-weighted surface elevation mean and within-cell population SD. DSM includes vegetation and other above-ground objects. It is not a bare-earth terrain model. Table SHA256: `0b24b047ad6ce0209b0de93dc3e8fa3aae4c78078d69d40d9a6991530ed65d43`.

LC100 2019 V3.0.1 (DOI 10.5281/zenodo.3939050), whole-landscape fractions from discrete 100 m classifications of broadleaf, needleleaf, mixed and other forest. These are not fractional canopy leaf cover; "other" is retained as a separate class, not assigned a leaf type. Full 1,713,345,228-byte original raster verified against published MD5 `6898fbe3fb46a1110cd65e3a81ed7624`; SHA256 `b2203d6dd8b6918e27cd1413e7dfec4a9e4ce03dbf50f209d7f04c550c23cf53`. All 1,796 candidate cells have valid covariates. Native class masks and area weighting were fixed before model evaluation. LC100 table SHA256 `0712db21f70bb087d21c806fa28bf5dc65eb6463c041b386c125626c0082048b`. No observed labels enter either raster extraction.

The 31,601 original comparisons in 1,626 pair groups and 51 200-km blocks were reconstructed, with 14 taxa, 40 contributing providers and 1,543 actual comparison endpoint cells. Candidate cells and actual endpoint cells differ because capped comparisons do not use every recorded cell. Every original comparison survives; original fold counts and weights retained. Four baseline families and their profile-augmented versions use the original AR-plus-orthogonal-residual baseline parameterization, species-specific R50 slopes, training-only normalization and ridge 0.1. Forty fold-model fits converged. The neutral score is −log(2). Compare each profile model with its own baseline rather than choosing an overall best model.

## Full matched results

| Baseline family | Without R50 | With R50 | Increment | Positive folds | Positive blocks | Conditional test-block bootstrap 95% range | Delete-one-block mean range |
|---|---:|---:|---:|---:|---:|---|---|
| B | -0.66629891 | -0.65190104 | 0.01439786 | 5/5 | 37/51 | 0.00793620 to 0.02158189 | 0.01260101 to 0.01530269 |
| T | -0.66121365 | -0.64837764 | 0.01283601 | 5/5 | 39/51 | 0.00695830 to 0.01933711 | 0.01117187 to 0.01373906 |
| L | -0.66619767 | -0.65471367 | 0.01148400 | 5/5 | 39/51 | 0.00576692 to 0.01860305 | 0.00891550 to 0.01218796 |
| TL | -0.66225540 | -0.65166209 | 0.01059332 | 5/5 | 37/51 | 0.00525608 to 0.01714609 | 0.00823164 to 0.01129947 |

B: original climate, land cover and RH98. T: B + two DSM surface-topography proxies. L: B + four LC100 forest-class area fractions. TL: both sets. Increments are equal-block weighted log-score gains in nats per composite comparison, not coefficients. Conditional test-block bootstrap holds fitted predictions fixed and is not a population-level confidence interval. Each single-block omission mean is positive for TL. The primary predeclared alternative screen passes.

| Original fold | B + R50 − B | T + R50 − T | L + R50 − L | TL + R50 − TL |
|---:|---:|---:|---:|---:|
| 1 | 0.01200316 | 0.01127269 | 0.00890183 | 0.00879843 |
| 2 | 0.01718866 | 0.01460768 | 0.01349878 | 0.01161768 |
| 3 | 0.01189166 | 0.01145726 | 0.00749665 | 0.00773448 |
| 4 | 0.00856512 | 0.00803182 | 0.00764414 | 0.00736429 |
| 5 | 0.02258018 | 0.01896691 | 0.02013685 | 0.01763119 |

The adjusted profile gain retains 73.58% of the original increment; attenuation 26.42% is descriptive, not a mediation estimate. More baseline covariates need not improve the absolute held-out score under fixed shrinkage: TL − T = -0.00104176 and (TL+R50) − (T+R50) = -0.00328445. The full adjusted model is not the best-scoring model. All fixed results are retained.

## Inference boundary and run history

Original DLT + terrain run 45659440994 obtained all terrain data but timed out requesting DLT service metadata. The terrain fit's output serialization stopped on a NumPy scalar; corrected only scalar serialization and re-executed from authenticated prior artifacts, run 45713275711. Its original B and T results re-agree with the LC100 alternative run 45713474572. The alternative was separately frozen before its source extraction and fit (BASELINE_LC100_ALTERNATIVE_CONTRACT_V1.md). See [terrain receipt](../../prospective/gedi_trait_macro_sdm/BASELINE_TERRAIN_DIAGNOSTIC_RECEIPT_V1.json) and [LC100 receipt](../../prospective/gedi_trait_macro_sdm/BASELINE_LC100_ALTERNATIVE_RECEIPT_V1.json) for original source, all model and block results and audit checks. This is outside the earlier four-analysis core replay. The audit inspected registered output digests and successful runner checks; output ZIPs have not been independently rehashed in this turn.

R50 adds predictive information conditional on the observed forest-class and surface-topography proxies. This does not isolate a causal vertical-structure effect, remove all forest composition/terrain/observation confounding, establish transfer to other regions or taxa, or recover flight height. The stricter DLT main challenge remains stopped; direct GEDI PAVD and calibrated biological detection remain unresolved. No post-outcome class regrouping, predictor selection or penalty tuning.
