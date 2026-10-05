# Carollia fixed-axis external validation result v1

## Status

**SUPPORTED EXTERNAL VALIDATION, WITH ROBUSTNESS AUDITS PASSED.**

Branch:
`prospective/task-reset-lockin-v1`

External species:
*Carollia perspicillata*

Source:
Eveland et al. (2026), *Looking ahead: echolocation and flight behaviors of two fruit bat species navigating a corridor*.

Pinned public repository:
`00keveland/Tunnel_2026@59928a71887d521fec143080b0b187736c046a0e`

## Frozen representation transferred from Rhinolophus

No Carollia-specific weights were fit.

Eight movement features used the same definitions as the Rhino programme.

Fixed transparent axes:

`I = mean(z_median_speed, z_p90_speed, z_median_abs_vertical_speed, z_p90_abs_vertical_speed)`

`M = mean(-z_median_speed, z_median_turn_rate, z_p90_turn_rate, z_path_efficiency, z_vertical_range)`

Standardization was frozen within source date blocks before the external outcome was opened.

## Fixed external primary

Frozen biological individuals:

2023-12-16:
- C2
- C3
- C4

2023-12-22:
- C5
- C6
- C7
- C8

Numeric support after coordinate opening:
- C2: 3 trials
- C3: 4
- C4: 5
- C5: 5
- C6: 4
- C7: 3
- C8: 4

All fixed support rules passed.

Observed fixed 2-D identity:
- `K = 0.3475817112`
- block 2023-12-16: `0.3279087688`
- block 2023-12-22: `0.3672546537`
- positive bats: **6/7**
- 9,999 permutations
- null mean: `-0.0355501`
- null 95% interval: `[-0.199412, 0.188426]`
- one-sided `p = 0.0007`

Verdict:
`SUPPORTED_FIXED_TWO_AXIS_EXTERNAL`

## Component boundary

Post-primary component audit:

### FlightIntensity I

- `K_I = 0.3677478962`
- 6/7 positive
- `p = 0.0014`

Thus the fixed intensity axis independently generalizes to this external species.

### ManeuverStructure M

- `K_M = 0.0893270347`
- 5/7 positive
- `p = 0.0392`

M is directionally supported alone, but weak.

### Incremental M beyond I

`Delta K_{2D-I} = -0.0201662`

`p = 0.6278`

Therefore the external success does **not** establish that adding M improves prediction beyond I in *Carollia*.

Allowed generality statement:

> The fixed movement-intensity axis replicated strongly in an independent species and tracking system. A second maneuver-structure axis is supported within *R. nippon* but its incremental cross-species value remains unestablished.

Do not claim a universal two-axis bat law.

## Single-trial robustness

A source-track anomaly was detected after the external primary:
`C3_2_20231216_traj_bat_pos_RESULTS.mat`
had an implausibly large interpolated path length.

This trial was not selectively removed from the historical primary.

An exhaustive leave-one-trial-out audit was frozen over every deletion that preserved the support floor.

Admissible deletions:
**22**

Results:
- support retained: **22/22**
- minimum K: `0.2778434971`
- maximum p: `0.0050`
- minimum positive fraction: `5/7 = 0.7143`

Deleting the anomalous C3_2 trial specifically:
- `K = 0.3245415464`
- 6/7 positive
- both date-block means positive
- `p = 0.0050`

Thus the external success is not driven by that anomalous public track or any single removable trial.

## Turn-condition robustness

The source paper used shallow versus steep turns with a 90-degree threshold.

A post-outcome audit froze trial class before opening `RESULTS.turns.angleDeg` values:
- `le90`
- `gt90`
- `no_annotated_turn`

Observed exposure:
- 2023-12-16 contained 2 le90 and 10 gt90 trials;
- 2023-12-22 contained 16 gt90 trials.

Condition-stratified label permutation:
- observed `K = 0.3475817112`
- 6/7 positive
- 9,999 permutations
- null mean: `-0.0232249`
- null 95% interval: `[-0.199327, 0.219320]`
- `p = 0.0017`

Removing all le90 trials while preserving the support gate:
- `K = 0.3237460725`
- 6/7 positive
- both date blocks positive
- `p = 0.0094`

Removing gt90 trials failed the frozen support gate and was not rescued.

Therefore the external signal is not explained by the broad shallow/steep turn mixture that was estimable from the public source annotations.

## Claim ceiling

This external result supports portability of a fixed low-dimensional movement-policy representation, especially the FlightIntensity axis.

It does not establish:
- identical latent axes in all bat species;
- morphology as the carrier;
- learned versus innate origin;
- independence from every unmeasured micro-geometric or recording difference;
- a deterministic trajectory equation.
