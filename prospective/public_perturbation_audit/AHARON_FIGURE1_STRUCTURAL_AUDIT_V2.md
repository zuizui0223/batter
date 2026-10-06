# Aharon Figure-1 structural audit v2

## Status

**OUTCOME-BLIND STRUCTURAL AUDIT. NUMERIC TURNING VALUES FORBIDDEN.**

Parent:
- `AHARON_CROSS_CONDITION_IDENTITY_CONTRACT_V1.md`

The frozen first-eligible-figure rule selects Figure 1 if its public MAT matrices satisfy support.

Expected source structure from public filenames:

Bats:
- 500
- 503
- 505
- 510

Conditions:
- con
- 75
- 300

Expected cells:
4 bats × 3 conditions = 12 turning matrices.

## Authorized opening

For each internal MAT file:
- filename;
- top-level variable names;
- matrix shape/class only.

Do not load or report numeric turning values.

## Structural PASS

Require:
- exactly the four expected bats;
- all three expected conditions for every bat;
- one numeric matrix per bat × condition;
- rows >=2;
- columns >=5.

If PASS:
proceed to finite-mask audit only.

If FAIL:
`STOP_AHARON_FIGURE1_STRUCTURE`.
