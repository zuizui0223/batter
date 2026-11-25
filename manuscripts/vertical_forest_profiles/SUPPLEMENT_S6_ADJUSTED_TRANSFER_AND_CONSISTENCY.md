# Supplement S6. Adjusted baseline consistency and simultaneous provider/block holdout

26 November 2026 JST. Two targeted post-pilot sensitivity tests, with their designs frozen before the new adjusted scores. Same four baseline families and R50 augmentation as Supplement S5, no new covariate or model selection. Neither test is independent regional replication. Original 10-m DLT and 20-taxon/PAVD SDM gates remain nonadmitted.

## Fixed GBIF snapshot A

The original A cohort was reconstructed exactly, with 9,705 screened records, 2,826 species-cells, 14 taxa, 1,763 candidate cells, 1,685 pair groups, 34,350 comparisons, 50 blocks and 42 comparison providers (1,501 actual endpoint cells). The original five geographic folds each contain 10 blocks. We reused identical covariates for the 1,635 common cells and extracted the remaining 128 cells from the same LC100 raster and DSM source. The LC100 full SHA256 matched the previously verified source, and all 51 previously read terrain tiles among 65 required tiles were byte-hash matched (14 newly read tiles). All candidate cells had complete support; no pairs were lost. Original baseline and R50 scores reproduced to the frozen tolerance. Forty optimization fits converged.

| Baseline | Without R50 | With R50 | Increment | Positive folds/intersections | Positive blocks | Conditional 95% bootstrap range | Delete-one-block means |
|---|---:|---:|---:|---:|---:|---|---|
| B | -0.67341772 | -0.66357494 | +0.00984277 | 5/5 | 32/50 | 0.00366356 to 0.01620130 | 0.00838549 to 0.01133156 |
| T | -0.67178950 | -0.66246246 | +0.00932704 | 5/5 | 32/50 | 0.00341490 to 0.01535312 | 0.00802574 to 0.01074653 |
| L | -0.68497660 | -0.67496688 | +0.01000972 | 5/5 | 33/50 | 0.00393187 to 0.01666423 | 0.00796172 to 0.01133173 |
| TL | -0.68354906 | -0.67396146 | +0.00958760 | 5/5 | 32/50 | 0.00376762 to 0.01592175 | 0.00769729 to 0.01084451 |

The adjusted profile increment is 0.00958760, retaining 97.41% of the original R50 increment. The full adjusted model is **not** the best absolute predictor: TL−B = -0.01013134, and TL+R50 minus B+R50 = -0.01038652. Thus a positive conditional increment is not proof that the expanded model as a whole improves forecasting. Forty-seven of the 50 blocks overlap the earlier pilot; these are overlapping consistency tests, not independently sampled experiments.

## Simultaneous source and block holdout

Reconstructed the original 31,601 capped comparisons from the pilot and the exact 15 supported source×block intersections. Each training partition excludes all observations belonging to both the held-out source fold and the held-out geographic fold. The original 29,247 scored comparisons (92.55%), 48 blocks and 30 contributing test providers were retained, with no new support-based selection; all 120 optimization fits converged. All original intersection-specific scores and original aggregate B/B+R50 reproduced to the predeclared tolerance.

| Baseline | Without R50 | With R50 | Increment | Positive folds/intersections | Positive blocks | Conditional 95% bootstrap range | Delete-one-block means |
|---|---:|---:|---:|---:|---:|---|---|
| B | -0.65701453 | -0.64404559 | +0.01296894 | 15/15 | 34/48 | 0.00752337 to 0.01874264 | 0.01150093 to 0.01355813 |
| T | -0.64876220 | -0.63792445 | +0.01083775 | 15/15 | 35/48 | 0.00613462 to 0.01583238 | 0.00960475 to 0.01140237 |
| L | -0.64879701 | -0.63941820 | +0.00937881 | 14/15 | 33/48 | 0.00547322 to 0.01346680 | 0.00870289 to 0.00987791 |
| TL | -0.64208225 | -0.63378586 | +0.00829639 | 14/15 | 33/48 | 0.00469351 to 0.01208132 | 0.00760146 to 0.00877769 |

TL+R50 minus TL = 0.00829639; 63.97% of the original increment remains. One intersection has a negative adjusted increment and is retained. The full adjusted model also improves absolute score over the original profile model by 0.01025973. This is a held-out provider-and-geography robustness diagnostic within the same original archive, not external validation.

## Inference and reproducibility

Conditional block-bootstrap intervals are descriptive, holding fitted predictions fixed; the delete-one range is a sensitivity to any one block. Neither is an independent-study confidence interval. The alternative LC100 class-area fractions and DSM topography proxies are not the original DLT leaf fractions or bare-earth terrain. The observation process, correlated remote-sensing variables, roosting/accessibility and residual confounding remain unresolved. The relative increments, including their attenuation, do not isolate causal structure effects or prove transferable biological habitat preference.

Frozen protocols: [fixed A](../../prospective/gedi_trait_macro_sdm/FIXED_SNAPSHOT_ADJUSTED_BASELINE_CONTRACT_V1.md), [strict holdout](../../prospective/gedi_trait_macro_sdm/ADJUSTED_SOURCE_BLOCK_HOLDOUT_CONTRACT_V1.md). Results: [fixed A receipt](../../prospective/gedi_trait_macro_sdm/FIXED_SNAPSHOT_ADJUSTED_BASELINE_RECEIPT_V1.json), [strict holdout receipt](../../prospective/gedi_trait_macro_sdm/ADJUSTED_SOURCE_BLOCK_HOLDOUT_RECEIPT_V1.json). Runs 45714546886 and 45714736537. All runner checks, original-score replays and registered upload digests passed; output ZIP bytes not independently rehashed in this review. These analyses are outside the earlier four-model core replay. No further tuning, no calibrated 3D distribution claim.
