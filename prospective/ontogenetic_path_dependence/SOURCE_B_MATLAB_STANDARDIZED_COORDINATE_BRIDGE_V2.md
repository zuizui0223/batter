# Source B MATLAB-to-Python standardized coordinate bridge v2

## Status

**PARSER BRIDGE CONTRACT — supersedes v1 before bridge execution and before the primary biological outcome is opened.**

Supersession reason:
`SOURCE_B_PERMUTATION_ELIGIBILITY_CLARIFICATION_V1.md` makes explicit that juveniles with fewer than 20 valid days can remain eligible **other** donors at early target ordinals. The bridge must therefore retain their frozen valid-day history rather than exporting only primary targets.

No biological outcome has been inspected.

## Parent contracts

- `SOURCE_B_SELF_HISTORY_ESTIMATOR_CONTRACT_V1.md`
- `SOURCE_B_COORDINATE_STRUCTURAL_OPENING_V1.md`
- `SOURCE_B_MATLAB_NATIVE_READER_AMENDMENT_V1.md`
- `SOURCE_B_PERMUTATION_ELIGIBILITY_CLARIFICATION_V1.md`

## Purpose

Native MATLAB restores both archive serializations:
- 2016–2017 struct-array `track`;
- 2017–2018 table `track`.

MATLAB performs only the already-frozen within-day standardization, then writes simple numeric arrays for one common Python inferential pipeline.

## Input fields

Exact source fields only:
- `data(day).track.x`;
- `data(day).track.y`;
- `data(day).track.time`.

## Frozen within-day standardization

1. finite x/y/time;
2. chronological sort;
3. seconds relative to first retained fix;
4. 30-second bins;
5. first fix per bin;
6. no interpolation;
7. no smoothing;
8. valid day = >=20 standardized fixes.

Valid days retain source chronology.

## Bridge payload

For **every ordinary juvenile**, write one MATLAB v7 file containing:

- `xyDays`: a cell array of the first `min(20, n_valid_days)` structurally valid days;
- each cell: N×2 double x/y array.

No day after valid-day ordinal 20 is needed for the frozen primary.

Manifest:
- cohort;
- individual;
- full-source valid-day count;
- number of exported days;
- bridge filename.

Primary targets are later restricted to juveniles with >=20 valid days.

Shorter histories can serve only as other donors when they satisfy the target-specific >=t rule.

## Forbidden output

No:
- self/other distances;
- route overlap;
- destination information;
- R, B, L;
- permutation result;
- map.

## Precision

MATLAB `save(...,'-v7')`, native doubles. No CSV coordinate rounding.

## Downstream Python

Must implement the already-frozen estimator and the v1 permutation clarification exactly.

## Stop rule

Execute only after MATLAB-native coordinate structural support is adjudicated.

## JAE firewall

No effect on JAE v0.4.0.
