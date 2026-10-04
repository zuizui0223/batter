# Post-primary robustness contract v1 — route shape and policy decomposition

## Status

**POST-PRIMARY ROBUSTNESS DIAGNOSTICS.**

These diagnostics were designed only after the frozen Primary A and Primary B outcomes were opened.

They are therefore:
- not new prospective confirmations;
- not allowed to replace or rescue either primary;
- used only to diagnose alternative explanations for the dual PASS.

Primary result:
`RHINO_CONFIGURATION_IDENTITY_PRIMARY_RESULT_V1.md`.

## Diagnostic A1 — start-centered literal-route identity

Use the exact Primary A route-valid trajectories, eligible environments, 101-point arc-length standardization, weighting, and identity permutations.

For each standardized route:

`r_start(s) = r(s) - r(0)`.

Recompute the frozen A statistic and its same-form within-environment identity permutation null.

Purpose:

> test whether Primary A can be explained merely by stable differences in the absolute starting position of each bat.

Requested permutations:
9,999.

Seed:
`202610042211`.

## Diagnostic A2 — chord-residual route-shape identity

For each 101-point standardized route at normalized arc-length s:

`chord(s) = (1-s) r(0) + s r(1)`

and

`r_shape(s) = r(s) - chord(s)`.

Use the same route distance, equal weighting and within-environment permutation as Primary A.

This removes:
- absolute start position;
- absolute end position;
- straight-line displacement between them.

What remains is the 3-D deviation / curvature structure of the route relative to its own start–end chord.

Requested permutations:
9,999.

Seed:
`202610042212`.

If A2 remains strong, the configuration-specific identity is not just endpoint placement.

## Diagnostic B1 — leave-one-feature-out observed stability

Using the exact Primary B target set and environment-standardization procedure:

For each of the eight frozen features, remove that feature and recompute **observed K only**.

No new p-value is assigned.

Report:
- K_without_feature;
- ratio to primary K.

Purpose:
identify whether one feature dominates the full 8-D transfer result.

## Diagnostic B2 — performance-magnitude-only transfer

Use only:

1. median 3-D speed;
2. p90 3-D speed;
3. median absolute vertical speed;
4. p90 absolute vertical speed;
5. vertical range.

Retain the exact Primary B:
- environment-wise z-scoring;
- equal-environment history centroids;
- fixed target set;
- equal-target -> equal-bat weighting;
- environment-wise cluster-label permutation.

Requested permutations:
9,999.

Seed:
`202610042213`.

This diagnoses whether stable kinematic magnitude / performance alone is sufficient for cross-configuration identity.

## Diagnostic B3 — steering-style-only transfer

Use only:

1. median absolute horizontal turning rate;
2. p90 absolute horizontal turning rate;
3. path efficiency.

Apply the same frozen Primary B cross-environment estimator and null.

Requested permutations:
9,999.

Seed:
`202610042214`.

This deliberately removes:
- 3-D speed magnitude;
- vertical speed magnitude;
- absolute vertical range.

If B3 remains positive and permutation-supported, the transfer result cannot be reduced to simple speed or vertical-scale differences.

## Diagnostic interpretation

### A1/A2 both persist

Configuration-specific route identity includes route shape, not merely stable release/end position offsets.

### B2 only, B3 absent

The portable individual signature is primarily performance magnitude. Stable morphology/biomechanics becomes the leading explanation.

### B3 persists

A portable steering/efficiency style exists beyond speed magnitude, supporting a broader sensorimotor-policy interpretation.

### B2 and B3 both persist

Individual flight organization is distributed across both performance magnitude and steering style.

## Calibration

For A1, A2, B2 and B3, report the same:
- observed statistic;
- null mean;
- null 95% interval;
- one-sided permutation p;
- individual means and positive fraction.

Because these are post-primary diagnostics, p-values are descriptive robustness calibrations and are not treated as new familywise-confirmatory tests.

## No rescue

Do not:
- select only favorable diagnostics;
- alter features inside B2/B3;
- change environments;
- change route interpolation;
- change target set;
- add morphology covariates after seeing these diagnostics;
- reinterpret a diagnostic failure as invalidating the already frozen primary.
