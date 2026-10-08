# PR #79 target-blind scalar forecast: synthetic exchangeability stress test (risk only)

## Status
**METHOD SENSITIVITY, NOT AN EMPIRICAL RE-TEST.** This note does **not** reopen the pre-existing 45 *Rhinolophus nippon* trajectories, change the target-blind result, alter the 0.0003 conditional permutation statistic, or diagnose its exact Type-I error. No original bat outcome/feature files were fetched in this audit.

## Why the concern is transferable in principle

The executed #79 forecast result reports `G=+0.443714` for training-only-reference personal-history prediction and a one-sided p=0.0003 from independently permuted identity labels **within observed configurations**. That conditional label test presumes that observed bat feature centroids are **label exchangeable** under its chosen null. If bats differ in stable *residual/noise variance* but have no stable mean policy, unconditional label permutations can change the implied variance profile of artificial matched individuals. An apparently better match can then arise from nuisance variance structure without learned policy or repeatable individual means.

This is a **possible identifiability/calibration failure**, not a finding that the observed #79 effect is false. The #79 bat-cluster confidence interval already crosses zero, so generality was never confirmed.

## Synthetic simplified target-blind analog

To establish whether the concern persists beyond the two-occasion covariance toy, a separate JavaScript simulation used:
- 5 **fictional** bats A–E, in 7 configurations with counts A5/B4/C5/D6/E5 = 25 occupied bat×environment cells; configuration membership is **fabricated** and not the published exact occupancy matrix.
- One simulated scalar observation per bat×environment; this is a **1-D analog**, NOT the published four-feature, 45-trajectory estimator.
- For each target environment e, fit z-score mean and SD using all other environments only; predict focal standardized scalar from other configurations of the bat; compare to a training-only zero baseline. Weight targets equally within bat, and bats equally.
- Exactly the same within-environment observed-ID permutation *structure*, with 199 Monte Carlo label permutations per synthetic data draw, for one-sided `p<=.05`.
- Data generator: `y_ie = sigma_i * iid N(0,1)` with zero persistent bat mean or policy, no stable bat×environment reaction norm, and context effects absent.

Illustrative independent synthetic runs:
| Condition | Simulated archive replications | Empirical false-positive rate at nominal 5% |
|:--|--:|--:|
| Equal sigma=[1,1,1,1,1] | 600 | **4.67%** |
| Unequal sigma=[0.3,0.6,1.2,2.5,5] | 600 | **14.0%** |
| Unequal sigma, second independent RNG seed | 600 | **16.0%** |

The mean observed G under both nulls remained **negative**; false positives arise from the **conditional reference null**, not a fabricated average positive effect. The reported false-positive rates are model-specific and cannot be transplanted as a correction factor for the real p=0.0003 or as evidence that the real data have this exact variance structure.

## What is and is not challenged

1. The **numerically observed** personal-history gain in the 5-bat archive is unchanged.
2. The **interpretation** of its label-permutation p as robust to realistic bat-specific heteroscedasticity remains **unvalidated**. It should continue to be reported specifically as conditional upon identity-label exchangeability, not as a general-population causal discovery.
3. A preregistered variance-aware inference would require `sigma_i` and task/bat/configuration structure from independent training or pilot samples, explicit misspecification and measurement calibration, and an untouched new evaluation cohort/occasion. Retrofitting a favorable sensitivity model from the same outcome-exposed five bats is **not** independent confirmation.
4. A simple two-occasion corrected oracle with known sigmas [see `KNOWN_SIGMA_GAUSSIAN_NULL_ORACLE_V3.md`] does **not** directly solve the leave-configuration-out 4-feature G-statistic; the null and missingness structure differ.
5. Do not conflate within-archive label correspondence with whole 3-D trajectory prediction, personal learned memory, adaptive foraging benefit, or individualized fitness outcomes.

## Decision

**NO RECLASSIFICATION OF #79.** Add `UNTESTED_HETEROSCEDASTIC_LABEL_EXCHANGEABILITY` as an explicit inferential caveat. Continue the public-data source search only for independently crossed bat×challenge×occasion datasets, otherwise stop; no same-source numerical endpoint rescue.
