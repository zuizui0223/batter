# Pattern-first comparative ecology of behavioral individuality

**Status:** Research design / source triage, NOT a cross-taxon empirical finding.  
**Scope:** Draft PR #100 only (`prospective/multitaxon-identity-ecology-v1`). Do not modify the frozen bat endpoints or the integrated bat manuscript PR #99.  
**Framing change (19 October 2026):** Do **not** make estimation of an individuality-to-partitioning threshold or boundary the primary scientific aim.

## Ecological question

> Across animal taxa and ecological contexts, **which dimensions of individual behavior and ecological use are differentiated, and which remain shared?**

The question is ecological, not primarily a new transfer score or a mathematical boundary:
1. Can individually repeatable movement choices be observed **where animals use the same places**?
2. Does differentiated **geographic space use** necessarily accompany differences in movement behavior?
3. When space overlaps, is use nevertheless differentiated along **time, habitat/resources, or (when measured) height/depth**?
4. How do these recurring configurations vary among biological systems such as central-place foragers, resident territorial animals, migratory animals, and animals sharing concentrated resources?

The target deliverable is a transparent, comparative **distribution of configurations and effect sizes**, including counterexamples and inconclusive source populations. Estimating transitions or moderators is an optional, downstream step supported only after replication. Avoid an a priori binary "partitioned/not partitioned" classification based on an arbitrary score cutoff.

## Separate ecological axes, measured on the same eligible individuals

| Axis | Operational observation | Biological reading | Hard boundary |
|---|---|---|---|
| R — behavioral repeatability | Held-out individual-versus-conspecific prediction for comparable movement modes **within common places, time-gap and season strata** | Repeatable differences in movement use | Not proof of learned policy, diet, competition or route causality |
| X — horizontal sharing | Balanced pairwise 2D utilization-distribution overlap in the same available region and season, with source-aware uncertainty | Shared versus different *estimated geographic use* | Not simultaneous co-presence or resource sharing |
| T — temporal sharing | Shared-patch visit and diel/activity-time overlap on externally justified windows; opportunity/phase-shift null when resolution permits | Temporal differentiation *within geographic overlap* | Low-frequency 2-h fixes do not resolve fine encounter avoidance |
| E — environmental/resource exposure | Individual use of **independently obtained** land-cover/vegetation/phenology/habitat layers over common environmental availability; source-supported foraging observations where present | Habitat-exposure differentiation; independently measured diet only where available | Exposure to NDVI/landcover is not feeding, diet or resource consumption |
| Z — altitude/depth (optional) | Actual calibrated height or dive-depth distributions for appropriately measured systems | Vertical differentiation | 2D GPS, individual-centered relative height and smoothed 3D overlap are not physical airspace/resource segregation |

`R` and `X` summarize different functionals of tracking data: their comparison is descriptive, *not* independent causal validation. For a biological resource conclusion require an independent ecological endpoint (remote environmental layers, verified feeding/foraging records, diet or prey data). Each axis has its own explicit **ESTIMABLE / NOT ESTIMABLE** flag; unavailable outcomes are missing, never zero.

## Pattern classes worth discovering (descriptive, not forced bins)

- **Same places, different ways of moving:** positive individual repeatability with broad 2D overlap and common ecological opportunity; test whether time or habitat then differs.
- **Different places, no demonstrated movement-mode individuality:** geographic separation can arise from home range, central-place constraint or landscape access even without a repeatable mode effect conditional on comparable places.
- **Same places, different times:** shared geography but temporally partitioned patch use; distinguish diel scheduling from verified simultaneous encounter avoidance.
- **Same geography, different habitat/resource exposure:** only if a source-independent environmental or trophic dimension distinguishes individuals after habitat availability and spatial effort are considered.
- **Context-dependent individuality:** individuals retain a signature in a season/task but shift or lose it in another; only within-source repeated re-exposure can establish that pattern.

Plot **continuous R versus X** across independent cohorts, with separate panels for temporal sharing and resource/habitat divergence and symbol coding for ecological context. Show uncertainty, sample support and `NOT ESTIMABLE` status. Do not invent thresholds to put cohorts into quadrants.

## Why this is not just another statement that individual niches overlap

Previous studies already describe individual niche overlap, movement hypervolumes and relationships between individual movement and community resource use (e.g., Caldwell et al. 2026, *Current Biology*, DOI: 10.1016/j.cub.2026.05.041). The possible *new empirical contribution* is a **matched-cohort cross-clade ecology of how R, X, T and E agree or dissociate**, across objectively included source studies, with independent ecological covariates and negative/unidentifiable systems preserved. Any general claim depends on real source-level results, not the number of repository DOIs.

