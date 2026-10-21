# Pattern-first cross-taxon movement individuality and ecological use (database programme)

## 21 October 2026: fine-distance source-GPS time alignment, 500 m to >2 km

The [source-verifiable four-band report](SUBHOUR_DISTANCE_BANDS_RESULT_2026_10_21.md)
now separates original-GPS matched-time distance observations
into [0,500m], (500m,1km], (1,2km], and >2km bins. It distinguishes
actual observed pair-fix distance frequency O, exact same-date
time-assignment reference N, and conditional surplus D=O−N,
without claiming physical encounters. The
[fixed, explicitly post-inspection design](DISTANCE_BAND_CLOCK_ALIGNMENT_DESIGN_2026_10_21.md),
[reproduction and receipt validator](distance_band_from_subhour_v1.py),
[10 synthesis/receipt tests](tests/test_distance_band_from_subhour_v1.py),
[full 480 seed×band rows](SUBHOUR_DISTANCE_BANDS_2026_10_21.json)
and [40-row independent-check CSV](SUBHOUR_DISTANCE_BANDS_SUMMARY_2026_10_21.csv)
are committed; original source GPS files were verified in the
preceding source-geodesic analysis, not newly downloaded here.

**White-tailed deer 2019 and 2020:** in these particular sources,
absolute observed GPS proximity within 500 m is higher in summer,
but conditional source-clock pairing surplus within 500 m is
higher in winter, while the surplus in the 1–2 km distance band
is lower in winter. At ±15 min, both seasonal band contrasts
hold their direction in 12/12 finite-source GPS subsamples;
at ±30 min, deer 2019's 1–2 km seasonal contrast is negative
in **11/12**, not 12/12. Turkey has higher *absolute* winter
500-m GPS proximity and more positive conditional winter
near-band surplus, while black bear is inconsistent when the
time tolerance and eligible dyad set change (38 vs 47).
These are time-matched *geographic* patterns, NOT biological
synchronization, avoidance, social-network links, resource
sharing, or general taxon-level laws. Four band D values
necessarily sum to zero, a mathematical identity, not a
mechanism. Independent population labels, source clock
calibration, GPS error and autocorrelation-preserving null
comparisons remain unresolved.

## 20 October 2026: source-clock-matched temporal sharing versus 2D space

