# P. hastatus 2023 co-use horizontal-proximity diagnostic contract v1

## Status

POST-OUTCOME LOCALIZATION DIAGNOSTIC.

This contract is fixed while the separately predeclared temporal-gradient diagnostic is still running and before its outcome is known.

The corrected 2023 co-use primary result is already known:
- 679 frozen encounters;
- 8 frozen dyads;
- 6 individuals;
- all-space 500-m-cell co-use;
- +3.57 m phase-null excess, p = 0.0231.

This diagnostic cannot replace or upgrade that primary result.

## Question

Within the same frozen 500-m-cell co-use encounters, is vertical separation stronger when the two individuals are horizontally closer?

An interaction-proximity mechanism predicts that vertical displacement should be greatest when horizontal proximity is greatest.

## Frozen encounter universe

Use exactly the frozen 679-encounter 2023 primary set:
- SHA256: d4250eafeb7b602e47f7b9449bb76d4a71af0f0bfaa3bc3b801b260e69f2f6bb
- same 8 dyads;
- same 6 individuals;
- no rematching;
- no alternative cell size;
- no endpoint filtering for the primary diagnostic.

For encounter e:

d_xy,e = Euclidean projected distance between the two matched GPS fixes in metres.

No vertical value is used to define d_xy.

## X-Y preflight

For each frozen dyad report:
- encounter count;
- min, median, mean, max and SD of d_xy;
- number of distinct rounded-metre distances.

A dyad is spatial-slope-evaluable if:
- >=5 frozen encounters;
- >=3 distinct rounded-metre d_xy values;
- SD(d_xy) > 0.

The diagnostic proceeds only if at least 5/8 dyads pass.

The slope-evaluable dyad set is frozen before vertical separation is opened as a function of d_xy.

## Primary spatial-gradient statistic

For each encounter:
- response A_e = absolute terrain-relative, session-centered vertical separation (m);
- predictor q_e = d_xy / 100, in hundreds of metres.

Within each frozen spatial-slope-evaluable dyad:

gamma_d = covariance(q, A) / variance(q).

Panel:
- equal mean of gamma_d across dyads.

Predeclared direction:
- gamma_panel < 0.

Interpretation of a negative slope:
greater vertical separation when animals are horizontally closer.

## Null

Use the exact corrected fixed-encounter phase null:
- preserve encounter membership, x-y positions, d_xy, timestamps and dyad structure;
- preserve each individual-session-cell terrain-relative z distribution;
- independently circularly phase-shift z_rel within each frozen phase group;
- one nonzero shift per group per replicate.

For each null replicate recompute gamma_d and the equal-dyad panel mean.

B = 9,999.
Seed = 20261002115.

Diagnostic support requires:
- observed - null mean < 0;
- p(null <= observed) <= 0.05.

This remains post-outcome localization evidence, not a new independent test.

## Descriptive distance bands

Using the fixed encounters report:
- 0–50 m
- >50–100 m
- >100–250 m
- >250 m

Also report cumulative <=50, <=100 and <=250 m.

For each band, if at least 3 frozen dyads contribute >=3 encounters:
- equal-dyad median observed separation;
- phase-null mean;
- descriptive tail location.

Bandwise tails are not separate tests.

## Joint interpretation with temporal gradient

The temporal- and horizontal-proximity diagnostics are interpreted jointly; neither may rescue the other.

- both predicted negative gradients: strongest localization consistent with an interaction-proximity layer;
- temporal only: separation tracks synchrony but not within-cell physical proximity;
- spatial only: separation tracks physical proximity but not timestamp closeness;
- neither: retain the 2023 result as a coarse shared-site co-presence association.

No rule may be changed after either diagnostic output is known.

## Claim ceiling

Even dual proximity gradients would not uniquely identify:
- competition;
- intentional avoidance;
- feeding interactions;
- resource identity;
- causality.
