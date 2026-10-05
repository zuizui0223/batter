# Phyllostomus fixed-bin bivariate carrier diagnostic v1

## Status

**POST-OUTCOME MECHANISM DIAGNOSTIC. CANNOT RESCUE THE FROZEN FIELD GATE.**

Frozen after fixed-bin 360-s harmonization showed in *P. hastatus* 2023:

- scalar four-feature FlightIntensity: H = +0.0068, p = 0.273;
- horizontal-only intensity: H = +0.2039, p = 0.0488;
- vertical-only intensity: H = +0.2064, p = 0.0291.

Thus two component carriers are visible while their scalar average is weak.

## Question

Is the apparent scalar failure caused by projecting a genuinely multivariate individual movement policy onto one dimension?

## Data

Use exactly the fixed-bin 360-s valid sessions from
`phyllostomus_fixed_bin_harmonization_v2.py`.

No new session or individual inclusion rule.

## Two-dimensional session policy

Within each frozen cohort:

### Horizontal coordinate H

From fixed-bin:
- median horizontal speed;
- p90 horizontal speed.

Z-score each across valid sessions in the cohort and define:

`H_session = mean(z_hmed, z_hp90)`.

### Vertical coordinate V

From fixed-bin:
- median absolute vertical speed;
- p90 absolute vertical speed.

Z-score each across valid sessions and define:

`V_session = mean(z_vmed, z_vp90)`.

Policy vector:

`p_session = (H_session, V_session)`.

No fitted weights.

## Held-out self-history statistic

For target session s of individual i:

- self centroid = equal-session mean 2-D policy vector over i's other sessions;
- donor centroid j = equal-session mean vector over all sessions of donor j in the same cohort;
- require >=2 donor individuals.

Target advantage:

`H2_s = mean_j ||p_s - p_j||_2 - ||p_s - p_i,-s||_2`.

Aggregate:
- equal sessions within individual;
- equal individuals within year.

Year statistic:
`H2_year`.

## Null

Within each frozen cohort independently:
- permute the exact observed multiset of individual labels across complete sessions;
- preserve the 2-D vectors, cohort membership and label counts.

9,999 permutations.

Seeds:
- 2022: `202610051441`
- 2023: `202610051442`

One-sided p.

## Interpretation

### 2023 2-D carrier supported while scalar I remains weak

Strong evidence that the 2023 native/fixed-bin policy is **multidimensional rather than absent**; scalar averaging cancels persistent component structure.

### 2-D also unsupported

The component-wise results do not combine into a stable joint individual coordinate.

## Ceiling

This diagnostic:
- cannot change the frozen 2/4 field carrier result;
- cannot reopen the vertical-shape bridge;
- cannot claim the lab two-axis law is identical to the field H/V axes;
- is a dimensionality diagnostic only.
