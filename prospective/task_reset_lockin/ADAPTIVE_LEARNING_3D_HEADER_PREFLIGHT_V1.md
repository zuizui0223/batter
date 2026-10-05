# Adaptive-learning 3-D external header preflight v1

## Status

**OUTCOME-BLIND HEADER-ONLY TRIAGE.**

Candidate source:
Taub & Yovel (2021), adaptive learning and recall of motor-sensory sequences in adult echolocating bats.

Public Mendeley dataset:
- id: `wccbjdrrsg`
- version: 1
- DOI: `10.17632/wccbjdrrsg.1`

## Purpose

Determine whether the public stage-1/stage-3 workbooks retain call-level or trajectory-level 3-D movement coordinates sufficient for an independent fixed-axis policy validation.

## Authorized files

Inspect only workbook structure and row-1 headers from:

- Bat1-stage1.xlsx
- Bat1-stage3.xlsx
- Bat2-stage1.xlsx
- Bat2_stage3.xlsx
- Bat3-stage1.xlsx
- Bat3-stage3.xlsx
- Bat4-stage1.xlsx
- Bat4-stage3.xlsx
- Bat5-stage1.xlsx
- Bat5-stage3.xlsx
- Clutter Chamber Data.xlsx

## Allowed

For every workbook:
- verify public filename, byte size and SHA256 against frozen metadata;
- open XLSX container structure;
- report sheet names;
- report sheet used dimensions;
- report row-1 cell references and header strings only.

## Forbidden

Do not read row 2+ values.

Do not calculate:
- flight features;
- echolocation outcomes;
- stage differences;
- individual identity;
- learning effects.

## 3-D continuation rule

A movement-policy external route may continue only if at least one repeated-data table per bat exposes a reproducible schema containing:
- time/order;
- x;
- y;
- z;

or an explicitly equivalent 3-D position representation.

If public workbooks contain only derived acoustic/sensory summaries, classify:
`STOP_NO_PUBLIC_3D_MOVEMENT_VALUES`.

Do not reinterpret distance-to-target, day, trial, acoustic intensity or IPI as spatial coordinates.
