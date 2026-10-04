# Naive-to-familiar metadata preflight contract v1

## Status

**OUTCOME-BLIND METADATA PREFLIGHT.**

Public source:
Figshare DOI `10.6084/m9.figshare.19102712.v1`.

No dataset file content may be downloaded in this stage.

## Allowed metadata

Read only through the public Figshare API:

- article id/title/DOI/version;
- publication/modification date;
- licence;
- file ids;
- filenames;
- file sizes;
- hashes;
- download URLs as metadata only;
- public descriptions.

## Structural questions

Determine whether filenames/metadata expose or plausibly encode:

1. bat identity;
2. acoustic condition;
3. repeated-flight number 1–12;
4. trajectory coordinates;
5. pulse timing/emission information;
6. pulse direction if present;
7. fixed-start or obstacle geometry files if present.

## Minimum architecture

The programme may proceed toward an individual-policy formation test only if metadata support is consistent with:

- >=5 independent bats total;
- repeated observations spanning at least flights 1 and 12;
- bat identity recoverable;
- flight order recoverable without outcome inspection.

Preferred:
- >=5 bats with >=8 recoverable flight numbers.

If the metadata do not expose these fields directly, do not declare scientific failure. Freeze a header/schema-only file-opening amendment.

## No-outcome list

At this stage do not inspect:

- coordinates;
- flight speed;
- route width;
- pulse counts;
- pulse timing;
- pulse direction;
- individual differences;
- flight-number trends.

## Decision

Return:

- `PASS_TO_SCHEMA_OPENING`;
- `STOP_INSUFFICIENT_METADATA_ARCHITECTURE`; or
- `SCHEMA_OPENING_REQUIRED`.

No thresholds may be lowered after file contents are opened.
