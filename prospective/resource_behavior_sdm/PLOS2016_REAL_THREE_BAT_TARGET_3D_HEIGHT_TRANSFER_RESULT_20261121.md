# PLOS 2016 publisher-original 3D flight: post-gate three paired bats, exploratory heldout transfer

Date: 2026-11-21. **REAL original-author PLOS S1 numerical XYZ was opened and analyzed in the GitHub Actions runner, only after the separate exploratory protocol was committed and source-free tests passed.** Original 5-bat paired target claim remains STRUCTURAL STOP. This is not Goldshtein, not wild resource-abundance data, not a validated 3D species SDM, and not a confirmatory population study.

## Original source and provenance

Original publication: PLOS ONE (2016) DOI [10.1371/journal.pone.0163492](https://doi.org/10.1371/journal.pone.0163492); exact publisher supplement [10.1371/journal.pone.0163492.s001](https://doi.org/10.1371/journal.pone.0163492.s001), SHA256:

    3cce76e3f75c1eb49ac1a8344880a42da1de163886372a944080e074cdd1fb42

GitHub [original data run #44903000259](https://github.com/zuizui0223/batter/actions/runs/44903000259); only source-redacted output was retained as artifact **14706433264**, name *plos2016-three-paired-bats-postgate-exploratory*. Source original XLSX, XYZ, target labels and animal IDs were not committed.

**Before any numeric XYZ was opened**, the new protocol [PLOS2016_EXPLORATORY_THREE_PAIRED_BATS_HEIGHT_TRANSFER_FROZEN_20261121.md](PLOS2016_EXPLORATORY_THREE_PAIRED_BATS_HEIGHT_TRANSFER_FROZEN_20261121.md) was committed, preserving the earlier failed 5-bat **30-trial** paired design as STOP and defining a *new*, explicitly post-failure exploratory estimand among 3 genuinely paired animals. New source-free synthetic XML and grouped-CV tests passed before the original dataset job began.

## Source-supported sample: no fake five-bat replication

- Source label-only support: **5 bats, 2 source target categories, 30 trial sequences and 3,226 rows** in full original supplement, but only **8/10 bat×target cells** existed, so the original **five-bat fully paired** validation remains ineligible.
- New exploratory source-valid subset: **3 complete target-paired bats, 24 independent trial sequences, 2,671 recorded 3D positions** (each heldout bat contributes 8 trials). Whole-bat folds hold out 866, 904 and 901 observed frames, respectively.
- Source numeric A/B/C measured relative to experimental target: X/Y relative horizontal coordinates, Z relative target; **NOT above-ground/sea-level bat altitude**. The source column D *Distance toT* contains Z and is never used as an independent predictor.
- Per training fold: weighted training quantiles define 3 XY radial bins and 5 Z bins. Baseline conditional Z distribution uses radial bin; augmented model uses radial bin plus original target class. Each training bat-target is equally weighted across trials and within-trial frames; fixed Jeffreys 0.5 smoothing. The heldout score uses the identical Z-bin target on both models, aggregate per trial → per target → per whole bat. No heldout bat parameters fitted.
- Negative controls swap **entire training-bat target labels**, 2²=4 possibilities per fold; all are descriptive rather than independent confirmatory null trials. Real target labels remain in test.
- 3 bat groups determine inferential granularity, not the 2,671 3D frames. Exact one-sided paired bat signflip p cannot reach 0.05 (minimum 1/8=0.125), even if all had positive effects.

## Real out-of-bat exploratory heldout results

Primary response is **target-relative height class** conditioned on distance from the target. Outcome is *heldout target-aware minus target-blind* log score (nats per recorded frame).

| Anonymous heldout whole bat | Observed 3D frames | Eligible trials | Added target-label heldout Δ log score |
|---|---:|---:|---:|
| Fold 1 | 866 | 8 | **−0.01874458** |
| Fold 2 | 904 | 8 | **−0.04002345** |
| Fold 3 | 901 | 8 | **−0.03035355** |
| **Equal-bat mean** | **2,671** | **24** | **−0.02970719** |

All **0/3** bat folds improve in log score when the experimental target category is added. This is an exploratory **predictive failure** for this binned learning rule, not evidence that bats physically ignore the target, that individual specialization is caused by memory, that continuous height has no target response, or that nectar/plant distributions have no effects in nature. The original paper's target-specific flight patterns remain prior art and were not disputed by this model comparison.

The frozen training-whole-bat label-swap negative control outputs were:
- Fold 1 original −0.018745; 1-bat-swaps −0.081173/−0.033340; 2-bat-swap −0.092404.
- Fold 2 original −0.040023; 1-bat-swaps −0.019518/−0.019555; 2-bat-swap −0.016762.
- Fold 3 original −0.030354; 1-bat-swaps −0.020616/−0.075610; 2-bat-swap −0.068933.

The nonuniform rank of the original-label fit among these four possibilities varies by fold. Do not treat the 12 folds/shuffles as 12 independent biological units, or compute a 0.05 significance claim from them.

## Ecological interpretation and boundaries

A priori testable question was not "Do flower targets alter bats' 3D flight?"—original literature already showed these kinds of differences. It was: **Does the target category add information for predicting target-relative flight height in a bat not used to train the relationship?** Under this new, post-support-failure exploratory design, it did **not**: the binned predictor transferred less well than target-blind height prediction across all three eligible animals.

The failure could reflect different bat-level responses, weak generalizable category effect, trial layout, unequal conditions and timing, small training population, coarse height/radius bins, or strong shrinkage. It cannot distinguish these mechanisms from 3 subjects. It does not justify tuning bins, smoothing, exclusions, or target recoding on this same opened response and then promoting a positive result. Treat this as **ceiling for this frozen exploratory protocol**. Sensitivity analyses after response opening must be separately designated post-hoc and not used to restore confirmatory claim.

This study contains **no local plant flower-abundance map, no regional SDM occupancy, no height-verified individual GPS from the wild**. The independent Goldshtein 2020 same-night flower×GPS+AGL join remains inaccessible (official Mendeley metadata gate HTTP401). Thus **no true wild resource-conditioned M2−M1 or M3−M2** has been estimated in the broader higher-dimensional SDM project.

## Source boundaries / next decisions

This PLOS original exercise supplies a small genuine **controlled-experimental target×3D height transfer constraint**, not a resource×height positive signal. Better next evidence would be a field dataset with matched bat-night resource survey, repeated individuals, independent height calibration and independent behavioral-state labels. Hermans et al. (2023) 3D bat×LiDAR DataverseNL DOI [10.34894/CHW0HB](https://doi.org/10.34894/CHW0HB) has public file *metadata* (including raw 3D height/error and LiDAR files) but **all nine files are restricted** on DataverseNL V2; an authorized access request is required. It is habitat structure, not measured food. Do not bypass restricted access. Frozen JAE/BE, batter main and esdm main remain untouched; keep PR #102 DRAFT.
