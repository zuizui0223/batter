# Configuration-conditioned estimator implementation appendix v1

## Status

**FROZEN BEFORE ANY CSV TRAJECTORY ROW VALUE IS OPENED.**

This appendix makes the already-frozen Primary A/B estimators computationally explicit.

## Common trajectory cleaning

For every CSV:

1. parse only `Time (Seconds), X, Y, Z`; `pulse` is ignored;
2. retain rows where all four parsed values are finite;
3. stable-sort by time ascending;
4. for duplicate timestamps retain the first row;
5. require >=100 retained rows;
6. require at least 50 strictly positive consecutive time intervals;
7. no smoothing or manual clipping.

## Primary A interpolation

For retained rows:

- compute consecutive 3-D Euclidean step lengths;
- cumulative arc length starts at zero;
- total path length must be positive;
- where successive points add zero arc length, retain the first occurrence of each unique cumulative arc-length position;
- require at least two unique cumulative positions;
- normalize cumulative arc length to [0,1];
- independently linearly interpolate X, Y, Z at 101 points `0, .01, ..., 1`.

No alignment, translation, rotation, Procrustes transform or direction reversal is applied.

## Primary B feature formulas

For positive-time consecutive intervals:

`dt_t = time_{t+1} - time_t`

`dx, dy, dz` are coordinate differences.

3-D speed:
`v3 = sqrt(dx^2+dy^2+dz^2)/dt`.

Absolute vertical speed:
`vz_abs = |dz|/dt`.

Horizontal heading for intervals with positive horizontal displacement:
`theta = atan2(dy,dx)`.

For consecutive valid heading intervals, wrapped heading difference:
`dtheta = atan2(sin(theta_t-theta_{t-1}), cos(theta_t-theta_{t-1}))`.

The time divisor for turning is the difference between segment mid-times, equivalently:
`dt_turn = (dt_t + dt_{t-1})/2`.

Absolute horizontal turning rate:
`omega_abs = |dtheta|/dt_turn`.

Require >=50 finite positive-time intervals for speed features and >=20 finite turning-rate values for turning features. Otherwise the trajectory is invalid for Primary B.

Features:
1. median(v3);
2. percentile90(v3);
3. median(vz_abs);
4. percentile90(vz_abs);
5. median(omega_abs);
6. percentile90(omega_abs);
7. path efficiency = straight-line distance from first to last retained point / sum of 3-D step lengths;
8. vertical range = max(Z)-min(Z).

Percentile uses NumPy's default linear quantile interpolation.

All eight values must be finite. Path efficiency requires positive total path length.

## Environment removal

Use `PRIMARY_B_STANDARDIZATION_AMENDMENT_V1.md` exactly:
- subtract species × environment feature mean;
- divide by pooled species-wide SD of centered residuals;
- drop a feature species-wide if that pooled SD is zero or nonfinite;
- require >=6 retained features.

## Identity permutations

Primary A:
- independently within each species × eligible environment, shuffle the full observed bat-label multiset across valid trajectories;
- thus exact per-label trajectory counts are preserved.

Primary B:
- use `PRIMARY_B_NULL_AMENDMENT_V1.md`;
- independently within every species × environment, shuffle the exact observed label multiset across complete trajectory feature vectors.

## Monte Carlo comparison

For one-sided positive alternatives, count null statistics satisfying:
`T_null >= T_observed`.

Use:
`p = (1 + count)/(1 + 9999)`.

No mid-p adjustment.

## Hierarchical weighting details

Primary A:
- target-route advantages are averaged equally within each bat × environment;
- bat × environment means are averaged equally within environment for the species statistic;
- eligible environment means are averaged equally for `A_species`;
- the bat-level sign-consistency quantity is the equal-environment mean of that bat's bat × environment means.

Primary B:
- for a candidate bat j and held-out environment e, first average j's trajectory feature vectors within each training environment;
- then average those environment centroids equally across all eligible training environments other than e;
- this prevents environments with more repeat trials from dominating a bat centroid;
- target K values are averaged equally within focal bat, then focal bats equally for `K_species`.

## Numeric precision

Use float64 throughout.
No rounding before final reporting.
