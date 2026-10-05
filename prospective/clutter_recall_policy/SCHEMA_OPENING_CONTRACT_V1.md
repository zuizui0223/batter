# Clutter recall schema opening contract v1

## Status

**OUTCOME-BLIND XLSX SCHEMA OPENING. NO NUMERIC DATA ROW VALUE MAY BE READ.**

Parent:
- `SOURCE_RECEIPT_V1.md`
- `METADATA_PREFLIGHT_CONTRACT_V1.md`
- metadata run 37298385047

## Frozen source files

The metadata inventory exposed exactly 11 XLSX files:
- Bat1-stage1.xlsx / Bat1-stage3.xlsx
- Bat2-stage1.xlsx / Bat2_stage3.xlsx
- Bat3-stage1.xlsx / Bat3-stage3.xlsx
- Bat4-stage1.xlsx / Bat4-stage3.xlsx
- Bat5-stage1.xlsx / Bat5-stage3.xlsx
- Clutter Chamber Data.xlsx

All file IDs, sizes and SHA256 digests are inherited from the metadata receipt.

## Authorized opening

For every XLSX file, download only for structural inspection and verify the inherited SHA256.

Open only ZIP/XML structures needed to report:

1. workbook sheet names;
2. worksheet dimension reference (for example A1:H250);
3. row-1 cell references, cell types and **string/header text**;
4. if row 1 contains no string cells, continue downward only until the first row containing at least one string cell and report that row as the header candidate;
5. no more than the first **5 rows** may be inspected to locate a header;
6. numeric cell values are never decoded or printed;
7. formulas are not evaluated;
8. no acoustic or movement outcome value is opened.

Shared-string entries may be decoded only when referenced by an authorized header-candidate cell.

## Questions

Determine structurally:

- whether Bat1...Bat5 are reproducible identities across stage files;
- what stage1 and stage3 files contain by sheet/column labels;
- whether `Clutter Chamber Data.xlsx` exposes stage/encounter, bat identity, day/trial and IGI or a documented equivalent;
- whether first and second clutter encounters can be distinguished without outcome values;
- whether the archive contains repeated rows rather than only bat-level summaries.

## Proceed rule

A new recall estimator may be frozen only if the schema establishes, without opening numeric outcomes:

- >=4 reproducible bat identities;
- a reproducible first-clutter late phase and second-clutter recall phase, or an equivalent source-defined mapping;
- an IGI / pre-takeoff timing outcome or source-documented equivalent;
- repeated observations per bat/phase or an explicitly summary-level architecture suitable for a separate bat-level contract.

Otherwise STOP before numeric outcome opening.

## No rescue

Do not:
- infer a stage meaning from acoustic values;
- inspect numeric rows to discover phase boundaries;
- substitute a different outcome because IGI support is inconvenient;
- infer missing bat/stage mappings from published effect direction.


## Trigger provenance

The schema workflow is fail-closed and may be re-triggered without changing the frozen opening rules. This note changes no authorized field, threshold or proceed rule.
