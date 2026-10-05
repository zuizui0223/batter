# Spatial-learning XLSX header opening allowlist v1

## Status

**FROZEN BEFORE ANY ROW-2+ CELL VALUE IS OPENED.**

Parent:
- `SOURCE_RECEIPT_V1.md`
- `METADATA_PREFLIGHT_CONTRACT_V1.md`

Dataset:
Figshare article `19102712`, version 1.

## Authorized files

### A. chain and acryl_environments_flight datasets.xlsx

- Figshare file id: `33969677`
- bytes: `932367`
- MD5: `2226ea5b19fb077ddcce66cb6e97088c`

### B. raw_analysis_data_by_yamada.xlsx

- Figshare file id: `33969680`
- bytes: `18023`
- MD5: `cb7e2f738d85ee80becb5949317ff625`

## Authorized opening

For each workbook:

1. verify filename, byte size and MD5 against the pinned metadata;
2. inspect workbook sheet names;
3. inspect each worksheet used-range/dimension metadata;
4. open **row 1 only** from every worksheet;
5. decode only the shared-string entries referenced by row-1 cells;
6. report row-1 cell references and values.

No cell in row 2 or later may be dereferenced.

## Purpose

Determine which sheet(s) plausibly expose:

- individual bat identity;
- acoustic condition / environment;
- flight or trial number;
- maximum / mean flight speed;
- route width / meandering / lateral deviation;
- pulse count / pulse timing;
- beam/acoustic-gaze variables;
- other source-defined repeated-flight outcomes.

## If row 1 is not the real header

Do not automatically read more rows.

Instead:
- document the row-1 content;
- freeze a second header-location amendment specifying exactly which additional header row(s) may be opened.

## Forbidden

At this gate do not inspect:

- any individual identifier value below a header;
- condition assignments;
- trial numbers;
- speed values;
- route/meandering values;
- pulse values;
- individual means;
- learning slopes;
- individual rank/order;
- any early-versus-late contrast.

## Decision

After this gate, either:

- identify a raw repeated-flight table and freeze a structural row-value allowlist; or
- freeze a limited additional header-location amendment; or
- STOP if the public files do not contain analyzable repeated individual data.
