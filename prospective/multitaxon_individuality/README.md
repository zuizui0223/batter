# Pattern-first cross-taxon movement individuality and ecological use (database programme)

**New branch: `prospective/multitaxon-identity-ecology-v1`**  
**Research status as of 19 October 2026:** Movebank's **437 published source packages** are fully censused and metadata-screened. Original animal-reference and positional CSV audits have begun across diverse taxa. **One exploratory source-level geographic X curve** exists for 12 2018 green turtles, but **no paired nonbat R–X population pattern, independently measured trophic E, cross-clade effect or generalized ecological result exists.** This is deliberately independent of the [original bat integration draft PR #99](https://github.com/zuizui0223/batter/pull/99), whose source records, source p-values and historical freeze remain unchanged.

## Governing biological question — compare patterns, not invent a threshold

**Across animal taxa and ecological contexts, which dimensions of individual behavior and ecological use differ, and which remain shared?** The authoritative framework is [pattern-first comparative ecology](PATTERN_FIRST_COMPARATIVE_ECOLOGY_V1.md): independently report **R** (held-out behavioral repeatability), **X** (2D geographic use overlap), **T** (temporal shared-place use) and **E** (independently characterized environmental/resource exposure), marking unavailable axes as NOT ESTIMABLE rather than zero. The earlier conditional individuality→partitioning hypothesis is a **secondary follow-up**, not the main publication thesis. An untested threshold or proof of universal niche decoupling is **not** the target.

We require true cross-clade source-based data analysis with clearly eligible animal/site/year cohorts rather than replaying a few bat papers.

Importantly, stable overlapping individual environmental niches (Carlson et al. 2021), movement-derived individual niche hypervolumes (Takola 2026) and individual movement → community resource overlap across Yellowstone ungulates (Caldwell et al. 2026) **already exist**. The prospectively testable addition is the **independent, conditional identity → resource/encounter-partitioning relationship and its ecological moderators**, not the mere existence of individuality or niche overlap.

## 19 October 2026: original source-file and first 2D X pilot

- [Broad metadata sensor/rights/taxon selector](MOVEBANK_METADATA_SCREEN_V1.json) rechecks the same 437 packages with more inclusive **GPS/Argos/radio** sensor tags: **227** metadata-priority CC0/BY with one Latin label, 25 NC review, 50 taxon labels unresolved/multiple and 135 sensor metadata unresolved. This **does not replace** the earlier narrower GPS-keyword ranking (182 + 16 + 239) or confirm any animal-level primary eligibility.
- [Nine original individual-reference CSV receipts](PILOT_SOURCE_REFERENCE_FEASIBILITY_V1.json): elk 175, biological tapirs **74** (eight calibration records excluded), fox 35, experimental pigeon 35, green turtle 33 reference, herring gull 16, loggerhead turtle 11, stork **5 in one 2017 adult part**, and reef manta **n=1** exclusion. These are original reference IDs, **not validated matched GPS cohort n**.
- [Original event quality](ORIGINAL_SOURCE_EVENT_PREFLIGHT_V1.json): loggerhead 10,271 location source rows were **entirely Argos Doppler shift** with 9,013 repeated animal/timestamp keys; nine animals have preliminary multi-date coverage but fail the fine-GPS sensor class. The one-manta sample has 75 GPS rows from **one** animal, which cannot test individuality.
- [Original green turtle year/site cohorts and herring gull STOP](ORIGINAL_GREEN_TURTLE_AND_GULL_COHORT_SOURCE_PREFLIGHT_2026_10_19.json): same Diego Garcia release site, **52,846 original GPS positions from 32 source-tagged animals**; July/October deployment cohorts **2012 n=8**, **2015 n=8 of nine references**, **2018 n=12** pass a *broad 4-fix/day temporal support screen*. **2017 n=4 STOP**. They represent **one species at one source site across three years**, not independent taxa. The other original gull source has **28,649 Argos-only records** and just 2/7/7 animals by source year (2008/2013/2014): not fine-GPS core evidence.
- [First exploratory observed 2D X-only source result](EXPLORATORY_GREEN_TURTLE_2018_SOURCE_X_SCALE_V1.json): 12 July 2018 female green turtles, **2,762 original GPS fixes in first 30 postdeployment days**, daily-equal observation weights and **66 dependent animal pairs**. Mean pair 2D overlap changes from **0.307 at 0.1km to 0.451 at 0.5km, 0.525 at 1km, 0.985 at 5km and 0.999 at 25km** because the sampled geographic extent is only ~11×12km. The initial 25km grid is too coarse: later fine-grid checks are explicitly *post-inspection exploratory sensitivity*, not a predeclared positive ecology test. This is **geographic X only, not diet, actual synchronous co-use, individual conditional R or cross-taxon generality**. [Authorized-original-CSV reproduction script](reproduce_turtle_X_source_v1.py), [synthetic check](tests/test_reproduce_turtle_X_synthetic_v1.py) and [source-cohort axis estimability matrix](NONBAT_R_X_T_E_SOURCE_STATUS_MATRIX_2026_10_19.json) added.
- The original confirmed wolf source remains an independent mammal candidate (12 actual GPS source IDs, 10 source-cadence repeat-pass) with **pack/cohort opportunity not yet validated**; it is not pooled with turtles. No original animal IDs or raw GPS coordinates are committed to this branch.

