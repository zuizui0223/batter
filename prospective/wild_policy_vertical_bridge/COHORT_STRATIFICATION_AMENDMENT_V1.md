# Cohort-stratification amendment v1

## Status

**FROZEN BEFORE STRUCTURAL PREFLIGHT AND BEFORE ANY VERTICAL BRIDGE OUTCOME.**

Parent:
`BRIDGE_CONTRACT_V1.md`

## Rule

All individual comparisons are cohort-stratified.

### Policy standardization

Within each panel × reciprocal fold:
- z-score the five session-level horizontal policy features **separately within each source cohort** using only policy-side sessions from that cohort.

### Individual identity

Use biological key:
`cohort::individual`.

### Pair construction

Construct policy/vertical pairs only between individuals belonging to the **same cohort**.

Never calculate a policy distance or vertical divergence across cohorts.

### Panel statistic

After cohort-local pair distances are constructed:
- concatenate all eligible within-cohort pairs in the panel;
- compute the panel Spearman rho on that concatenated set.

Thus each pair remains on a cohort-standardized policy scale and no cross-cohort distance is introduced.

### Null

Permute complete individual policy labels **within cohort**.

Use the same within-cohort permutation in the two reciprocal folds.

Do not permute labels across cohorts.

## Rationale

The source JAE architecture treats cohorts as distinct exchangeability units. The bridge preserves that structure and avoids interpreting cohort/year differences as personal policy differences.
