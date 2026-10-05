# Public 3-D external candidate XLSX header opening v1

## Status

**FROZEN AFTER METADATA-ONLY INVENTORY AND BEFORE ANY DATA ROW VALUE IS READ.**

Parent:
`PUBLIC_3D_EXTERNAL_CANDIDATE_PREFLIGHT_V1.md`

## Candidate A — pregnancy 2023

Metadata exposed ten individual workbooks:
`Bat 1.xlsx ... Bat 10.xlsx`.

Header-only representatives are fixed as:

- pregnant representative:
  - `Bat 1.xlsx`
  - file id `49856030-9ce0-4082-94ea-7725f89aa3b1`
  - bytes 1,108,243
  - SHA256 `eb358e554b6c25d4837c99b5b1d957dd9c0ed7daaa8a116e71f77f83713b1943`

- post-lactating representative:
  - `Bat 10.xlsx`
  - file id `9726518e-8433-441e-86c8-5009102afbcf`
  - bytes 1,846,191
  - SHA256 `8d18da29b1e5bdc3ba35b2e11683fef1d9591a38373a9147d4c4314770dac003`

Using one representative from each source-defined group prevents choosing a workbook after inspecting schema.

## Candidate B — adaptive learning 2021

Header-only representatives fixed as:

- `Bat1-stage1.xlsx`
  - id `b0304e74-5801-4b7b-ab28-61239cf5e572`
  - bytes 39,136
  - SHA256 `e93d07e05cb35b790432f24ee08bffee3d924e689da131b420f9facf27f8fdb1`

- `Bat1-stage3.xlsx`
  - id `e3c1a9b4-79aa-496f-9c0f-7a35a7369e0e`
  - bytes 61,181
  - SHA256 `1219dc8da7886485d95d35e7968711e9009cbf84314d81a0e14677cc5a583c1f`

- `Clutter Chamber Data.xlsx`
  - id `68317f75-3a03-4756-b7e5-3f5fd94853d5`
  - bytes 1,435,343
  - SHA256 `bc1b2b40c5e3198a2cccd9211fa1e001d8b23e71833b784a9803781a83b31032`

## Authorized operation

For each frozen workbook:

1. verify public file metadata, size and SHA256;
2. open the XLSX ZIP container;
3. read only:
   - workbook sheet names;
   - sheet used-dimension reference;
   - **row 1 cell values**;
4. shared-string text may be resolved only for row-1 cells.

Do not inspect:
- row 2+ values;
- formulas outside row 1;
- charts/caches;
- pivot caches;
- embedded media.

## Structural decision

A candidate becomes `RAW_3D_PLAUSIBLE` only if headers explicitly expose a source-compatible combination such as:

- Time/frame/trial plus X/Y/Z;
- bat center-of-mass X/Y/Z;
- 3-D position/trajectory coordinates.

Derived parameters such as:
- max speed;
- altitude;
- curvature;
- IPI;
- signal duration

without raw X/Y/Z are **summary-only** and do not validate the fixed 3-D two-axis policy.

If sheet structure is ambiguous but includes likely raw coordinate tables, freeze a row-value structural allowlist before opening any outcome.