## Verified 18 October 2026 metadata-only Movebank result

The original Movebank Data Repository *Data packages* DSpace public collection was censused on all nine pages (50 records per page, the last 37), with unique DOI and package UUID:

| Original published repository package metadata | Count |
|---|---:|
| Total packages | **437** |
| Source CC0 packages | **376** |
| Source CC BY 4.0 packages | **27** |
| Source CC BY-NC 4.0 packages | **34** |
| Literal GPS keyword anywhere in stored title/subjects/abstract excerpt | **198** (not confirmed GPS source files) |

This catalogue contains birds, mammals, reptiles and marine movement examples; it **does not** establish 437 independent eligible studies or species. Some DOI/subject records are versions, subsets, multiple taxa or missing usable sensor/individual support. Current metadata alone cannot quantify ecological individuality.

## Expanded 18 October GPS-screening and data-quality implementation

An additional source-hash-pinned [metadata-triage registry](MOVEBANK_METADATA_TRIAGE_V1.json) now separates the full **437** published DOI packages into **182** with explicit **GPS terms in source subject keywords**, **16** with GPS only in title/abstract excerpt and **239** with no such indexed evidence. The latter do **not** represent proven non-GPS exclusions; original file metadata and sensor type must be checked. Original source-package licenses remain **376 CC0 / 27 CC BY / 34 CC BY-NC**.

**14 nonbat, source-metadata-selected potential biological pilots** are separately listed in this registry across carnivores, herbivores, birds, reptiles and marine/soaring foragers, with one deliberately uncertain Galápagos tortoise sensor case. These are a **candidate screening queue**, not 14 eligible cohorts. Five historical bat data packages are labeled benchmark-only and **cannot** serve as independently replicated cross-taxon effects. The **15 pilot examples below** serve a different purpose: testing original metadata and source-format diversity, including one marine mammal. Neither selection is a handpicked list of positive empirical results.

[Executable streaming stage-1 event preflight](preflight_movebank_events_v1.py) accepts an **authorized local original GPS CSV/TSV/GZIP**, requires an independent animal-ID field, valid UTC times, source coordinates and sensor type, and emits **aggregate-only counts**. The provisional stage-1 screening limit is **≥8 individually tracked animals**, **≥4 days with ≥50 fixes each over ≥7 elapsed days**, and **≥3 dates with ≥2 overlapping eligible animals**. Even a passing source count is not a verified single-population/sample-size or a true spatial-overlap/resource-contrast test; source reference/deployment and environment gates remain. Missing source IDs, naive timestamps without explicit operator UTC assumption, invalid coordinates, non-GPS sensors and partial reads are explicit structural/undecided outcomes rather than assumed successes.

