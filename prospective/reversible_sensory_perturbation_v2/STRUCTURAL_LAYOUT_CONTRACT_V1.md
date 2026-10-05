# Reversible sensory structural-layout opening contract v1

## Status

**OUTCOME-BLIND WORKSHEET-LAYOUT OPENING. NUMERIC MOVEMENT/ACOUSTIC VALUES REMAIN CLOSED.**

Parent:
- `SCHEMA_OPENING_CONTRACT_V1.md`
- schema run **37389412739** — PASS

The schema establishes six reproducible individual workbooks and source-named 3-D condition sheets, including:
- `No masker_xyz`;
- `board30_xyz`;
- `board10_xyz`;
- `No masker foam_xyz` or source-equivalent;
- `foam30_xyz` / source-equivalent where present.

## Authorized opening

For the six individual workbooks only, and only sheets whose names contain `xyz` (case-insensitive) or `no masker foam`:

1. inspect all **string-valued cells** and report:
   - cell reference;
   - literal string text;
2. inspect formula text only:
   - cell reference;
   - formula string;
   - never cached numeric result;
3. inspect merged-cell ranges;
4. inspect occupancy structure without decoding numeric values:
   - used dimension;
   - for each column: first occupied row, last occupied row, number of occupied cells;
   - for each row: first occupied column, last occupied column, number of occupied cells;
   - contiguous occupied-column runs;
5. report cell type/style identifiers if useful for structural grouping.

## Forbidden

Do not:
- decode any numeric cell value;
- calculate x/y/z;
- calculate speed, turning, route, angle or condition effect;
- inspect acoustic outcomes;
- infer trial groups from behavioral similarity.

## Structural goal

Determine source-native repeated movement units within each condition sheet.

Preferred structural interpretation:
- explicit string/file labels define trials;

otherwise:
- repeated fixed-width coordinate blocks may be used only if the workbook occupancy/layout establishes them deterministically before numeric values are opened.

## Proceed rule

A numeric support contract may be frozen only if, for >=4 bats and >=3 shared source conditions:

- repeated 3-D units can be partitioned deterministically;
- each unit has a source-defined or layout-defined x/y/z triplet;
- at least 3 candidate repeated units per bat-condition are structurally present.

No numeric support threshold may be chosen after x/y/z values are opened.

## No rescue

Do not select different column grouping after outcomes.
Do not use movement smoothness to infer x/y/z order.
Do not merge/split flights based on trajectory shape.
