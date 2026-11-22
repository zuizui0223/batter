# PLOS 2016 real-source secondary 3-bat target-relative altitude: within-trial vs cold-start

2026-11-21, **POST-FIRST-OUTCOME EXPLORATORY**, not preregistered confirmation. Source-independent tests passed before publisher original XYZ opened in this second workflow. This is secondary analysis **of the same source and same three animals**, not independent replication, and not ecological true food availability / wild GPS / 3D SDM.

Original study: Gonzalez-Terrazas et al. (2016), *How Nectar-Feeding Bats Localize their Food: Echolocation Behavior of Leptonycteris yerbabuenae Approaching Cactus Flowers*, PLOS ONE DOI 10.1371/journal.pone.0163492, original S1 DOI 10.1371/journal.pone.0163492.s001. The author's experimentally manipulated conditions were natural cactus flowers (*Pachycereus pringlei*) versus an acrylic hollow hemisphere; the original study reports approach and sonar differences. Our models ask a different question about predictive transfer of **relative target Z** between trials or animals.

## Provenance

Frozen *after first exploratory outcome but before second original-source outcome*: [PLOS2016_SECONDARY_WITHIN_VS_BETWEEN_TRIAL_FROZEN_20261121.md](PLOS2016_SECONDARY_WITHIN_VS_BETWEEN_TRIAL_FROZEN_20261121.md), commit 33a1c761. Real original-run [Actions #44903292033](https://github.com/zuizui0223/batter/actions/runs/44903292033) PASS; artifact **14706388992** retains only anonymized animal-level aggregate outcomes. Author-original SHA256 was again checked:

    3cce76e3f75c1eb49ac1a8344880a42da1de163886372a944080e074cdd1fb42

The prior [3-paired-bat original LOBO result](PLOS2016_REAL_THREE_BAT_TARGET_3D_HEIGHT_TRANSFER_RESULT_20261121.md) had a fully independent branch freeze and same-source 3 eligible paired bats (24 target trial groups, 2,671 3D frames). Its equal-bat leave-animal-out gain was **−0.02970719061394642 nats/frame**, all 3 bat folds negative. This exact value was **recomputed from the new 24 trial fold structure** as −0.029707190613945514, passing a numerical equality gate at 1e−11.

## New secondary within-animal trial holdout

For each of the 24 original trials, hold out the **entire trial** and score the exact heldout Z category among 5 training-only equal-frequency Z bins, conditioned on one of 3 training-only XY radial bins, using identical α=0.5 Jeffreys-smoothed conditional histograms with and without the original target category. Compare:

- **Personal-trial learner:** train only on the 7 other trials by the same bat, including both target classes;
- **Other-bat (cold-start) learner:** train only on 16 trials belonging to the 2 other fully paired bats.

Aggregate heldout trial score → equal source-target category → equal bat. Note the deliberately **different training-set sizes**, 7 vs 16 trials, which make any contrast unsuitable for identifying memory, learning, or pure individual differences. The same 24 actual heldout test trials and original response observations are used for both methods. Numeric XYZ and animal keys exist only in the Actions runner; no source rows, trial IDs, raw coordinates, original file, or human-linked animal IDs leave the original source environment.

### Publisher original results

| Anonymous bat | Personal-trial target increment | Other-bat target increment | Personal minus other-bat increment |
|---|---:|---:|---:|
| 1 | −0.00766249 | −0.01874458 | +0.01108209 |
| 2 | −0.01326314 | −0.04002345 | +0.02676031 |
| 3 | −0.01818177 | −0.03035355 | +0.01217177 |
| **Three bat-equal mean** | **−0.01303580** | **−0.02970719** | **+0.01667139** |

Personal-trial positive **0/3** animal groups, other-bat positive **0/3** groups. The positive *difference* (+0.01667) means target information was **less harmful** in this coarse predictor when trained using the same animal; it **does not mean** target-aware height prediction improved over a target-blind baseline for any bat. A difference between negative increments is not a positive target prediction gain.

## What can be said scientifically

Under two strictly separated source-local exploratory transfer designs, the PLOS 2016 original 3D trajectories **do not support additional heldout target-category height prediction** using this pre-fixed binned radius/height model. This is a genuine negative prediction result, not merely a synthetic counterexample. It does NOT falsify the source publication's observed approach differences, detect nectar use, explain altitude selection from learning or establish population-wide absence of cue effects.

Reasons this small-sample negative can arise include unequal trials/target histories, context dependence, individual flight geometry, coarse 3×5 quantization, and strong shrinkage. With only 3 paired bats, the minimum one-sided exact bat signflip p is 0.125. No source-wide generalization, frequentist 0.05 inference, or species-level 3D distribution inference is possible.

This analysis has now been **closed as a source-specific exploratory ceiling** to prevent iterative redesign after seeing the original outcomes. The earlier five-bat fully paired structural gate remains STOP and may not be represented as having passed. Never turn this controlled acoustic target into measured wild flower availability or a statement about resource causality.

## Relation to higher-dimensional 3D SDM

This original dataset has 3D motion and an experimentally assigned stimulus condition, but lacks independent landscape-scale abundance, repeated same-night nectar availability and valid regional occurrence. It is therefore a **local movement-response / altitude transfer boundary**, not a source for fitting p(occupancy,resource,behavior,AGL,individual). The Goldshtein (2020) published bat/cactus field source remains necessary for resource×3D. Its Mendeley published metadata is public but prior authenticated API returned HTTP 401. Hermans et al. (2023) bat×LiDAR DataverseNL DOI 10.34894/CHW0HB is **restricted for all 9 deposited files**, and independent true food availability is not included. No access restrictions were bypassed.

Source-free tests and exact original-source receipt: [workflow #44903292033](https://github.com/zuizui0223/batter/actions/runs/44903292033). Main/JAE/BE frozen sources and esdm main untouched. Keep Draft PR #102.
