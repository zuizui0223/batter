# Comparative generality candidate ledger v1

## Status

**FROZEN SEARCH-SNAPSHOT LEDGER. Numeric vertical outcomes were not used for admission or ranking.**

Programme:
`post_freeze_extensions/comparative_generality/contract_v1.json`

Historical opened sources are excluded from the count of new prospective sources.

| source | repository | taxon | vertical field documented? | repeated multi-individual tracking? | status | notes |
|---|---|---|---|---|---|---|
| Dryad 10.5061/dryad.stqjq2cfg | Dryad | *Leptonycteris nivalis* | yes — `Altitude (m)`, WGS84 ellipsoidal altitude | 21 tagged bats, but no individual has >=2 public nights with >=50 valid fixes | **STRUCTURAL FAIL / ALTITUDE UNOPENED** | comparative run 36721180314; repeat-eligible n=0; no threshold rescue |
| Dryad 10.5061/dryad.7wm37pw53 | Dryad | *Desmodus rotundus* | yes — raw GPS `ALTITUDE` above sea level | multi-local tracking, but no local has >=3 repeat individuals under frozen rule | **STRUCTURAL STOP / ALTITUDE UNOPENED** | 1,678 presence-qualified rows; 4 >=50-fix sessions total; only Pacayca has one repeat ID; horizontal axis not evaluable |
| Dryad 10.5061/dryad.7m0cfxq4t | Dryad | *Hypsignathus monstrosus* | **no vertical field documented in deposited GPS table** | yes | **REJECT — VERTICAL FIELD ABSENT** | Dryad README defines `Bats2022_2023.csv` as x/y/time/trackId only; do not download 6.86-GB archive merely to search for an undeclared response |
| Dryad 10.5061/dryad.j0zpc86r1 | Dryad | *Hipposideros armiger* / *H. pratti* | yes — AGL `height` | yes | **HISTORICAL OPENED / EXCLUDE FROM NEW COUNT** | prospective primary already opened and FAIL; retained as v10 boundary anchor |
| Zenodo 10.5281/zenodo.7535030 | Zenodo | *Nyctalus noctula* | yes — native GPS `Height` | yes | **HISTORICAL OPENED / EXCLUDE FROM NEW COUNT** | first prospective primary already opened and FAIL; same-source programme closed |
| Movebank 10.5441/001/1.278 | Movebank Data Repository | *Hypsignathus monstrosus* | yes — height above ellipsoid | yes | **HISTORICAL ORIGINAL ARCHIVE / EXCLUDE** | original comparative Hypsignathus panel |
| Plazi / article-only Zenodo records returned by frozen queries | Zenodo | various Chiroptera | no event-level raw tracking table established | — | **REJECT** | publication/taxonomic record only |
| Zenodo 10.5281/zenodo.21915776 | Zenodo | mixed birds + bats; 38 biologging species total | **PENDING SCHEMA AUDIT** | 1,524,121 GPS observations, 853 individuals in source RDS | **PENDING HEADER/SCHEMA AUDIT** | large multi-species dataset; must establish bat subset, individual/session fields and vertical field without reading numeric vertical values |
| high-altitude bat acoustic/radar datasets returned by frozen queries | mixed | various Chiroptera | not individual fix-level GPS | no individual repeated trajectories | **REJECT** | wrong data type |
| UAV / video bat datasets returned by frozen queries | mixed | various Chiroptera | not individual repeated GPS altitude trajectories | no | **REJECT** | wrong data type |

## Admission order

The programme does **not** rank sources by expected vertical outcome.

Execution order is operational only:

1. *Leptonycteris nivalis* — individually downloadable file, already identified before v10 and still vertically unopened.
2. *Desmodus rotundus* — admitted but archive size/access must be solved without reading altitude.
3. *Hypsignathus monstrosus* Dryad 2022–2023 — header audit first; reject if no raw vertical field.

Any further source returned by the frozen search snapshot is appended whether promising or not.

## Outcome firewall

For every admitted new source:
1. verify vertical-field presence and semantics without numeric vertical values;
2. freeze structural eligibility;
3. compute and freeze horizontal individuality first;
4. freeze exact vertical target/training universe;
5. open centered vertical response once;
6. retain PASS or FAIL without rescue.

No source is replaced because its vertical result is negative.
