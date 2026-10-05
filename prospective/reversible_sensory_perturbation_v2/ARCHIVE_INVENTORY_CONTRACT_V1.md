# Reversible sensory perturbation archive inventory contract v1

## Status

**OUTCOME-BLIND ZIP CENTRAL-DIRECTORY OPENING. NO MEMBER CONTENT MAY BE READ.**

Parent:
- `METADATA_PREFLIGHT_CONTRACT_V1.md`
- metadata run **37307474636** — `PASS_PUBLIC_RESOLUTION`
- `SOURCE_DESIGN_SEQUENCE_V1.md`

The source-declared Dropbox currently resolves to:
- HTTP 200;
- `application/zip`;
- Content-Disposition filename `Taub&Yovel_2019.zip`;
- Content-Length **1,672,094 bytes**.

## Authorized operation

Download the exact source-declared ZIP with a hard maximum budget of **2,500,000 bytes**.

Read only the ZIP central directory.

For every archive member report:
- path/name;
- compressed size;
- uncompressed size;
- CRC32;
- compression type;
- directory flag.

Do **not**:
- read member bytes;
- extract members;
- parse CSV/MAT/XLSX/text;
- inspect headers inside members;
- calculate movement or acoustic values.

## Structural questions

Determine from member names only whether the archive plausibly exposes:

1. biological bat identity;
2. source condition/block labels;
3. repeated trials/flights;
4. movement/trajectory files;
5. 3-D coordinates or position-tracking data;
6. acoustic-only versus movement-containing branches.

## Classification

Each member may be assigned only by filename/path to:
- `MOVEMENT_PLAUSIBLE`;
- `ACOUSTIC_PLAUSIBLE`;
- `METADATA_OR_CODE`;
- `UNKNOWN`.

No classification may use file contents.

## Proceed rule

A header/schema opening may proceed if the filename architecture exposes at least:
- >=4 reproducible biological individuals;
- >=2 sensory conditions or source blocks;
- repeated movement-plausible members;
- a deterministic subset of members whose schemas can be opened without inspecting outcomes.

If filenames are opaque but contain plausible movement files, freeze a deterministic header-only sample rule before reading any member bytes.

## No rescue

Do not select members after inspecting numerical values.
Do not infer condition from file size or movement phenotype.
Do not open acoustic data merely because movement naming is ambiguous.
