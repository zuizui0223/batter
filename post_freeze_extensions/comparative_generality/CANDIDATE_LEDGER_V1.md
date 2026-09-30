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
| Zenodo 10.5281/zenodo.21915776 | Zenodo | mixed birds + bats; bat subset = *Eidolon helvum* + *Pteropus lylei* | yes in point RDS (`height_gener` from source MSL/ellipsoid height) | 8 bat study×species panels in segment metadata | **STRUCTURAL STOP / POINT VERTICAL UNOPENED** | 5 necessary-screen panels entered sealed point preflight; all 5 had zero >=50-fix nights. Three Eidolon panels belong to historical 10.5441/001/1.k8n02jn8 data universe; two Pteropus panels are new but structurally stopped in the thinned commuting-segment compilation |
| Movebank 10.5441/001/1.j25661td | Movebank Data Repository | *Pteropus lylei* (Cambodia 2016) | **no native vertical field in event headers** | 14 GPS-collared bats reported | **REJECT — NO VERTICAL RESPONSE** | DOI landing/header audit found two event-like headers and neither contained accepted native height/altitude; no numeric event rows opened |
| Movebank 10.5441/001/1.5bd6pq55 | Movebank Data Repository | *Pteropus poliocephalus* | yes — `height-above-msl` | 4 repeat individuals under frozen gap>4h / >=50-event session rule | **STRUCTURAL STOP / HEIGHT UNOPENED** | 148,084 rows; 145,262 presence-qualified; 158 eligible sessions; repeat IDs 403, 588, 657, 684; frozen minimum repeat individuals = 5 |
| Movebank 10.5441/001/1.kk3bg2f4 | Movebank Data Repository | *Myotis vivesi* | yes — `height_above_ellipsoid` | 4 repeat individuals under frozen session rule | **STRUCTURAL STOP / HEIGHT UNOPENED** | 14,328 presence-qualified rows; 15 eligible sessions; taxon corrected from frozen-screen provenance label *Noctilio leporinus*; numerical screen result unchanged |
| Movebank raw-screen remaining candidates | Movebank Data Repository | *Lavia frons*, *Noctilio albiventris*, *Vespertilio murinus*, *Rhinolophus ferrumequinum*, *Trachops cirrhosus*, *Myotis daubentonii*, *Carollia* spp. | no accepted native height in event headers | mixed | **REJECT — NO VERTICAL RESPONSE** | outcome-blind raw repository screen; no numeric height parsed |
| high-altitude bat acoustic/radar datasets returned by frozen queries | mixed | various Chiroptera | not individual fix-level GPS | no individual repeated trajectories | **REJECT** | wrong data type |
| UAV / video bat datasets returned by frozen queries | mixed | various Chiroptera | not individual repeated GPS altitude trajectories | no | **REJECT** | wrong data type |

## Final search-snapshot outcome

**No genuinely new source or study panel in the frozen search universe reached the full structural gate for opening a new vertical outcome.**

Accordingly:
- new comparative vertical outcomes opened: **0**;
- new-source PASS results: **0**;
- new-source FAIL results: **0**;
- all new candidates ended as structural STOP, no-native-vertical REJECT, wrong-data-type REJECT, or historical overlap.

This is a **structural-scarcity result**, not evidence that the new taxa lack vertical individuality.

The common limiting feature was repeated-session support at the predeclared >=50-event threshold, especially the requirement for >=5 repeat individuals.

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


## Airflows closure update

The Airflows segment-table audit identified five necessary-screen panels, but the sealed point-level preflight showed **zero >=50-fix nights in all five panels**. No vertical magnitude was accessed or exported.

- Eidolon 14253246: structural STOP; historical data-universe overlap.
- Eidolon 183770262: structural STOP; historical data-universe overlap.
- Eidolon 259100173: structural STOP; historical data-universe overlap.
- Pteropus 6609898: structural STOP; genuinely new study panel, compiled data too sparse under frozen session rule.
- Pteropus 8239320: structural STOP; genuinely new study panel, compiled data too sparse under frozen session rule.

The pre-frozen Airflows vertical design remains **UNUSED** because the height-opening receipt is STOP.

## Provenance-follow-up boundary

The Cambodia *Pteropus lylei* repository DOI `10.5441/001/1.j25661td` is admitted only for an outcome-blind header/structure audit. It was identified while resolving raw provenance for the new Pteropus taxon and before any new-source vertical magnitude in this comparative programme was opened.

This does not authorize:
- new search terms after its header result;
- lowering the current >=50-fix rule;
- substituting Cambodia for the Thailand panels based on a vertical effect.

If it lacks a native event-level vertical field, it is REJECTED and the current search universe closes.


## Subsequent separately frozen small-panel programme

The statements above remain the final outcome of **comparative-generality v1**, whose frozen minimum was >=5 repeat individuals.

After that v1 structural search closed, exactly two independent native-height sources had:
- numeric vertical values still unopened;
- exactly **4** repeat individuals under the unchanged >=50-event / >4-h-gap session rule.

Those two sources were admitted **together** to a new programme, `small_panel_generality/contract_v1.json`, before either source's numeric vertical outcome was opened.

The original v1 structural STOPs were not relabeled or deleted.

### Outcome-blind horizontal axis

Before vertical opening:

| source | taxon | horizontal calibrated excess | p_upper |
|---|---|---:|---:|
| 10.5441/001/1.kk3bg2f4 | *Myotis vivesi* | -0.12378 | 0.5846 |
| 10.5441/001/1.5bd6pq55 | *Pteropus poliocephalus* | +3.48659 | 0.0001 |

Both sources then passed the separately frozen four-individual exact common-support gate.

### Prospective vertical outcomes under the new n=4 design

| source | taxon | centered vertical calibrated excess | p_upper | verdict |
|---|---|---:|---:|---|
| 10.5441/001/1.kk3bg2f4 | *Myotis vivesi* | +0.00470 | 0.4419 | FAIL |
| 10.5441/001/1.5bd6pq55 | *Pteropus poliocephalus* | **+0.16873** | **0.0001** | **PASS** |

Therefore:
- comparative-generality v1 still has **0** opened outcomes under its >=5-individual gate;
- the later small-panel programme has **2** prospective outcomes;
- *P. poliocephalus* supplies a successful independent prospective external replication under that separately frozen design;
- *M. vivesi* supplies a prospective null/FAIL under the same programme.

Do not use the Pteropus PASS to rewrite the earlier v1 structural STOP. The two programmes answer related but distinct design questions.
