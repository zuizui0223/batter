# Configuration-conditioned structural support amendment v1

## Status

**OUTCOME-BLIND STRUCTURAL GATE — frozen before any CSV numeric field is parsed.**

Parent:
- `SPECIES_CSV_MAPPING_PROVENANCE_V1.md`
- `CONFIGURATION_CONDITIONED_IDENTITY_CONTRACT_V1.md`

## Authorized structural read

For each of the 64 trajectory CSV files:

- download raw bytes;
- verify Figshare-supplied MD5;
- count newline-delimited records only;
- do not split or parse any data row by commas;
- do not decode numeric fields.

Report:

- species from the frozen file-id batch mapping;
- environment and bat identity from filename;
- trial token from filename;
- total text lines;
- data-row count = total lines minus one header line.

## Structural valid-file proxy

Before coordinate parsing, a file passes the row-count proxy if:

`data_rows >= 100`.

This does not guarantee >=100 finite coordinate rows; that remains a later fail-closed coordinate-support condition inside the frozen estimator.

## Primary A structural gate

Within species × environment:

- >=3 bats;
- each bat has >=2 row-count-passing files.

A species may open Primary A only if >=2 environments satisfy that rule.

## Primary B structural gate

A bat is candidate-evaluable if:

- it has row-count-passing files in >=3 distinct environments.

A species may open Primary B only if:

- >=3 bat identities are candidate-evaluable.

## No-outcome rule

Do not parse:
- Time;
- X;
- Y;
- Z;
- pulse.

Do not calculate:
- route length;
- speed;
- turning;
- vertical range;
- route similarity;
- identity advantage.

## Decision

For each species separately report:

- `PASS_A` / `STOP_A`;
- `PASS_B` / `STOP_B`.

No species pooling or threshold relaxation.
