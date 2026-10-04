# Yamada raw-dataset metadata preflight contract v1

## Status

**OUTCOME-BLIND METADATA PREFLIGHT.**

Dataset:
`10.6084/m9.figshare.19102712.v1`

Expected Figshare article id:
`19102712`.

## Allowed metadata

Read only public Figshare metadata:

- article id/title/DOI/version;
- publication/update dates;
- licence;
- file ids;
- filenames;
- file sizes;
- supplied/computed hashes;
- content type;
- file description;
- download URL as metadata, without downloading file content.

## Structural questions

Determine whether the archive plausibly exposes:

- individual bat identity;
- acoustic condition;
- flight number / trial number;
- maximum flight speed;
- meandering width;
- pulse-count variables;
- pulse-direction variables;
- raw or processed flight trajectories.

No row values may be opened at this step.

## Decision

If one or more tabular files plausibly contain individual × flight rows:
`PASS_TO_SCHEMA_OPENING`.

If the archive contains only aggregated/model output with no individual repeated observations:
`STOP_NO_INDIVIDUAL_LEARNING_SERIES`.

Do not infer schema from published figures if the public dataset itself is insufficient.
