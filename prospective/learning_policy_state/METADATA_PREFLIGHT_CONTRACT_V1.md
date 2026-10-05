# Spatial-learning raw-data metadata preflight contract v1

## Status

**OUTCOME-BLIND METADATA PREFLIGHT.**

No file content or row value may be downloaded/opened in this gate.

## Dataset

Figshare article:
`19102712`

Version:
v1.

Expected total public size:
approximately 928 kB.

## Authorized metadata

Use the public Figshare API to read only:

- article id;
- title;
- DOI;
- version;
- publication/modification date;
- licence;
- file id;
- filename;
- file size;
- supplied/computed MD5;
- file description;
- download URL as metadata only.

Do not follow download URLs.

## Structural questions

From filenames/metadata only determine whether the archive plausibly contains:

1. raw/row-level behavioural tables;
2. individual identity;
3. acoustic condition;
4. repeated-flight number/order;
5. flight speed;
6. route/meandering metric;
7. pulse count/timing/direction;
8. any processed-model-only files.

## Next gate

If one or more tabular raw-data files are present:

- freeze a header-only opening allowlist;
- inspect only file schema/header names;
- do not open row 2+ values.

If only processed/statistical outputs are present:
- STOP the prospective individual-learning-state analysis.

## Outcome firewall

Do not calculate or inspect:

- trial trajectories;
- individual means;
- learning slopes;
- condition effects;
- rank stability;
- random-intercept variance;
- pulse changes;
- path-width changes.
