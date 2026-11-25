# Supplement S3. Historical independent northern forest-structure comparison

26 November 2026 JST. Auxiliary environmental-proxy test, not a bat response fit, a calibration of waveform energy, or a north–south test. Original frozen design: [ECODES_DK15_VALIDATION_CONTRACT_V1.md](../../prospective/gedi_trait_macro_sdm/ECODES_DK15_VALIDATION_CONTRACT_V1.md); completed result: [ECODES_DK15_STRUCTURAL_VALIDATION_RECEIPT_V1.json](../../prospective/gedi_trait_macro_sdm/ECODES_DK15_STRUCTURAL_VALIDATION_RECEIPT_V1.json).

## Data provenance and execution

EcoDes-DK15 historical ALS 2014–15, source DOI 10.5281/zenodo.5752926, publication DOI 10.5194/essd-14-823-2022. GVSM 2020. All 909 predefined candidate forest-supported 1-km cells selected before examining ALS values. Six actual 10-m raster layers from five archives; EPSG:25832 native grid. Clipped tiles use actual affine extents, not nominal filenames. The final index reported zero conflicting overlapping pixels. Native mask/data QC and shared-area aggregation are in the versioned analysis script. Each of the five full source archives passed MD5 in both runs. The two runs are repeated computations using the same source, not independent replicates.

| Archive | Published/verified MD5 | Selected member manifest SHA256 |
|---|---|---|
| masks | `994af8e8cdeee5f85ee4aedcdff0b0c3` | `dd53d86978ec102cd289241aaa32928210b01eb76357234ca195cff8d96b9a80` |
| building_proportion | `2b1f149d954d15346fb63b864b5f0525` | `40fd4e13af086510b5e473ece0162f9733d3e5a4c2f7b3ec8204ec4756935540` |
| canopy_height | `0fcbae7de6442800f6815d1951fa5cc6` | `154f14c00e37e242f51c4442674d80e66d3ba76679d60c4473152989d1fc14f6` |
| normalized_z_mean | `3fbbf56ef15a932d63040dd26ef5cbfd` | `903322cb514a4b9e1eba566b46177889de39be87a6e0de200dd5eb17acc90bbb` |
| canopy_openness | `29c230ec59064110b41062881740835c` | `86648d037137f5bd8d3d0633fe6bcb9a226be817c29e2c27e67562e1a7ac5718` |

Matched table SHA256 in both runs: `1a133c3932fd19aed8369c75544fd612bb11a18d06dbe99a3321b8fa1b8e2377`. Source environment hash: `5fc8ae81149ba9436882f3614b6eac8e51c7e79d0d88aa3c5ba15ccc717331e8`. The numerical support comparison checked 39 fields, maximum absolute difference 1.110223e-16.

## Full threshold sensitivity

| Shared valid fraction | n cells | distinct 50-km blocks | Pearson R50 vs ALS mean/P95 | Spearman | Pearson R50 vs ground/water return fraction | Spearman | Pearson RH98 vs vegetation P95 | Spearman |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.50 | 426 | 33 | 0.568053 | 0.565397 | -0.556966 | -0.568335 | 0.784292 | 0.793865 |
| 0.70 | 375 | 31 | 0.497555 | 0.517471 | -0.555086 | -0.560416 | 0.795722 | 0.807784 |
| 0.90 | 277 | 29 | 0.431175 | 0.433520 | -0.529865 | -0.530199 | 0.784701 | 0.794000 |

| Shared valid fraction | Baseline RMSE | Augmented RMSE | Baseline minus augmented RMSE | Blocks with improved mean squared error |
|---:|---:|---:|---:|---:|
| 0.50 | 0.06482410 | 0.05987820 | +0.00494589 | 22/33 |
| 0.70 (primary) | 0.06349077 | 0.05984963 | +0.00364114 | 21/31 |
| 0.90 | 0.06155438 | 0.06274986 | -0.00119548 | 19/29 |

The main 70% common-support result is a descriptive gain of roughly 5.7% in ratio RMSE, and 50% support also yields a gain; 90% does not. The latter evaluates a different subset, not an independent falsification or direct measurement of how prediction varies with data quality. These are not uncertainty intervals. Return-count metrics and the ground/water return fraction differ from waveform-energy RH; the relative-height proxy does not establish vegetation density, an airspace fraction, or bat flight height. The historical comparison offers evidence of environmental correspondence in a northern domain but does not isolate the causes of failed northern bat-label transfer.

## Execution record and remaining validation

Successful runs [45622231502](https://github.com/zuizui0223/batter/actions/runs/45622231502) and [45622202091](https://github.com/zuizui0223/batter/actions/runs/45622202091). Their matched-table hashes are identical; the receipts contain source member manifests and registry digests. Output archive bytes were not separately rehashed in this review. The earlier Danish clipped-raster extent stop is archived separately. The Dutch AHN4 primary comparison has not yet produced structural outcomes; its geometry preflight succeeded but the subsequent hash comparison stopped on a malformed expected digest, not changed source bytes. Corrected execution is registered separately. Do not pool these historical structural comparisons with the observed-label ecological scores. Manuscript V3 remains frozen; V4 adds the historical result and all thresholds, without refitting bat models.
