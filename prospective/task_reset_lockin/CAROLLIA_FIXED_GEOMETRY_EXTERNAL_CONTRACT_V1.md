# Carollia fixed geometry-policy external diagnostic contract v1

## Status

**POST-PRIMARY EXTERNAL DIAGNOSTIC WITH A REPRESENTATION FIXED IN RHINOLOPHUS.**

This is not a pristine external confirmatory primary because the Carollia movement archive has already been opened for the fixed I/M validation.

However:
- the exact eight geometry features were defined in the independent *Rhinolophus nippon* programme;
- no Carollia-specific geometry feature selection, sign choice or weighting is permitted;
- the main external statistic is frozen before the Carollia geometry values are calculated.

## Independent source

Species:
*Carollia perspicillata*

Pinned repository:
\`00keveland/Tunnel_2026@59928a71887d521fec143080b0b187736c046a0e\`

Fixed biological blocks:

### 2023-12-16
- C2
- C3
- C4

### 2023-12-22
- C5
- C6
- C7
- C8

C1 remains excluded prospectively because it has only two public trials.

## Trajectory source and support

Use exactly:
- \`RESULTS.track.tSec\`
- \`RESULTS.track.pos_sm\`

Apply the existing frozen Carollia support:
- exactly 3-D positions;
- >=100 finite unique-time rows;
- positive path length and duration;
- >=3 valid trials for every fixed bat.

No trial may be excluded based on geometry outcome.

The historically noted C3_2 track remains included in the main statistic.
Its effect may be reported only through the already frozen leave-one-trial robustness logic or a separately labeled audit.

## Arc-length route representation

For each valid trajectory:

1. stable-sort by time;
2. retain first duplicate time;
3. calculate consecutive 3-D segment lengths;
4. cumulative path distance;
5. remove repeated cumulative-distance positions caused by zero-length steps;
6. normalize cumulative path distance to [0,1];
7. linearly interpolate x,y,z onto exactly **101 equal arc-length points**.

This is the same route representation used for the Rhino geometry programme.

## Fixed eight scale-free geometry features

Start-center the 101-point route and divide coordinates by the trajectory's own total 3-D path length.

Compute exactly the Rhino features:

1. 3-D path efficiency;
2. horizontal displacement ratio;
3. absolute vertical displacement ratio;
4. vertical range ratio;
5. median absolute horizontal turn angle;
6. p90 absolute horizontal turn angle;
7. median absolute vertical slope;
8. p90 absolute vertical slope.

No time derivative, speed, turn rate per unit time, absolute route length, absolute vertical range, or absolute position enters the feature vector.

All 8 must be finite.
No feature dropping.

## External standardization

Within each source date block and each fixed feature:
- subtract the date-block mean across complete valid trial vectors;
- divide by date-block sample SD.

Require all 8 SDs finite and positive.

This removes date/session scale without fitting an identity axis.

## E1 — fixed full-geometry individual identity

For each target trajectory q from bat i:

- self centroid = equal-trial mean of all other valid trials of i in the same date block;
- donor centroid = equal-trial mean for each other bat in the same date block;
- self distance = Euclidean distance in the fixed 8-D standardized geometry vector;
- donor distance = mean distance to donor centroids, donors weighted equally;
- \(K_q=D_{other}-D_{self}\).

Aggregate:
1. equal target trials within bat;
2. equal bats within date block;
3. equal date-block means.

## Broad turn-condition blocking

The source archive contains source-native turn annotations.

Use the same frozen trial classes as the existing robustness programme:
- \`le90\`
- \`gt90\`
- \`no_annotated_turn\`

The main null permutes bat labels **only within date × turn-class strata**.

This preserves broad corridor/turn-condition exposure and prevents a bat's condition mix from creating apparent geometry identity.

Do not redefine turn classes.

## Exact/Monte Carlo null

9,999 condition-stratified label permutations.

Seed:
\`202610061301\`.

Require >=9,500 valid statistics.

## External support rule

Call the fixed geometry representation externally supported only if all are true:
- overall K > 0;
- one-sided p <= 0.05;
- >=70% of evaluable bats have positive bat-level mean K;
- both date-block mean K values > 0.

## Family localization

After E1, report the Rhino-fixed families descriptively:

### G
global route organization, features 1–4.

### H
horizontal maneuver geometry, features 5–6.

### V
vertical slope geometry, features 7–8.

These are descriptive only and cannot rescue E1.

No Carollia-specific family selection.

## Interpretation

### Supported

Allowed:

> **A scale-free route-geometry representation fixed in Rhinolophus also contains persistent individual information in an independent Carollia navigation system after broad turn-condition exposure is preserved.**

This strengthens generality of distributed coordinative individuality.

It does not establish that:
- the numerical geometry coordinate is identical across species;
- motor degeneracy causes the signal;
- the same feature family dominates both species.

### Unsupported

Allowed:

> scale-free coordinative geometry is strong within Rhinolophus but does not transfer as a general identity representation to this independent Carollia system.

This would narrow the functional-abundance interpretation rather than invalidate the Rhino result.

## No rescue

Do not:
- fit PCA in Carollia;
- change feature signs or weights;
- drop vertical features after output;
- remove a date block;
- select turn classes;
- remove C3_2 from the main result after inspecting E1;
- use speed variables to rescue failed geometry identity.

## JAE firewall

No change to JAE v0.4.0.
