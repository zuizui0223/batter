# Structural-audit numeric-opening incident v1

## Status

**RECORDED PROVENANCE INCIDENT — BOUNDED.**

During the first browser structural audit, two Ma et al. spreadsheet files were opened with a generic spreadsheet reader that treated row 1 as a header.

Those sheets do not contain textual headers. As a result, a small number of row-1 numeric amplitude values were written into the structural audit receipt.

No:
- treatment effect;
- individual identity statistic;
- group comparison;
- p-value;
- route/movement analysis

was calculated from those values.

## Affected files

- `LandingNoiseAmplitude.xlsx`
- `LandingSileneceAmplitude.xlsx`

## Consequence

Those amplitude spreadsheets are no longer eligible as confirmatory endpoints in this programme.

They may be used only:
- as already-opened descriptive source material;
- or ignored.

The Ma public-data route remains eligible for **different, unopened movement variables**, including structurally identified raw `batloc` arrays, provided their numerical values are frozen under a new contract before opening.

## Correction

All future spreadsheet structural audits:
- report sheet names;
- report dimensions;
- report only cells that are strings;
- replace numeric/boolean/formula cell contents with type labels;
- never emit numeric sheet values.

Nested archives are inspected recursively only for:
- filenames;
- sizes;
- MAT variable names/shapes/classes;
- script identifiers/file references.

## Claim boundary

This incident does not contaminate Aharon 2017.

For Ma 2025, confirmatory use of landing-amplitude spreadsheets is prohibited.

No outcome-based choice was made from the exposed numbers.
