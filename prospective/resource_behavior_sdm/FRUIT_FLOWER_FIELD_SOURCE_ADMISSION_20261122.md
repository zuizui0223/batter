# Fruit/flower source admission: original data grain and support (2026-11-22)

**Status:** newly reviewed public metadata and a source-free, outcome-blind support validator. No source-original bat/cactus/fruit rows opened; no new empirical fitted score. Draft batter PR #102 only.

## What is and is not available

| Candidate | Source-based observation | Eligible conclusion now | Hard source blocker |
|---|---|---|---|
| Goldshtein et al. (2020), [article](https://doi.org/10.1016/j.cub.2020.07.079), [Mendeley Data v1](https://data.mendeley.com/datasets/jxghjjsttw/1), DOI 10.17632/jxghjjsttw.1 | Published tracking of 17 bats, ~3,600 mapped cactus **positions** in fields associated with eight GPS bats; separate repeated open-flower surveys of 414 cacti in three fields. Landing page identifies movement, video and nectar-model files but does not expose a verified file roster in the public text reader. Mendeley public-data [API docs](https://data.mendeley.com/api/docs/) describe OAuth2 authorization for metadata and file-download routes. The last independently authenticated original API result in the project remains HTTP401 on 2026-11-21. | **Stage A may become possible:** static cactus spatial opportunity and heldout GPS altitude *after* original source and same-field coverage inspection; not true nectar quantity. | Exact original archive members, publisher/source digest, survey polygon, GPS height/reference and source-table join uninspected. **Stage B additionally requires dates and direct flower census matched to GPS area and nights.** Simulation-assigned flowers are not evidence. |
| Panama *Phyllostomus hastatus*, [Calderón-Capote et al. 2024](https://doi.org/10.1098/rsbl.2024.0424), [Dryad](https://doi.org/10.5061/dryad.5qfttdzgj) | Linked GPS cohorts in Movebank DOIs 10.5441/001/1.282, 10.5441/001/1.321, 10.5441/001/1.322; public Dryad lists README.md and stan.zip, but **no separate quantitative, event-aligned flower/fruit table**. The published study notes limited diet and resource-availability knowledge. | GPS and season/colony behavioral questions may be separately addressed; **not** measured resource × individual altitude. Qualitative dry-season balsa availability is not a numeric same-night measure. | Independent, dated and quantitative balsa/fruit survey on used and available habitat; event/field/night keys and detection/height calibration not verified. |

This is a targeted public-source audit, not proof that a private, later or otherwise unlisted quantitative survey does not exist. The Mendeley landing page's Download All text is not proof that unauthenticated programmatic access works. Neither access barrier nor absent resource table is a negative biological result.

## Implemented source-independent gate

The new [fruit_flower_source_support_gate_v1.py](fruit_flower_source_support_gate_v1.py) and [synthetic tests](test_fruit_flower_source_support_gate_v1.py) take four **locally normalized, separate** inputs: a height-blind GPS projection (animal, canonical study-night, independent field); original cactus layout (cactus, field); independent field-survey coverage (positive area and independently declared field polygon); and directly observed flower counts (cactus, *exact* study-night, nonnegative count, sampling effort).

- **Stage A:** counts potential GPS support within independently surveyed cactus-layout fields. Cactus position is stable opportunity, **not a sampled flower quantity**.
- **Stage B, strict complete-field-night sub-design:** requires a directly observed count for **every mapped cactus** in a field on the exact matched bat night. Incomplete and otherwise sampled cacti are NOT imputed zero; true surveyed zero is valid. Partial censuses require a separately predeclared sampling-design/inclusion-weight estimand rather than promotion by this strict validator.
- Detects duplicate plants and censuses, undeclared survey polygons, unverified/simulated flowers, invalid days, missing or impossible count/effort, and any altitude or height-derived visit labels in the GPS projection.
- Emits aggregate counts only (individuals, animal-nights, records, mapped sites, missing cactus-night cells); never outputs field/cactus/bat IDs or original rows.
- Reports **schema coverage / potential only**, explicitly leaving publisher identity, independent source geometry, sensor error, behavior-state validation, observation sampling and any biological predictive effect **unverified/null**. User-supplied JSON assertions cannot certify an original source.

The gate is intentionally **not** a fitter, geographic assignment engine, or source authenticator. It does not compute a new GPS-resource score and cannot verify its own input-provenance declarations. Synthetic fixtures test Stage A-only, complete/partial Stage B, different dates, explicit observed zero, duplicate keys, simulated bloom rejection, height-label leakage and identifier suppression.

## Next source-normalization order (after legitimate archive acquisition)

1. Verify original DOI/version, official file roster and local SHA; use [existing original-archive structural gate](goldshtein_user_archive_structural_gate_v1.py) without executing downloaded source scripts or opening outcome heights.
2. Independently document the actual surveyed polygons, field mapping, night-key convention and direct flower-census effort. Build the height-blind normalized projections *locally*, without sharing original GPS/cactus rows in GitHub.
3. Run the new gate to enumerate potential matched bat-nights; independently verify altitude datum/error and relevant source coverage **before** freezing any height prediction test.
4. If admissible, freeze a same-support, out-of-night/individual Stage A comparison. Freeze Stage B only if independent directly measured flowers and scientifically defensible availability support actually match. Otherwise keep it STOP.

**Current claim gate:** Goldshtein Stage A NOT_SOURCE_ADMITTED; Goldshtein Stage B STOP_UNVERIFIED_DATED_FLOWER_JOIN; Panama measured-food × individual height STOP_NO_QUANTITATIVE_MATCHED_RESOURCE_TABLE. All seven strict unestimated resource-behavior-SDM effects remain null. No PLOS/Krauel/Cistrone reopening, protected main or frozen manuscript changes.
