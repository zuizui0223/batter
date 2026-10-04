# Task-reset lock-in metadata preflight contract v1

## Status

**OUTCOME-BLIND METADATA PREFLIGHT.**

No trajectory coordinate, velocity, turning angle, pulse series, route similarity or model prediction may be opened at this stage.

## Public source

Figshare article id:
`29209493`

Expected title:
*Flight policy in obstacle space: estimation from imitation learning in two echolocating bat species*

## Allowed metadata

From the public Figshare API read only:
- article title;
- DOI;
- version;
- publication/posting timestamps;
- licence;
- file id;
- filename;
- file size;
- supplied md5 if available;
- file download URL only as metadata, without downloading file content;
- file description if available.

## Structural questions

Determine from filenames/metadata alone whether the archive can plausibly expose:

1. species identity;
2. individual bat identity;
3. arena / obstacle-layout identity;
4. repeated trials per individual × arena;
5. any ordering/session/date information;
6. coordinate trajectory files;
7. obstacle geometry files;
8. pulse/acoustic files if present.

## Minimum architecture for a reset test

A full individual reset/re-stabilization endpoint may proceed only if metadata suggests at least one species has:

- >=3 individual bats;
- >=3 distinct obstacle layouts per bat;
- >=3 repeated trajectories within at least two layouts per bat.

This metadata criterion is intentionally permissive. A later row/content structural gate will be stricter.

If metadata cannot resolve those dimensions, do not infer failure; freeze a limited file-header/content allowlist before deciding.

## Strong reset architecture

Preferred source structure:

- repeated flights in layout A;
- switch to layout B;
- repeated flights in B;
- trial/session order recoverable.

If chronological transition order is unavailable, the programme may still test **configuration-conditioned re-stabilization**, but must not claim literal temporal reset/relearning.

## No-outcome list

Do not calculate:
- within-layout route similarity;
- across-layout route similarity;
- individual classification;
- VRNN predictions;
- obstacle clearance;
- turning distributions;
- path entropy;
- route stereotypy.

## Decision outputs

Return one of:

- `PASS_TO_SCHEMA_OPENING`
- `PASS_CONFIGURATION_ONLY_NO_TEMPORAL_RESET`
- `STOP_INSUFFICIENT_METADATA_ARCHITECTURE`

The last status is only appropriate if even filenames/metadata establish inadequate replication.
