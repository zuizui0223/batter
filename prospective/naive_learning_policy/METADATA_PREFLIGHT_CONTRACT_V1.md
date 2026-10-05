# Naive-learning Figshare metadata preflight contract v1

## Status

**OUTCOME-BLIND METADATA PREFLIGHT.**

Dataset:
Figshare article `19102712`, version 1.

No dataset file content may be downloaded at this stage.

## Allowed public metadata

Read only:

- article id;
- title;
- DOI;
- version;
- published / modified date;
- licence;
- description;
- file id;
- filename;
- file size;
- supplied/computed MD5;
- content type or link-only status where available.

## Structural questions

From filenames and metadata alone determine whether the archive plausibly contains:

1. bat identity;
2. acoustic condition;
3. flight number / repetition order;
4. movement trajectory coordinates or source movement summaries;
5. pulse / acoustic variables;
6. obstacle geometry or source code;
7. one file per bat/flight versus pooled tables.

## Minimum architecture

Proceed to schema opening only if metadata supports at least one of:

### Route A — repeated row-level movement
- >=10 individual bats represented;
- repeated observations or files plausibly spanning flight order;
- source data sufficient to recover at least a movement-control variable per individual × flight.

### Route B — source-level individual summary
- exact bat identity;
- flight 1 and flight 12 values for >=10 bats;
- at least one movement-control response.

If neither is plausible:
`STOP_INSUFFICIENT_PUBLIC_ARCHIVE`.

## No-outcome rule

Do not:

- inspect numerical data values;
- infer learning direction from file size;
- calculate first-vs-last differences;
- classify bats by apparent trajectories;
- read spreadsheet row 2+ or CSV row 2+.

## Next gate

If metadata passes:

- freeze exact file-content/header opening;
- inspect only workbook sheets/headers or CSV header lines;
- then freeze policy and learning endpoints before data values.
