# Across taxa, when does individual movement identity become an ecological niche?

**Study scope:** cross-taxon original-data database study. This is a **prospective analytical design as of 19 October 2026**, not the already-completed bat paper, not a newly discovered movement law, and not a preregistered outcome-blind analysis of every source: repository metadata and a limited nine-source feasibility probe have already been examined. No source-wide individual-identity or partitioning test has yet been fitted.

## Center question

**When can a population maintain individually predictable movement/space-use strategies without correspondingly partitioning the ecological resources actually used, and how do habitat/resource dynamics and social context modify that relationship across animal lineages?**

This is **not** the simplistic claim "individuals differ" and not a bat-specific 3D flight-altitude formula. Different animals move on land, through air or water; movement dimensionality, sensor accuracy, range and activity states must be compared with domain-specific measurement rules. The primary common estimand is **predictive individuality after holding measured context constant**. Ecological realized niche partitioning is a **different secondary estimand, requiring independently measured resource or appropriate co-use evidence**.

## Falsifiable competing hypotheses

**H1: Conditional individuality beyond environment and state.** Even after matching/adjusting location, habitat, season, time-of-day, speed/movement mode and shared conditions, the *correct animal's independent past sessions* predict its future movement or habitat-choice distribution better than histories from other conspecifics at the same site and time. Null: histories exchangeable under a source- and cohort-specific animal-label assignment. A source-valid held-out conditional log-score contrast G_i > its whole-session null is the primary result, not overlap percentages.

**H2: Ecological predictability versus individual flexibility.** Two alternatives are predeclared: (a) a *habit/resource reuse* model predicts greater G in stable, predictable resource landscapes with repeated accessible patches; (b) a *flexible individual response* model predicts greater context-conditioned G across temporally fluctuating resource landscapes even when absolute route fidelity declines. These opposing slopes can be evaluated against independently compiled vegetation phenology/seasonality and weather covariates; present both and do not reframe whichever signs appear as prior-confirmed.

**H3: Persistence is not necessarily physical partitioning.** Predictive G and independently *observed* resource/diet/foraging-patch separation need not be monotonically associated. This is a **jointly measured relationship**, not inferable from two mathematically coupled overlaps computed on the same smoothed movement distribution. If no validated resource observation exists, ecological partitioning outcome is **missing**, never automatically zero. True time-synchronized proximity, resource patch or diet data form separately sampled/measured secondary analyses, not simulated sharing from generic 2D/GPS probability maps.

**H4: Sociality and collective resources modify the mapping.** Conditional individuality may coexist with a high incidence of co-used resources, for example in colony-associated or central-place foragers. Compare source-derived social group structure only where original source metadata or independent observations define group membership. Do not infer sociality from clustering of animal positions alone.

## Appropriate hierarchy and denominators

1. **Source DOI data package (437 public packages in Movebank DSpace census).** A published package is NOT a species, cohort or independent bat-like experimental replication. Keep the published 376 CC0 / 27 CC BY / 34 CC BY-NC rights strata, as verified in the frozen 18 October census.
2. **Taxon (authoritatively resolved scientific name), original study, site/colony and sampling year/season.** Merge parts and years only with verified source animal identity and data ownership, never by package DOI alone. Do not mix parent studies or tag aliases into independent species.
3. **Independent biological animals and sessions.** Primary *minimum source-candidate gate*: ≥8 unique real conspecific animal IDs in a comparable original site-season cohort; each animal needs ≥30 usable **distinct timestamps** spanning ≥3 different source UTC dates, with at least two predeclared nonoverlapping held-out sessions/days. These are initial minimum support thresholds, NOT inferential power or evidence of behavior. Verify actual original timestamps, outliers, GPS coordinate and animal/dyad definitions, repeated deployments and tag reuse.
4. **Location sensor/measurement class.** GPS/FastLoc or comparable calibrated high-precision positions are core for fine spatial/context comparisons. Argos Doppler-only, light-level geolocator and radio/low-precision telemetry get a **separate precision stratum/measurement model** and do not enter fine-grid GPS inference by default. An original dataset may contain GPS and Argos in different files; preserve file- and individual-level sensor type.
5. **Temporal/observation controls:** split data by entire individual-by-day/foraging trip or other independently defined excursion blocks; never randomly split single GPS fixes across train and test. Preserve cohort/season/time support, device precision and unequal recording schedules. A source from one animal can never contribute an individual-difference test regardless of 10^4 locations.

## Core statistical estimand

For held-out future data Y_i from individual i and independently observed context X (e.g. habitat, weather, source time, common accessible landscape):

    G_i = mean_over_heldout_blocks [ log p_hat(Y_i | X, correct own independent history)
                                   - log p_hat(Y_i | X, eligible other animal histories) ].

The original animal histories and held-out target blocks must be disjoint. Estimate one population-level, individual-balanced G per original comparable cohort with uncertainty and **whole-individual/session identity rematching permutation**, not fixed-event p-values or thousands of autocorrelated GPS points treated as replicates. Permutations reassign training identities while preserving target tracks, sampling and ecological strata; a joint permutation of *both* training and test IDs would be invalid because it preserves matches.

