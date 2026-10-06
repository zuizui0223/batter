# Public obstacle-geometry availability result v1

## Status

**STOP — NO PUBLIC OBSTACLE-GEOMETRY SCHEMA RECOVERED.**

The purpose of this programme was to test whether solution abundance could be defined from obstacle geometry alone, independently of realized bat trajectories.

## Public Figshare inventory

Article:
`29209493`

Metadata inventory shows:
- trajectory CSV files named by Env × Bat × trial;
- `kiku.pkl`;
- `yubi.pkl`;
- no standalone obstacle/layout geometry file.

## Pickle structure-only probe

Authoritative workflow:
- run: **37393116306**
- job: **112042619777**
- conclusion: **success**

Probe constraints:
- first 16 MiB only;
- HTTP Range;
- pickle never executed;
- numeric payload never decoded.

Result:
- `kiku.pkl`: no obstacle/layout/arena/geometry structural key candidate;
- `yubi.pkl`: no obstacle/layout/arena/geometry structural key candidate;
- no source-native Env token recovered in the scanned prefix;
- only generic x/y/z-like byte tokens were present.

Verdict:

`STOP_NO_PUBLIC_OBSTACLE_GEOMETRY_SCHEMA`

## Consequence

Do not define environmental solution abundance using:
- observed trajectory dispersion;
- number of recorded trajectories;
- route-cluster count;
- VRNN prediction error;
- individual policy dispersion;
- file size.

Those quantities are outcomes or sampling properties and would make an abundance-to-specialization test circular.

## What remains supported

A scale-free route-geometry personal signature is supported independently:

- K_geometry = **+0.38857**;
- 5/5 bats positive;
- p = **0.0153**.

This shows individual movement organization extends beyond speed/performance magnitude.

It does **not** measure the number of feasible environmental solutions.

## Next route

A direct solution-abundance test requires either:
- source-provided obstacle coordinates/layouts;
- a new experiment with designed corridor/obstacle geometry;
- or another public source where feasible paths are specified independently of animal behavior.

## JAE firewall

No change to JAE v0.4.0.
