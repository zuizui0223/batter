# Early-experience schema file-opening allowlist v1

## Status

**FROZEN BEFORE ANY DATA ROW VALUE OR NEW HISTORY/repeatability OUTCOME IS OPENED.**

Parent:
`METADATA_PREFLIGHT_CONTRACT_V1.md`

Dataset:
`wh7c636y3t`, version 1.

## Authorized files

### 1. All seasons personality data.xlsx

- id: `97b85935-2a81-4af3-be1e-7ff8cfa1eccc`
- bytes: 44,838
- SHA256: `8155be769fc3e6cf9d3cc0d59fa7c216a176999662cd8272dd99d7741acd723f`

Allow:
- workbook/sheet names;
- used dimensions;
- row-1 headers only.

No row 2+ values.

### 2. Exploraion in squares.xlsx

- id: `74189289-f4ba-4db4-8b33-24be7589dc8f`
- bytes: 13,056
- SHA256: `0e276042876b537df07807fbc6784dfe0ec93fdd034df9f4b095bb6b25a558d0`

Same header-only rule.

### 3. Outdoor data.xlsx

- id: `48df4e40-8f31-4bbd-a854-4078274e8fb1`
- bytes: 52,518
- SHA256: `03a89b2c7de5db56b9776c34a1827f6063da1074909c081e1dbb942f88c9bd0f`

Same header-only rule.

### 4. Calculate_time_and_distance.py

- id: `ebefaa74-0669-4750-8082-15fefc804468`
- bytes: 7,845
- SHA256: `d62ed4c02899749a1deb8d863b0e93aa9b8d0e7e526d253518d77ab2be785d2b`

Allow reading source-code text only to identify:
- input file expectations;
- identity/date fields;
- coordinate field names;
- nightly aggregation logic;
- whether raw GPS is externally referenced but absent.

Do not execute against hidden/unpublished inputs.

## Purpose

Determine whether the public archive supports either:

A. the preregistered route-history treatment test; or, if raw routes are absent,

B. a distinct prospective test of treatment effects on **within-individual temporal repeatability of published nightly behavioural dimensions**.

B is not an automatic rescue. It requires a new biological contract after headers are known and before row values are read.

## Forbidden

At this gate do not read:
- treatment assignments;
- individual outcome values;
- baseline scores;
- nightly movement values;
- route coordinates;
- treatment contrasts;
- repeatability estimates.

## Decision

After header/code inspection:

- if raw or row-level trajectory coordinates are present, continue toward the frozen history-carrier route test;
- if only nightly summaries are present, declare the route-history primary structurally unavailable and decide prospectively whether a separate repeatability test is scientifically worthwhile.
