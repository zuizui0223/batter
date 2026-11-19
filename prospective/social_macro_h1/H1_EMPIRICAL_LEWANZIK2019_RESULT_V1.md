# H1 observed-data reanalysis: source recovered, incremental interaction NOT supported (2026-11-19)

**Status: Empirical single-source audit, not a global bat macro-comparative effect.** Source recovery and results do not amend the frozen JAE batter manuscript or the original authors' findings. This prospective branch remains in draft PR #101.

## 1. Exact input provenance and QA

The user supplied the original Dryad v20190410 ZIP for [Lewanzik, Sundaramurthy & Goerlitz (2019)](https://doi.org/10.1111/1365-2656.12989), dataset [10.5061/dryad.gp65g2t](https://doi.org/10.5061/dryad.gp65g2t). Source XLSX `Lewanzik_etal_2019_JAE_DATA.xlsx` SHA256 **fbabb5021c613aa7033ad13bc1a357a68700a7d3683ec16ae1bcf4a65e121c86**; ZIP SHA256 **903fa69ed15110322c37805bbf609f3704e84306a0319111c389742a2ece86cf**. These are the actual bytes opened, unlike the previously blocked automated download, which remains a valid historical 401/403 audit.

Original workbook validated using artifact_tool: one sheet, **1,440 observations, 12 columns, no missing entries**; 12 lakes × 6 caller species × 5 buzz contents × 4 recipient species/groups; within each lake all 30 randomized playback combinations present. Source's `playback_minus_pre.playback` matches exactly. The author's published exclusion of cases with pre=0 AND during=0 yields 250 *Myotis daubentonii*, 94 NEV (pooled Nyctalus/Eptesicus/Vespertilio), 110 *Pipistrellus nathusii*, 180 *P. pipistrellus*: exact published counts. *P. nathusii* is entirely absent pre/during/post from **Maistaettenweiher_Paehl**, matching paper's statement of one site absent; structurally exclude that lake from its recipient-specific H1 evaluation (330 rows, 11 lakes). Other groups: 360 rows, 12 lakes.

No original raw XLSX or row-level bat observations are committed to the repository. Source file checksum and grouped results only.

## 2. Primary frozen H1 contrast

For each recipient group separately, we fitted **log1p(actual playback bat-seconds/min)** as response, standardised log1p(pre-playback conspecific activity) and minutes after sunset, buzz ordinal (0, 12, 24, 48, 96 remapped as 0..1), caller identity, buzz×caller, **buzz×pre-activity**, and a flag for other recipient groups active in the *pre*-playback minute. Site-fixed-effects were used for in-sample coefficient estimates with lake-cluster robust SE and t reference df=11 (Pnat df=10). The pre-period covariate is not an experimental manipulation of competition.

Incremental predictive value of `buzz×pre-activity` was measured with **leave-one-lake-out** prediction comparing models with/without that interaction. Train-fold-only standardization, no unavailable held-out site intercept, Gaussian log-score on transformed activity, lake-equal averaging. We retained all randomized treatment conditions without conditioning admission on the response `Y_playback`, except for the structurally absent Pnat lake.

| Recipient | n | independent lakes | β interaction (log1p response) | cluster-robust 95% CI | exploratory p | equal-lake Δ log score | lakes improved |
|---|---:|---:|---:|---|---:|---:|---:|
| *M. daubentonii* (`Myotis`) | 360 | 12 | -0.013318 | [-0.207942, +0.181306] | 0.883012 | **-0.00119484** | 3/12 |
| NEV pooled genera | 360 | 12 | +0.108547 | [-0.123370, +0.340464] | 0.325056 | **-0.00171772** | 7/12 |
| *P. nathusii* | 330 | 11 | +0.033968 | [-0.203182, +0.271117] | 0.756184 | **-0.00309600** | 1/11 |
| *P. pipistrellus* | 360 | 12 | -0.023004 | [-0.313932, +0.267924] | 0.864999 | **-0.00308932** | 1/12 |

**Primary decision: no positive independently held-out lake-level predictive increment** for the new linear buzz×pre-activity moderator in any of the four measured response groups. All coefficient intervals include zero. This is neither an equivalence test nor evidence that bats do not eavesdrop; the original 2019 experiment already reported caller-specific and buzz-rate responses.

For NEV, raw pre-activity 25th and 75th percentiles are BOTH zero in the full recipient data: the prior low-versus-high quartile contrast is structurally uninformative for that group, even if its regression coefficient can be estimated from the rarer high-pre records.

## 3. Source-faithful/functional sensitivities (do not switch primary after outcomes)

| Recipient | Quadratic buzz×caller nuisance: held-out Δ score | Published original outcome-conditioned pre+playback>0 filter n | Δ score after original filter | Positive lakes filtered |
|---|---:|---:|---:|---:|
| *M. daubentonii* | -0.00113618 | 250 | -0.00219549 | 4/12 |
| NEV pooled | -0.00063200 | 94 | -0.01048413 | 2/12 |
| *P. nathusii* | -0.00299257 | 110 | **+0.00626978** | 9/11 |
| *P. pipistrellus* | -0.00342574 | 180 | -0.00585156 | 4/12 |

Quadratic (source-paper buzz²×caller) sensitivity leaves all four mean held-out gains negative. The published authors' source-filter condition depends on the actual playback outcome `Y`: conditioning on it can select observed positive activities, distort randomized treatment contrasts and cause sample-specific model performance. The apparently positive Pnat filter-only CV therefore does NOT rescue the primary claim and requires independent replication if used as a new estimand.

Exploratory negative-binomial GLM sensitivities had source-dependent instability/nonconvergence in several low-activity groups. We do **not** promote them as confirmatory evidence; a more complex specification cannot be chosen post-outcome to rescue H1. Inference is constrained by 12 lakes from one geographical study, individual bat identities unavailable, many zero counts, and correlated leave-one-lake-out training folds.

## 4. Scientific conclusion and next admissible work

The simple hypothesis **"pre-playback conspecific activity consistently modulates the value of feeding-buzz content in a way that generalizes to another lake"** was not supported by the newly tested increment in this experimental archive. No universal species-independent tradeoff of personal and social information, reciprocity, actual density manipulation, memory attribution, or 3D individual niche mechanism is identified.

A positive result from some later novel study must be evaluated with a new study-level holdout and harmonized outcomes. Here we **STOP outcome-driven respecification of this same source**, retaining it as a transparent negative/boundary case.

To reproduce, obtain original XLSX from the DOI, validate the SHA, and run the source-pinned script in this PR (or the complete standalone analysis bundle returned in this conversation). The file is intentionally NOT redistributed in this PR.
