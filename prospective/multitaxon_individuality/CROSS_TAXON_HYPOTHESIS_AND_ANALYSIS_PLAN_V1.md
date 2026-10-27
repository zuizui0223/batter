# Cross-taxon movement individuality: database research design v1

**Working paper:** *When does persistent individuality become ecological niche separation? A cross-taxon movement-data test*

**Status at 18 October 2026:** outcome-unopened **design and metadata census**, NOT registered statistical protocol, empirical multiclass confirmation, individual-level population dataset, or a completed macroanalysis. The original bat reanalyses motivate the question but **must not** be counted as independently confirmed replication here.

## 1. Positive, testable ecological question

**Among animals occupying the same available landscapes, is individual-specific movement behavior predictably repeatable within comparable places and seasons, and when does this behavioral individuality coincide with exclusive geographic-space use?**

This moves the study beyond a proposition already supported in named species (that individual niches differ but overlap). The target is a **cross-population *coupling surface***: how strongly *behavioral identity conditional on shared place* and *geographical niche partitioning* covary across genuinely different populations and taxa, with prespecified ecological moderators and source-study dependence.

**Novel candidate result (not yet observed):** predictable movement signatures can persist under overlapping geographic use, and the association between signature strength and exclusive spatial partitioning varies systematically with habitat/resource seasonality and spatial heterogeneity. A null or opposite coupling and a finding that differences vanish after accounting for habitat are important falsifiers.

## 2. Data source and non-independence unit

The single public metadata census saved in this branch includes all **437 publicly indexed Movebank Data Repository data packages** at the DSpace Datapackage collection as of 18 Oct 2026. It has **376 CC0**, **27 CC BY 4.0** and **34 CC BY-NC 4.0** packages, and **182** with an explicit GPS term in subject metadata (16 additional mention GPS only in title/excerpt, 239 lack this index signal). None of these numbers is an eligible *independent biological replicate* count. Source metadata are not a census of all Movebank tracking studies (public Data Repository only) or of all GPS location events.

A package can span different taxa/colonies/years, several packages can contain repeated samples of one taxon, and repeated animal IDs may appear across years. We will define the main **population-by-season-by-source-study** grouping (site/colony × species × year × biologically meaningful tracking season) **after inspecting source-reference metadata, before looking at individuality or overlap scores**. Individual bat/animal identifier and session are observational units nested within that grouping; sources/taxon/genus are higher-level dependence units. Consecutive fixes, sessions from one animal and dyads sharing an animal **are not independent replicates**.

All 14 initial **nonbat** pilot packages (multiple birds, terrestrial mammals, one/two reptiles) are preselected by **metadata diversity**, not tracking outcomes. The five originally studied bat packages are a **historical method calibration/boundary panel**, not the primary generality test and never part of the initial new-taxon effect search. Broader discovery must continue after pilot validation using objective coverage criteria.

## 3. Same-bat/same-animal estimands, different ecological concepts

**Primary universal comparison is 2D** (verified longitude/latitude and times) to avoid 3D source GPS vertical-datum incompatibility and to include terrestrial/marine taxa where altitude is unavailable. The following are **separate, statistically dependent functionals from the *same validated animal sets***, not independent confirmations.

### A. Identity-bearing movement within shared place (B)

For each animal i and held-out independent **tracking-day or bout block** d, derive standardized kinematic modes from GPS coordinates: time-step-aware speed/step length and turning-angle categories, allowing sensor accuracy/gap constraints. Define a comparable within-population place cell c, season/resource block s and fix-gap bin g.

\[
B = E_{\mathrm{held-out}}\!\left[
\log \widehat p_{i,-d}(m\mid c,s,g)
-\log \widehat p_{\mathrm{cohort},-d}(m\mid c,s,g)
\right]
\]

where m is an objectively defined movement mode and both densities are estimated **without the target day or any future observations**. Person-specific tuning and conditional bin thresholds are fit **only within training folds**. Uniform species-independent spatial pixel resolution is **not assumed**: source-specific pre-opened horizontal precision, within-cohort movement scale and shared-place sample support define a fixed main cell width, later subjected to a predefined coarser resolution check. Compare entire source day-blocks through an outcome-independent label-exchangeability null within shared cohort/context, preserving sessions and matching. If shared XY/context support fails, report **STRUCTURAL STOP**, not a zero score or a nonsignificant individual effect.

