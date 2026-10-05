# Wild FlightIntensity-to-vertical-shape bridge contract v1

## Status

**CONDITIONAL PROSPECTIVE BRIDGE CONTRACT.**

This contract is frozen **before** the wild FlightIntensity persistence outcome is known.

It may open only if:
- `WILD_FLIGHT_INTENSITY_PERSISTENCE_CONTRACT_V1.md` passes its preregistered cross-panel rule;
- at least 3 of 4 frozen field panels support within-individual FlightIntensity persistence.

If that gate fails, this contract remains closed and no substitute policy axis is opened.

JAE v0.4.0 remains frozen.

## Biological question

Does the persistent low-dimensional wild movement coordinate identified as FlightIntensity explain part of the held-out individual vertical-distribution organization that survives place and coarse movement-state matching?

The key distinction is:

- **carrier persistence**: the same individual has similar FlightIntensity across sessions;
- **vertical consequence**: individual differences in FlightIntensity predict individual differences in vertical-use organization.

This contract tests only the second link.

## Panels

Use exactly the same four frozen terrain-evaluable field panels:

- *Hypsignathus monstrosus*;
- *Phyllostomus hastatus* 2022;
- *P. hastatus* 2023;
- *P. hastatus* 2016.

No new individual, session, outlier, manipulation, or source inclusion rule.

## Frozen individual FlightIntensity parameter

For each panel/cohort and biological individual i:

- use all policy-valid sessions admitted by the persistence contract;
- calculate session-level I exactly as frozen there;
- define

`theta_I,i = equal-session mean(I_session)`.

This individual parameter is fixed before any new vertical-shape association is calculated.

## Vertical identity target

Use the exact frozen JAE vertical-distribution representation already used for held-out individual identity in each panel.

The new bridge must not redefine bins, smoothing, terrain correction, or held-out folds.

For each admissible individual × held-out unit, obtain the existing vertical-profile target from the frozen JAE pipeline.

## Primary predictor architecture

The bridge is directional and low-dimensional.

For every held-out vertical target of focal individual i:

1. estimate `theta_I,i` from policy sessions that are strictly outside the held-out target unit wherever chronology/session structure permits;
2. for every other eligible individual j, use the corresponding `theta_I,j`;
3. define scalar policy distance
   `d_I(i,j)=|theta_I,i-theta_I,j|`;
4. define vertical-profile distance using the exact frozen JAE profile-distance metric.

Primary panel statistic:

`B_panel = -correlation(d_I(i,j), d_vertical(i,j))`

is **not** used because pairwise distances are non-independent.

Instead use a target-level nearest-policy comparison:

For target vertical profile q from individual i:
- choose the other individual j* with minimum policy distance to i among eligible donors;
- compare vertical-profile distance from q to:
  - the focal individual's own frozen/self-history profile;
  - the closest-policy donor j*;
  - the mean donor baseline.

The exact target-level scalar contrast will be implemented from the frozen JAE profile functions, preserving equal-target and equal-individual weighting.

## Required mechanistic direction

The simplest policy-consequence prediction is:

> individuals with similar FlightIntensity should have more similar held-out vertical-use organization than expected under exchangeable individual labels.

Thus the final implementation must be one-sided in that direction.

## Null

Within each panel/cohort:
- permute complete biological individual labels attached to frozen `theta_I` values;
- preserve all vertical data, support, cohort membership and policy-value distribution;
- break only the mapping between policy coordinate and individual vertical identity.

9,999 permutations per panel.

Seeds:
- Hypsignathus: `202610051321`;
- P. hastatus 2022: `202610051322`;
- P. hastatus 2023: `202610051323`;
- P. hastatus 2016: `202610051324`.

## Cross-panel rule

A field policy-to-vertical bridge is called supported only if:

- at least 3 of 4 panels show the preregistered positive direction;
- at least 2 of 4 panels individually pass p <= 0.05;
- a predeclared equal-panel combined statistic exceeds its panel-wise label-permutation null at p <= 0.05.

No panel weighting by sample size.

## Critical negative control

Because JAE already conditions on coarse movement state, also report whether the policy bridge survives after matching/restricting to the exact frozen place × movement-state conditioning architecture where available.

If the bridge appears only without that conditioning, do not claim that FlightIntensity explains the JAE residual individuality.

## Claim ceiling

A positive result may support:

> a persistent low-dimensional movement-intensity coordinate covaries with the individual vertical-use organization observed in the wild.

It still does not establish:
- causation;
- morphology;
- learning;
- a universal bat law.

A negative result would mean the laboratory/external FlightIntensity carrier is real but does not explain the specific wild vertical-specialization signal in JAE.
