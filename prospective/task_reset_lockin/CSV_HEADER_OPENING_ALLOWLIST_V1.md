# Task-reset CSV header opening allowlist v1

## Status

**FROZEN BEFORE ANY TRAJECTORY ROW VALUE IS READ.**

Parent:
- `SOURCE_RECEIPT_V1.md`
- `METADATA_PREFLIGHT_CONTRACT_V1.md`
- filename-only architecture audit from Figshare metadata.

## Source files

All 64 files matching:
`Env#_Bat#_no#.csv`

in Figshare article 29209493.

Explicitly excluded at this gate:
- `kiku.pkl`
- `yubi.pkl`

## Authorized operation

For each CSV:

1. use the public Figshare file download URL;
2. request only an HTTP byte range sufficient to contain the first text line;
3. require partial-content behavior or otherwise fail closed;
4. decode only the first line;
5. report the comma-separated column names.

No second line may be parsed or reported.

## Purpose

Determine whether CSV schema directly exposes:
- species;
- individual;
- environment;
- trial/session;
- timestamp/order;
- x/y/z position;
- velocity;
- pulse/acoustic variables;
- obstacle coordinates.

## Species mapping rule

If a source-native species column exists, later structural parsing may use it.

If species is not encoded in the CSV schema, do **not** infer species from:
- coordinate values;
- trajectory shape;
- file size;
- movement speed;
- filename ID ranges.

Instead, species linkage must come from:
- source documentation;
- deterministic relation to `kiku.pkl` / `yubi.pkl` established without opening trajectory outcomes;
- or a new source-provenance amendment.

## Temporal reset rule

A literal temporal reset/re-learning claim is allowed only if source-native metadata or fields establish trial/session ordering across environments.

Environment numbers alone are not assumed to be chronological.

If no chronological ordering field exists:
- downgrade to a configuration-conditioned re-stabilization test;
- do not call it temporal reset or relearning.

## Forbidden

Do not inspect:
- coordinate numbers;
- trajectory lengths;
- velocity values;
- pulse timings;
- obstacle distances;
- route shape;
- first data row values.

## Next decision

After header opening, freeze either:

A. a full temporal reset structural gate; or  
B. a configuration-conditioned individual-policy structural gate; or  
C. STOP if required identity/configuration fields cannot be linked.
