# Phyllostomus fixed-bin measurement harmonization diagnostic v2

## Status

**POST-OUTCOME MEASUREMENT DIAGNOSTIC. CANNOT RESCUE OR RECLASSIFY THE FROZEN FIELD CARRIER GATE.**

The exact-360-s lag diagnostic removed the strong negative 2023 sign, but its support became colony-asymmetric because exact timestamp phase differed among source sampling schedules.

This v2 diagnostic is frozen before calculating any fixed-bin carrier outcome.

## Question

Does the 2022 -> 2023 FlightIntensity contrast persist when both years are represented at the same 6-minute temporal bandwidth without requiring phase-aligned timestamps?

## Frozen source

Use exactly the source-admitted *P. hastatus* 2022 and 2023 sessions from the original field carrier programme:
- identical source files;
- identical exclusions;
- identical >4 h sessionization;
- identical frozen cohorts;
- identical native height field per year.

No session may be added or removed based on the new outcome.

## Fixed temporal grid

Bin width: **360 seconds**.

Grid origin: Unix epoch UTC.

For every valid source fix with timestamp t:

`bin = floor(unix_time(t) / 360)`.

Within each occupied bin independently compute median projected x, median projected y, and median native z. No interpolation.

## Consecutive-bin movement

Use a displacement only between occupied bins whose integer bin indices differ by exactly 1.

For every such pair compute horizontal, vertical and 3-D displacement from the bin medians and divide all displacements by exactly 360 s.

Thus both years are filtered to the same temporal bandwidth and the estimator is insensitive to whether raw sampling was nominally 60, 120 or 180 s.

## Support

A fixed-bin session is valid if it contains >=20 consecutive occupied-bin displacement intervals.

An individual is evaluable only if it has >=2 valid fixed-bin sessions within the same frozen cohort.

A year-level diagnostic opens only if:
- >=5 evaluable individuals overall;
- each source colony that contributed >=5 repeat individuals to the original year retains >=3 evaluable individuals.

This colony-retention rule prevents a harmonized result from being driven by a different colony subset in the two years. No threshold relaxation.

## F1 — 4-feature fixed-bin FlightIntensity

Session features: median and p90 3-D speed, plus median and p90 absolute vertical speed.

Within each frozen cohort z-score each feature across valid fixed-bin sessions, require finite nonzero SD for all four, and define `I_bin360 = mean(z1,z2,z3,z4)`.

Use the exact original held-out self-history statistic H and equal-individual aggregation.

## F2 — horizontal-only

Use median and p90 horizontal speed and define `IH_bin360 = mean(z_hmed,z_hp90)` after within-cohort standardization.

## F3 — vertical-only

Use median and p90 absolute vertical speed and define `IV_bin360 = mean(z_vmed,z_vp90)` after within-cohort standardization.

## Null

For each year × diagnostic independently permute the exact individual-label multiset across complete valid sessions within each frozen cohort, preserving cohort, feature values and label counts.

9,999 permutations.

Seeds: 2022 F1 202610051431; 2023 F1 202610051432; 2022 F2 202610051433; 2023 F2 202610051434; 2022 F3 202610051435; 2023 F3 202610051436.

Report H, positive fraction, p, individuals/sessions retained per colony, occupied bins and consecutive-bin intervals per session.

## Interpretation

If the original strong negative 2023 result disappears under this common-bandwidth representation while 2022 remains positive, the direction of the original year contrast is observation-scale dependent.

If 2023 remains strongly negative while both colonies retain support, measurement cadence is not an adequate explanation.

If support fails the colony-retention gate, return structural STOP and make no harmonized year inference.

## Ceiling

This is a measurement-sensitivity diagnostic only. It cannot change frozen PASS/FAIL labels, reopen the vertical-shape bridge, or prove either measurement artefact or ecological year dependence.