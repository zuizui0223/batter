# Individual wind reaction-norm outcome contract v1

## Status

POST-OUTCOME MECHANISM TEST. This contract is frozen after the ERA5 wind-support preflight passed in three of four panels and before any numeric vertical outcome is opened for this analysis.

Eligible panels are fixed by the completed wind-support preflight:
- Hypsignathus monstrosus
- Phyllostomus hastatus 2022
- P. hastatus 2023

P. hastatus 2016 is stopped because its frozen matched-wind fraction was 0.344 < 0.50. It cannot be rescued.

## Biological question

What is maintained across sessions: a relatively stable personal vertical solution, or an individual-specific mapping from wind conditions to vertical position?

The primary test asks whether adding the individual's own wind-response slope estimated from other sessions improves held-out prediction beyond a stable same-individual solution.

## Fixed response and conditioning

For each retained GPS fix:
1. subtract the exact pinned Mapzen/AWS Skadi HGT DEM elevation using the completed terrain-diagnostic bilinear interpolation;
2. within the full retained target session, subtract the median terrain-relative height;
3. use the resulting terrain-relative, session-centered height z_rel in metres.

Movement endpoints, 500-m cells and speed2_turn2 states are reconstructed exactly as in the completed 500-m place x kinematic stress test.

Only target endpoints that:
- are in a 500-m place x state stratum represented in the same individual's other sessions and in other individuals;
- lie inside the same-individual other-session q05-q95 ERA5 wind-speed range; and
- lie inside the q05-q95 wind range of at least two other individuals in the same cohort
are scored.

ERA5 wind is fixed to hourly 10-m wind speed sqrt(u10^2+v10^2), nearest 0.25-degree grid point and nearest hour, from the Earthmover public Icechunk ERA5 store used in the completed preflight.

## Models

For a held-out target session of individual i and target stratum s:

### B — stable self-history model

Using all other eligible sessions of i:
- mu_z(i,s) = mean z_rel in stratum s.

Prediction:
z_hat_B = mu_z(i,s).

### C — individual wind reaction-norm model

Using the same self-history training observations:
- mu_z(i,s) = mean z_rel within stratum s;
- mu_w(i,s) = mean wind speed within stratum s;
- pool all self-history events after subtracting their stratum means;
- beta_i = sum[(w-mu_w_s)(z-mu_z_s)] / sum[(w-mu_w_s)^2].

Prediction:
z_hat_C = mu_z(i,s) + beta_i * (w_target - mu_w(i,s)).

No nonlinear wind term, threshold, direction term, tailwind term or alternative weather variable may replace this primary slope after output is opened.

If the slope denominator is numerically zero for a target's self-history, that target session is not reaction-norm evaluable; no ridge or alternative model is substituted.

### A — population wind model, secondary

Using other individuals in the same cohort only, fit the analogous stratum-demeaned common wind slope and stratum means. This model is a secondary comparator for whether stable self-history itself remains informative beyond a population-level wind response.

## Scoring and biological weighting

For each target session, use exactly the same scored target endpoints for A, B and C.

Primary session statistic:
D_CB = MAE_B - MAE_C.

Positive D_CB means the individual's own wind-response rule improves held-out prediction over its stable stratum-specific solution.

Secondary:
D_BA = MAE_A - MAE_B.

Positive D_BA means stable same-individual history outpredicts the population wind model.

Sessions are averaged equally within biological individual; biological individuals are then weighted equally within panel. GPS endpoints are not biological replicates.

Always report:
- panel D_CB and D_BA in metres;
- per-individual values;
- number of scored sessions and endpoints;
- beta_i estimates as descriptive slopes in m height per m/s wind.

## Calibration

The complete prediction statistic is calibrated by whole-session individual-label permutation within frozen cohort.

A permutation:
- keeps every session's x-y-time, wind, terrain-relative z and kinematic states intact;
- permutes whole session identity labels within cohort while preserving the exact multiset of session counts assigned to labels;
- reconstructs A, B and C and all eligibility under the permuted labels.

B = 4,999 per panel.

Seeds:
- Hypsignathus: 20261003101
- P. hastatus 2022: 20261003102
- P. hastatus 2023: 20261003103

Panel support for the reaction-norm mechanism requires:
- observed D_CB - mean(null D_CB) > 0; and
- one-sided p(null >= observed) <= 0.05.

Stable-self support uses the same rule for D_BA.

## Synthesis rule

- reaction-norm support in 2 or 3 of 3 panels: repeatable individual wind responses contribute across multiple systems;
- support in 1 of 3: wind-dependent maintenance is context-dependent, not a general mechanism;
- support in 0 of 3, with stable-self D_BA supported in at least 2 panels: current evidence is more consistent with stable self-history than with this measurable wind reaction norm;
- otherwise: maintenance mechanism remains mixed/unresolved.

## Claim ceiling

A positive result supports a repeatable individual-specific response to broad ERA5 wind context under held-out prediction. It does not prove learning, memory, adaptation, optimality, personality, genetic determination, or direct sensing of 10-m wind.

A negative result rules out neither nonlinear wind responses nor finer atmospheric structure, canopy microclimate, resource phenology or sub-500-m route/resource mechanisms.

## Stop rule

After this contract is committed:
- no 2016 rescue;
- no alternative wind metric after opening;
- no nonlinear or threshold search;
- no change to 500-m place, speed2_turn2 state, terrain source, centering or environmental support;
- no change from MAE to another primary loss;
- no additional environmental family may rescue a failed wind outcome in this manuscript.
