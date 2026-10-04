# Yamada coordinate / policy-feature support opening v1

## Status

**STRUCTURAL FEATURE-SUPPORT GATE.**

Frozen after:
- 14-bat structural gate PASS;
- 28-sheet deterministic crosswalk PASS;
- `PERSONAL_POLICY_LEARNING_CONTRACT_V1.md` was frozen.

This gate may open raw trajectory coordinates but may not calculate self-vs-other identity persistence.

## Authorized source

`chain and acryl_environments_flight datasets.xlsx`

Figshare id:
`33969677`

MD5:
`2226ea5b19fb077ddcce66cb6e97088c`

Use exactly the 28 mapped worksheets from the passed crosswalk.

## Authorized cells

For every mapped raw sheet, read only:

- A: `time[s]`
- B: first `bat(X)[mm]`
- C: first `bat(Y)[mm]`
- D: first `bat(Z)[mm]`

No other column is opened.

## Allowed support calculations

Per sheet calculate only:

- finite-row count after cleaning;
- unique-time row count;
- positive-time interval count;
- finite horizontal-turn count;
- whether duration is positive;
- whether 3-D path length is positive;
- whether each of the eight frozen movement-policy features is finite.

Do not report the numerical feature values.

## Feature support

The eight features are exactly those frozen in
`PERSONAL_POLICY_LEARNING_CONTRACT_V1.md`.

For support only, the gate may:

1. compute those eight feature values internally;
2. subtract condition × trial feature means;
3. compute the frozen pooled within-state residual scales;
4. report only:
   - finite/positive versus zero/nonfinite scale;
   - retained/dropped feature names.

Do not report:
- means;
- SD magnitudes;
- individual feature values;
- first-vs-twelfth changes;
- individual rank;
- self-vs-other distances.

## Bat support

A bat is eligible only if both mapped trial sheets pass the frozen trajectory rules.

Primary may open only if:
- >=5 eligible bats in condition 1;
- >=5 eligible bats in condition 2;
- >=12 eligible bats total;
- >=6/8 features retained species-wide.

## Decision

Return:
- `PASS_OPEN_PERSONAL_POLICY_PRIMARY`, or
- `STOP_COORDINATE_OR_FEATURE_SUPPORT`.

No threshold relaxation after this gate.
