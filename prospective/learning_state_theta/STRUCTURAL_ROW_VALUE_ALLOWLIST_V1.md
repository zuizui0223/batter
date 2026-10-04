# Yamada structural row-value allowlist v1

## Status

**FROZEN BEFORE ANY KINEMATIC OR ACOUSTIC OUTCOME VALUE IS OPENED.**

Parent:
- `SOURCE_RECEIPT_V1.md`
- `SCHEMA_OPENING_CONTRACT_V1.md`

Source workbook:
`raw_analysis_data_by_yamada.xlsx`

Authoritative file:
- Figshare id: `33969680`
- MD5: `cb7e2f738d85ee80becb5949317ff625`

Sheet:
`1st_table`

## Authorized row values only

Read rows 2+ from exactly these columns:

- C: condition
- D: bats_id
- E: trial
- N: origin_name
- O: for_article_datasets_name

Do **not** read:

- F: pulse-direction outcome
- G:J: pulse-count outcomes
- K: max_flight_speed
- L: meandering width
- any other outcome cell.

## Structural questions

Report:

1. exact condition vocabulary and counts;
2. exact bat-ID vocabulary;
3. exact trial vocabulary;
4. rows per bat;
5. condition per bat;
6. trial set per bat;
7. `origin_name` and `for_article_datasets_name` by bat × trial;
8. whether the source table gives a one-to-one crosswalk to the 28 raw trajectory sheets.

## Frozen support rule

The learning-state personal-policy programme proceeds only if:

- exactly **14 unique bats** are present;
- exactly **7 bats per acoustic condition**;
- every bat has exactly **2 rows**;
- every bat has the same two source-defined trial labels;
- those two trial labels can be mapped unambiguously to first and twelfth exposure from source metadata/naming;
- all 28 bat × trial rows map one-to-one to exactly 28 raw trajectory sheets.

If any of these fail:
**STOP** before opening kinematic outcomes.

## Crosswalk rule

Use source-native `origin_name` / `for_article_datasets_name` first.

Workbook sheet-name similarity may be used only as a deterministic normalization of obvious formatting tokens:
- file extension removal;
- spaces/underscores;
- parenthesized dates;
- case;
- literal tokens `1st` / `12th`.

Do not invent or repair a bat ID based only on alphabetical sequence.

In particular, the suspicious acrylic workbook sheet names containing `bat_F_ac_*` are **not** assumed to be bat H unless the source table itself establishes the mapping.

## Outcome firewall

At this gate:
- no speed value;
- no X/Y/Z;
- no turning rate;
- no pulse count/timing;
- no meandering;
- no personal-policy statistic

may be calculated or reported.
