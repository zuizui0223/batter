# Supplement S2. Reproducibility and release boundaries

Version 3, 25 November 2026 JST. This supplement documents the four core recorded-label models and their reproducibility. It is not a new fit, validation on independent biological observations or authorization to redistribute the underlying records.

## S2.1 Authenticated computational inputs

The independent execution run [45601651413](https://github.com/zuizui0223/batter/actions/runs/45601651413) retrieved six original input artifacts and the full original northern report archive, checked their actual ZIP SHA256 digests, and checked original script Git blob hashes before execution. The receipt is [PAPER_CORE_REPLAY_V1_PASS_RECEIPT.json](../../prospective/gedi_trait_macro_sdm/PAPER_CORE_REPLAY_V1_PASS_RECEIPT.json).

| Role | Artifact ID | Verified ZIP SHA256 |
|---|---:|---|
| common_forest | 15007174727 | `a5a08ae265f9729cd0b57f820b88b8440199288749006cb14dd82ee38616cbbb` |
| fixed_environment | 15012939978 | `afca6bf11fe5a75d7638a49de73b2cba1874e75d8cb24ed3f65c28957f25650a` |
| holdout | 15010764600 | `4ce5c239b1ad442d83b4861b899c504e40dfb02bb1a0c5e9ef335a650b34460c` |
| observation | 15012136742 | `053567fa0cc43993aec472a3c5bc966a2c6df5306767e66ff6d65f826a7cf900` |
| traits | 15005261316 | `7ed2df73b812f51f6376590136c79fb5acf42b41395e4e3f68830fb66120b490` |
| physical | 15004406365 | `3866df0cc71e1e5556162d26f9a757b7f31b0edddc339c1105ba7bd47e197408` |
| original_northern_result | 15014832006 | `36447f8b3d4c074c038d28c3fa7916c6274efe61c0b4fca917f38d865c24e02e` |

Execution environment: Python 3.12.16, NumPy 2.5.5, pandas 3.1.1, SciPy 1.18.1. Single-threaded BLAS environment settings are retained in the workflow. All four ecological scripts are unchanged.

## S2.2 Replayed analyses

| Analysis | Original run | Script | Numeric aggregate checks | Largest absolute numeric difference |
|---|---:|---|---:|---:|
| observed_label_sorting | 45591260188 | [observed_label_sorting_v1.py](../../prospective/gedi_trait_macro_sdm/observed_label_sorting_v1.py) | 450 | 0.000000e+0 |
| sorting_transfer_diagnostic | 45593419232 | [sorting_transfer_diagnostic_v1.py](../../prospective/gedi_trait_macro_sdm/sorting_transfer_diagnostic_v1.py) | 578 | 2.032291e-10 |
| fixed_profile_validation | 45599009912 | [fixed_snapshot_profile_validation_v1.py](../../prospective/gedi_trait_macro_sdm/fixed_snapshot_profile_validation_v1.py) | 303 | 3.324241e-11 |
| northern_transfer | 45599153163 | [fixed_northern_transfer_v1.py](../../prospective/gedi_trait_macro_sdm/fixed_northern_transfer_v1.py) | 116 | 1.224840e-11 |

The additional comparison to the digest-verified complete original northern report checked 1277 numeric fields, including the per-species support and pair-level lists that were omitted from the old workflow log. Total: 1,447 aggregate numeric checks plus 1,277 complete-northern-report numeric checks (2,724 checks including overlap). These are audit comparisons, not independent statistical observations. Maximum absolute numeric difference across these comparisons: 8.412667230e-10. The original audit stop and its correction remain visible; the correction changed only the comparator input, not the analyses. Solver stopping details and output serialization hashes are not asserted identical; numerical comparisons have fixed tolerance.

Run [paper_core_replay_v1.py](../../prospective/gedi_trait_macro_sdm/paper_core_replay_v1.py) using the pinned workflow [.github/workflows/gvsm-paper-core-replay.yml](../../.github/workflows/gvsm-paper-core-replay.yml) with access to the recorded GitHub artifacts. The receipt records the original blob IDs. Artifact retention and restricted underlying data mean this is a verified internal replay, not yet a durable public reproduction package. Full raw-source extraction, the upstream multitrait diagnostic and structural validation are outside the scope of this four-analysis replay.

## S2.3 Evidence and remaining release conditions

| Claim or artifact | Status | Boundary |
|---|---|---|
| Within-domain profile increment | Reproduced | Predicts recorded species-label allocation, not absolute occurrence or biological filtering |
| Provider-and-block holdout | Reproduced | Same source archive, supported folds only |
| Fixed-snapshot consistency | Reproduced | Substantial overlap with original archive; not independent replication |
| Novel-block in-domain validation | Stopped by support gate | Four comparisons in three novel test blocks; no fitted result |
| Disjoint northern transfer | Reproduced | No supported positive profile gain; extrapolated structural predictor and changed observation geography are confounded |
| Independent ALS structure validation | Not established at V3 | Primary attempt failed in transport, legacy source timed out after masks, bounded primary repair remains in progress |
| Primary 20-species SDM and 3D utilization | Not admitted | Sixteen taxa meet forest geography support in training latitude; no calibrated effort or altitude-specific responses |

Before external submission: complete authorship and bibliography, verify source version/licence and redistribution terms (including noncommercial records), provide a durable permitted reproduction route, review the two actual SVG figures at publication size, and decide whether the narrower recorded-label research question is the intended submission. A successful computational replay cannot substitute for environmental calibration, detection calibration, or independent in-domain biological data. Preserve negative and stopped tests. Main and earlier papers remain unchanged; no submission authorized.