An [original GPS source-clock analysis](SAME_CLOCK_BIN_COUSE_RESULT_2026_10_20.md)
now independently measures X (the same dates' pooled geographic overlap),
T6/T3 (overlap in identical 6-hour/3-hour source-clock bins) and D = T−N,
where N is the exact within-day time-bin-relabeling expectation. All 3
original published Movebank GPS/reference archives passed publisher MD5,
previously pinned SHA256 and an independent exact source-time/position QC
reconstruction. Five source/year cohorts have 480 source/year/clock/grid/seed
aggregate outcomes; black bear 2019 remains STOP for inadequate supported
dyads. At 1 km, turkey 2019/2020 and white-tailed deer 2019/2020 have higher
winter D in all 12 observation draws under both 6-hour and 3-hour binning.
In white-tailed deer, **winter geographic X is actually lower than summer
at 1 km**, so the temporal ordering cannot be inferred from X's direction.
At primary 5 km spatial resolution this pattern is not stable across all
cohorts; no taxon-general winter time-coincidence law or actual encounters
are claimed. Verified aggregate outputs, source-native code, fixed
post-inspection design, CI and synthetic controls are linked in the report.

## 20 October 2026: GPS effort-standardized original-source seasonal X audit

Three source-matched published GPS datasets (wild turkey, black bear and
white-tailed deer) were redownloaded from their complete original Movebank
files and verified against original MD5 plus pinned SHA256. The
[observation-effort report](SEASONAL_EDGE_EFFORT_BALANCE_RESULT_2026_10_20.md),
[source-locked design](SEASONAL_EDGE_OBSERVATION_BALANCE_DESIGN_2026_10_20.md),
[reproduction code](seasonal_edge_observation_balance_v1.py) and
[aggregate-output verifier](validate_seasonal_effort_output_v1.py) cover
**two supported months/season, seven common dates/month, exactly one or two
GPS fixes/animal/date, 24 deterministic sampling draws and four declared grids**.
The original 1-fix dyad risk sets exactly reconcile to prior V2. The three
full aggregate-only output JSONs are permanently committed.

At the reference 5-km grid, turkey 2019 has positive winter incidence and
positive conditional strength. Turkey 2020 has positive winter incidence but
grid-sensitive strength. Black bear 2020 has **more summer-positive overlap
dyads and stronger winter-positive overlap**, nearly cancelling mean X.
White-tailed deer 2020 has **more winter-positive dyads but stronger
summer-positive overlap** in every seed across all four declared grids
at both fix rates, even though the mean X seasonal direction reverses
with the grid. These are exploratory geography-only descriptions, **not**
source-population membership, social association or resource partitioning.
The bear k=2 dyad cohort falls from 104 to 69 and cannot be compared with
k=1 as if it were the same pair set.

## 20 October 2026: source-derived overlap edge retention (post-inspection)

The [edge topology audit](EDGE_TOPOLOGY_CROSS_SOURCE_2026_10_20.md) now contrasts
*which matched individual pairs share geographic space* separately from the
mean overlap X. The [aggregate-only reference ledger](EDGE_TOPOLOGY_REFERENCE_2026_10_20.json),
[pinned-archive verifier](validate_edge_topology_v1.py), and
[synthetic and receipt tests](tests/test_edge_topology_v1.py) check 80 source/year/window/risk-set
strata and 1,280 spatial-grid scenarios. Turkey 2019/2020 seasonal differences
are configured differently; bear 2020 has more summer-overlapping dyads but
weaker positive-overlap strength; white-tailed deer 2019 replaces some pairs
without changing edge density, whereas 2020's incidence and strength move
in opposite directions across all 16 settings. These are *exploratory
source-specific geographic X descriptions only*. No social encounters, food
segregation, population-independent cross-taxon generality, or other-taxon R
has been inferred.

## 20 October 2026: source-verified turkey, bear and moose seasonal X comparison

The [independent-source seasonal sharing synthesis](CROSS_SPECIES_SEASONAL_NETWORK_SYNTHESIS_2026_10_20.md) now covers original-file-MD5-verified published GPS archives from wild turkey, black bear and two moose sources. Full source-level output and all 16 grid-width/origin sensitivities are archived in [aggregate JSON](CROSS_SOURCE_SEASONAL_X_EXPLORATORY_ACTION.json) and [comparison table](CROSS_SOURCE_SEASONAL_X_EXPLORATORY_ACTION.md). For turkey 2019 and 2020 the mean geographic X is higher in winter on the reference 5-km grid, but the change primarily involves conditional-positive strength in 2019 and dyad incidence in 2020. For black bear 2020, an increase in the proportion of sharing pairs is offset by weaker conditional sharing strength, nearly eliminating the mean seasonal X difference. These are source-level descriptive contrasts, **not** independent populations or niche-partitioning mechanisms. Snowy Range moose supports only a separate Jan–Feb vs Mar–Apr contrast with opposite signs in 2019 and 2020; the Bighorn archive remains timestamp-format STOP. Other-taxon R, resource E and encounters T are not measured, and numeric pooling with bat/deer R is prohibited.

**New branch: `prospective/multitaxon-identity-ecology-v1`**  
**Research status as of 20 October 2026:** Movebank's **437 published source packages** are fully censused and metadata-screened. Original animal-reference and positional CSV audits span diverse taxa. The fox pilot is exactly reproduced, with **six source-months of paired descriptive movement-gain R and geographic-overlap X for the same 3–5 animals and heldout period**. The larger mule-deer analysis is now complete for **all 36 months of 2018–2020**, using **836,636 cadence-matched steps** and 9–88 evaluated animals per month. Annual constant-cohort geographic overlap is higher in winter than summer in all 48 declared year/scale/origin settings. The personal movement model has a small positive same-record weighting gain in 27/36 months; this is descriptive model evidence, not a calibrated biological identity effect. Cross-taxon generality, independently measured environmental/resource exposure E and encounter T remain unestablished. This work is independent of the [original bat integration draft PR #99](https://github.com/zuizui0223/batter/pull/99).

## 20 October 2026: completed mule-deer seasonal R/X analysis

- [Full findings, all 36 months and reproduction commands](DEER_SEASONAL_RX_RESULT_2026_10_20.md),
  [figure](DEER_SEASONAL_RX_FIGURE_2026_10_20.png),
  [monthly CSV](DEER_SEASONAL_RX_MONTHLY_2026_10_20.csv),
  [primary numerical outputs](DEER_SEASONAL_RX_RESULT_2026_10_20.json),
  [144 additional R sensitivity scenarios](DEER_SEASONAL_RX_SENSITIVITY_2026_10_20.json),
  [same-record comparator audit](DEER_EQUAL_DATA_AUDIT_2026_10_20.json).
- Source: one source-labeled Sublette herd, **135 adult females**. Original GPS
  and reference files match published MD5 and pinned SHA-256 receipts. Of 948,632
  original GPS rows, 948,400 fall in 2018–2020. No individual migration labels,
  quantitative GPS error or verified absolute UTC offset are available.
- **836,636** same-animal/tag/date/month steps have 108–132-minute duration.
  Every month is retained. Primary conditional net-displacement prediction uses
  two calendar-half cross-fitting folds and **343,879 heldout steps**; each
  monthly X result uses exactly those final R animals, with pair-shared-date
  geographic occupancy weights.
- Holding the X cohort constant within each year leaves **66/64/42 animals**.
  At the unshifted 5-km grid, winter/summer mean overlap is **0.1692/0.0097**,
  **0.0833/0.0279** and **0.0879/0.0265** in 2018/2019/2020. The winter-minus-summer
  mean is positive at all four scales and four origins in all three years.
  These are dependent sensitivity settings, and pair medians are zero in 2019
  and 2020; the average does not imply every pair converges.
- The original personal model beats a peer-only model in **35/36 months**
  (mean CRPS gain +0.010343). That contrast adds focal training data. A transparent
  **post-primary-inspection** audit compares the unchanged model with an
  anonymous pool using the **same records**: **27/36 months**, mean +0.001093.
  Paired seasonal personal-weighting gains are slightly negative in winter and
  positive in summer in each year. Changing training precision, peer references
  and unmeasured context remain possible explanations. The same-record audit
  covers the 36 primary 5-km/origin-zero settings only.
- The [design](DEER_SEASONAL_RX_DESIGN_2026_10_20.md) was recorded locally before
  primary R/X inspection and uploaded with the results; it is not an external
  preregistration. Independent weighted-CRPS and original-source geographic
  reconstructions agree with stored results. No raw animal/tag identifiers,
  exact tracking dates, coordinates or grid cells are published.

Executable programs: [source preparation](deer_source_pipeline_v1.py),
[geographic occupancy](deer_geography_v1.py),
[primary and sensitivity analysis](deer_seasonal_rx_v1.py),
[same-record audit](deer_equal_data_audit_v1.py) and
[figure generation](plot_deer_seasonal_rx_v1.py).

The [next acquisition batch](NEXT_COMPARATIVE_SOURCE_BATCH_2026_10_20.json)
contains 19 packages selected by an exact archived abstract-prefix match,
including the completed deer source. Of the **18 new metadata candidates**,
**nine have CC0 and three CC BY metadata**, with six CC BY-NC. They are not yet
eligible cohorts or independent source replications; full source support and
independence remain to be checked.

## Earlier 20 October 2026: original-file acquisition and coarse support screen

The [deer/stork original-file receipt](NEXT_SOURCE_STORK_DEER_RECEIPT_2026_10_20.json)
and [reproduction program](next_source_stork_deer_receipt_v1.py) extend the existing
source queue beyond the small fox example. The complete CC0 mule-deer GPS source
([DOI 10.5441/001/1.708](https://doi.org/10.5441/001/1.708)) has **948,632 rows and
135 source animals**, all female in the reference table. The downloaded original
GPS and reference files match the publisher's MD5 values. All event rows have
GPS sensor type, explicit visibility, the expected taxon, valid coordinate ranges
and parseable times. No event animal is absent from the reference table, and no
animal/timestamp duplicates were found.

| Source year | Animals with GPS | GPS rows | Animals with ≥100 rows on ≥7 dates | Animals passing monthly shared-context support, min–max |
|---|---:|---:|---:|---:|
| 2018 | 106 | 338,581 | 105 | 43–99 |
| 2019 | 107 | 330,944 | 107 | 47–99 |
| 2020 | 93 | 278,875 | 92 | 38–85 |

An additional **232 rows from 61 animals on one source-calendar date in 2021**
are included in the original-file count but excluded from the 36-month support
screen. Animals recur across years; the annual counts cannot be summed as
independent animals. The main-year median sampling interval is two hours, so the
fox's ten-minute movement classes cannot simply be transferred to this source.

The support screen uses **5-km cells × 6-hour source-clock bins**. An animal must
have ≥15 fixes on ≥2 dates in a context; a shared context needs ≥2 such animals;
the final supported animal must have ≥15 fixes on ≥3 dates across its own
qualifying shared contexts. All 36 months are retained. This establishes coarse
repeated geographic/time-of-day support, not verified common biological
populations, simultaneous encounters, environmental exposure or a movement
effect. The source README allows **UTC or GPS time**; its absolute clock basis
has not been resolved. The receipt separately reports same-date shared-context
support, which can be zero for an otherwise supported animal.

This acquisition-stage screen preceded the completed deer R/X analysis above.
Its coarse support counts differ from the final heldout analysis cohorts and
did not justify transferring the fox identity test unchanged.

For white storks ([DOI 10.5441/001/1.4192t2j4_2](https://doi.org/10.5441/001/1.4192t2j4_2)),
the original reference file is verified: **109 deployment rows, 108 animal IDs
and 70 tags**, with 30 tags assigned to multiple animals. The full 508-MB GPS set
is catalogued but not downloaded in this bounded acquisition. This is reference
availability only, not a validated GPS cohort.

## 20 October 2026: completed fox matched R/X continuation

- [Full result and interpretation](FOX_MATCHED_CORRESPONDENCE_RESULT_2026_10_20.md),
  [all numerical outputs](FOX_MATCHED_CORRESPONDENCE_RESULT_2026_10_20.json),
  [design fixed before the new outputs](FOX_MATCHED_CORRESPONDENCE_DESIGN_2026_10_20.md).
- Original CC0 files checked against public MD5: **166,338 source rows → 145,581
  quality-controlled fixes → 130,923 same-day steps**, with 35 source IDs and 39
  deployments. [Legacy reproduction](FOX_LEGACY_REPRODUCTION_2026_10_20.json)
  recovers all 60 count fields and 30 gains (maximum numerical difference 7.64e-17).
- The shared-calendar sensitivity uses the first/second calendar-month halves for
  every animal and a fixed evaluation mask. Alternative identity models must have
  training support for **every** scored context. No unsupported pooled fallback
  can manufacture self-identity evidence.
- Primary Somerley May 2019: **4 animals, 5,783 test steps**, B=+0.001442 nats/step,
  matched X1km=0.182089 over six dependent dyads. Only two allowed whole-identity
  maps exist, so the reference tail fraction is 0.5 and is support-limited.
- Britford May 2016: the true mapping ranks first of 24, but B=**−0.011198** against
  pooling. The binary-speed and independent activity-channel diagnostics each
  have reference tail 0.125. Do not call this a supported positive R effect.
- Every preselected month and both grid widths are reported. Geographic overlap
  is strongly sensitive to cell size/origin. The mapping reference is conditional
  on an explicit observational exchangeability assumption, **not a randomized
  biological p-value**. Broader ecological generality remains unestablished.

Executable programs: [source/pilot reproduction](fox_source_pipeline_v1.py) and
[calendar correspondence plus matched geography](fox_matched_correspondence_v1.py).
They accept separately obtained source CSVs and publish aggregate-only outputs.

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

1. **Next:** continue actual source analysis through the reproducible comparative acquisition queue. Verify real sensors, repeated animals, cadence, deployments, clock basis and source-population independence before estimating each cohort. Retain the full 437-package census and report exclusions without treating metadata counts as biological replication.
2. Compare source-specific heldout **R** with the same training records and comparable context support, and report **X** at declared scales and origins. The deer same-record comparator is a descriptive model contrast; calibrated biological identity evidence requires additional defensible exchangeability or model assumptions. Do not numerically pool CRPS with the fox log-score endpoint.
3. Measure **environmental/resource exposure E** and **simultaneous co-use T** separately where the source supports them, accounting for opportunity and dyad dependence. Missing E or T does not erase an estimable R/X pattern and must not be substituted with geographic overlap.
4. A cross-taxon pattern requires independent eligible populations beyond this single deer source and the small fox pilot. The earlier protocol's ≥3-taxonomic-group and D3-endpoint conditions apply to its secondary individuality-to-resource-segregation model. Report negative and nonidentifiable populations alongside positive descriptions.
5. A vertically measured **3D tier** applies only to properly calibrated flight height or dive depth; never pretend terrestrial 2D GPS provides an additional altitude niche axis.

**No cross-taxon generality or universal law is established at this stage.** The programme now includes source-derived fox and deer R/X descriptions and a turtle X-only result, with explicit limits on their comparability and ecological meaning.