B measures predictive movement-mode individuality **at shared sampled places**, *not* a discovered learned personal motor policy or a neutral space-use entropy.

### B. Geographic exclusivity (P) and overlap (O_XY)

Estimate each eligible animal's **out-of-day sample-balanced 2D spatial utilization distribution** on the same source-appropriate spatial grid, within the **same availability region and biological season**. Let

\[
O_{ij}^{XY}=\sum_c\min\{\widehat p_i(c),\widehat p_j(c)\}\quad
\mathrm{and}\quad
P=1-\overline{O}_{ij}^{XY}.
\]

The overlap is defined on a calibrated **estimated probability distribution**, not the physical square kilometers jointly occupied nor instantaneous co-presence. The estimator, location-accuracy eligibility, common accessible region and per-cell smoothing must be declared before outcome opening. Use fixed matched biological animals and balanced animal-day weights; animal-block/bootstrap uncertainty keeps network/dyad dependence. Report **continuous overlap and uncertainty**, plus explicit chance/reference comparisons under source-cohort-aware nulls. A non-significant positive P contrast **does not establish equivalence**. Source P is **not a direct independently sampled prey/resource niche difference or synchronized encounter test**. An ecological equivalence claim needs a justified outcome-independent magnitude, error tolerance and sufficient biological support; none is inferred from a negative p.

### B2. Independent ecological consequence remains mandatory

A 2D utilization-overlap complement **cannot establish resource or competition-based niche partitioning on its own**. Where the source has comparable remotely sensed land-cover/resource/phenology data and a defined shared accessible region, measure **environmental/resource-exposure divergence** independently of the movement-mode predictor. Where animals have contemporaneous, independently accurate physical GPS positions, measure **same-patch/time co-use relative to opportunity-corrected block/phase-shift baselines**, with explicitly preselected fine temporal and distance thresholds. Animals lacking resource or time-synchronous support are recorded as **missing/structurally ineligible for ecological translation**, never a zero inferred ecological effect. These are the **actual independent ecological consequence endpoints**; the geographic P defined above is an intermediate that can be estimated more widely.

### C. The *nontrivial cross-taxon response*

As a broadly computable **descriptive intermediate**, ask whether **B remains positive across cohorts with high O_XY**, and how the across-population relationship \(B\sim P\) changes with independent environmental predictors. B uses movement-mode identity **conditional on location**, whereas P measures **marginal location partitioning**; they are related through observations but **not the same mathematical overlap metric**. The two require a **matched animal sample and session definitions** to avoid the original bat project's cross-estimand eligibility caveat.

Additional 3D geometry using common-datum calibrated height/dive depth is strictly **secondary**: no use of ellipsoid–MSL mixtures, source sensor types or pseudocount 3D-bin overlap as observed shared physical airspace.

## 4. Main ecological competing predictions

- **Partition-coupled individuality:** where spatial resources are predictably distributed into defendable/nonoverlapping patches, high positive B tends to co-occur with high P after accounting for available habitat and source biology. A negative/near-zero association or positive B at low P contradicts a universal need for territorial exclusion.
- **Behavior-within-overlap individuality:** different stable movement-mode strategies persist at high geographic overlap (low P) even within independently comparable place × time × resource blocks. High raw B at different actual places **does not** support this hypothesis.
- **Apparent individuality from environmental/task allocation:** B is weakened after controlling verified task, local environmental patch/time and measurement error; original metadata such as sociality, coloniality or home range descriptors cannot stand in for externally verified behavior labels.

The strongest generality claim requires a quantitative **hierarchical estimate across separately sampled taxon/source clusters** and leave-study/leave-genus predictive validation, not a gallery of selected positive case studies.

## 5. Outcome-blind preflight gates and data quality

Before looking at the outcome estimates, record all exclusion/structural outcomes for all indexed packages, not only successes:

**Source and license stage:** authenticated DOI, downloadable public GPS-event and reference metadata, verified source-specific reuse license/terms, stable animal identifier with deployments, timestamps and WGS84 latitude/longitude. CC BY requires citation; CC BY-NC outputs are stored separately until permitted study reuse and distribution decisions. A metadata GPS keyword is only an invitation to inspect—not verified GPS coordinates or eligibility. Light-level geolocator/Argos data cannot silently enter a high-precision GPS primary analysis.

