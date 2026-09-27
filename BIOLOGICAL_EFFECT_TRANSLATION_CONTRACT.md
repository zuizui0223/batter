# Biological effect translation v1 — frozen definitions

Frozen: 2026-09-27

These quantities translate the already-calibrated vertical-identity results into magnitudes that
are easier to interpret biologically. They do **not** create new significance tests.

## 1. Likelihood multiplier

For each panel report:

`exp(common-cell marginal identity)`

and

`exp(common-cell marginal identity - permutation-null mean)`.

The first is the observed geometric per-fix self-versus-other likelihood multiplier under common
horizontal weights. The second puts the finite-sample null correction on the same multiplicative
scale.

The calibrated multiplier is not described as a literal biological odds ratio.

## 2. Entropy-equivalent fraction

On the exact target fixes used for scoring, calculate empirical Shannon entropy of the vertical
bins. Average sessions within individuals and individuals equally.

Report:

`(observed common-cell marginal - null mean) / target vertical entropy`.

This says how large the calibrated identity signal is relative to the target's vertical-state
uncertainty. It is **not** mutual information or variance explained and is not forced into 0–1.

## 3. Pairwise self-identification

For every target session, compare the same bat against each alternative bat in the same cohort.

Both candidate vertical profiles are integrated using identical self cell-use weights on common
supported cells. A comparison is a self win when the held-out target has higher mean log
probability under its own bat's profile.

Report equal-individual self-win fraction and a 20,000-replicate individual-bootstrap 95%
interval. Fifty percent is shown only as an intuitive chance reference; no new p-value gate is
introduced.

## 4. Meter-scale focal effect

Only for *Tadarida* AGL, report the common-cell-weighted absolute difference between the same-bat
and other-bat expected mean AGL, in metres.

This is a descriptive mean-height separation and does not capture distribution-shape identity.

## Rules

- no new inferential threshold;
- no panel ranking;
- no cross-datum meter comparison;
- no cherry-picking among these four predeclared effect translations.
