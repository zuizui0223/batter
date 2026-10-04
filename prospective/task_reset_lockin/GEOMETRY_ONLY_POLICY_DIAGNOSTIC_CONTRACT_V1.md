# Post-primary geometry-only policy diagnostic contract v1

## Status

**POST-PRIMARY EXPLORATORY ROBUSTNESS.**

This diagnostic is designed after:
- Primary A PASS / Primary B PASS;
- start-centered and chord-residual A failures;
- performance-only B support;
- steering-style B support.

It is not a new confirmatory primary and cannot rescue any result.

## Question

Does cross-configuration individual identity persist when all explicit time scale,
speed magnitude and absolute spatial scale are removed?

## Input trajectories

Use the exact 45 *Rhinolophus nippon* trajectories already opened by the frozen programme.

For each trajectory:
- same finite Time/X/Y/Z cleaning;
- same chronological sorting;
- same duplicate-time handling;
- same >=100-row route-valid rule;
- same 101-point equal-arc-length interpolation.

Time values are used only to establish row order. No speed or time derivative enters the diagnostic feature vector.

## Scale normalization

Let the 101-point 3-D route be r(s), s in [0,1].

Let:
- L = total 3-D path length of the cleaned original route;
- if L <= 0, trajectory invalid.

Translate:
`q(s) = (r(s)-r(0))/L`.

Thus q is dimensionless and start-centered.

No rotation, reflection or Procrustes alignment is allowed.

## Frozen geometry-only feature vector

From q(s):

1. **3-D path efficiency**:
   straight-line distance from q(0) to q(1), since total path length is normalized by L.

2. **horizontal displacement ratio**:
   horizontal distance between q(0) and q(1).

3. **absolute vertical displacement ratio**:
   `|q_z(1)-q_z(0)|`.

4. **vertical range ratio**:
   `max(q_z)-min(q_z)`.

5. **median absolute horizontal turn angle** between consecutive nonzero horizontal resampled segments.

6. **90th percentile absolute horizontal turn angle**.

7. **median absolute vertical slope**:
   for consecutive resampled points, `|dz| / sqrt(dx^2+dy^2+dz^2)`, omitting zero-length segments.

8. **90th percentile absolute vertical slope**.

All eight are dimensionless or angular.

No speed, elapsed time, absolute path length, absolute vertical range, or turn rate per unit time appears.

Require all eight features finite.

## Environment removal

Use the same main-Primary-B configuration removal:

Within each environment and feature:
- subtract environment mean;
- divide by environment sample SD.

An environment is usable only if:
- >=2 valid trajectories;
- >=2 bats;
- all 8 feature SDs finite and >0.

If one feature is invalid in any otherwise usable environment, drop that feature species-wide.
Require >=6 features.

## Cross-configuration estimator

Use the exact Primary B architecture:

- leave target environment out;
- bat history centroid averages trajectories within environment first;
- then averages environments equally;
- require >=2 other environments for own centroid;
- require >=2 other-bat centroids;
- K = mean distance to other-bat centroids - distance to own centroid;
- equal target -> equal bat.

## Null calibration

Use the exact Primary B environment-wise complete bat×environment cluster relabeling null.

9,999 permutations.

Seed:
`202610042215`.

Require >=9,500 valid permutations.

Report:
- K_geometry;
- five individual means;
- positive fraction;
- null mean and 95% interval;
- one-sided descriptive robustness p.

## Interpretation

If positive and calibrated beyond the null:

> Individual identity transfers across obstacle configurations even in route geometry stripped of time, speed and absolute spatial scale.

This would weaken a pure body-size / speed-scale explanation, but would still be compatible with:
- stable morphology affecting maneuver geometry;
- stable sensorimotor control style;
- long-lived learned policy.

If unsupported:

> The transferable identity is carried mainly by performance magnitude and time-scaled steering rather than scale-free route geometry.

## No rescue

No alternate geometry feature set, alignment, selected environments or subset of bats may replace this diagnostic after opening.
