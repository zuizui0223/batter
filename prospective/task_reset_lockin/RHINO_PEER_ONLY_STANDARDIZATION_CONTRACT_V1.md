# Rhino target-excluded reference audit v1 — locked before numerical execution

## Status and intent
**Post-outcome data-integrity sensitivity**, not new independent validation, not new mechanistic discovery, and not a rescue analysis for JAE or any frozen primary. The preceding theta-correspondence audit already inspected the outcomes. This audit isolates one additional problem: its within-configuration z-scoring includes the focal bat's **target** movement features in the mean and standard deviation of the reference against which that same bat is predicted.

This branch is separate from `main`, the JAE v0.4 manuscript and the upstream theta-correspondence result. Do not change previous numerical results.

## Source, unit and baseline
- Source: the same fixed 45 feature-valid *Rhinolophus nippon* 3-D trajectories from Figshare article 29209493, through the original `rhino_configuration_identity_primary_v1.py` loader, and the same original first four movement features (median speed, 90th speed, median absolute vertical speed, 90th absolute vertical speed).
- Biological unit: bat (A–E), with bat × obstacle-configuration centroids as target observations. Replicate trials are averaged **within** a cell, never counted as independent bats.
- Leave-one-configuration-out (LOCO) target: predict the focal bat's centroid for configuration e from that same bat's centroids in other eligible configurations. Equal weight per environment within bat, equal bat weight in the overall loss.
- Reference baseline: zero in the relevant configuration-specific standardized space (mean of the peer trial reference). This is a **reference-assisted** forecast, conditional on other bats being observed in the target configuration. It is NOT a fully prospective forecast without contemporaneous reference animals.

## Three locked outputs, in order
**A. Reproduce the prior inclusive-standardization result first.** Recompute all 25 bat×environment centroids, including target in each environment's z-score mean/SD, and check the published result against the original 2026-10-08 theta audit. The G check tolerance is 2e-5 for rounding; expected G=+0.293072, MSE_zero=0.633974, MSE_self=0.340902. If the check fails, STOP before peer-only inference.

**B. Paired-support inclusive reference.** Restrict the original inclusive estimator to exactly the same structurally eligible environments and bats that peer-only standardization permits. This fixes sample-composition differences when comparing the reference systems.

**C. Target-excluded peer-only reference (scientific endpoint).**
For each bat i in configuration e, calculate the feature mean and sample SD (ddof=1) from every feature-valid trajectory of all OTHER bats in e, excluding **all** trajectories of i. For each trajectory of i compute four z-scores using those peer-only mean/SD values, then average first over four features and then over all focal trajectories in the bat × environment cell.

Apply the same target exclusion to the focal bat in every other environment used for its training history. Thus neither the target nor the training centroids are standardized using that bat's own corresponding observations. Do not choose components, weighting, outlier removal or regularization after numerical opening.

## Structural gate, before numerical endpoint output
- Eligible configuration: at least **three distinct bats**, each with feature-valid trajectories.
- For every focal bat in an eligible configuration, its peer reference must contain at least **two other distinct bats** and **two trajectories**; all four peer-only feature sample SDs must be finite and strictly positive.
- Every bat in the retained collection must have **three or more** eligible configurations.
- Global gate requires **five bats** and **at least 18** eligible bat×environment cells.
- If any requirement fails, record the precise structural stop and do not produce the numerical peer-only inference. No fallback to a changed threshold, borrowed SD, deleting selected cells, winsorization or selection based on gain.
- Do not use environment 7 just because a single peer has multiple trajectories if it has fewer than three distinct bats.

## Estimand
For `y[i,e]` denoting an environment-normalized scalar centroid:
- `pred[i,-e] = mean(y[i,f] for eligible f != e)`.
- `G_i = mean_e(y[i,e]**2 - (y[i,e]-pred[i,-e])**2)`.
- `G = mean_i G_i`; `MSE0 = mean_i mean_e y[i,e]**2`; `MSEself = mean_i mean_e (y[i,e]-pred[i,-e])**2`.
- `R2 = 1 - MSEself/MSE0`.

The primary peer-only outcome is `G` with one-sided conditional bat-correspondence calibration. If G > 0 and p <= 0.05, report `SUPPORTED_WITH_PEER_REFERENCE`; otherwise `UNSUPPORTED_WITH_PEER_REFERENCE`. Irrespective of p, report per-bat outcomes, all observed support and all score extremes. This is only an exploratory/post-outcome conclusion.

## Null and uncertainty
- Permute *entire original bat × environment score bundles* among the **observed labels within each configuration**, independently by configuration; retain environment membership, trials per source cell, and the fixed eligibility mask.
- Compute peer-only score bundles BEFORE permutation, each relative to the original physical peers; under relabeling move the precomputed bundle as a unit. This avoids reintroducing focal observations into their own normalization, and keeps the transformation label-symmetric.
- `B=19,999`, RNG seed `20261008121`; one-sided p with +1 correction. Recompute LOCO predictions, G and per-bat gains for every mapping.
- Bat-cluster bootstrap (5 bats, 9,999 replicates, seed `20261008122`) for the G 95% percentile CI. Also five leave-one-bat-out programme gains. Both describe small-n uncertainty; they are NOT population-level confirmatory inference.
- Paired change between peer-only G and inclusive G is descriptive because scales differ; never treat raw delta as an effect size on a common standardized scale.

## Necessary diagnostic interpretation
- The old within-configuration all-bat reference is **transductive**: the held-out bat contributes movement values to the target configuration's scaling.
- The peer-only endpoint removes focal leakage but still requires peer measurements in the target configuration; it cannot predict a bat in a completely new configuration before any bat has been measured there.
- Randomization can establish that observed bat correspondence exceeds within-archive exchangeability; bat-cluster uncertainty with n=5 may still straddle no gain.
- No inference about a unique differential equation, memory as cause, optimality, stable personal 3-D route maps, universal two axes, or *Miniopterus* species differences follows from this check.
- Do not rerun this as a source of fresh confirmatory p-values or merge its results into frozen submissions without a separate transparent amendment.
