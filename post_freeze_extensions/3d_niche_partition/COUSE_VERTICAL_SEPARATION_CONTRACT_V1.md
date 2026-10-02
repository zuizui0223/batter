# Simultaneous co-use vertical-separation contract v1

## Status

POST-OUTCOME MECHANISM TEST GENERATED AFTER THE TERRAIN-RELATIVE 3D-GEOMETRY RESULTS.

The target panels are selected because they already show supported terrain-relative vertical-strategy fidelity. This analysis therefore cannot establish generality or serve as independent confirmation.

Before the new vertical-separation outcome is computed, all encounter definitions, temporal-window selection rules, structural gates, terrain processing, null model, aggregation and decision criteria are fixed here.

Eligibility and temporal-window selection use x-y-time structure only. No vertical value or vertical separation is used to choose a window or admit a panel.

## Ecological question

When two tracked individuals use the same fine-scale horizontal space at the same time, do they separate vertically **more than expected from their already-existing personal spatial strategies**?

This distinguishes:
- stable personal vertical strategies, which persist even when individuals are not interacting;
from
- competitor-/co-presence-dependent vertical separation, which should increase specifically during synchronous local co-use.

A positive result is consistent with interaction-dependent vertical partitioning. It still does not uniquely identify competition, because social coordination, resource depletion or other synchronous processes can also generate separation.

## Fixed panel universe

Only the four original panels with supported terrain-relative V_rel under the completed 500-m geometry audit:

- Hypsignathus monstrosus
- Phyllostomus hastatus 2022
- Phyllostomus hastatus 2023
- Phyllostomus hastatus 2016

No panel is added after the co-use results are opened.

## Fixed spatial universe

- Exact target-session universe used by the completed terrain-relative 3D-geometry analysis.
- Horizontal grid: 500 m.
- Same source-specific projected coordinates.
- Pair comparisons are only within the same admitted cohort.
- Individuals must be distinct.

## Structural preflight: encounter definition

Candidate synchronization tolerances, evaluated in this fixed order:

1. 60 s
2. 120 s
3. 300 s
4. 600 s

For an unordered individual pair within a cohort:

1. fixes must fall in the same 500-m cell;
2. timestamp difference must be <= candidate tolerance;
3. a matched fix pair must be a **mutual nearest temporal neighbour within that cell**;
4. each fix may occur in at most one encounter for that individual pair.

Mutual-nearest matching prevents high-frequency tracks from generating one-to-many pseudo-encounters.

## Structural panel gate

At a candidate tolerance, a dyad is structurally usable with at least 5 matched encounters.

A biological individual is structurally usable with:
- at least 10 matched encounters total;
- encounters with at least 2 distinct partner individuals.

A panel passes at a candidate tolerance only if it has:
- at least 5 structurally usable biological individuals;
- at least 5 structurally usable dyads;
- at least 50 matched encounters total.

The primary tolerance for a panel is the **smallest candidate tolerance that passes all gates**.

If no candidate tolerance passes, the panel stops as structurally non-evaluable. No additional tolerance is opened.

This window-selection rule is based only on x-y-time support and is fixed before vertical separation is computed.


## Endpoint / central-place exclusion before vertical opening

Because synchronous same-cell encounters can be dominated by colony/roost departure and arrival, the already-established x-y-only night-endpoint proxy is applied before any vertical-separation outcome is opened.

Proxy definition:
- within each target session, take the first five and last five finite projected fixes;
- pool these endpoint fixes within biological individual and admitted cohort;
- select the observed endpoint minimizing summed Euclidean distance to all other pooled endpoint fixes as that individual's proxy centre;
- the proxy is not asserted to be the true biological roost, lek or colony centre.

For endpoint-excluded panels, fixes within 1,000 m of their own individual's proxy centre are removed **before mutual-nearest encounter matching**. The observed encounter set and the vertical phase-shift null therefore use the same reduced fix universe.

The 1,000-m radius is inherited from the existing endpoint-neighbourhood audit and is not chosen from the new vertical outcome.

This pre-matching exclusion supersedes the earlier match-then-filter bookkeeping and is fixed before any vertical-separation outcome is computed.

### Pre-outcome primary-scope rule

After the selected synchronization tolerance is frozen, x-y-time support is recomputed on endpoint-excluded encounters.

