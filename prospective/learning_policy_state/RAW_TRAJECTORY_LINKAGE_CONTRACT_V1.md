# Raw-trajectory subject linkage contract v1

## Status

**OUTCOME-BLIND LINKAGE GATE. NO TRAJECTORY CELL VALUE IS AUTHORIZED.**

Branch:
`prospective/learning-policy-state-v1`

Parent evidence:
- `STRUCTURAL_ROW_VALUE_ALLOWLIST_V1.md`
- structural result: 14 source subjects with unique `bats_id`, condition, `origin_name`, and `for_article_datasets_name`;
- `XLSX_HEADER_OPENING_ALLOWLIST_V1.md`
- large workbook sheet names only.

## Source workbook

`chain and acryl_environments_flight datasets.xlsx`

The header-only gate exposed 28 trajectory sheets:
- seven condition-1 subjects × 1st/12th;
- seven condition-2 subjects × 1st/12th.

No data row from those sheets has been opened.

## Sheet parsing

For every trajectory sheet:

### Condition

- sheet containing `_chain_` -> condition 1;
- sheet containing `_ac_` or `_acril_` -> condition 2.

### Trial

- sheet containing `_1st` -> trial 1;
- sheet containing `_12th` -> trial 12.

### Sheet bat token

Extract the substring beginning `bat_` through the single bat code immediately before the condition token.

Normalize identifiers for matching by:
- lowercase;
- remove underscores;
- remove spaces.

Examples:
- `bat_A` -> `bata`;
- `bat_F` -> `batf`.

## Subject linkage rule

Within the parsed acoustic condition only:

1. First attempt exact normalized match between the sheet bat token and source `for_article_datasets_name`.
2. If and only if no dataset-name match exists, attempt exact normalized match to source `origin_name`.
3. A sheet must resolve to exactly one source `bats_id`.
4. Every source subject must resolve to exactly one 1st sheet and exactly one 12th sheet.
5. No sheet may be reused.

**Dataset-name matches always take priority over origin-name matches.**

This precedence is frozen because the public summary table explicitly distinguishes the two identifier systems, and the published-analysis dataset name is the intended analysis linkage key.

## Stop rule

Proceed to raw trajectory outcomes only if:

- all 28 trajectory sheets resolve;
- all 14 source subjects resolve;
- each subject has exactly trials {1,12};
- conditions agree between workbook sheet and summary table;
- no one-to-many or many-to-one ambiguity remains.

Otherwise:
`STOP_RAW_TRAJECTORY_LINKAGE`.

No coordinate value may be opened to resolve identity ambiguity.
