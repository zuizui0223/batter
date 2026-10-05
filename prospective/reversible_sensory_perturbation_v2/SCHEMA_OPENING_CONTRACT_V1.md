# Reversible sensory XLSX schema opening contract v1

## Status

**OUTCOME-BLIND XLSX SCHEMA OPENING. NO NUMERIC DATA ROW VALUE MAY BE READ.**

Parent:
- `ARCHIVE_INVENTORY_CONTRACT_V1.md`
- archive run **37389296083** — PASS

The source ZIP contains six individual workbooks:
- Lucy.xlsx
- Alvin.xlsx
- Betty.xlsx
- Stevie.xlsx
- Dolores.xlsx
- Clementine.xlsx

and two aggregate workbooks:
- All bats data.xlsx
- All bats_no masker_xy.xlsx

## Authorized opening

For every XLSX member:

1. read workbook sheet names;
2. read worksheet used-dimension reference;
3. inspect row 1 only;
4. decode string header cells only;
5. report cell reference, cell type and header text;
6. do not decode numeric cell values;
7. do not inspect row 2+;
8. do not evaluate formulas.

The ZIP member bytes may be read only for XLSX container/XML schema parsing.

## Questions

Determine structurally:

- whether source condition/block is encoded in sheet names;
- whether repeated flights/trials are encoded as separate sheets or columns;
- whether each individual workbook exposes time + x + y + z or an explicit equivalent;
- whether condition order can be reconstructed without using movement outcomes;
- whether the recovery-control / masker re-addition blocks are identifiable.

## Proceed rule

A structural support opening may continue only if:

- >=4 of 6 bats have reproducible identity;
- >=3 source conditions/blocks can be distinguished by schema or source-native sheet labels;
- repeated movement units are present;
- a 3-D movement representation can be defined from source headers.

If only x/y and no z are public, the fixed 3-D policy representation stops; a separate 2-D causal programme would require a new contract.

## No rescue

Do not:
- infer condition from movement values;
- infer trial boundaries from behavioral transitions;
- reinterpret acoustic variables as movement coordinates;
- choose different columns after seeing outcome direction.
