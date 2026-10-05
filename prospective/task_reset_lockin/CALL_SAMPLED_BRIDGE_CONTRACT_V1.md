# Call-sampled observation-process bridge contract v1

## Status

PROSPECTIVE OBSERVATION-PROCESS COMPATIBILITY GATE.

This gate is frozen before any row-2+ value from the independent call-sampled 3-D candidate is opened.

The fixed transparent axes are not redefined:

- FlightIntensity = mean(z1,z2,z3,z4)
- ManeuveringExtent = mean(-z1,z5,z6,z7,z8)

## Question

Does the fixed transparent two-axis individual policy remain detectable when the original Teshima Rhinolophus nippon trajectories are observed only at echolocation-pulse times?

If not, the independent call-sampled 3-D candidate is not an admissible external test of the frozen representation.

## Source cohort

Use only the authoritative 45 Teshima R. nippon CSV trajectories.

For every CSV:
- retain rows with pulse != 0;
- retain finite Time, X, Y, Z;
- stable-sort by time;
- retain the first duplicate timestamp.

No non-pulse position enters the feature calculation.

## Frozen support

A pulse-sampled trajectory is valid if:
- >=20 retained pulse points;
- positive total duration;
- positive 3-D path length;
- >=19 positive-time speed intervals;
- >=10 finite horizontal turning-rate observations.

## Frozen eight features

Calculate exactly:

1. median 3-D speed;
2. p90 3-D speed;
3. median absolute vertical speed;
4. p90 absolute vertical speed;
5. median absolute horizontal turning rate;
6. p90 absolute horizontal turning rate;
7. 3-D path efficiency;
8. vertical range.

Turning rate uses the same wrapped-heading and segment-midtime definition as the Teshima primary estimator.

## Environment standardization

Within each obstacle environment and feature:
- subtract environment mean;
- divide by environment sample SD.

An environment is usable only if:
- >=2 valid trajectories;
- >=2 bat identities;
- all eight SDs are positive and finite.

No feature dropping.

## Fixed transparent coordinates

I = mean(z1,z2,z3,z4)

M = mean(-z1,z5,z6,z7,z8)

No fitted weights.

## B1 — call-sampled 2-D identity

Use the exact leave-one-environment-out cross-configuration identity architecture:
- equal-environment training centroids;
- Euclidean target distance in fixed (I,M);
- donor bats averaged equally;
- equal target -> equal bat species statistic K.

Require:
- >=3 candidate bats;
- each candidate in >=3 usable environments;
- each target has >=2 training environments for self and >=2 eligible donor identities.

## B2 — descriptive components

Also report observed K for I alone and M alone.

## Null

Within every usable environment independently permute complete bat labels among bat-by-environment trajectory clusters.

9,999 permutations.

Seed: 202610051101.

Bridge PASS requires:
- K_2D > 0;
- p <= 0.05;
- >=70% evaluable bats positive.

## Decision

PASS_CALL_SAMPLED_BRIDGE:
the independent call-sampled external estimator may open if its structural gate also passes.

STOP_OBSERVATION_PROCESS_MISMATCH:
do not open external movement outcomes for fixed-axis validation.

## Ceiling

PASS shows only that the frozen policy remains detectable under pulse/call subsampling in the source cohort. It is not external replication.
