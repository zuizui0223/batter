# Result — target-configuration-blind rank-two forecast (archived-feature reimplementation)

## Evidence tier
**POST-OUTCOME diagnostic, not independent validation.** This source's 45 validated trajectory features were already used for multiple diagnostics. The contract `RHINO_RANK_TWO_COLD_START_CONTRACT_V1.md` was written before this numeric endpoint was computed; this does not erase earlier outcome exposure.

Input is the already-published feature support artifact, workflow 37205598790, artifact 11304089545, SHA256 `d6d3d3e8baa08c0417b77b0b32334859285200ae1a8b3e42c87f0aaee8e60b88`. No new source filtering, individual exclusion or feature selection.

## Provenance and integrity
- 45 trajectory-level eight-feature arrays; 25 bat×configuration cells, 7 configurations, 5 bats.
- Independent local reimplementation: target environment excluded from **all eight reference means and SDs**, all training bat centroids and SVD.
- The original four-feature inclusive scalar audit was independently reproduced from this exact source: `G=+0.2930716924`, `MSE0=0.6339736814`, `MSEself=0.3409019890`.
- Source archive digest passed; synthetic target-feature perturbation/reference-invariance and all fold structural checks passed.
- Null: 9,999 whole-cell identity permutations, fixed seed 20261008171. Bat bootstrap: 9,999 samples, fixed seed 20261008172.
- Companion GitHub Actions workflows had not completed as of this result memo. Numbers are local archived-feature reimplementation rather than workflow-artifact outputs.

## Nested quantitative 8-feature prediction

| Training-only rank | Held-out equal-bat loss |
|---:|---:|
| 0 | 1.293420026 |
| 1 | 1.072491563 |
| 2 | **1.040582578** |
| 3 | 1.058209743 |
| 4 | 1.060213306 |

- Rank-one gain relative to zero: `L0-L1 = +0.220928463`.
- Frozen primary rank-two increment: `L1-L2 = +0.031908985`.
- Relative rank-two versus rank-one loss decrease: **2.9752%**.
- Frozen rank-two correspondence null: mean and 95% percentile interval `[-0.143025763, +0.094264399]`; **p=0.1215**.
- Bat-cluster 95% interval for increment: **[-0.038914426, +0.087703481]**.

| Bat | Rank-two incremental gain `L1-L2` |
|---|---:|
| A | +0.021735705 |
| B | **−0.096247794** |
| C | +0.046346992 |
| D | +0.115274474 |
| E | +0.072435546 |

Four of five positive. The frozen rule requires `delta>0`, `p<=0.05`, >=4 positive and positive cluster-bootstrap lower bound. The permutation and bootstrap conditions both fail.

**Frozen conclusion: `UNSUPPORTED_COLD_START_SECOND_AXIS_INCREMENT`.**

## Comparison with transductive rank-two forecast
Previous target-configuration-standardized same-endpoint test from `post-freeze/rhino-rank-two-forward-test-v1`, reimplemented independently on the same original archived features:

- 1-D loss 0.736064739; 2-D loss 0.626392841;
- additional 2-D gain +0.109671898; 14.90% relative reduction;
- p=0.0080, 5/5 positive; bat-bootstrap 95% [+0.061301790,+0.175200072].

This original within-configuration normalized endpoint **uses the held-out configuration's own distribution, including the test animal**, when expressing its test features. The cold-start comparison removes all target-configuration feature values from reference fitting.

**Crucial distinction:** The estimates have different feature standardization and therefore different estimands. The changed gain/p is not by itself proof of leakage as the sole biological/statistical cause. Nonetheless, the supported transductive rank-two advantage cannot currently be called a validated fully target-blind rank-two improvement.

## Current biological interpretation
A finite low-dimensional *movement-organization representation* is still consistent with the supported identity results. Its **second coordinate** did not demonstrate added benefit for an entirely new obstacle configuration when target-environment reference data were unavailable.

This separates:
1. stable identity signal;
2. portable forecasting of 4-feature flight intensity (a distinct analysis);
3. incremental 8-feature forecasting from a second learned coordinate;
4. causal or biomechanical determinants of those features;
5. prediction of 3-D trajectory geometry.

No inference here tests (4) or (5). Do not reopen a new within-archive rank search or declare biological intrinsic dimension equal to one or two.

## Important next biological data
Repeated cross-design trajectories for **the same bats under a new obstacle configuration** with controlled, observed task geometry, with all model references trained before seeing the new configuration, would distinguish a portable personal movement strategy from task-specific expression or reference-dependent identification.
