# Naive-learning XLSX schema opening allowlist v1

## Status

**FROZEN BEFORE ANY DATA ROW VALUE IS READ.**

Parent:
- `SOURCE_RECEIPT_V1.md`
- `METADATA_PREFLIGHT_CONTRACT_V1.md`
- `BIOLOGICAL_CONTRAST_CONTRACT_V1.md`

Dataset:
Figshare article `19102712`, version 1.

## Authorized files

### Flight dataset workbook

Filename:
`chain and acryl_environments_flight datasets.xlsx`

Figshare file id:
`33969677`

Bytes:
`932367`

MD5:
`2226ea5b19fb077ddcce66cb6e97088c`

### Analysis-summary workbook

Filename:
`raw_analysis_data_by_yamada.xlsx`

Figshare file id:
`33969680`

Bytes:
`18023`

MD5:
`cb7e2f738d85ee80becb5949317ff625`

## Authorized operations

For both workbooks:

1. download exactly the pinned public file;
2. verify size and MD5;
3. inspect ZIP/XLSX structure;
4. report workbook sheet names;
5. report each worksheet used dimension;
6. read **row 1 only** from every sheet and report cell/header text;
7. report merged-cell metadata if it affects row 1.

No row 2+ cell value may be dereferenced.

## Purpose

Determine whether source data expose:

- bat identity;
- acoustic condition;
- flight number;
- time;
- x/y(/z) position;
- speed;
- pulse/acoustic variables;
- precomputed source responses such as maximum flight speed or meandering width.

## Next gate

After header opening:

- choose the minimum source variables needed for the naive→late policy test;
- freeze exact row-value columns and support thresholds;
- only then open row values.

## Forbidden

Do not read:
- numerical flight values;
- first-vs-twelfth differences;
- individual rankings;
- route coordinates;
- pulse counts;
- any outcome in rows 2+.

Do not select a response because it appears to show strong individual separation.
