# Yamada workbook schema-opening contract v1

## Status

**FROZEN BEFORE ANY DATA ROW (row 2+) VALUE IS OPENED.**

Parent:
`METADATA_PREFLIGHT_CONTRACT_V1.md`

Dataset:
`10.6084/m9.figshare.19102712.v1`.

## Authorized files

### File A
- name: `chain and acryl_environments_flight datasets.xlsx`
- Figshare id: `33969677`
- bytes: 932,367
- MD5: `2226ea5b19fb077ddcce66cb6e97088c`

### File B
- name: `raw_analysis_data_by_yamada.xlsx`
- Figshare id: `33969680`
- bytes: 18,023
- MD5: `cb7e2f738d85ee80becb5949317ff625`

## Authorized opening

For each workbook:

- workbook sheet names;
- worksheet XML used dimension;
- row-1 cell references;
- row-1 header text only.

If headers are stored as shared strings:
- resolve only shared-string indices referenced by row 1;
- do not report or materialize unrelated shared strings.

## Forbidden

Do not read or report:
- any cell in row 2 or later;
- speed values;
- flight number values;
- bat IDs;
- acoustic-condition row values;
- trajectory coordinates;
- pulse variables.

## Structural questions

Determine whether one or more sheets expose headers compatible with:
- bat identity;
- condition;
- flight/trial number;
- maximum flight speed;
- meandering width;
- pulse counts/directions;
- raw x/y/time or trajectory data.

## Decision

If a tabular sheet exposes at minimum:
- individual identity;
- repeated-flight identity;
- one speed variable,

freeze a row-value structural allowlist next.

Otherwise STOP the personal-learning-state endpoint.
