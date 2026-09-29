# Prospective external bat-panel search — candidate ledger v1

## Scope

This ledger belongs to the independent external-data search frozen in
`post_freeze_extensions/external_panel_search/contract_v1.json`.

The previous Movebank search universe is excluded. Numeric vertical values are not used for candidate admission.

## Candidate ledger

| Candidate | Repository / DOI | Native event-level vertical | Individuals | Repeat-session evidence | >=50 fixes/session evidence | Decision |
|---|---|---|---:|---|---|---|
| *Hipposideros armiger* + *H. pratti* | Dryad 10.5061/dryad.j0zpc86r1 | YES: `height` AGL | 17 (9 + 8) | Strong: source paper reports site fidelity across 7–10 consecutive nights and 105 bat-night observations | **PENDING exact row/session count** | PENDING |
| *Leptonycteris nivalis* Texas 2024 | Dryad 10.5061/dryad.stqjq2cfg | YES: `Altitude (m)` HAE | 21 | GPS programmed every 10 min sunset–sunrise; exact per-individual multi-night structure not yet proven | **PENDING exact row/session count** | PENDING |
| *Desmodus rotundus* disturbance dataset | Dryad 10.5061/dryad.7wm37pw53 | YES: `ALTITUDE` | 93 tagged; 55 in cleaned GPS | Up to 9 nights; 242 cleaned bat-nights reported | cleaned data are very sparse (1,321 fixes / 242 bat-nights), but exact eligible-session count not yet proven | PENDING / low priority |
| *Nyctalus aviator* acoustic-GPS | Dryad 10.5061/dryad.mgqnk993n | GPS altitude represented | one GPS-tagged bat in study description | insufficient individuals | impossible to meet >=8 individuals | FAIL |
| Hammer-headed bat GPS | Dryad 10.5061/dryad.7m0cfxq4t | NO native vertical field in public bat table (`x`, `y`, `time`, `trackId`) | multiple | not relevant after vertical-axis failure | not relevant | FAIL |
| Spring migration small insectivorous bat | Zenodo 10.5281/zenodo.22017606 | processed coordinate-free public data only | multiple | raw high-resolution spatial data restricted | public raw-event requirement fails | FAIL |
| Chirocopter UAV bat recordings | Dryad 10.5061/dryad.cf472n3 | not individual tagged bat tracks | not applicable | not applicable | raw movement-panel requirement fails | FAIL |

## Most promising candidate

The *Hipposideros* Dryad source is currently the strongest candidate because it has:

- 17 tracked adults;
- a native event-level AGL `height` column;
- 10-min GPS scheduling from 20:00–06:00 when movement is detected;
- repeated use of individual foraging sites for 7–10 consecutive nights;
- 105 reported bat-night observations.

It is **not admitted yet** because the frozen gate requires at least five individuals with at least two sessions each containing >=50 usable fixes. The publication-level metadata do not establish that exact count because GPS logging was movement-triggered.

## Data-access constraint

Dryad metadata and file schemas are publicly inspectable, but current Dryad file downloads require an authenticated API session. The exact per-night row count therefore remains pending unless the raw file becomes accessible through an allowed public route.

No numeric height value has been used for any decision recorded here.
