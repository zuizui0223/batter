# Source B MATLAB-native parser diagnostic result v1

## Status

**PASS — cohort-wide parser repair authorized.**

Authoritative workflow:
- run: **37175878024**
- job: **111358253269**
- conclusion: PASS.

Parent contract:
`SOURCE_B_MATLAB_NATIVE_READER_AMENDMENT_V1.md`.

## Outcome firewall

The deterministic diagnostic printed only:
- MATLAB classes;
- object sizes;
- field / variable names;
- presence and shapes/classes of exact frozen variables `x`, `y`, `time`.

It printed no numeric coordinate or time values and calculated no movement statistic.

## Deterministic probes

### Ali — 2016–2017

- `data`: struct, size 1×70.
- `data(1).track`: struct, size 1×35.
- track fields include exact `x`, `y`, `time`.
- each of the three frozen fields is `double`, size 1×35.

### Anka — 2017–2018

- `data`: struct, size 1×85.
- `data(1).track`: **table**, size 478×18.
- table variables include exact:
  - `x`;
  - `y`;
  - `time`.
- each frozen field is `double`, size 478×1.

## Diagnosis

The previous 2017–2018 zero-support result was caused by a reader mismatch:

- SciPy represents the saved MATLAB table as `MatlabOpaque`;
- native MATLAB restores the table and exposes the exact source fields required by the frozen estimator.

Therefore the 2017–2018 cohort did **not** fail because x/y/time were absent.

## Authorized consequence

Re-run the already frozen coordinate structural gate using MATLAB-native access to the same exact fields.

This is a parser-only repair:
- no variable substitution;
- no change to 30-s standardization;
- no change to >=20 fixes/day;
- no change to >=20 valid days/juvenile;
- no change to donor gate;
- no change to the primary experience estimator.

## Claim boundary

This result is software/provenance evidence only. It contains no biological effect.

## JAE firewall

No effect on JAE v0.4.0.
