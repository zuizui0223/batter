# Source B MATLAB-to-Python standardized coordinate bridge v1

## Status

**PARSER BRIDGE CONTRACT — may execute only if the MATLAB-native coordinate structural gate passes.**

Parent:
- `SOURCE_B_SELF_HISTORY_ESTIMATOR_CONTRACT_V1.md`
- `SOURCE_B_COORDINATE_STRUCTURAL_OPENING_V1.md`
- `SOURCE_B_MATLAB_NATIVE_READER_AMENDMENT_V1.md`

## Purpose

The 2016–2017 archive stores `track` as a MATLAB struct array, whereas 2017–2018 stores `track` as a MATLAB table.

The frozen scientific estimator is independent of this serialization difference.

To avoid implementing two scientific pipelines, native MATLAB will perform **only the already-frozen within-day sampling standardization**, then write simple numeric day arrays that Python can read identically across cohorts.

## Allowed MATLAB input

Exact source fields only:
- `data(day).track.x`;
- `data(day).track.y`;
- `data(day).track.time`.

No longitude/latitude substitution.

## Frozen standardization

Exactly as frozen before coordinate outcome opening:

1. finite x/y/time;
2. chronological sort;
3. seconds relative to first retained fix;
4. 30-second bins;
5. first fix in each bin;
6. no interpolation;
7. no smoothing;
8. structurally valid day = >=20 standardized fixes.

Valid days retain their original chronological order.

## Bridge payload

For each primary-eligible juvenile, write:

- one MATLAB v7 file;
- variable `xyDays`: 1×20 cell array;
- each cell: N×2 double matrix with standardized x,y for valid-day ordinals 1..20.

Only the **first 20 structurally valid days** are exported because the frozen primary target horizon is ordinals 3..20 and uses no later day.

Also write a manifest containing:
- cohort;
- individual;
- source data.mat file ID/hash;
- number of valid days in the full source;
- bridge filename;
- bridge SHA256.

Do not write:
- route distances;
- home ranges;
- destination labels;
- any self/other statistic;
- B, R, or L.

## Precision

Use MATLAB `save(...,'-v7')` with native double precision. Python must read the doubles without rounding or CSV conversion.

## Python outcome

The downstream Python outcome must use the bridge arrays exactly and implement the already-frozen:
- history cap 5;
- target ordinals 3..20;
- same-cohort donor rule;
- minimum 3 donors;
- point-to-history minimum Euclidean distance;
- equal history-day and donor weighting;
- B_i Spearman experience slope;
- equal-individual B;
- 9,999 whole-history identity permutations;
- seed 20261004021;
- 70% individual-direction rule;
- secondary late L.

## No scientific rescue

This bridge is serialization repair only. It cannot alter any biological design choice.

## Stop rule

If the MATLAB-native structural gate does not pass, do not execute this bridge.

## JAE firewall

No effect on JAE v0.4.0.
