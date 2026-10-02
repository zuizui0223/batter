# P. hastatus 2023 co-use temporal-gradient diagnostic contract v1

## Status

POST-OUTCOME LOCALIZATION DIAGNOSTIC.

The corrected 2023 co-use primary result is already known:
- frozen all-space encounter set: 679 encounters, 8 dyads, 6 individuals;
- synchronization tolerance: 600 s;
- observed equal-dyad separation: 26.57 m;
- phase-null excess: +3.57 m;
- p = 0.0231.

This diagnostic is specified before vertical separation is examined as a function of within-encounter time difference.

It cannot replace or upgrade the frozen primary result.

## Question

If the 2023 co-use signal reflects a genuinely synchronous interaction layer, is extra vertical separation strongest when the two matched fixes are closest in time?

The fixed primary encounter set is not rebuilt or subset-selected for inference.

## Fixed encounter universe

Use exactly the 679 encounters in the frozen 2023 primary encounter set:
- encounter SHA256: d4250eafeb7b602e47f7b9449bb76d4a71af0f0bfaa3bc3b801b260e69f2f6bb
- all-space scope
- 500-m cell
- mutual-nearest matching
- maximum allowed time difference 600 s
- 8 frozen dyads
- 6 frozen individuals

No encounter, dyad, cell or individual is added or removed by vertical outcome.

## X-Y-time preflight

Before opening the temporal-gradient vertical outcome, report for each frozen dyad:
- encounter count;
- minimum, median and maximum |Δt|;
- standard deviation of |Δt|;
- number of distinct rounded-second |Δt| values.

A dyad is slope-evaluable if:
- >=5 frozen encounters;
- at least 3 distinct rounded-second |Δt| values;
- SD(|Δt|) > 0.

The diagnostic proceeds only if at least 5 of the 8 frozen dyads are slope-evaluable.

This gate uses x-y-time only.

## Primary temporal-gradient statistic

For encounter e in dyad d:
- response A_e = absolute terrain-relative, session-centered vertical separation in metres;
- predictor x_e = |Δt_e| / 60, measured in minutes.

Within each slope-evaluable dyad, fit the ordinary least-squares slope:

beta_d = covariance(x, A) / variance(x).

Units: metres of vertical separation per additional minute of temporal mismatch.

Panel statistic:
- equal mean of beta_d across slope-evaluable dyads.

Prediction:
- beta_panel < 0.

A negative slope means closer-in-time co-use is associated with larger vertical separation.

No dyad is weighted by its encounter count.

## Null

Use exactly the same fixed-encounter vertical-phase null as the corrected primary co-use analysis:
- preserve encounter identities, cells, timestamps and |Δt|;
- preserve each individual x session x 500-m-cell terrain-relative vertical distribution;
- independently circularly rotate each phase group's z_rel sequence by one random nonzero index;
- one shift per phase group per replicate.

For every null replicate:
- recompute A_e;
- recompute beta_d using the frozen slope-evaluable dyads;
- average dyads equally.

B = 9,999.
Seed = 20261002114.

Primary temporal-gradient support requires:
- beta_observed - mean(beta_null) < 0;
- one-sided p(null <= observed) <= 0.05.

Always report null mean, q025, q50, q975 and both empirical tails.

## Secondary descriptive localization

Using the same fixed 679 encounters, report x-y-time support and observed/null separation for four predeclared |Δt| bands:

- 0–60 s
- >60–120 s
- >120–300 s
- >300–600 s

For each band report:
- encounters;
- represented frozen dyads;
- observed equal-dyad median separation where at least 3 dyads have >=3 encounters in the band;
- phase-null mean and descriptive upper-tail location using the same 9,999 phase shifts.

These bandwise tail locations are descriptive post-outcome diagnostics, not four new hypothesis tests.

Also report cumulative <=60, <=120 and <=300 s summaries descriptively.

## Interpretation

### Negative primary slope supported

The 2023 separation signal becomes stronger as local co-use becomes more synchronous. This strengthens an interaction-/co-presence-dependent interpretation.

It still does not uniquely establish competition.

### Primary slope not supported

The 2023 primary excess does not localize toward closer temporal coincidence. The 600-s positive result should remain a coarse local co-use association rather than evidence for near-synchronous interaction.

### Positive slope

Do not reinterpret post hoc. Report that the temporal pattern runs opposite to the interaction-proximity prediction.

## Stop rule

After the x-y-time slope preflight:
- do not change the fixed 679-encounter universe;
- do not change the slope-evaluable dyads;
- do not transform or threshold Δt differently for the primary statistic;
- do not promote a favourable time band if the primary slope is unsupported;
- do not change B, seed or phase null.

## Claim ceiling

This diagnostic can localize the 2023 effect with respect to temporal proximity.

It cannot identify:
- competition;
- intentional avoidance;
- exact behavioural interaction;
- feeding/resource identity;
- causality.
