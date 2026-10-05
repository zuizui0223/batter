# Phyllostomus measurement-harmonized carrier diagnostic v1

## Status

**POST-OUTCOME MEASUREMENT DIAGNOSTIC. CANNOT RESCUE THE FROZEN FIELD GATE.**

Frozen after:
- *P. hastatus* 2022 FlightIntensity persistence passed;
- 2023 failed strongly negative;
- support-matched sparsity alone was found unlikely;
- measurement audit showed dominant sampling cadences of 120/180 s in 2022 and 60 s in 2023, with much larger 2023 vertical-speed variance.

## Question

Does the 2022→2023 reversal persist after forcing both years onto the same displacement timescale?

## Common lag

Use exactly:

**360 seconds**

Rationale fixed before this outcome:
- common multiple of the dominant 60, 120 and 180 s cadences;
- long enough to reduce amplification of high-frequency height noise;
- short enough to retain repeated within-session support.

## Source sessions

Use exactly the frozen admitted sessions and individuals from the two original *P. hastatus* panels.

Do not change session boundaries, source exclusions, cohorts, manipulation exclusions or height fields.

## Exact-lag interval construction

Within each source-admitted session:

1. sort valid source fixes by timestamp;
2. for duplicate timestamps retain the first fix;
3. build exact timestamp lookup;
4. for every fix at time t, use a displacement interval only if a retained fix exists at exactly t+360 s;
5. each starting fix may contribute one interval;
6. overlapping 360-s lag intervals are allowed.

No interpolation and no nearest-neighbour time matching.

A session is harmonization-valid if it has >=30 exact 360-s lag intervals.

An individual is evaluable if it has >=2 harmonization-valid sessions in the same frozen cohort.

A panel opens a diagnostic only if >=5 evaluable individuals remain.

## H1 — harmonized original FlightIntensity

For every 360-s interval calculate:
- 3-D speed;
- absolute vertical speed.

Session features:
1. median 3-D speed;
2. p90 3-D speed;
3. median absolute vertical speed;
4. p90 absolute vertical speed.

Within frozen cohort z-score the four features and define:
`I360 = mean(z1,z2,z3,z4)`.

Use exactly the original held-out session self-history statistic H and equal-individual aggregation.

## H2 — horizontal-only diagnostic

For every exact 360-s interval:
- horizontal speed = sqrt(dx²+dy²)/360.

Session features:
- median horizontal speed;
- p90 horizontal speed.

Within cohort z-score both and define:
`IH = mean(z_median_hspeed,z_p90_hspeed)`.

This is a post-outcome measurement diagnostic and cannot become the primary carrier.

## H3 — vertical-only diagnostic

Use:
- median absolute vertical speed;
- p90 absolute vertical speed.

Within cohort:
`IV = mean(z_median_abs_vspeed,z_p90_abs_vspeed)`.

This diagnoses whether the year reversal is concentrated in the vertical component.

## Null

For every year × diagnostic independently:

- permute the exact individual-label multiset across complete harmonization-valid sessions within each frozen cohort;
- preserve session values and cohort structure.

9,999 permutations.

Seeds:
- 2022 I360: `202610051421`
- 2023 I360: `202610051422`
- 2022 IH: `202610051423`
- 2023 IH: `202610051424`
- 2022 IV: `202610051425`
- 2023 IV: `202610051426`

Report H, positive fraction and one-sided p.

## Interpretation

### 2023 I360 remains negative/unsupported, and IH also fails

Sampling cadence/high-frequency altitude noise alone is not an adequate explanation.

### 2023 I360 recovers while original I failed

The original year reversal is plausibly observation-process dependent.

### IH persists in 2023 but IV fails

The reversal is concentrated in the vertical measurement component, strongly implicating altitude measurement architecture.

### Both IH and IV fail in 2023

A broader year-specific behavioral/context change becomes more plausible.

## Ceiling

No harmonized diagnostic can:
- reclassify the frozen carrier panel;
- reopen the JAE vertical-shape bridge;
- prove ecological causation.
