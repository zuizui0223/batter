# Carollia fixed two-axis external validation contract v1

## Status

**PROSPECTIVE EXTERNAL VALIDATION — frozen before movement values are opened.**

Parent:
`CAROLLIA_EXTERNAL_STRUCTURAL_PREFLIGHT_V1.md`.

The fixed representation was derived in a different species and experiment and is not refit here.

## Independent biological system

Species:
`Carollia perspicillata`.

The source experiment used an L-shaped corridor with pseudorandomized corridor configurations across bats and trials. All bats experienced the principal 90-degree and 180-degree turn conditions.

## Fixed eligible identity architecture

Date blocks are fixed from filenames:

Block A — 20231216:
- C2
- C3
- C4

C1 is excluded prospectively because only two public trial files exist.

Block B — 20231222:
- C5
- C6
- C7
- C8

Comparisons and permutations never cross date blocks.

This prevents date/session batch structure from creating apparent individual identity.

## Trajectory source

For every pinned MAT file:
- load only `RESULTS`;
- require `RESULTS.track.tSec`;
- require `RESULTS.track.pos_sm`.

A valid trajectory requires:
- tSec and pos_sm aligned;
- pos_sm has exactly 3 columns;
- >=100 finite unique-time rows;
- >=50 positive-time derivative intervals;
- >=20 finite horizontal turning-rate observations;
- positive total 3-D path length and duration.

Each prospectively eligible bat must retain >=3 valid trajectories.

Each date block must retain >=3 eligible bats.

If not: STOP.

## Frozen eight features

Compute exactly:

1. median 3-D speed;
2. p90 3-D speed;
3. median absolute vertical speed;
4. p90 absolute vertical speed;
5. median absolute horizontal turning rate;
6. p90 absolute horizontal turning rate;
7. path efficiency = endpoint displacement / total 3-D path length;
8. vertical range.

Turning rate uses the same wrapped-heading and segment-midtime definition as the source Rhino programme.

No smoothing beyond the public source's already-saved `pos_sm`.
No re-interpolation.

## Date-block standardization

Within each date block and each feature:
- subtract mean across all valid trial feature vectors;
- divide by sample SD.

All eight SDs must be finite and positive.

No feature dropping.

## Frozen transparent axes

`I = mean(z1,z2,z3,z4)`

`M = mean(-z1,z5,z6,z7,z8)`

No weight is learned from Carollia.

## C1 — fixed two-axis individual identity

For target trajectory q from bat i:

- self centroid = mean of all other valid trials of i in the same date block;
- each donor centroid = mean of all valid trials for another bat in the same date block;
- `K_q = mean distance to donor centroids - distance to self centroid` in fixed (I,M).

Aggregate:
1. equal target trials within bat;
2. equal bats within date block;
3. equal date-block means overall.

## C2 — fixed component diagnostics

Report the same observed identity statistic for:
- I only;
- M only.

Descriptive only.

## Null

Within each date block independently:
- shuffle the exact observed bat-label multiset across complete trial feature vectors;
- preserve the number of trajectories assigned to every bat label;
- preserve date block and all feature values.

9,999 permutations.

Seed:
`202610051141`.

One-sided p.

Require >=9,500 valid permutations.

## External support

Call the fixed two-axis representation externally supported only if:
- overall K > 0;
- p <= 0.05;
- >=70% of evaluable bats have positive bat-level mean K;
- both date-block mean K values > 0.

No rescue by:
- PCA refitting;
- changing I/M signs or weights;
- dropping a date block;
- selecting trials by trajectory outcome;
- lowering minimum trial support.

## Interpretation

If supported:

> a two-axis movement-policy representation fixed in *Rhinolophus nippon* recovers persistent individual organization in an independent *Carollia perspicillata* cohort under a different 3-D navigation task and tracking pipeline.

This is cross-species representation transfer, not equality of axis distributions or individual parameter magnitudes.

## Claim ceiling

Support does not establish a universal bat law and does not identify the causal origin of I or M.
