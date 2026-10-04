# Yamada deterministic raw-sheet crosswalk contract v1

## Status

**OUTCOME-BLIND IDENTITY CROSSWALK.**

Frozen after the structural row-value gate passed:
- 14 bats;
- 7 per condition;
- exactly trials 1 and 12 for every bat.

No kinematic or acoustic outcome has been opened.

## Source identity fields

For every bat, the trial-1 structural row exposes:
- `origin_name`;
- `for_article_datasets_name`.

The large raw workbook exposes 28 worksheet names, one first and one twelfth sheet per source bat.

## Deterministic normalization

### Raw worksheet label

From a raw worksheet name:

1. lowercase;
2. remove an optional leading `y_`;
3. require a prefix matching `bat_<LETTER>` or `bat<LETTER>`;
4. extract only that single letter as the worksheet bat label;
5. infer trial only from an explicit token `1st` or `12th`;
6. infer condition:
   - token `chain` => condition 1;
   - token `_ac_` or `acril` => condition 2.

Dates and all other suffixes are ignored.

### Source candidate labels

From each source `origin_name` and `for_article_datasets_name`:

- lowercase;
- accept a leading `bat`;
- split remaining text on underscores;
- collect every **single alphabetic token** as a candidate label;
- for compact form such as `batA`, collect A.

Examples:
- `batA` -> {A}
- `bat_M_B` -> {M,B}
- `bat_F` -> {F}
- `batH` -> {H}

No alphabetical-sequence inference is allowed.

## Frozen mapping rule

For each source bat:

1. determine its source condition from the structural table;
2. construct the union of candidate labels from its trial-1 `origin_name` and `for_article_datasets_name`;
3. among raw workbook bat labels in that condition, require **exactly one** candidate label to match;
4. map both trial 1 and trial 12 to the raw sheets with that matched label and corresponding explicit trial token.

The mapping passes only if:
- all 14 source bats resolve uniquely;
- all 28 source bat×trial records resolve;
- every raw sheet is used exactly once;
- no two source bats map to the same raw bat label within condition.

Any ambiguity or leftover sheet = STOP.

## Important special case

No special-case code for the suspicious `bat_F_ac` sheet is allowed.

It may resolve only through the generic candidate-label rule above.

## Outcome firewall

Read only:
- the already-authorized structural identity columns from the small workbook;
- large-workbook sheet names.

Do not read:
- X/Y/Z;
- time;
- velocity;
- turn rate;
- pulse;
- max speed;
- meandering.
