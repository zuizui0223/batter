# Carollia external leave-one-trial robustness contract v1

## Status

**POST-OUTCOME ROBUSTNESS AUDIT.**

Frozen after the fixed external primary passed:
- K = 0.34758171124589077;
- p = 0.0007;
- 6/7 bats positive;
- both date-block means positive.

The audit was motivated by one obvious source-track anomaly:
`C3_2_20231216_traj_bat_pos_RESULTS.mat` had total path length about 2350 m over 6.84 s in a corridor experiment.

No trial is prospectively declared removable based on this observation.

## Purpose

Test whether the fixed external support is dependent on any single removable public trial.

## Eligible deletions

Use every valid trial whose removal leaves its bat with at least the frozen minimum of 3 valid trajectories.

With the primary counts:
- C2: 3 -> no deletion permitted;
- C3: 4 -> all 4 trials are admissible deletions;
- C4: 5 -> all 5;
- C5: 5 -> all 5;
- C6: 4 -> all 4;
- C7: 3 -> no deletion permitted;
- C8: 4 -> all 4.

Thus exactly **22** leave-one-trial deletions are evaluated.

Do not select deletions by outcome.

## For each deletion

1. remove exactly one admissible trial;
2. recompute date-block means and SDs of the eight fixed features from the remaining trials;
3. recompute the frozen I and M axes with no weight changes;
4. recompute the exact fixed 2-D individual-identity statistic;
5. rerun the exact within-date label permutation null with 9,999 permutations.

Seed for deletion index k in filename-sorted order:
`202610051200 + k`, k=1..22.

## Report

For every deletion:
- removed filename;
- K;
- p;
- positive bats / fraction;
- both date-block means;
- external-support rule PASS/FAIL.

Summary:
- minimum K across deletions;
- maximum p;
- minimum positive fraction;
- number of deletion runs retaining full external support;
- result after deleting C3_2 specifically.

## Additional noninferential track-QC table

For all 28 fixed-primary trials report:
- duration;
- total path length;
- straight-line displacement;
- median speed;
- p90 speed;
- p99 speed;
- maximum speed;
- maximum single-step distance;
- ratio max step / median nonzero step;
- x/y/z coordinate ranges.

No QC threshold is used to delete a trial.

## Interpretation

If all 22 admissible deletion runs retain support:

> the external result is not dependent on any single removable trial, including the obvious C3_2 track anomaly.

If some fail:
- report exactly which;
- do not redefine the external primary;
- treat generalization strength as sensitivity-limited.

## Ceiling

This is a robustness audit, not a replacement primary.
