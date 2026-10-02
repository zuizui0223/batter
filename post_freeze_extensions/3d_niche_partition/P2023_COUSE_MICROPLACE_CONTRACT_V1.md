# P. hastatus 2023 co-use micro-place preservation diagnostic contract v1

## Status

POST-OUTCOME MECHANISM-LOCALIZATION DIAGNOSTIC.

Known before this contract:
- the corrected 2023 fixed-encounter co-use excess (+3.57 m, p=0.0231);
- the temporal-proximity gradient is not supported (p=0.095);
- the horizontal-proximity gradient is not supported and runs opposite to the near-contact prediction.

This diagnostic is therefore not an independent test of interaction. It asks whether the 2023 co-use excess can be explained by **fine-scale x-y structure within the original 500-m encounter cell**.

No micro-place-conditioned vertical result is opened before the preflight and null are fixed.

## Why this diagnostic is necessary

The corrected primary phase null preserves:
- the fixed encounter set;
- each 500-m encounter cell;
- each individual-session-cell vertical distribution.

But it circularly rotates z_rel over all fixes within an individual x session x 500-m cell. That operation can break a stable association between:
- fine-scale x-y location inside the 500-m cell; and
- terrain-relative vertical position.

Therefore a positive primary co-use excess could arise if two individuals repeatedly occupy different sub-cell routes or microhabitats whose characteristic z_rel values differ, even without any momentary interaction.

## Frozen encounter universe

Use exactly the corrected 2023 primary encounter set:
- 679 encounters;
- 8 frozen dyads;
- 6 frozen individuals;
- all-space scope;
- original encounter SHA256:
  d4250eafeb7b602e47f7b9449bb76d4a71af0f0bfaa3bc3b801b260e69f2f6bb

Encounter identities, timestamps, dyads, x-y coordinates and z_rel endpoint values are never rematched or subset-selected by the vertical result.

## Candidate micro-place scales

Before opening the micro-place-conditioned vertical null, evaluate x-y support only at these subcell sizes, in this fixed order from finest to coarsest:

1. 50 m
2. 100 m
3. 250 m

For each candidate scale, assign every primary-scope fix to:
floor(x / scale), floor(y / scale).

The original 500-m encounter cell remains part of the group key so subcells are nested within the frozen encounter-cell geometry.

## X-Y-only support preflight

For each candidate scale, define a phase group as:

individual x target session x original 500-m cell x micro-subcell.

An encounter endpoint is micro-place-shiftable if its phase group contains at least 2 primary-scope fixes.

A candidate scale passes if:
- at least 90% of all 1,358 encounter endpoints are shiftable;
- every frozen dyad retains at least 70% shiftable encounter endpoints;
- at least 7/8 frozen dyads retain >=5 encounters with both endpoints shiftable.

The **finest candidate scale that passes all gates** becomes the primary micro-place scale.

If none of 50, 100 or 250 m passes, this diagnostic stops structurally. Do not revert to a data-chosen intermediate scale.

All support calculations use x-y-time only.

## Primary micro-place-preserving null

At the frozen selected micro-place scale:

For each individual x target session x original 500-m cell x selected micro-subcell:

1. order all primary-scope fixes by timestamp;
2. retain x-y-time records and encounter membership exactly;
3. take the complete terrain-relative, session-centered z_rel sequence;
4. circularly rotate that z_rel sequence by one random nonzero index;
5. use the rotated z_rel at the already-fixed encounter endpoints.

Groups with one fix remain unchanged, but the preflight guarantees the frozen shiftability threshold.

This preserves:
- fixed co-use encounters and dyads;
- exact horizontal endpoint positions;
- original 500-m encounter cells;
- each individual's micro-place-specific vertical distribution;
- stable individual vertical strategy;
- stable fine-scale route/microhabitat-specific z structure.

It destroys only:
- momentary cross-individual vertical alignment within those preserved micro-places.

## Primary statistic

Unchanged from the corrected 2023 co-use primary:

- absolute terrain-relative, session-centered vertical separation at each frozen encounter;
- median within each of the 8 frozen dyads;
- equal mean across dyads.

Observed statistic is the same frozen 26.5656705 m.

## Calibration

- B = 9,999.
- seed = 20261002116.
- same eight frozen dyads.
- one micro-place phase shift per group per replicate.

Support requires:
- observed - null mean > 0;
- p(null >= observed) <= 0.05.

Always report q025, q50, q975 and both empirical tails.

## Interpretation

### Primary remains supported

The 2023 excess cannot be absorbed by preserving fine-scale x-y-specific vertical structure at the smallest structurally supported subcell scale.

This would strengthen a momentary co-presence / interaction-linked interpretation, though competition remains unproven.

### Primary becomes unsupported

The 2023 excess is explainable by stable fine-scale spatial organization inside the coarse 500-m encounter cell.

Preferred wording:

> the apparent co-presence separation reflects micro-place / route-specific spatial structure rather than demonstrated active vertical avoidance.

### Null mean rises toward observed

Interpret as progressive absorption of the co-use signal by fine-scale spatial conditioning.

## Secondary fixed-scale diagnostics

Regardless of which scale is selected as primary, if 100 m or 250 m meets the preflight support gate, report its result descriptively using seeds:
- 100 m: 20261002117
- 250 m: 20261002118

The 50-m result is primary only if 50 m passes; otherwise report it as structurally unavailable, not as a failed biological effect.

No favourable scale may replace the predeclared finest-passing primary.

## Stop rule

After the x-y preflight:
- do not change candidate scales or support gates;
- do not alter encounter universe, dyads or endpoint scope.

After vertical output:
- do not add new micro-place scales;
- do not use nearest-neighbour smoothing, splines, kernels or route clusters as rescue;
- do not promote a coarser favourable scale over the finest-passing primary;
- do not reinterpret failure as evidence of attraction.

## Claim ceiling

This diagnostic can distinguish:
- momentary co-presence-linked vertical separation;
from
- stable sub-cell spatial geometry that creates apparent co-use separation.

It cannot identify:
- competition;
- intentional avoidance;
- feeding/resource identity;
- causal behavioural response.
