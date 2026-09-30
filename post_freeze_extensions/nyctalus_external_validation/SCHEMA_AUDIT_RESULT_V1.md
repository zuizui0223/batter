# Nyctalus outcome-blind schema audit v1

## Status

**Numeric `Height` values were not parsed.**

Authoritative workflow:
- run: `36668180916`
- head: `deabddf543eb3241a3343d84163bf42ba14c9e12`
- artifact: `11076596974`
- digest: `sha256:d0d26d62780e7364bf2132abca4ca98e91177d4a922895179b9b662ccaa7e0b3`

Source:
- *Nyctalus noctula*
- Zenodo DOI `10.5281/zenodo.7535030`
- file `Observed_GPS_locations.csv`
- raw file SHA256 `2f373d47706c5b56313de70b623bb5446f5925c69af30f1b145993419e382aa9`

## Structural facts

- rows: **8,129**
- individuals: **60**
- tracks: **107**
- nonblank native `Height`: **8,129 / 8,129**
- source movement state: `ARM`, `COM`, `undefined`
- source period field: `field_period` = `one` / `two`
- years: 2019 / 2020

Outcome-blind cohorts are frozen as **Year × field_period**:

| cohort | individuals | tracks |
|---|---:|---:|
| 2019::one | 11 | 19 |
| 2019::two | 16 | 24 |
| 2020::one | 18 | 33 |
| 2020::two | 15 | 31 |

No numeric Height magnitude was used to define cohorts.
