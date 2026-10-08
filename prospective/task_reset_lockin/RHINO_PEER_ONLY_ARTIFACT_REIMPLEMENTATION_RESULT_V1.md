# Peer-only reference audit — local archived-feature result v1

## Provenance and evidence status
**POST-OUTCOME SENSITIVITY**, not an independent confirmatory analysis. The numeric endpoint was computed from the same 45 already validated movement-feature rows archived in:

- GitHub Actions run `37205598790`, artifact `11304089545`;
- source ZIP SHA256 `d6d3d3e8baa08c0417b77b0b32334859285200ae1a8b3e42c87f0aaee8e60b88` (matches frozen source receipt);
- original article Figshare 29209493, *Rhinolophus nippon*.

This is an independent local reimplementation of the prewritten `RHINO_PEER_ONLY_STANDARDIZATION_CONTRACT_V1.md`, using the preserved derived **trajectory-level features** rather than redownloading the 45 raw tracks. Its GitHub Actions workflow was queued when the local calculation completed. Its result must be reconciled with the eventual authoritative Actions artifact; do not claim the queued workflow succeeded.

## Structural and source reproduction
- Five bats (A–E), seven configurations, 45 trajectories, 25 biological bat×configuration centroids.
- Env7 has only bats A and B and exactly one trajectory per bat; the inclusive 4-feature centroid values are `A=+0.70710678`, `B=-0.70710678`. These values arise from the two-observation, sample-SD-standardized reference and should not be treated as a precise quantitative separation.
- The target-excluded peer-reference fixed gate requires >=3 distinct bats per configuration: six configurations, **23 cells**; all eligible bat-specific histories retain >=3 distinct configurations.
- Original all-trial within-configuration baseline reproduced exactly from 45 source features:
  - `G=+0.2930716924`
  - `MSE_zero=0.6339736814`
  - `MSE_self=0.3409019890`
  - `R²=0.462277`.

## Frozen matched support control (inclusive scaling, 23 cells)
- `G=+0.408302`
- `MSE_zero=0.657282`
- `MSE_self=0.248980`
- `R²=0.621198`.
- Per-bat G: A=+1.306063, B=+0.185738, C=−0.219724, D=+0.615213, E=+0.154219.

In the independent local matched-support sensitivity, the within-environment correspondence p was 0.0006, with five-bat bootstrap G 95% interval [+0.010946, +0.891553]. This remains transductive (the focal animal contributed to the target normalization). The change is due partly to removing the two-observation Env7, not an ecological treatment.

## Predeclared peer-only scaling, 23 cells
For each target bat×configuration, the feature mean and SD are estimated only from **other bats in that same configuration**. No observation of the focal animal contributes to either value.

| Score | Value |
|---|---:|
| MSE zero-peer-reference | 24.027995 |
| MSE own-history | 17.731405 |
| G | **+6.296590** |
| R² | **0.262052** |
| permutation p (19,999, seed 20261008121) | **0.00545** |
| null 95% interval | [−9.600058, +2.696076] |
| bat-cluster 95% interval for G (9,999, seed 20261008122) | **[−0.004303, +18.087577]** |

Per-bat G: A=+29.7487; B=+0.3086; C=−0.3990; D=+1.5907; E=+0.2339.

Strictly under the predeclared post-outcome rule `G>0 && p<=.05`, the score is marked `SUPPORTED_WITH_PEER_REFERENCE`. **That should not be translated into strong biological generality**: the five-bat bootstrap includes zero and the result is massively scaled by A.

### Serious peer-reference precision limitation
In Env5 and Env6 the focal bat A has **only two peer trajectories** for estimating its SD:

- Env5:A minimum peer-feature SD = **0.011078** and maximum focal |z| = **60.305**;
- Env6:A minimum peer-feature SD = **0.027676** and maximum focal |z| = **23.211**.

No post-hoc trimming, fallback SD, dropping these environments or changing frozen gate is justified. These extreme values show why `G=+6.297` cannot be compared directly with `G=+0.408` as an ecological effect size. Peer-only standardization is technically target-excluded, but locally unstable with only two references.

## Complementary fully target-configuration-blind test
The separately frozen `post-freeze/target-blind-forecast-audit-v1` used **all six other configurations** to fit each fold's reference mean and SD. The independent local feature-level reconstruction gives:
- fully target-blind four-feature G=+0.443714;
- baseline MSE=0.932749, personal-history MSE=0.489035, relative R²=0.475706;
- correspondence p=0.0003 (9,999 permutations);
- bat-bootstrap 95% interval [−0.148938, +1.130310];
- only 3/5 bats have positive absolute gain (A,D,E).

The companion peer-conditioned secondary (training-only SD; contemporaneous peer mean) gives G=+0.748123, R²=0.540700, p=0.0005, bat-bootstrap 95% [−0.224858, +1.794212], also 3/5 positive.

**Current limit:** Evidence within this five-bat archive supports personal flight-intensity correspondence and overall target-blind forecast improvement conditional on this source; it does **not** support a universal reliable bat-specific forecast, unique flight equation, or predicted spatial 3-D path.

See the frozen comparison of distinct prediction estimands in `FORECAST_AUDIT_CROSSWALK_V1.md`.
