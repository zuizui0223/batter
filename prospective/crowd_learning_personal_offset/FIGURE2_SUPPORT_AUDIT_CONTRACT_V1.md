# Prat 2017 Figure-2 support audit contract v1

## Status

**STRUCTURAL SUPPORT AUDIT ONLY. LD1/LD2 MAGNITUDES REMAIN CLOSED.**

Parent:
- `AUDIT_CONTRACT_V1.md`
- `S1_DATA_SCHEMA_V1.md`

## Authorized opening

From the `Figure 2` sheet, use row-2 labels only to identify the frozen source columns for:
- sessions 1–4;
- groups High-F0 / Low-F0 / Control;
- bats 1–4 in High-F0;
- bats 1–5 in Low-F0;
- bats 1–5 in Control;
- LD1 / LD2 paired columns.

For every pup × session unit, report only:
- LD1 numeric-cell count;
- LD2 numeric-cell count;
- number of rows where both LD1 and LD2 are finite numeric values.

Do **not** report:
- any LD coordinate magnitude;
- means / medians;
- distances;
- group differences;
- identity statistics.

## Frozen support floor

A pup × session unit is primary-eligible if it has at least **5 finite paired LD1/LD2 calls**.

This threshold is frozen before LD magnitudes are opened. It is deliberately below the smallest structural column count already visible in the schema audit (8), while requiring repeated call support rather than a single call.

## Proceed gate

Proceed to the numeric identity primary only if:
- exactly 56 pup × session units are reconstructed;
- all expected 14 pups are represented in all 4 sessions;
- every unit has >=5 finite paired calls;
- each LD1/LD2 column pair has the same source group, bat and session label.

If any condition fails:

`STOP_FIGURE2_REPEATED_SUPPORT`

No pup, group, session or coordinate may be dropped to rescue the primary.

## Zero handling

Zero is a valid LDA coordinate and is **not** treated as a missing-value sentinel.
Only nonnumeric / nonfinite / blank cells are excluded.

## Numeric opening after PASS

If this gate passes, the later frozen state for each pup × session will be the equal-call arithmetic mean of all finite paired LD1/LD2 rows in the source column pair.

The biological unit remains the pup; unequal call counts do not create unequal pup weights.