[Stage-1 synthetic-only unit tests](tests/test_preflight_movebank_events_v1.py) and [complete metadata triage verifier](validate_movebank_metadata_triage_v1.py) run in the [GitHub Actions test workflow](../../.github/workflows/multitaxon-individuality-metadata-v1.yml), alongside the original 437-record census check and identity-versus-overlap synthetic counterexamples. No actual source individual GPS events or animal IDs are committed.

The [cross-taxon hypothesis and matched-sample statistical plan](CROSS_TAXON_HYPOTHESIS_AND_ANALYSIS_PLAN_V1.md) and the [original broader cross-taxon protocol](CROSS_TAXON_RESEARCH_PROTOCOL_V0_1.md) now both distinguish the general **2D geographic utilization-overlap *intermediate*** from **independently assessed ecological-resource differences** and **physical near-synchronous encounter outcomes**. Geographic overlap itself does not demonstrate diet, competition or a common motor policy. Taxon-level inference and climate/resource moderators remain untested.

## Files and reproducibility

- [Complete 437-publication source metadata and rights census](MOVEBANK_PUBLISHED_DATAPACKAGES_CENSUS_2026_10_18.json): published DOI, UUID, title, issued date, source keywords, rights and limited abstract text — **no bat/animal IDs or GPS points**.
- [Complete cross-taxon scientific analysis and eligibility design](CROSS_TAXON_RESEARCH_PROTOCOL_V0_1.md): pre-outcome eligibility, independent individual predictability versus resource/encounter segregation, multilevel cross-clade inference, altimetry caveats, and failure/stop rules.
- [15 actual published DOI format/rights examples](METADATA_FORMAT_PILOT_SOURCES_V1.json): birds/mammals/reptiles/sea mammal and **all three licenses**. These only exercise source-format review; they are **NOT a convenience science sample**, and original GPS/sensor contents, animal repeats and ecological eligibility are **not yet checked**.
- [Whole-source census/seed verifier](validate_metadata_census_v1.py): standard-library Python, exact count/right checks and source catalogue blob guard.
- [Separate-estimands synthetic controls](validate_distinct_identity_partition_estimands_v1.py): demonstrate that held-out movement-decision individuality is logically distinct from spatial allocation overlap, not a source bat result or ecology mechanism.
- [Offline GitHub Actions validation](../../.github/workflows/multitaxon-individuality-metadata-v1.yml): tests only source metadata, licence receipts and synthetic logic; **no network animal-data acquisition**.

## Analysis and publication boundary

1. **Next:** audit all 437 original source package bitstream/reference records for real GPS events, repeated animals, deployments, UTC, locations, outlier flags, independent site/study/sampling-year populations, source permissions. Publish every DOI's eligibility or reason for rejection. DO NOT claim a biological effect.
2. Freeze **identity information G** from individual-trained but held-out conditional step choices, using the same covariates and effort as a pooled conspecific model, and an appropriate block-permuted null.
3. Independently measure **environmental/resource use** or **physically opportunity-corrected simultaneous co-use** in the source datasets where those ecological quantities are actually identifiable, with disjoint heldout time blocks and dyad dependence.
4. Only if adequate **independent source populations across ≥3 taxonomic groups** and adequate D3 ecological endpoints survive, fit a multilevel source/clade/habitat model testing moderators of individuality-to-segregation. Report negative and nonidentifiable populations openly.
5. A vertically measured **3D tier** applies only to properly calibrated flight height or dive depth; never pretend terrestrial 2D GPS provides an additional altitude niche axis.

**No cross-taxon biology result or journal-ready universal law is claimed at this stage.** The source metadata census and mathematical protocol are completed research infrastructure for the first data-eligibility screen.
