# Structural support implementation audit v1

## Status

**IMPLEMENTATION AUDIT — the structural-support zero counts are not biological/source support results.**

Authoritative workflow:
- run: **37306562249**
- job: **111751546983**
- conclusion: success

Parent:
`STRUCTURAL_ROW_VALUE_ALLOWLIST_V1.md`

## Finding 1 — date parser omission

The source `bat info` sheet stores structural dates as strings such as:

- `26.08.17`
- `05.11.17`
- `17.06.18`

The structural parser accepted:
- `%Y-%m-%d`
- `%d/%m/%Y`
- `%m/%d/%Y`
- `%d.%m.%Y`

but **not** the actual two-digit-year format:

`%d.%m.%y`.

Therefore `dparse()` could not convert the source-native dates, and all stage-window call counts were reported as zero.

The resulting:
- eligible_stage2_last14d = 0;
- eligible_stage4_all = 0;
- eligible_stage4_first_date = 0;

must **not** be interpreted as absent call/landing support.

## Finding 2 — source metadata chronology inconsistency for Bat3

The opened source structural row for Bat3 reports:
- second-clutter start: `20.01.19`;
- second-clutter end: `02.02.18`.

The end precedes the start by nearly a year and is inconsistent with the source paper's stage-4 design.

This is retained as a source metadata inconsistency rather than silently corrected.

## Programme consequence

No acoustic outcome reopening or parser rescue is required for the intended confirmatory individual-identity primary because that programme is independently stopped by a stronger design ceiling:

- stage-4 environment classes contain 3 same-chamber and 2 enhanced-chamber individuals;
- condition-preserving identity exchangeability has only (3!\times2!=12) mappings;
- exact one-sided (p_{min}=1/12=0.0833).

Thus the intended 5%-level individual-recall primary is mathematically unattainable regardless of structural call counts.

The correct programme status remains:

`STOP_INDIVIDUAL_RECALL_IDENTIFIABILITY`.

## No rescue

Do not:
- repair the date parser and then open IPI for the stopped identity primary;
- silently correct the Bat3 source date;
- pool same/enhanced stage-4 classes to obtain more permutations;
- reinterpret the zero structural counts as evidence of absent data.