- If the endpoint-excluded encounter set still satisfies the exact same panel gate (>=5 usable individuals, >=5 usable dyads, >=50 encounters; individual and dyad gates unchanged), the endpoint-excluded set becomes the primary vertical-separation universe.
- If it fails, the all-space encounter set remains primary, but the interpretation is limited to generic synchronous co-presence; no foraging-competition or away-from-central-place language is allowed.
- No radius sensitivity analysis is opened as rescue.

## Vertical outcome

For each retained GPS fix:

terrain_relative_height = native_height - DEM_terrain_elevation.

Then subtract the median terrain-relative height of that fix's full target session:

z_rel = terrain_relative_height - session_median(terrain_relative_height).

The DEM source, pinned tiles, SHA checks and bilinear interpolation are exactly those already fixed in ORIGINAL_TERRAIN_GEOMETRY_CONTRACT_V1.

For a matched simultaneous co-use encounter between individuals i and j:

A_e = abs(z_rel_i - z_rel_j).

## Primary observed statistic

Within each structurally usable dyad:
- take the median A_e across matched encounters.

Panel statistic:
- equal mean across structurally usable dyad medians.

Thus bursts of many GPS fixes do not dominate the biological comparison.

## Synchrony-destruction null

The null preserves each individual's full x-y-z trajectory and personal vertical strategy while destroying cross-individual synchrony.

For every target session independently:

1. keep each event's x-y-z record intact;
2. circularly shift the complete session timestamps by one random time offset modulo the original session duration;
3. the random shift must be at least 2 × the panel's frozen encounter tolerance away from zero modulo the session span;
4. recompute mutual-nearest same-cell encounters from the shifted timestamps;
5. recompute the complete dyad support gate and panel statistic.

Sessions with duration < 4 × the frozen encounter tolerance are not shiftable and are excluded from both observed and null encounter universes before the vertical outcome is opened. The structural preflight reports this count.

This null retains:
- each individual's route;
- terrain-relative heights;
- stable individual vertical preference;
- within-session movement sequence;
- horizontal cell use;
- sampling schedule intervals up to circular phase.

It destroys:
- which other tracked individual is locally co-present at the same moment.

## Calibration

- B = 9,999 per evaluable panel.
- Seeds:
  - Hypsignathus: 20261002101
  - P. hastatus 2022: 20261002102
  - P. hastatus 2023: 20261002103
  - P. hastatus 2016: 20261002104

A null replicate is valid only if it retains at least:
- 5 usable dyads;
- 5 usable individuals;
- 50 encounters.

Primary support requires:
- observed minus null mean > 0;
- one-sided p(null >= observed) <= 0.05.

Always report null mean, q025, q50, q975, valid/invalid replicate counts.

## Secondary descriptive quantities

Report without additional confirmatory promotion:

- observed total encounter count;
- encounter count under the time-shift null;
- median number of partners per usable individual;
- per-dyad observed vertical separation;
- per-individual encounter counts;
- cell distribution of encounters;
- whether observed encounter count is lower or higher than the time-shift expectation.

These distinguish possible horizontal avoidance/attraction from the primary vertical-separation endpoint, but do not create extra primary claims.

## Interpretation matrix

### Primary separation supported

Synchronous local co-use is associated with greater vertical separation than expected from stable personal trajectories alone.

Allowed wording:
"vertical separation is interaction-/co-presence-dependent under the fixed synchrony null."

Do not automatically write "competition causes partitioning."

### Primary separation not supported

Stable personal vertical strategies do not translate into extra vertical separation during synchronous local co-use.

This supports the distinction:
individual specialization != interaction-driven niche partitioning.

### Observed encounter count below null, vertical separation unsupported

Potential horizontal avoidance rather than vertical partitioning; descriptive only.

### Encounter count near/above null and vertical separation supported

Strongest geometry consistent with individuals sharing horizontal space while increasing vertical separation during co-use; still not uniquely competition-mediated.

## Stop rule

After the x-y-time preflight:
- do not change the candidate tolerance set or selection rule;
- do not change 500-m cell size;
- do not lower encounter/dyad/individual/panel support gates.

After the vertical outcome:
- do not change terrain source or interpolation;
- do not change session centering;
- do not replace median absolute separation with another primary statistic;
- do not use a different time-shift null;
- do not select only favourable dyads, cells or nights;
- do not rescue a failed panel with looser support.

## Claim ceiling

This analysis can test whether extra vertical separation is associated with synchronous local co-use beyond stable personal spatial strategies.

It cannot by itself identify:
- competition as the unique cause;
- intentional avoidance;
- resource identity;
- diet partitioning;
- adaptive benefit.
