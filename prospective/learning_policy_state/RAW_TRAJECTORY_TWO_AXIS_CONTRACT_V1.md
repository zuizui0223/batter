# Raw-trajectory two-axis learning maintenance contract v1

## Status

**PROSPECTIVE EXTERNAL POLICY-AXIS REPLICATION — frozen before any trajectory row value is opened.**

Branch:
`prospective/learning-policy-state-v1`

Parent gates:
- `RAW_TRAJECTORY_LINKAGE_CONTRACT_V1.md`
- linkage result: **28/28 sheets linked to 14/14 subjects, no ambiguity**.

## Aim

Test whether the two transparent policy coordinates derived independently from the Teshima 2026 *Rhinolophus nippon* obstacle-flight dataset also carry individual identity across first-to-twelfth learning in the Yamada 2020 experiment.

This is an external replication of the **policy representation**, not of identical obstacle geometry.

## Source workbook

`chain and acryl_environments_flight datasets.xlsx`

Pinned:
- Figshare file id `33969677`
- bytes `932367`
- MD5 `2226ea5b19fb077ddcce66cb6e97088c`

Use only the 28 trajectory sheets frozen by the linkage result.

## Authorized raw columns

From each linked trajectory sheet read only:

- A: `time[s]`
- B: `bat(X)[mm]`
- C: `bat(Y)[mm]`
- D: `bat(Z)[mm]`

Do **not** read source-provided velocity, turn-rate, pulse or obstacle columns for the primary.

Coordinates are converted from mm to m.

## Common trajectory cleaning

For each sheet:

1. retain rows where time, X, Y, Z are finite;
2. stable-sort by time ascending;
3. retain the first row for duplicated timestamps;
4. require >=100 retained rows;
5. require >=50 strictly positive consecutive time intervals;
6. no smoothing or manual clipping.

A subject is evaluable only if both its linked trial-1 and trial-12 sheets pass.

Primary opens only if:
- >=12 evaluable subjects total;
- >=5 evaluable subjects per acoustic condition.

No support threshold relaxation.

## Eight movement-policy features

Derive exactly the same eight feature definitions used in the task-reset programme.

For positive-time consecutive intervals:

1. median 3-D speed;
2. p90 3-D speed;
3. median absolute vertical speed;
4. p90 absolute vertical speed;
5. median absolute horizontal turning rate;
6. p90 absolute horizontal turning rate;
7. path efficiency;
8. vertical range.

Definitions:

[
v_{3D}=
rac{sqrt{dx^2+dy^2+dz^2}}{dt}
]

[
v_z = |dz|/dt.
]

Horizontal heading:
[
phi=mathrm{atan2}(dy,dx).
]

Wrapped consecutive heading change:
[
Deltaphi=
mathrm{atan2}(sin(phi_t-phi_{t-1}),
              cos(phi_t-phi_{t-1})).
]

Turning-rate divisor:
[
dt_{turn}=(dt_t+dt_{t-1})/2.
]

Absolute horizontal turning rate:
[
omega=|Deltaphi|/dt_{turn}.
]

Require >=20 finite turning-rate values.

Path efficiency:
[
rac{	ext{first-to-last 3-D displacement}}
     {	ext{total 3-D path length}}.
]

Vertical range:
[
max Z-min Z.
]

All calculations use float64.

## Relative-policy standardization

For each of the eight features separately within every:

`condition × trial`

cell:

- subtract arithmetic mean;
- divide by sample SD.

All required SDs must be finite and >0.

This removes the shared learning shift and acoustic-condition scale before asking whether relative individual policy coordinates persist.

## Transparent policy axes

Use the exact frozen definitions from the task-reset programme.

### FlightIntensity

[
I=mathrm{mean}(z_1,z_2,z_3,z_4).
]

### ManeuveringExtent

[
M=mathrm{mean}(-z_1,z_5,z_6,z_7,z_8).
]

No fitted weights, PCA refitting or endpoint selection is allowed.

---

# Primary R1 — transparent two-axis maintenance

For every evaluable subject i:

[
u_{it}=(I_{it},M_{it}).
]

Within its acoustic condition:

- `D_self = ||u_i1-u_i12||`;
- `D_other` = mean distance from `u_i1` to trial-12 states of all other subjects.

[
K_i=D_{other}-D_{self}.
]

Aggregate:
- equal subject mean within condition;
- equal mean of the two conditions.

Call this `K_IM`.

## Null

Independently within each condition:
- permute complete trial-12 ((I,M)) labels among subjects;
- keep trial-1 labels fixed.

9,999 permutations.

Seed:
`202610050951`.

## Frozen support rule

R1 supported only if:
- K_IM > 0;
- p <= 0.05;
- >=70% of evaluable subjects have K_i > 0.

With 14 subjects this requires >=10 positive.

---

# Secondary R2 — axis-specific maintenance

Repeat the same identity architecture separately using scalar absolute distance for:

- I only, seed `202610050952`;
- M only, seed `202610050953`.

These cannot rescue R1.

---

# Secondary R3 — full eight-dimensional maintenance

Use ordinary Euclidean distance in the complete condition × trial standardized 8-D feature vector.

Same within-condition trial-12 label permutation.

Seed:
`202610050954`.

This asks whether the transparent two-axis result retains the same direction as the full measured policy.

It cannot rescue R1.

---

# Descriptive learning vector in fixed baseline coordinates

For each acoustic condition separately:

1. estimate feature means and SDs from **trial 1 only**;
2. use those trial-1 scaling parameters on both trial 1 and trial 12;
3. compute I and M with the same transparent formulas;
4. report condition mean ((I,M)) at trial 1 and trial 12;
5. report the mean learning displacement vector.

No inferential p-value is attached to this quantity because the group learning effect is already published.

This descriptive vector distinguishes:
- policy **updating** in absolute baseline coordinates;
from
- relative personal-state **maintenance** in R1.

## Interpretation

### R1 supported

Strong external bridge:

> the same transparent two-axis policy representation that carries identity across obstacle configurations also preserves individual position across repeated spatial learning in an independent *R. nippon* experiment.

### R1 unsupported but summary-endpoint primary supported

Maintenance is real in speed/meandering space, but the exact Teshima-derived transparent policy axes do not externally replicate.

### R1 and R3 unsupported

Do not claim a common low-dimensional policy representation across experiments.

## Ceiling

Even successful external replication does not identify whether persistent policy coordinates originate from:
- morphology;
- physiology;
- developmental history;
- prior learning;
- neural control.

## JAE firewall

No result changes JAE v0.4.0.
