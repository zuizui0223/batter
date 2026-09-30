# Airflows multispecies nonvertical schema audit v1

**No point-level RDS file and no numeric vertical value was opened.**

- segment rows: **194,558**
- unique species in biologging summary: **38**
- GBIF-classified bat species: **2**
- bat study×species panels: **8**
- necessary-screen candidate panels: **5**

## Bat panels

| panel | species | individuals | >=2 segments | segments | point-count proxy | known taxon? | exact known study? | necessary screen |
|---|---|---:|---:|---:|---:|---|---|---|
| 10061238 | Pteropus lylei | 3 | 3 | 22 | 94 | no | no | FAIL |
| 14253246 | Eidolon helvum | 5 | 5 | 37 | 203 | yes | no | PASS |
| 183770262 | Eidolon helvum | 23 | 19 | 97 | 863 | yes | no | PASS |
| 259100173 | Eidolon helvum | 14 | 14 | 136 | 1038 | yes | no | PASS |
| 6609898 | Pteropus lylei | 7 | 5 | 22 | 86 | no | no | PASS |
| 8239320 | Pteropus lylei | 8 | 6 | 31 | 129 | no | no | PASS |
| 8266613 | Pteropus lylei | 3 | 1 | 7 | 31 | no | no | FAIL |
| 8862993 | Eidolon helvum | 1 | 0 | 1 | 19 | yes | no | FAIL |

## Candidate panels for separately frozen point-level preflight

- `studyID:14253246::Eidolon helvum`: 5 individuals, 5 with >=2 segments, 37 segments
- `studyID:183770262::Eidolon helvum`: 23 individuals, 19 with >=2 segments, 97 segments
- `studyID:259100173::Eidolon helvum`: 14 individuals, 14 with >=2 segments, 136 segments
- `studyID:6609898::Pteropus lylei`: 7 individuals, 5 with >=2 segments, 22 segments
- `studyID:8239320::Pteropus lylei`: 8 individuals, 6 with >=2 segments, 31 segments
