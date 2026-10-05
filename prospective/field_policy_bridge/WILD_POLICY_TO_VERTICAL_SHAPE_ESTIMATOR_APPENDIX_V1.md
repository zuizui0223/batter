# Wild policy-to-vertical-shape estimator appendix v1

## Status

**FROZEN BEFORE THE wild FlightIntensity persistence outcome is known.**

Parent:
`WILD_POLICY_TO_VERTICAL_SHAPE_CONTRACT_V1.md`

This appendix may be executed only if the carrier gate passes:
`WILD_FLIGHT_INTENSITY_PERSISTENCE_CONTRACT_V1.md` must support >=3 of 4 field panels.

JAE v0.4.0 remains frozen.

## Core idea

For each held-out centered-height target session of focal individual i:

1. estimate the focal individual's FlightIntensity coordinate from other policy-valid sessions;
2. identify which other biological individual is nearest in FlightIntensity;
3. ask whether that policy-nearest donor also gives a better donor-specific prediction of the target's centered vertical shape than the other donors.

This is target-level and avoids treating pairwise distances as independent replicates.

## Vertical representation

Use exactly the frozen shift-invariant JAE shape architecture from:

- `scripts/run_tag_altitude_bias_shape.py`;
- `scripts/run_cross_panel_estimator_calibration.py`.

Fixed settings:
- every retained session median-centered before vertical binning;
- centered edges:
  `(-inf,-400,-200,-100,-50,0,50,100,200,400,+inf)`;
- horizontal cell = 5 km;
- Dirichlet alpha = 0.5;
- minimum scored fixes = 50.

No new binning, smoothing or vertical transformation.

## Policy coordinate

Recompute session-level FlightIntensity exactly as in
`WILD_FLIGHT_INTENSITY_PERSISTENCE_CONTRACT_V1.md`.

For target vertical session s of individual i:

- if s is policy-valid, focal policy history excludes s;
- otherwise use all policy-valid sessions of i;
- require at least one focal policy-history session after exclusion.

Define:
`theta_i,-s = mean(I)`
over those allowed focal policy sessions.

For every donor j:
`theta_j = mean(I)`
over all policy-valid sessions of donor j in the same frozen cohort.

No target vertical outcome enters theta.

## Donor-specific centered-shape gain

Within one centered-shape cohort construct the exact session arrays used by the JAE estimator.

For target session t of focal i:

- self training sessions = all centered-shape sessions of i except t;
- donor-j training sessions = all centered-shape sessions of j.

For each donor j separately:

1. calculate session-equal conditional vertical profiles by horizontal cell for focal self-history and donor j;
2. retain target cells with:
   - target fixes > 0;
   - a focal self-history profile;
   - a donor-j profile;
3. require >=50 target fixes over those cells;
4. calculate focal self-history cell weights exactly as the JAE common-cell estimator:
   - normalize the focal self-history occupancy within the supported cells separately for every self-history session;
   - average those normalized vectors equally over self-history sessions;
   - renormalize to sum to one;
5. integrate both focal-self and donor-j conditional profiles over that **same focal-self weight vector**;
6. calculate the donor-specific common-cell marginal gain

`G_tj = mean_fix[ log p_self(z) - log p_donor_j(z) ]`

over the supported target fixes.

Interpretation:
- smaller `G_tj` means donor j's centered vertical shape is more similar/predictive for the focal target relative to the focal self baseline;
- the focal self baseline is used only to keep the score on the exact JAE log-score scale.

No pooled-other profile is used in this new donor-ranking endpoint.

## Nearest-policy target contrast

Among donor individuals with evaluable `G_tj` and an eligible policy coordinate:

`d_I(i,j)=|theta_i,-s - theta_j|`.

Let N be the donor or donor set with the minimum d_I.

Exact ties:
- keep all tied nearest donors;
- average their G values.

Require at least:
- one nearest donor;
- one non-nearest donor.

Target contrast:

`C_t = mean(G_tj for non-nearest donors) - mean(G_tj for nearest-policy donors)`.

Thus:
- `C_t > 0`: the policy-nearest donor is also more similar in centered vertical shape;
- `C_t = 0`: no policy-neighbour advantage;
- `C_t < 0`: the policy-nearest donor is worse than the other donors.

## Aggregation

Within each panel:
- average C_t equally over target sessions within biological individual;
- then average eligible biological individuals equally.

Panel statistic:
`C_panel`.

Report:
- C_panel;
- individual means;
- positive-individual fraction;
- target count;
- donor-support distribution.

## Panel null

Within every frozen cohort independently:

- permute **complete individual policy histories** among the eligible biological individual labels;
- preserve:
  - all centered vertical data;
  - all donor-specific G_tj values;
  - policy-session values and counts as blocks;
  - cohort membership;
  - all vertical support.

Recompute theta, nearest-policy donor selection and C_panel.

9,999 permutations.

Seeds:
- Hypsignathus: `202610051321`;
- P. hastatus 2022: `202610051322`;
- P. hastatus 2023: `202610051323`;
- P. hastatus 2016: `202610051324`.

Panel p:
`(1 + #null >= observed)/(10000)`.

A panel is directionally positive when C_panel > 0.
A panel individually passes when C_panel > 0 and p <= 0.05.

## Cross-panel rule

Open only carrier-passing panels.

The predeclared bridge succeeds only if all are true:

1. at least **3 of 4 original panels** are carrier-passing and therefore open;
2. at least **3 of 4 original panels** have C_panel > 0;
3. at least **2 of 4 original panels** individually pass p <= 0.05;
4. the equal-open-panel combined statistic exceeds its null at p <= 0.05.

Panels that fail the carrier gate count as non-support; they are not silently omitted from conditions 2–3.

## Combined statistic

For each permutation index b:
- independently draw the frozen within-panel policy-history permutation for every open panel;
- calculate that panel's null C_panel,b;
- calculate

`C_comb,b = equal-panel mean(C_panel,b)`.

Observed:
`C_comb = equal-panel mean(C_panel)`
over open carrier-passing panels.

Combined p:
`(1 + #C_comb,b >= C_comb)/(10000)`.

No sample-size weighting.

## Interpretation

A positive result supports:

> the wild low-dimensional movement-intensity carrier is not merely repeatable; individuals near one another on that coordinate also tend to express more similar held-out centered vertical-use organization.

A negative result means:
- FlightIntensity can be a real persistent movement carrier,
- yet it does not explain the JAE centered vertical-shape individuality.

## Claim ceiling

Even success does not establish causal mediation.

It does not prove that FlightIntensity:
- causes vertical specialization;
- is learned;
- is morphological;
- is genetically fixed.

It establishes a predictive ecological bridge between a portable movement-policy coordinate and wild individual vertical organization.
