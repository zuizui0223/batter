# Spatial-learning structural row-value allowlist v1

## Status

**FROZEN BEFORE ANY BEHAVIOURAL OUTCOME VALUE IS OPENED.**

Parent:
- `XLSX_HEADER_OPENING_ALLOWLIST_V1.md`

File:
`raw_analysis_data_by_yamada.xlsx`

Pinned file id:
`33969680`

Sheet:
`1st_table`

Observed used range:
`C1:O29`

## Authorized row values

For rows 2–29 only, read exactly:

- C: `condition(1:permeable(chain)_condition, 2:reflective(acrylic)_condition)`
- D: `bats_id`
- E: `trial`
- N: `origin_name`
- O: `for_article_datasets_name`

These are design / linkage variables only.

## Explicitly forbidden outcome columns

Do **not** read:

- F: Absolute Δ pulse direction
- G: Number of total pulse emissions
- H: Number of more than triplets
- I: Number of doublets
- J: Number of single pulses
- K: max_flight_speed
- L: meandering width

Any blank/intermediate columns remain unopened as well.

## Structural questions

Report:

1. number of non-empty rows;
2. unique bat IDs;
3. source condition vocabulary and bat counts per condition;
4. trial vocabulary;
5. number of rows per bat;
6. trial set per bat;
7. condition consistency within bat;
8. origin/dataset-name linkage uniqueness;
9. whether every biological subject has both first and twelfth-flight summary rows.

## Frozen support target

The primary 1st-versus-12th maintenance analysis may open only if the public table supports:

- at least **12 distinct biological subjects** total;
- at least **5 subjects per acoustic condition**;
- each included subject has exactly one row for trial 1 and exactly one row for trial 12;
- condition is constant within subject;
- no duplicated subject × trial row.

The expected source design is 14 bats, seven per condition, but the gate uses the weaker preregistered minimum above so a small amount of source missingness does not force post-outcome threshold changes.

## Identity ambiguity

If the same `bats_id` appears in both acoustic conditions:

- do not assume it is the same biological animal;
- use `condition × bats_id` as the provisional source-native subject key unless `origin_name` or `for_article_datasets_name` explicitly establishes a unique cross-condition identity.

This rule is frozen before structural values are opened.

## Decision

Return:

- `PASS_TO_OUTCOME_CONTRACT`; or
- `STOP_STRUCTURAL_SUPPORT`.

No behavioural endpoint may be inspected before this structural result is frozen.
