# Clutter recall formula and structural-date opening contract v1

## Status

**OUTCOME-BLIND STRUCTURAL OPENING. NO ACOUSTIC NUMERIC OUTCOME VALUE MAY BE READ.**

Parent:
- `SCHEMA_OPENING_CONTRACT_V1.md`
- schema workflow run 37305950880

The schema established:
- five reproducible identities Bat1...Bat5;
- one clutter workbook with one call table per bat;
- a `bat info` sheet containing source-stage boundary labels including:
  - start date;
  - end date;
  - after six months;
  - end date;
  - new box;
- call-table columns include call timing, IPI and duration.

## Authorized opening A — formulas / merged labels

For `Clutter Chamber Data.xlsx` only:

- inspect worksheet merged-cell ranges;
- inspect **formula text only** in cells;
- report cell reference and formula string;
- do not evaluate formulas;
- do not decode cached formula results;
- do not print non-formula numeric cell values.

Purpose:
determine whether IGI or source summaries are encoded by workbook formulas and how the call table is organized.

## Authorized opening B — structural bat-info values

From sheet `bat info` only, numeric/date/string values may be opened in columns:

- A:H only.

These columns are source-stage metadata:
- Bat;
- start date;
- landing start;
- time to first landing (days);
- end date;
- after six months;
- end date;
- new box.

No columns I:U may be opened at this stage.

Allowed outputs:
- source-native bat identifier;
- dates;
- landing-start dates;
- days-to-first-landing;
- stage/end dates;
- after-six-month dates;
- new-box indicator/value if source-native.

These are structural phase labels, not acoustic outcomes.

## Questions

1. Can the first clutter encounter and second clutter encounter be partitioned reproducibly by source dates?
2. Which bats returned first to the same clutter chamber versus the enhanced/new-box condition?
3. Is IGI directly encoded by formulas or must it be reconstructed from call timing fields?
4. Can the published first-two-week / last-two-week / second-encounter-two-week contrasts be implemented without selecting boundaries from acoustic outcomes?

## Proceed rule

Proceed to an outcome estimator only if:
- >=4 bats have reproducible first- and second-encounter date boundaries;
- same versus enhanced/new-box condition is structurally known;
- the IGI construction can be tied to the source definition without outcome-driven choices.

Otherwise STOP.

## No rescue

Do not:
- inspect acoustic values to infer takeoff boundaries;
- choose a different acoustic endpoint after seeing values;
- infer enhanced/same condition from the direction of IGI;
- use stage1/stage3 large-room values to rescue missing clutter support.
