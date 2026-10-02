# Simultaneous co-use structural preflight result v1

## Status

**X-Y-TIME ONLY. No vertical value or vertical separation was used to choose panel-specific synchronization tolerances.**

Authoritative workflow:
- run `36951544701`
- head `b505b0fd302678bf51a532ba987a34ab02dc0215`
- conclusion: success

## Selected tolerances

The frozen rule selected the smallest candidate tolerance that met all predeclared individual/dyad/encounter support gates.

| panel | selected tolerance | usable individuals | usable dyads | matched encounters |
|---|---:|---:|---:|---:|
| *Hypsignathus monstrosus* | **60 s** | 17 | 56 | 4,410 |
| *Phyllostomus hastatus* 2022 | **60 s** | 8 | 11 | 352 |
| *P. hastatus* 2023 | **600 s** | 6 | 8 | 679 |
| *P. hastatus* 2016 | **600 s** | 5 | 8 | 16,097 |

All four panels pass the structural preflight.

## Important structural asymmetry

The ecological meaning of "simultaneous" differs in temporal precision:

- *Hypsignathus* and 2022 pass at one minute;
- 2023 and 2016 require the predeclared maximum 10-minute window.

Therefore any later interaction interpretation must distinguish the one-minute panels from the 10-minute panels rather than treating them as identical-resolution encounter data.

The 2016 panel contains **16,097** matched encounters, far more than the other panels, despite only five usable individuals. Before any vertical-separation outcome is opened, an x-y-time-only endpoint/central-place concentration audit is required to determine whether this encounter abundance is dominated by recurring departure/arrival or roost-associated cells.

No tolerance will be changed after this preflight.

## Artifact receipts

- Hypsignathus: artifact `11204472072`, digest `sha256:2c044d5aa9d5b1d36fd7aa9dd3c86ce23a4c673e32b34e1aff753aa80ebceafb`
- P. hastatus 2022: artifact `11204322756`, digest `sha256:e21d91c8052bc8356660bc31bcd5e880bb75cc7c13c138219363092a1a415264`
- P. hastatus 2023: artifact `11204561097`, digest `sha256:e2f41c9d2a3ea98e1f420b6b5afbc104944366aaad3ba1303a2710b9c4d2b3bc`
- P. hastatus 2016: artifact `11204412479`, digest `sha256:c8883933519a8f97bb0a824add12887362a4ad986be207029ff4960fddd6d471`
