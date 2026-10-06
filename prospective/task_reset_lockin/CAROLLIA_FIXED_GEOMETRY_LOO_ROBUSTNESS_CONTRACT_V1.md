# Carollia fixed-geometry exhaustive LOO robustness contract v1

## Status

**POST-OUTCOME ROBUSTNESS AUDIT OF A NEGATIVE EXTERNAL DIAGNOSTIC.**

Parent:
- \`CAROLLIA_FIXED_GEOMETRY_EXTERNAL_CONTRACT_V1.md\`
- \`CAROLLIA_FIXED_GEOMETRY_EXTERNAL_RESULT_V1.md\`

The main fixed-geometry external diagnostic was unsupported:
- K = -0.0350;
- 3/7 bats positive;
- p = 0.2144;
- both date-block means negative.

One source track, \`C3_2_20231216_traj_bat_pos_RESULTS.mat\`, was already known from the earlier I/M external programme to have an implausibly large path length.

This audit does **not** remove that track selectively.

It evaluates every one-trial deletion permitted by the already frozen support floor.

## Admissible deletions

Use the same rule as \`CAROLLIA_EXTERNAL_LOO_ROBUSTNESS_CONTRACT_V1.md\`:

A valid trial is removable only if its bat has >3 valid trials before deletion, so that >=3 remain.

With the fixed external architecture, exactly **22** deletions must be evaluated.

No deletion is selected based on geometry outcome.

## For every deletion

1. remove exactly one admissible trial;
2. recompute date-block mean and SD for all eight fixed geometry features;
3. keep all eight features;
4. recompute the frozen fixed-geometry identity statistic;
5. preserve broad source turn class in the null;
6. rerun 9,999 date × turn-class-stratified label permutations.

Seed for filename-sorted deletion index k:

\[
202610061500+k.
\]

Require >=9,500 valid permutations.

## Report

For all 22 deletions:
- removed filename;
- K;
- p;
- positive fraction;
- both date-block means;
- whether the original external geometry support rule would pass.

Summary:
- min/max K;
- min/max p;
- min/max positive fraction;
- number of deletions that would yield support;
- specific result after deleting C3_2.

## Interpretation

### No deletion yields support

Strong negative boundary:

> the failure of fixed scale-free geometry transfer to Carollia is not caused by any single removable trial, including C3_2.

### Some deletions yield support

Do not replace the main negative result.

Instead conclude:
> the external geometry boundary is sensitivity-limited at the single-trial level.

## No rescue

Do not:
- redefine admissible deletions;
- select only C3_2;
- drop a date block;
- change turn classes;
- alter feature set;
- change alpha.

## JAE firewall

No change to JAE v0.4.0.
