# Carollia turn-conditioned null robustness contract v1

## Status

**POST-OUTCOME EXTERNAL ROBUSTNESS AUDIT.**

Frozen after the fixed two-axis Carollia external primary passed, and before this programme reads source `RESULTS.turns.angleDeg` values.

The purpose is to test whether the external individual-identity result could be explained by unequal exposure of bats to corridor/turn conditions.

## Source design

The peer-reviewed source describes straight, approximately 90-degree, and approximately 180-degree corridor/turn conditions, and uses a 90-degree threshold for shallow versus steep turn analyses.

The public source pipeline stores manually annotated turn angles in:

`RESULTS.turns.angleDeg`.

## Trial-level condition proxy

For each fixed-primary trial:

1. load only finite `RESULTS.turns.angleDeg`;
2. if no finite annotated turn exists:
   `turn_class = no_annotated_turn`;
3. otherwise let `Amax = max(angleDeg)`;
4. if `Amax <= 90`:
   `turn_class = le90`;
5. if `Amax > 90`:
   `turn_class = gt90`.

This rule is frozen before the values are opened.

It is a source-annotation condition proxy, not a claim that every trial corresponds exactly to one physical corridor design.

## R1 — exposure audit

Report by date block and bat:
- number of trials in each turn class;
- Amax for every trial;
- number of annotated turns.

This is descriptive.

## R2 — condition-stratified permutation null

Keep the observed fixed two-axis statistic exactly unchanged:

- same valid trials;
- same date-block standardization;
- same fixed I and M formulas;
- same self/donor identity statistic.

Change **only the permutation null**.

For every permutation:
- shuffle the exact observed bat-label multiset only within each `date × turn_class` stratum;
- never move a trial across date or turn class;
- preserve feature values and class composition exactly.

9,999 permutations.

Seed:
`202610051221`.

Report:
- observed K;
- conditional-null mean and 95% interval;
- one-sided p;
- number of distinct/permutable strata;
- effective number of trials participating in nontrivial shuffles.

## R3 — leave-one-turn-class-out sensitivity

For each turn class that can be removed while preserving:
- >=3 eligible bats per date block;
- >=2 valid trials per retained bat for leave-one-trial self centroids,

remove all trials in that class, restandardize within date block, and recompute the fixed two-axis identity statistic with the ordinary date-block label permutation null.

9,999 permutations per eligible class.

Seeds:
`202610051230 + class_index`, with classes sorted lexicographically.

If removal breaks support, report `STOP_SUPPORT_AFTER_CLASS_REMOVAL`; do not lower thresholds.

## Interpretation

If R2 remains significant:

> the fixed two-axis external signal is not explained by the broad source-annotated shallow/steep/no-turn trial mixture.

If R2 fails:
- the primary external result remains the historical primary;
- but its interpretation as portable individual policy is condition-confounded.

## Ceiling

This audit controls a broad source-annotated turn class only. It does not prove independence from every micro-geometric or luminance difference.
