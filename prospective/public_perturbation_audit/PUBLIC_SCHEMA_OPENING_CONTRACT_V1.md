# Public perturbation schema-only opening contract v1

## Status

**OUTCOME-BLIND STRUCTURAL OPENING. NUMERIC OUTCOME VALUES FORBIDDEN.**

This stage may download public files only to inspect file/container structure.

Authorized:
- filenames;
- hashes;
- file types;
- MATLAB variable names, shapes and classes;
- HDF5 group/dataset names, shapes and dtypes;
- spreadsheet sheet names, dimensions and header cells only;
- MATLAB script identifiers;
- filenames referenced by `load/readtable/readmatrix/readcell/xlsread`;
- condition / bat / trial tokens when encoded in identifiers or strings.

Forbidden:
- printing numeric MATLAB arrays;
- calculating turning/slowing/speed values;
- reading spreadsheet data rows beyond the header;
- executing MATLAB code;
- executing pickle or arbitrary serialized objects;
- computing any treatment effect or individual identity statistic.

## Aharon proceed rule

Aharon advances to a frozen numerical contract only if the structural opening can recover:

1. >=4 biological bat identifiers in at least one manipulation family;
2. >=2 source-defined conditions for those same bats;
3. trial-replicated source variables;
4. a common endpoint available in the compared conditions;
5. enough structural trial columns to support a predeclared within-individual held-out test.

Preferred endpoint order fixed before values:
1. turning-location organization;
2. slowing-location organization;
3. trial mean speed.

Do not choose a lower endpoint because the higher one later looks weak.

## Ma proceed rule

Ma advances only if the public structure exposes repeated individual/trial data within at least one task.

Because the published design uses separate groups of four for foraging and landing, cross-task identity transfer is not authorized unless the public schema contradicts that published grouping.

Priority:
1. within-foraging noise / prey-context individual persistence;
2. within-landing noise individual persistence.

With n=4, exact identity-permutation resolution must be checked before any confirmatory endpoint is opened.

## Stop rule

If individual × condition × trial structure cannot be recovered without reading outcome values:
**STOP_PUBLIC_STRUCTURE_INSUFFICIENT.**