**Primary example quantitative gate (fixed now for preflight software; revise only before biological outcomes, with a version bump):** at least **8 individually identified animals** in the same objectively identified population/season; at least **4 independently separated tracking days/bouts**, each with ≥**50** valid GPS fixes, over **≥7 elapsed days** per animal; **≥3 overlap dates** with at least two same-cohort animals monitored; suitable shared spatial/kinematic contexts and time-gap regularity. A dataset with 8 widely dispersed animals but no common available habitat fails common-support eligibility rather than representing partitioned animals. These numbers are screening thresholds, **not** claims that any of the 437 datasets passes.

**Leakage and dependence:** train thresholds and smoothing per source from training folds; completely held-out animal days; no adjacent same-day GPS fixes in both training and test; randomization exchanges animal-session blocks only among physically comparable cohort/season strata; bootstrap highest biological animals and source groups, not fixes or independent dyads. Record GPS precision, relocation schedules, study/colony duplicates, GPS versus Argos mix and tagged-animal reuse. Location projection UTM or geodesic methods must be calibrated per source.

## 6. Generality/meta-regression plan (not yet fitted)

For each **biologically eligible population–season** record j, estimate B_j, P_j and their source-aware covariance/uncertainty. Model a bivariate relationship with partial pooling by source study, population, genus/taxon (where species metadata are resolved) and source sampling variation; the primary cross-system coefficient on P asks whether conditional movement individuality needs exclusive geographic occupation.

Independent, predeclared explanatory covariates are **seasonal landscape-resource variability** (e.g., NDVI/EVI within the source-defined accessible region), **habitat patch heterogeneity**, source-specific GPS precision/sampling effort, migratory vs resident phase based on external source metadata, and **colonial/social organization only if independently coded by transparent sources**. Unlike the prior bat study, these ecological moderators are not reverse-engineered from significant output panels. Effects must be tested on adequately represented strata and held-out taxon/study folds; confounding of region, animal movement/body size, habitat, device and taxonomic history requires adjustment and caution.

Prespecify **minimum independent clusters** before declaring a broad model fit; a preliminary pilot of a few taxa is feasibility evidence, **not** a statistically powered phylogenetic macroanalysis. Publication-level generalized claims should require **multiple independent biological populations in at least three major clades** plus nontrivial independent taxonomic coverage, with numbers set based on observed source metadata feasibility *before* analyzing B/P outcomes. Do not assume 437 packages = 437 replicates.

## 7. Analytic decision checkpoints

1. [x] A complete DOI/license/subject metadata census exists for **all 437** publicly indexed Data Repository packages on 18 Oct 2026.
2. [x] Deterministic preliminary GPS-metadata queue with 182 keyword hits and 14 nonbat metadata-diverse pilot packages plus five bat prior benchmarks.
3. [ ] Confirm exact downloadable sensor/event/reference file structures, package versions and per-study permission; run blinded bat-ID/session-count source preflights across the full queue.
4. [ ] Lock per-taxon clade mapping, population/site/season grouping, duplicate packages/study families and independent sample denominators **before opening any B/P results**.
5. [ ] Validate GPS horizontal accuracy, temporal steps, session/bout definitions and common-place support, with tagged source DOI and recorded disqualification reasons.
6. [ ] Only then implement both source-controlled estimators, synthetic and source-label-permutation controls, within-cohort out-of-sample predictions and spatial utilization estimates **on the same animal sets**.
7. [ ] Fit bivariate hierarchical/measurement-error meta-regression with external ecological predictors, leave-study/leave-genus external validation and all negative/STOP cases; test sensitivity and publication generality.
8. [ ] Retain the original bat result as a labeled **legacy calibration/boundary**, never a newly selected positive replication; independently licensed source datasets and human credit/review are required for publication.

**Hard outcome boundary:** No nonbat animal identity/partition effect, posterior, p-value, ecology moderator or cross-clade generality is established yet. This branch is an original database-scope and test-plan *start*, not a completed macroanalysis.
