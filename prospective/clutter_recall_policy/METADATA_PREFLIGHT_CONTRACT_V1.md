# Clutter recall metadata preflight contract v1

## Status

**OUTCOME-BLIND METADATA PREFLIGHT.**

Dataset:
`10.17632/wccbjdrrsg.1`

Dataset id:
`wccbjdrrsg`
Version:
1.

## Allowed first-pass information

Read public Mendeley metadata only:
- snapshot title;
- version;
- DOI;
- publication date;
- licence;
- folder ids/names;
- filenames;
- file ids;
- file sizes;
- hashes;
- content types;
- file descriptions.

Do not download dataset file contents.

## Structural questions

Determine whether filenames/folder metadata plausibly expose:

1. bat identity;
2. first versus second clutter encounter;
3. same versus enhanced second encounter;
4. date/day/trial structure;
5. pre-takeoff IGI or another source-defined learned sensory-planning endpoint;
6. repeated observations rather than only figure-ready summaries.

## Minimum architecture

A new individual recall endpoint may proceed only if later structural opening can establish:

- at least 4 of the 5 source bats have a reproducible individual ID;
- at least 4 bats have observations in both:
  - late first clutter encounter;
  - second clutter encounter;
- at least 2 observations per bat in each comparison phase, unless the public source itself contains only source-defined phase summaries.

If only phase summaries are public:
- do not invent pseudo-replication;
- a bat-level paired recall diagnostic may be considered under a separately frozen summary-data contract.

## Enhanced-clutter secondary

May open only if:
- the two source-native enhanced-clutter individuals are reproducibly identified;
- their enhanced phase is distinguishable from same-chamber second encounter.

## Stop rules

STOP if:
- only group-level aggregate statistics are public;
- bat IDs cannot be linked across stages;
- the second encounter cannot be distinguished;
- the data release lacks the learned IGI endpoint or a documented equivalent.

No substitution of a different acoustic endpoint after support is inspected without a new contract.