Separate predictions to predeclare:
- **Identity**: G positive relative to its original source-cohort exchangeability null.
- **Source-dependent physical space use**: observed GPS site use, habitat selection, path geometry, actual synchronized co-use and diet/resource intake only where independently available.
- **Decoupling**: between-cohort relationship of G with an independently estimated resource/diet partition metric, not derived overlap S from same probability object. Estimate uncertainty across original animals/cohorts; failure to reject S is *not* proof of no partition.
- **Ecological moderators**: area/resource concentration, seasonality/NDVI phenology, disturbance, social group and movement mode. Include original study/spatial collection cohort effects and taxonomic/phylogenetic dependence when taxonomy phylogeny truly resolved; treat sensor class and duration as confounders/quality strata.

## First database audit already executed (not outcomes)

The immutable [437-package source census](MOVEBANK_PUBLISHED_DATAPACKAGES_CENSUS_2026_10_18.json) contains published title, original DOI/UUID, subject fields and license per package. The reproducible [first-stage metadata selector](screen_movebank_metadata_v1.py) flags **227 metadata-priority candidates**, **25 NC-rights-review**, **50 sensor-plus-multitaxon/taxon-unresolved** and **135 sensor-file-unknown**. This is a **preflight ranking**, not 227 fully usable movement studies.

The first [nine original reference-data CSV probes](PILOT_SOURCE_REFERENCE_FEASIBILITY_V1.json) identify eight packages with ≥5 original biological IDs and one explicit exclusion (one-tag reef manta). The tapir reference originally contains 82 IDs, **eight calibration records**, so its biological-reference count is **74**. Green turtle has both GPS and Argos files and must be sensor-stratified. One Mediterranean loggerhead position file is **exclusively Argos Doppler-shift**, with 10,271 original event rows collapsing to **1,258 distinct animal-timestamp tuples** and nine source animals exceeding an initial 30-position/three-day screen; it is **not** validated high-precision GPS and should not enter the fine-grid primary set. This is documented in [the sensor/event audit](ORIGINAL_SOURCE_EVENT_PREFLIGHT_V1.json).

These actual original public data-file observations are deliberately *negative source-quality gates*, not G estimates, proof of universal behavior, or new 3D niche inference.

## Core ecological design risks to pre-register explicitly

- **Study and species-selection bias:** GPS biologging overrepresents large animals, accessible colonies, commercial licensing patterns and long-term study systems. Small insects and many fish have few fine-GPS tracking datasets. Macro inference conditions on the publicly tracked sample; it is **not** a random sample of animal diversity.
- **Different ecological availability domains:** terrestrial territorial mammals, central-place birds, migratory turtles and aquatic fishes have different accessible environments. Compare standardized **within-species/cohort** log-score advantage and cohort-level moderators; never make altitude, depth and horizontal range directly interchangeable.
- **Apparent spatial overlap from smoothing or session-centering:** no biological law from a fixed alpha=0.5 3D overlap estimator. Dynamic position uncertainty and physical habitat use need measurement checks.
- **Cohort and individual non-independence:** repeated years within one lineage/study are not new species; repeated dyads and co-located events are not independent animals. Unit for population inference is independent verified animals; unit for taxonomic generality is independently sampled species/cohorts with proper nested errors.
- **Environment/task confounding:** true commuting/feeding/resting labels are not encoded reliably by coarse speed/turn alone. Dataset narratives suggest hypotheses, not observed labels for every fix.
- **Original-data legitimacy:** CC0 and CC BY require original appropriate attribution and source-ethical scrutiny. CC BY-NC must be separately assessed for reanalysis and redistribution. Avoid publishing original animal IDs, sensitive locations or original GPS files in this source-only methodological branch without a recorded rights and governance decision.

## Frozen execution sequence

1. **Metadata:** source audit (complete 437; repeatable deterministic checks).
2. **Reference/deployment files:** source ID counts, biological-versus-calibration records, species names and deployment structure (nine pilot sources checked). Do not call reference counts accepted GPS n.
3. **Original movement tables:** verify sensor, timestamp collisions, valid position error/outliers and independently held-out source days. Mark cohorts feasible only after raw source checks. Aim for ≥3 major clades, ≥2 source studies per clade and ≥2 independently sampled cohorts per study *where actual data exist*; the exact achievable n is an **outcome of the inventory**, not invented.
4. **Identity G + nulls:** freeze final eligible cohorts and nulls before inspecting G results. Analyze without copying third-party original animal IDs into public commits.
5. **Macro model:** estimate study/taxon/moderator effects and publication/measurement biases; explicitly test source and clade holdout transfer, and test ecological resource partitioning only in genuinely independently observed resource-data subsets.
6. **Manuscript decision:** prepare a new **cross-taxon macroecology article**, retaining the bat 3D case only as an explicitly limited motivating/example system; keep existing unified bat PR #99 frozen and separately reviewable until authors decide publication overlap.

**Not yet achieved:** no cross-taxon p-values or ecological moderator coefficients; 227 metadata-priority packages are not verified bio-eligible, and no universal principle has been empirically accepted.
