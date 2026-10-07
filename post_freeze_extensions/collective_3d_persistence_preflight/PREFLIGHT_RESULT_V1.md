# Collective 3D persistence preflight result v1

## Status

**PASS FOR TWO DISTINCT FOLLOW-UP LANES. No new 3D collective outcome was opened in this preflight.**

Authoritative workflow:
- run: **37613425654**
- head: `c4320349db7ad4722afd2f1171c633d2bcd8161f`
- conclusion: **success**
- artifact: **11479266174**

The preflight used cohort, individual, session, timestamp, x-y coordinates and fix counts. It did not calculate any new centered-height distribution, z-bin probability, vertical overlap, 3D overlap, or collective-versus-personal predictive gain.

## Lane A — natural tracked-member turnover

Frozen gate:
- >=2 tracked individuals per night;
- >=3-day lag;
- zero shared tracked identities between paired nights;
- >=50 pooled fixes from each night inside shared 500-m cells;
- >=10 eligible night pairs involving >=5 unique nights.

Results:

| panel | eligible zero-identity night pairs | unique nights | gate |
|---|---:|---:|---|
| *Tadarida teniotis* | 0 | 0 | FAIL |
| *Eidolon helvum* | 1 | 2 | FAIL |
| *Hypsignathus monstrosus* | 4 | 5 | FAIL |
| *Phyllostomus hastatus* 2022 | **53** | **19** | **PASS** |
| *P. hastatus* 2023 | 1 | 2 | FAIL |
| *P. hastatus* 2016 | **16** | **8** | **PASS** |

Thus the archive contains a strict natural-turnover test of collective 3D persistence in the 2022 and 2016 *P. hastatus* panels.

## Lane B — cross-individual past-to-future prediction

Frozen gate:
- focal animal has >=1 own session at least 3 days in the past;
- >=3 other individuals have sessions at least 3 days in the past;
- >=50 target fixes occur in 500-m cells supported by both self and other history;
- >=5 target individuals per panel.

Results:

| panel | target sessions | target individuals | gate |
|---|---:|---:|---|
| *Tadarida teniotis* | 0 | 0 | FAIL |
| *Eidolon helvum* | 1 | 1 | FAIL |
| *Hypsignathus monstrosus* | **71** | **17** | **PASS** |
| *Phyllostomus hastatus* 2022 | **66** | **18** | **PASS** |
| *P. hastatus* 2023 | **8** | **6** | **PASS** |
| *P. hastatus* 2016 | 0 | 0 | FAIL |

The follow-up predictive decomposition is therefore frozen only for those three passing panels.

## Interpretation

Lane A can test whether a pooled 3D configuration recurs after complete turnover of the tracked individuals. This is the closest available archive test to a collective-level spatial memory, but stable landscape structure remains an alternative mechanism.

Lane B can test whether other individuals' past carries a shared spatial template and whether the focal individual's own past adds a further personal increment. A positive shared component alone must not be relabelled cognitive or social memory.
