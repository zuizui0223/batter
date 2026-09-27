# Cross-panel estimator calibration v1 — frozen before non-Tadarida outputs

Frozen: 2026-09-27

The Tadarida diagnostic showed two material facts before this contract was written:

- the finite-sample null of ordinary G_adv is not zero;
- common horizontal weighting changes the focal marginal/conditional decomposition strongly.

No calibration output from *Eidolon*, *Hypsignathus* or any *Phyllostomus* panel has been opened
before this contract.

## Panels

Exactly five already-frozen non-Tadarida panels are admitted:

- *Eidolon helvum*
- *Hypsignathus monstrosus*
- *Phyllostomus hastatus* 2022
- *P. hastatus* 2023
- *P. hastatus* 2016

No new source may be added.

## Permutation

For each panel and each admitted cohort separately:

- permute whole retained session blocks;
- preserve all x-y-z observations within a session;
- preserve the exact number of sessions assigned to every individual label in that cohort;
- preserve cohort membership and the original cohort participation pattern of labels;
- rerun the same 5-km estimator.

Run **4,999** Monte Carlo permutations per panel using the panel-specific seeds in the JSON
contract.

## Common-cell marginal

Use exactly the Tadarida v1 reweighting rule:

- construct equal-session self cell-frequency weights over cells supported by both conditional
  predictors;
- integrate both self and other P(z|cell) under the same weights;
- score the same held-out target fixes;
- report common-cell marginal identity and
  `G_cond - common-cell marginal`.

## Cross-panel comparison

Do **not** compare raw G_adv signs as biological classes.

For each panel report:

`A_cal = G_adv_common-cell(observed) - mean_null(G_adv_common-cell)`.

Also report the raw common-cell advantage and its individual bootstrap interval.

Evidence that horizontal conditioning contributes beyond the standardized marginal requires:

- calibrated common-cell advantage > 0; and
- one-sided `P(null >= observed) <= 0.05`.

This is a post-freeze calibration rule, not an original confirmatory endpoint.

For *P. hastatus* 2022 the key diagnostic is whether its previously negative architecture is
removed, retained or reversed after common-cell weighting and panel-specific calibration.

## Stop rule

Once any non-Tadarida calibration output is opened, do not change the algorithm, B, seeds,
cohort scope, cell weights, 5-km grid, altitude bins, Jeffreys alpha or eligibility thresholds.

The public source universe remains closed.
