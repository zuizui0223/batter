# Nyctalus independent-validation structural preflight v1

## Status

**OUTCOME-BLIND. Numeric `Height` magnitudes were never parsed.**

Authoritative workflow:
- run: `36668368016`
- head: `35d2cf528149ecbee568bcfde84bbdc990149ec5`
- artifact: `11076459650`
- digest: `sha256:b4b3aeda22b0cd90a76173b76c69ba991ead1054a6a051bfd35c09e2f15b00d4`

## Frozen structural decisions

| prospective stage | evaluable individuals | required | gate |
|---|---:|---:|---|
| 5-km centered identity | **36** | 8 | **PASS** |
| 5-km × source HMM state | **27** | 26 | **PASS** |
| 500-m × source HMM state | 10 | 19 | **STOP** |
| >=1-day × source HMM state | 7 | 19 | **STOP** |

Cohort definition: **Year × field_period**.

Source HMM state test uses only `ARM` and `COM`; `undefined` is excluded.

## Decision

Only two vertical outcomes may now be opened:

1. primary 5-km centered identity, exact observed n=36;
2. 5-km × source HMM movement-state identity, exact observed n=27.

No 500-m or lag result may be opened as a rescue or sensitivity after the external outcome is seen.
