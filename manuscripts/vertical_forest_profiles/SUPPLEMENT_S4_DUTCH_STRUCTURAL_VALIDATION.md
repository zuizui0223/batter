# Supplement S4. Independent Dutch structural comparison — full results

26 November 2026 JST. Distinct environmental measurement check; no new bat response fit. Frozen design and engineering correction: [AHN_STRUCTURE_VALIDATION_CONTRACT_V1.md](../../prospective/gedi_trait_macro_sdm/AHN_STRUCTURE_VALIDATION_CONTRACT_V1.md), [AHN4_GRID_GEOMETRY_REPAIR_CONTRACT_V2.md](../../prospective/gedi_trait_macro_sdm/AHN4_GRID_GEOMETRY_REPAIR_CONTRACT_V2.md). Source AHN4 2020–22, DOI 10.5281/zenodo.15261042. All 636 frozen candidate cells retained in matched output, 318 wholly south, 312 wholly north, six latitude-boundary cells. 362 have any valid ALS values.

## Source and geometry audit

| Member | SHA256 | ZIP CRC checked |
|---|---|---|
| brw | `57fdd56f2319093c242f3ceb23c0bbe492d19154aebe6cc960df3ea5c94e364f` | true |
| power | `2ad64705922036c1f565ec2fc50ef36294b745c0799b4a80cc1120b4d9a7411d` | true |
| H50 | `82883f749681380501680ff86c71b51edf85541a87416977e2e246247ce4194b` | true |
| H95 | `155ca0959ed5b99a6a88acec899775799bb51af9649932ab63fc7ec71f593ccc` | true |
| PPR | `1410255cf0bbbc63f33e2e2488603a2f4f927a5edf5535f09534253d05f17b56` | true |

Full mask archive MD5 verified. The 15.6 GB metric archive was selectively read, with member CRC and SHA256 checks, not a full-archive MD5 check. Actual building/road/water mask origin differs by −1074.666 m eastward and −4781.367 m southward from H50, corresponding to fractional 5.334 and 8.633 m offsets modulo 10 m; other layers are aligned within numerical precision. Integrate shared native rectangles without rounding origins, then approximate equal-area aggregation via GDAL average. Seven synthetic checks passed before actual aggregation. There are 177 verified native-window checkpoints, 121,434,259 bytes, manifest SHA256 `207ddd7afec72927ff4f07675f7c970ee97d275c63a6aff570e58a2b4b30eae0`. All matched-cell table SHA256s equal `a8018c854ce85e138f084e66bb4cc60a7560b496aa69f9be748ae5cd5fee8924` in the two completed runs. Source-member hashes, metrics and reported scores agree; no independent ecological replicate is implied.

## Descriptive correlations (all thresholds and regions)

| Common support | Region | Cells | 50-km blocks | R50 vs H50/H95 Pearson | Spearman | R50 vs PPR Pearson | Spearman | RH98 vs H95 Pearson | Spearman |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.5 | all | 298 | 22 | 0.56035405 | 0.44457708 | -0.58508038 | -0.54948057 | 0.66245815 | 0.55382833 |
| 0.5 | south | 103 | 7 | 0.49101268 | 0.44410886 | -0.59861503 | -0.52789615 | 0.64925632 | 0.57191495 |
| 0.5 | north | 194 | 18 | 0.58765329 | 0.42398212 | -0.60396669 | -0.57073628 | 0.66575330 | 0.53543244 |
| 0.7 | all | 58 | 13 | 0.50956871 | 0.48371220 | -0.70056238 | -0.69122397 | 0.76260467 | 0.72598357 |
| 0.7 | south | 22 | 5 | 0.50196906 | 0.45115754 | -0.73517823 | -0.72332016 | 0.72822833 | 0.72557877 |
| 0.7 | north | 36 | 9 | 0.50822726 | 0.49832690 | -0.68688431 | -0.65405405 | 0.77424778 | 0.73359073 |
| 0.9 | all | 10 | 4 | 0.53235324 | 0.55151515 | -0.32163922 | -0.18787879 | 0.51522466 | 0.55151515 |
| 0.9 | south | 5 | 2 | 0.16392327 | 0.10000000 | -0.77234113 | -0.60000000 | -0.08518999 | 0.00000000 |
| 0.9 | north | 5 | 2 | 0.45675110 | 0.20000000 | -0.97994380 | -0.60000000 | 0.93044577 | 0.70000000 |

The 90% side-specific correlations use five cells per side and are extremely weak support for interpretation. The primary 70% subset has no boundary cells; the 50% subset has one boundary cell.

## Spatially blocked incremental structural prediction

| Common support | Evaluation subset (pooled fold models) | Cells | Blocks | Baseline RMSE | Profile RMSE | Baseline−profile RMSE |
|---:|---|---:|---:|---:|---:|---:|
| 0.5 | all | 298 | 22 | 0.04770751 | 0.04596413 | 0.00174338 |
| 0.5 | south | 103 | 7 | 0.05061227 | 0.04972635 | 0.00088592 |
| 0.5 | north | 194 | 18 | 0.04621742 | 0.04395921 | 0.00225822 |
| 0.7 | all | 58 | 13 | 0.05498142 | 0.05628879 | -0.00130737 |
| 0.7 | south | 22 | 5 | Not estimated | Not estimated | INSUFFICIENT_SIDE_SUPPORT |
| 0.7 | north | 36 | 9 | 0.05818642 | 0.05961340 | -0.00142698 |

At 90% there are 10 cells across four blocks; no model admitted. The separate disjoint south-to-north sensitivity at 50% support has 62 train and 194 test cells, RMSE 0.04624085 vs 0.04550079, gain +0.00074006. Primary 70% south-to-north test stopped at 19 training and 36 test cells; the side-specific southern prediction also failed the minimum 30 cells. These are prespecified support failures, not observed negative effects. The 50% sensitivity does not rescue the primary result.

## Scope and reproducibility

Runs [45642146713](https://github.com/zuizui0223/batter/actions/runs/45642146713) and [45642032490](https://github.com/zuizui0223/batter/actions/runs/45642032490). See [complete receipt](../../prospective/gedi_trait_macro_sdm/AHN4_STRUCTURAL_VALIDATION_RECEIPT_V2.json) for artifacts, exact results and nine receipt checks. The observed positive correlations are evidence of structural correspondence, not accuracy of waveform-energy quantiles, plant area density, usable air volume, or actual flight altitude. Primary incremental RMSE is negative, and the support sensitivity changes sample size and composition. Neither national comparison isolates the cause of the failed northern ecological transfer. No additional predictors, mask thresholds or bat model selection were performed.
