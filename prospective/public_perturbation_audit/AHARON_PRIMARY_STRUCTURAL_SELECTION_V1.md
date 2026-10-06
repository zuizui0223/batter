# Aharon primary structural selection v1

## Status

**STRUCTURAL_FIGURE_SELECTED_NEEDS_FINITE_MASK_AUDIT**

Selection used the frozen first-eligible rule and structural metadata only.

Provenance:
- browser structural workflow run: `37467657772`;
- job: `112282647975`;
- audit step: success;
- workflow conclusion was failure only because the final result push raced with another branch update.

## Selected primary

**Figure 1**

Conditions:
- `300`
- `75`
- `con`

Common biological bats:
- `500`
- `503`
- `505`
- `510`

Thus:
- n bats = **4**;
- n conditions = **3**;
- exact cross-condition identity null size = ((4!)^{3-1}=576).

## Structural matrices

| bat | condition | rows | trial columns |
|---|---|---:|---:|
| 500 | 300 | 16 | 10 |
| 500 | 75 | 12 | 10 |
| 500 | con | 12 | 10 |
| 503 | 300 | 10 | 15 |
| 503 | 75 | 10 | 15 |
| 503 | con | 10 | 15 |
| 505 | 300 | 14 | 10 |
| 505 | 75 | 10 | 10 |
| 505 | con | 14 | 10 |
| 510 | 300 | 14 | 15 |
| 510 | 75 | 14 | 15 |
| 510 | con | 12 | 15 |

Every matrix has:
- >=10 trial columns;
- >=10 rows;
- source variable `totalTurns`.

The Mendeley source description defines each column as one trial, with odd rows representing right turns and even rows representing left turns.

## Why Figure 1

Figure 1 is the first source figure satisfying the frozen structural rules:
- >=2 conditions;
- >=4 bats common to every condition;
- >=5 trial columns in every bat × condition matrix.

Figure 2 has only three bats with both `moved` and `no` turning matrices and therefore fails the n>=4 gate.

Later figures are not allowed to replace Figure 1 after this pass.

## Next gate

Run `AHARON_FINITE_MASK_AUDIT_CONTRACT_V1.md`.

No turning-point magnitude has been used in this selection.
