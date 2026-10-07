# Route-centroid compression diagnostic contract v1

## Status

**POST-PRIMARY MECHANISM/COMPRESSION DIAGNOSTIC. NOT CONFIRMATORY.**

Frozen after:
- within-configuration absolute-route identity passed;
- start-centered route identity failed;
- chord-residual route identity failed;
- start, end and displacement-vector identity failed;
- route-centroid identity passed;
- centroid-centered route identity failed.

No held-out reconstruction comparison among the models below has been calculated before this contract.

## Question

Can the configuration-specific personal route be compressed from a 101-point 3-D curve to only a 3-D personal route centroid without materially losing held-out predictive information?

This directly tests whether the task-specific individual term behaves like a finite low-dimensional placement parameter rather than a persistent high-dimensional curve.

## Data and eligibility

Use exactly:
- authoritative *Rhinolophus nippon* route-valid trajectories;
- Primary-A eligible environments Env1–Env3;
- the frozen 101-point arc-length-normalized route representation.

A target trajectory is evaluable only when its bat has at least one other route-valid trajectory in that environment.

Aggregation follows Primary A:
- equal target trajectory within bat;
- equal bat within environment;
- equal environment.

## Three held-out reconstruction models

For target trajectory q from bat i in environment e, remove q from every training quantity.

### M0 — other-bat environment template

For each donor bat j != i:
- average all donor training routes within j;
- then average donor-bat mean routes equally.

This gives the environment template

[
R^{other}_{e,-q}(s).
]

M0 prediction:
[
hat R_0(s)=R^{other}_{e,-q}(s).
]

### M1 — environment shape + personal 3-D centroid

Center each donor-bat mean route by its own 3-D route centroid.

Average these centered donor shapes equally to obtain

[
S^{other}_{e,-q}(s).
]

From the focal bat's remaining same-environment routes estimate its mean 3-D centroid:

[
hat c_{i,e,-q}.
]

M1 prediction:
[
hat R_1(s)=S^{other}_{e,-q}(s)+hat c_{i,e,-q}.
]

M1 contains exactly three focal-specific route parameters: centroid X,Y,Z.

### M2 — full personal mean route

Average the focal bat's remaining same-environment 101-point routes:

[
hat R_2(s)=mean(R_{i,e,-q}(s)).
]

This carries the full spatially resolved personal route.

## Error

For each model:
[
E_m(q)=mean_s ||R_q(s)-hat R_m(s)||_2.
]

Primary summaries:
- E0, E1, E2 under equal-target → equal-bat → equal-environment weighting;
- centroid gain:
  [
  I_c=E_0-E_1;
  ]
- full-personal gain:
  [
  I_f=E_0-E_2;
  ]
- extra-shape gain beyond centroid:
  [
  I_s=E_1-E_2;
  ]
- centroid retention:
  [
  R_c=I_c/I_f
  ]
  when I_f>0.

## Frozen descriptive compression rule

Call the route individuality **centroid-compressible** if:
- I_c > 0;
- I_f > 0;
- R_c >= 0.80;
- and I_s <= 0.20 * I_f.

The 80% rule is a descriptive compression threshold, not an equivalence test.

## Label-permutation calibration

Within every eligible environment independently:
- permute complete bat labels among route trajectories;
- preserve label multiplicities;
- recompute M0/M1/M2 and I_c.

9,999 permutations.
Seed: 20261007921.

Primary one-sided centroid-information p:
[
p_c=(1+#{I_{c,null}>=I_{c,obs}})/10000.
]

Report but do not use permutation p for the retention ratio.

## Interpretation

### Centroid-compressible

A 3-D personal lane/placement vector preserves most held-out route information attributable to individual identity. The observed task-specific personal state is therefore much lower-dimensional than the raw 303-coordinate trajectory.

### Not centroid-compressible

Personal route information requires additional within-route shape beyond mean 3-D placement.

## Ceiling

Even centroid-compressibility does not imply:
- the centroid is cognitively encoded;
- route shape contains no biological information;
- three parameters determine the exact instantaneous trajectory;
- centroid placement is invariant across obstacle configurations.

It only identifies the dimension of the repeated same-configuration personal route component supported by this archive.
