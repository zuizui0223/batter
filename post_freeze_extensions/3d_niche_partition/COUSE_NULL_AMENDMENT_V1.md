# Co-use vertical-separation null amendment v1

## Status

**AMENDED AFTER X-Y-TIME PREFLIGHT AND ENDPOINT AUDIT, BEFORE ANY TERRAIN-RELATIVE VERTICAL-SEPARATION OUTCOME IS COMPUTED.**

No vertical separation, z-dependent encounter statistic or null result has been opened.

## Why the original synchrony null is replaced

The original contract proposed circularly shifting complete session timestamps and rebuilding encounters in every permutation.

The x-y-time preflight revealed:
- highly unequal encounter abundance among panels;
- 16,097 retained encounters in P. hastatus 2016;
- strong localization of encounters to one or a few shared 500-m cells.

Rebuilding the encounter network under each random shift would therefore mix two questions:

1. whether individuals meet in the same cell at the same time;
2. whether, **conditional on actually co-using the site**, they separate vertically.

The biological question motivating this analysis is the second.

The primary null is therefore replaced before vertical outcomes are opened by a fixed-encounter vertical-phase null.

## Revised primary null

The observed x-y-time encounter set is fixed exactly as determined by:
- the panel-specific frozen synchronization tolerance;
- mutual-nearest temporal matching;
- the frozen endpoint/all-space primary scope.

For each biological individual × target session × 500-m cell:

1. order all fixes in that group by timestamp;
2. retain the x-y-time records and observed encounter membership exactly;
3. take the terrain-relative, session-centered height sequence z_rel in that group;
4. circularly rotate the complete z_rel sequence by a random nonzero index;
5. use the rotated z_rel values at the already-fixed encounter fixes;
6. recompute dyad median absolute vertical separation and the panel mean.

Groups with fewer than two fixes cannot be phase-shifted. Before the vertical outcome is opened, an x-y-time-only support check records how many primary encounter endpoints belong to groups of size >=2. A panel may proceed only if at least 90% of primary encounter endpoints are shiftable; otherwise it stops structurally.

## What this null preserves

Exactly preserves:
- which individuals co-occur;
- which 500-m cell they co-occur in;
- encounter timestamps and time differences;
- horizontal trajectories and local shared-site geometry;
- each individual-session-cell's complete vertical distribution;
- stable individual-specific vertical strategy within that cell;
- number of encounters and dyad support.

Destroys:
- the moment-by-moment alignment between one individual's vertical position and a co-present individual's vertical position.

Thus a stable individual A-high / B-low difference that is present throughout their site use remains in the null distribution. Primary support requires **additional synchronous vertical separation beyond those stable personal strategies**.

## Primary statistic unchanged

For each frozen usable dyad:
- median absolute terrain-relative, session-centered vertical separation across fixed observed encounters.

Panel:
- equal mean of frozen usable-dyad medians.

No dyad or individual support is reselected from z.

## Calibration

B and seeds remain unchanged:
- 9,999 permutations;
- Hypsignathus 20261002101;
- P. hastatus 2022 20261002102;
- 2023 20261002103;
- 2016 20261002104.

Primary support remains:
- observed minus null mean > 0;
- p(null >= observed) <= 0.05.

## Secondary x-y-time encounter-frequency result

The earlier timestamp-shift idea is not reopened as a second hypothesis test.

Observed encounter count and localization remain descriptive structural information from the x-y-time preflight/endpoint audit.

## Claim ceiling

A positive result means:

> During actual synchronous local co-use, vertical separation exceeds what is expected after preserving each individual's site-specific vertical distribution but breaking momentary cross-individual vertical alignment.

This is stronger than stable personal vertical fidelity, but still does not uniquely identify competition. Social interaction, resource depletion, disturbance or other synchronous processes remain alternatives.
