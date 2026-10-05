# Neural-silencing Zenodo metadata preflight contract v1

## Status

**OUTCOME-BLIND ZENODO METADATA PREFLIGHT. NO DEPOSITED FILE CONTENT MAY BE DOWNLOADED.**

Parent:
`SOURCE_RECEIPT_V1.md`

Zenodo DOI:
`10.5281/zenodo.13857870`

## Allowed operation

Query public Zenodo record metadata only.

Primary metadata endpoint:
`https://zenodo.org/api/records/13857870`

Allowed fields:
- record id;
- DOI / concept DOI;
- title;
- publication date;
- version;
- license;
- creators;
- file keys/names;
- file byte sizes;
- checksums;
- content types if exposed;
- file links **as metadata strings only**.

Do not follow file-content links.

## Structural questions

Determine from filenames and metadata only:

1. which files contain trajectory data;
2. which contain behavioral/session metadata;
3. which contain source code;
4. whether files are archives, MAT files, spreadsheets or text/code;
5. whether filename architecture exposes bat IDs, treatment conditions or sessions;
6. whether the complete deposited archive is small enough for later bounded structural inspection.

## Classification

By filename only:
- `TRAJECTORY_PLAUSIBLE`
- `BEHAVIOR_PLAUSIBLE`
- `VOCAL_PLAUSIBLE`
- `ABR_PLAUSIBLE`
- `CODE_PLAUSIBLE`
- `UNKNOWN`

## Proceed rule

A schema opening may proceed if:
- at least one trajectory-plausible file is public;
- at least one behavior/session-metadata or code file can plausibly map trajectories to bat/treatment;
- file sizes are explicitly known so bounded download budgets can be frozen first.

## No rescue

Do not:
- download a file just because its name is ambiguous;
- open trajectory values before bat/treatment linkage is structurally defined;
- select only files likely to reproduce a published positive condition effect.
