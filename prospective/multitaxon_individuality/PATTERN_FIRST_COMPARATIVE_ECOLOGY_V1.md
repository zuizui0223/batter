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