## Verified October 19 original-source expansion (pattern-first scope)

A separate [broader GPS/Argos/radio keyword preflight](MOVEBANK_METADATA_SCREEN_V1.json) classified the identical 437 published source packages as **227 broad metadata priorities, 25 source-rights-NC review, 50 spatial-sensor but unresolved/multiple taxa, and 135 sensor metadata unresolved**. **This is NOT a replacement** for the existing stricter *GPS-only keyword* snapshot (182 GPS-tag, 16 GPS in description/title only, 239 not indexed) and **not 227 biologically usable studies**; broad Argos/radio/satellite tags can conceal sensor quality and time granularity.

Nine additional original small source reference CSVs have been checked: tapir **74 real taxon-labelled reference IDs** after removing eight calibration rows, elk 175, red fox 35, gull 16, experimental pigeon 35, loggerhead 11, green turtle 33, white stork **five in one 2017 adult part**, and a reef manta sample with **one animal** (STOP as individual contrast). These counts are source *reference membership*, not population-season eligibility.

**Original event sensor checks matter:** the loggerhead CSV (10,271 events, 11 source IDs) is entirely Argos Doppler-shift, with 9,013 same-animal/timestamp collisions, not a fine GPS R/X study; the one-manta sample has 75 GPS fixes from one animal, still n=1 STOP. A second original seabird file contained **28,649 Argos-only herring gull records** (16 reference IDs) but no deployment-year cohort with ≥8 bats/birds: 2008 n2, 2013 n7, 2014 n7, so hold for low-precision/small-cohort studies rather than changing thresholds.

**First genuine GPS cohort candidate beyond bats: green turtles.** At original Diego Garcia source site, the published original GPS file has **52,846 unique tagged/time georeferenced fixes**, **32 animals with tracking events** (33 referenced deployments), and original deployment-month cohorts **2012-10 n8**, **2015-07 n8** (9 in reference), **2018-07 n12** with source-cadence 4fix/day×10days×30day-span support and shared dates; 2017 only n4 STOP. The three qualifying years are **one species/site with potentially correlated multiyear biology**, not three independent taxa or independently confirmed ecological niche contrasts. The [source-year and Argos negative audit](ORIGINAL_GREEN_TURTLE_AND_GULL_COHORT_SOURCE_PREFLIGHT_2026_10_19.json) records the original file and support counts.

**First explicitly exploratory X-only original-source value, NOT R/X inference or a niche result:** In **12 original July 2018 female green turtles** at one site, the first 30 postdeployment days contain **2,762 valid GPS fixes**, 28–31 source calendar days per animal and 66 dependent animal pairs. After balancing each animal's calendar days equally, the original unsmoothed 2D occupancy overlap averaged **0.307 at 0.1 km, 0.451 at 0.5 km, 0.525 at 1 km, 0.596 at 2 km, 0.985 at 5 km, and 0.999 at 25 km**. The original 30-day geographic bounding region is only about **11 × 12 km**; thus the near-unit 5–25 km overlap is a **coarse-grid saturation artefact** and cannot be described as resource-sharing proof. Finer grid sensitivity was added *after* seeing the coarse 25-km result; mark the whole scale curve **EXPLORATORY**. No physical synchronous use, prey/diet, environmental E, time T or held-out movement identity R result was calculated. [Source aggregate X receipt](EXPLORATORY_GREEN_TURTLE_2018_SOURCE_X_SCALE_V1.json) · [offline original-CSV reproduction script](reproduce_turtle_X_source_v1.py) · [synthetic-only tests](tests/test_reproduce_turtle_X_synthetic_v1.py).

**Necessary pattern-first implication:** any future X comparison must report a **resolution curve relative to actual observed spatial range and positional error**, rather than one globally fixed kilometre grid. Within-species/source-cohort X and conditional movement R must use the **same verified individuals/season/environmental opportunity**, and independently measured habitat or food E must be reported as **NOT ESTIMABLE** until verified; a high X at a coarse grid alone does not mean common foraging resources.

## Present factual baseline — no cross-clade effect yet

