# Clutter recall structural row-value allowlist v1

## Status

**OUTCOME-BLIND STRUCTURAL OPENING. ACOUSTIC OUTCOME COLUMNS REMAIN CLOSED.**

Parent:
- `SCHEMA_OPENING_CONTRACT_V1.md`
- schema workflow run **37305950880** — PASS.

The schema establishes that `Clutter Chamber Data.xlsx` contains:
- five individual call sheets (Bat1...Bat5);
- columns `Time`, `Date`, `file no.`, `call.no`, acoustic call fields, `IPI`, `Duration`;
- a `bat info` sheet with structural fields including `Bat`, `start date`, `landing start`, `end date`, `after six months`, a second `end date`, and `new box`.

## Authorized values

### `bat info`

Open rows 2:end for columns A:H only:

- A: Bat
- B: start date
- C: landing start
- D: time to first landing (days)
- E: first clutter encounter end date
- F: after six months / second-encounter start field
- G: second-encounter end date
- H: new box / enhanced-clutter indicator

These are structural experimental-design values.

### Individual call sheets

For Bat1...Bat5 open rows 2:end for columns A:D only:

- A: Time
- B: Date
- C: file no.
- D: call.no

Do **not** open columns E onward.

In particular, keep closed:
- all envelope/frequency/power columns;
- IPI (R);
- Duration (S);
- any trailing numeric summary cells.

## Structural outputs

For each bat:

1. reproduce the stage-2 first clutter date interval from `landing start` through the first `end date`;
2. reproduce the stage-4 second clutter interval from `after six months` through the second `end date`;
3. record the source `new box` indicator;
4. count unique call-table dates and unique `file no.` values within:
   - all stage 2;
   - first 14 calendar days of stage 2;
   - last 14 calendar days of stage 2;
   - all stage 4;
   - earliest source-recorded stage-4 date;
   - first 7 calendar days of stage 4.

No acoustic values are summarized.

## Proceed gate

A numeric IGI recall contract may be frozen only if:

- >=4 biological bats have >=2 unique landing/file IDs in the last 14 days of stage 2;
- the same >=4 bats have >=2 unique landing/file IDs in stage 4;
- stage-4 environment type is reproducibly recoverable from `new box` or the source design;
- date windows can be assigned without inspecting IPI.

If the immediate first-stage4-date endpoint is later considered, it must additionally have >=1 landing for >=4 bats.

## No rescue

Do not:
- use IPI to infer phase membership;
- move phase boundaries based on outcome values;
- replace missing late-stage data with earlier days after outcome opening;
- infer `new box` from acoustic values.
