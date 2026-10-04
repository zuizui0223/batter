# Source B all-individual day-count result v1

## Status

**PASS — proceed to freeze the first-flight self-predictability estimator.**

Authoritative workflow:
- run: **37175075470**
- artifact: **11293435170**
- artifact SHA256: `30ad14c726303760579c14a451cde0464eb2bdb909ebefde7b47f2eb8d99334f`

Parent contract:
`SOURCE_B_ALL_INDIVIDUAL_DAYCOUNT_AMENDMENT_V1.md`

## Outcome firewall

This audit used only:
- public folder/file metadata;
- top-level MATLAB variable-directory metadata from `scipy.io.whosmat`;
- the top-level `data` struct shape.

Recorded:
- `route_geometry_opened = false`;
- `mat_struct_field_values_loaded = false`.

No x/y, longitude/latitude, destination, visit, route, or trajectory value was opened.

## Result

The two ordinary first-flight cohorts contain exactly **22 individual folders**, matching the peer-reviewed study population.

All 22 contain a unique `data.mat` with a valid top-level `data` struct.

All **22/22** exceed the frozen minimum of 6 chronological track-day objects.

Day-object counts:

| individual | n days |
|---|---:|
| Ali | 70 |
| Balaz | 29 |
| Camila | 48 |
| Koral | 101 |
| MitMit | 39 |
| Ozvelian | 80 |
| Rosie | 53 |
| Shavit | 47 |
| Anka | 85 |
| Eli | 57 |
| Eva | 27 |
| Fima | 61 |
| K | 44 |
| Mazi | 41 |
| Nadav | 87 |
| Nature | 95 |
| Nazir | 32 |
| Odelia | 64 |
| Shem_Tov | 158 |
| Tishray | 106 |
| Tzedi | 106 |
| V | 66 |

Range: **27–158 track-day objects**.

The frozen biological-replication floor was 5 individuals.

Observed:
**22 individuals**.

Verdict:
`PASS_NEXT_STRUCTURAL_GATE`.

## Interpretation

The public archive has ample longitudinal depth for a prospective formation test.

This resolves the main support problem that stopped Source A:
Source B does not merely contain isolated formation snapshots; it contains long within-individual series beginning from the source-defined first outdoor flight.

The result does not yet show that self-history predictability increases with experience. That route/spatial outcome remains unopened.

## Next authorized step

Freeze the exact held-out self-history estimator, donor matching, experience axis, calibration, and route/spatial sampling rules before any coordinate value is read.

## JAE firewall

This result is outside JAE v0.4.0.