- Historical bat research: six tracking panels, four bat taxa show repeatable vertical identity after common horizontal-cell weighting; five of six retain the centered shape endpoint in the later integrated audit. Four tropical panel estimates of relative-altitude segregation do not support positive segregation. Those estimands are **neither measured resource partitioning nor independent evidence that actual physical co-use is absent**; the four tropical panels represent two species. The original bat series is a motivating boundary case, **not independent new-clade replication**.
- Movebank public Data Repository metadata frame (18 October 2026): **437 distinct indexed packages**, **not 437 independent studies, populations or taxa**; source-format and rights triage exists.
- Published nonbat source files inspected to date: copperhead (radio telemetry, no GPS-event admission); Ukraine crane (4 GPS individuals); Humboldt penguin (421 GPS records, temporally insufficient); wolf (**12 GPS animal-ID strings, 15,159 records; 10 provisional repeat-pass at original 2-h cadence, 396 shared tracking dates**). The wolf cohort/precision/context and ecological outcomes remain unverified. See `FOUR_NONBAT_SOURCE_EVENT_AND_CADENCE_PREFLIGHT_2026_10_19.json`.
- Eight source reference tables were inspected, but **no reference-only cohort is an admitted biological test**. Example candidate group sizes (not confirmed source GPS eligibility): elephant 14, deer 135, tortoise 46 over species/sites, gull 15 across two breeding sites, tapir 82 including calibration labels. These are candidates for ecological contrasts, not measured patterns.

## Ecologically deliberate source expansion

Prioritize objectively screenable *independent source populations*, not spectacular GPS tracks. After verifying exact event/reference files, deployment and rights:

1. **Resident terrestrial mammals** — wolf (2-hour cadence), African elephant (30-min cadence) and mule deer (source cadence pending) are useful prospective contrasts in social/central-place structure and landscape/resource seasonality. Do not combine packs/sites/years before reference audit.
2. **Bird central-place foragers and migrants** — gull (15 reference IDs but 7/8 split across sites), adequately sampled seabirds and migratory birds should be screened independently; the gull site split may make either population ineligible. Pigeon experimental relocation must not be treated as undisturbed natural movement.
3. **Reptiles and different movement rates** — Galápagos tortoise (46 reference IDs across multiple species and sites) is a scale/cadence contrast; split taxonomy/site and verify event support before analysis.

The aim is **ecological and phylogenetic breadth with transparent source attrition**, not artificially identical GPS fix intervals. A 2-hour wolf track can support broad daily patterns but not high-frequency turns or encounter avoidance. Preserve pre-analysis cadence tiers and evaluate temporal and horizontal scales appropriate to each source, with a conservative shared-resolution sensitivity analysis. Do not lower gates after opening positive or negative `R/X/T/E` outcomes.

## First actual comparative output

Create a source-population-by-season analysis table with one row per independent eligible cohort and fields:

```
study_doi | taxon | biological_cohort | season | habitat_context |
n_animals | n_independent_days | sensor | sampling_cadence | precision |
R_effect | R_uncertainty | R_status |
X_overlap | X_uncertainty | X_status |
T_overlap | T_reference | T_status |
E_habitat_divergence | E_availability | E_status |
measured_trophic_resource | independent_trophic_evidence_status |
ecological_notes | cohort_exclusion_reason
```

All public outputs must suppress exact individual IDs, source animal GPS coordinates and tracking dates; protected wildlife movement locations require source-governance review. Biological cohort, population, individual and dyad uncertainties cannot be conflated; multiple DOI packages can share the same cohort.

**Figure 1:** Ecological pattern space R × X, each point an independently validated population–season (with source/phylogeny grouping, uncertainty and visibly missing T/E).  
**Figure 2:** For overlapping cohorts, gradients of temporal overlap and independent environmental exposure differences, not a fake "niche segregation index."  
**Figure 3:** How those different pattern components vary with externally measured resource predictability, landscape patchiness, independently documented social/foraging organization and season, **only if comparative replication permits**.

### Completion and claim gates

- The first milestone is **at least two independent nonbat, source-verified populations with reportable R and X** and explicit T/E eligibility. They constitute case comparison, not global inference.
- A cross-clade ecological result requires broad replicated populations and at least **three major represented clades**, genuine source-independent ecological outcomes, source/taxon clustering and full inclusion/STOP accounting. If T/E cannot be measured, publish an appropriately limited behavioral-and-spatial-comparison result, **not** a resource-partitioning paper.
- Do not report a universal coupling, threshold, cause or ecological generality while nonbat `R/X/T/E` remain unopened.

**Immediate next source action:** inventory elephant, deer, tortoise and an independent bird population event files; audit the wolf's same-population animals and common environmental opportunity; then compute the first **descriptive R × X patterns** from observed animals, not synthetic examples. Source environmental exposure and temporal co-use are separately established only where estimable.
