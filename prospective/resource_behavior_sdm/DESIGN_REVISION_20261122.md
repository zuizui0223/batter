# Resource, behavior and vertical use: current design and evidence (2026-11-22)


**2026-11-22 original-source altitude calibration UPDATE:** Original Goldshtein source now includes directly decoded daily flowering in legacy BIFF8 and overlapping GPS XY, but **3D use remains STOP**. In four same-animal cactus source maps with genuine altitude columns, 36,082 RMC/GGA GPS fixes fall ≤15m of cactus-alt references and show median *raw GPS altitude minus source cactus-alt* **−57.23m** (bat medians −79.35 to −28.20m); earlier independent drone-alt reference gives **−86.51m**. An available EGM96 gridded shift of roughly −33m is a sensitivity check only, not the author's EGM2008 and not a verified datum conversion. The NMEA GGA geoid field is missing. We **cannot** derive source-authenticated AGL by adding a constant to this response, and *cannot* claim measured resource×AGL heldout improvement. See [new source-quality crosscheck](GOLDSHTEIN_GGA_ORIGINAL_CACTUS_ALT_EGM96_DATUM_AUDIT_20261122.md). Keep fruit Stage B as incomplete 121/327 drone-cactus daily survey and 5 bats/6 local candidate bat-nights; no new numerical biological fit.


**2026-11-22 later original-source CORRECTION — legacy flower census now parsed:** The user-uploaded Goldshtein open flowers.xls source is a genuine pinned BIFF8 workbook containing 414 source cacti. Among 327 drone cacti, 121 have 1,016 numeric date-indexed flower counts (377 positive/639 observed zero); 206 do NOT have observed daily numeric values. Separate drone reference sheet has 332 geographic altitude positions and 327/327 drone flowering points coincide within 2m. Actual original valid GPS RMC fly near independently observed bloom cacti on provisionally matched 2016 study nights: **227 XY fixes / 99 proximity episodes / five bats / six bat×morning dates**, 22 episodes near positive recorded flower counts. This supersedes the old claim that the legacy XLS could not be read and that no real space/date overlap candidate existed. **Source eligibility still not equal to qualified food×height effects:** local-day conversion/flower observation effort and altitude must be verified; a pre-frozen original GGA/drone datum audit finds raw altitude − drone sheet altitude median **−86.51m** at ≤15m and NMEA geoid separation missing. Never relabel raw GGA minus cactus altitude as AGL. Original 3D resource model scores remain NULL. [Complete source result & STOP](GOLDSHTEIN_REAL_LEGACY_BLOOM_GPS_NIGHT_SOURCE_QC_20261122.md), [replayable BIFF8 parser](goldshtein_legacy_biff_source_gate_v1.py), [source-aligned XY gate](goldshtein_drone_bloom_xy_morning_gate_v1.py), [sensor-datum gate](goldshtein_gga_drone_datum_source_gate_v1.py).


**2026-11-22 uploaded Goldshtein source OVERRIDE (newest):** The user has now supplied a 256 MB claimed Mendeley v1 ZIP, hash-pinned as 069b12e6383fa7d84a1f7164fcfe16b0ce693469a7661262ce1a0ed73e423ebb. **The previous HTTP401 is no longer an access barrier to this local upload.** Original 17 GPS-labelled animal folders, 19 NMEA files, eight cactus position tables (2,483 coordinate rows), 205,166 valid RMC observations, and 42,562/105,580 de-duplicated mapped-bat XY fixes geometrically inside mapped-cactus convex hulls are verified. This is **NOT mapped survey coverage or a fitted resource effect**. Per-cactus survey dates, official surveyed-area polygons and independently corrected GPS AGL are not verified; open flowers.xls is present but its legacy workbook schema remains unparsed. Video dates overlap GPS on nine days without validated bat/cactus/field keys. **New active source goal:** independently recover survey footprint plus altitude terrain correction; only then freeze Stage A height test. Stage B remains STOP without directly surveyed cactus×night flowers. [Source upload audit](GOLDSHTEIN_UPLOADED_ORIGINAL_SOURCE_AUDIT_20261122.md), [anonymized receipt](goldshtein_original_source_structural_receipt_20261122.json), [source-only local reader](goldshtein_original_xy_source_audit_20261122.py). No GPS height responses inspected, no new SDM fit, prior 7 strict effects still NULL.

**2026-11-22 implementation continuation:** The [fruit/flower field source-admission review](FRUIT_FLOWER_FIELD_SOURCE_ADMISSION_20261122.md), [source-free outcome-blind A/B support gate](fruit_flower_source_support_gate_v1.py), and [synthetic tests](test_fruit_flower_source_support_gate_v1.py) now separate static cactus-layout opportunity (A) from directly observed exact-night full-field flower census (strict B). This is a *potential data-support audit only*, with original Goldshtein and Panama same-event food×flight-height inputs still unqualified. Original-height scores remain unestimated. See §5 for unchanged source STOPs.

**Status:** prospective design revision and audit of committed results; **no new empirical fit**. Audited batter PR [#102](https://github.com/zuizui0223/batter/pull/102) at commit `731972c2ecce3275e1d7469346bff85f2e5ec3e3`. This document supersedes earlier current-status and broad novelty wording, while the dated source protocols, results and null outcomes remain the evidence record. The PR remains a draft.

**Current conclusion:** measured local resource indicators improve some source-local predictions of recorded acoustic activity or captured-guild composition. The two field recorded-stratum comparisons and one laboratory target-relative-height comparison have negative mean heldout increments. These different responses, predictors and evaluation units do **not** establish that resources affect horizontal use but not height. A joined field test of independently measured resource amount, behavior and individual flight height remains **not estimated**.

**One active objective:** establish whether a fruit/flower-using bat source supplies a defensible resource-survey × bat-event join. The immediate task is source admission, not another fit to the three closed negative comparisons. The two named candidates are Goldshtein cactus mapping and Panama *Phyllostomus hastatus*. Their input deficiencies are explicit in §5.

## 1. Evidence carried forward, with response and score units

| Source and comparison | Heldout result | Exact target and scope |
|---|---:|---|
| Hendel: MRE + moth count | **+0.10990** | Reduction in squared prediction error of training-standardized `log1p(acoustic activity)`; 65 whole-plot holdouts. Mean standardized training coefficient **−0.2952**. |
| Hendel: *P. pipistrellus* + moth count | **+0.16283** | Same error scale and site support; mean coefficient **−0.3722**. |
| Hendel: LRE + ground-beetle richness | **+0.13708** | Same error scale and site support; mean coefficient **−0.3370**. |
| Ducke: two fruit-composition predictors versus environmental/design baseline | **+0.028769 nats/capture within plot, plot-equal mean**; versus pooled fruit total **+0.026107** | Conditional four-guild composition among mist-net captures; plots equally weighted, seven spatial/design source blocks withheld, 46 plots and 809 included captures. Not total activity or occupancy. |
| Krauel: ground moth catch added to the recorded-height model | **−0.004404 nats/recorded pass** | Three recorder strata, ten complete nights at one site; nights equally weighted. The distinct **height + buzz joint** increment is **−0.004729**, not the height-only result. |
| Cistrone: total insect-catch contrast added to environmental baseline | **−0.015784 nats/recorded pass within plot** | Ground/canopy recorded-pass allocation, two nights pooled; 19 positive-pass plots equally weighted, 11/19 positive plot increments. The all-zero twentieth plot remains in source coverage. |
| PLOS 2016: target-aware versus target-blind conditional height model | **−0.029707 nats/frame**, 0/3 bats positive | Actual laboratory XYZ relative to the target; 24 trials and 2,671 positions nested in three paired bats. Natural cactus flower versus acrylic hemisphere, **not two food types or measured resource amounts**. |

Source reports: [Hendel](HENDEL_USER_UPLOAD_ORIGINAL_HELDOUT_RESULT_V1.md), [Ducke joint model](DUCKE_JOINT_FOUR_GUILD_V3_RESULT.md), [Ducke equal-complexity control](DUCKE_EQUAL_COMPLEXITY_V4_RESULT.md), [Krauel](KRAUEL2018_FIELD_ACOUSTIC_HEIGHT_RESOURCE_RESULT_20261121.md), [Cistrone](CISTRONE_RECORDED_STRATUM_RESOURCE_RESULT_20261121.md), [PLOS](PLOS2016_REAL_THREE_BAT_TARGET_3D_HEIGHT_TRANSFER_RESULT_20261121.md). Full precision and provenance remain in [the evidence ledger](evidence_ledger_v1.json) and source receipts. This revision checks those committed summaries; it does not independently rerun the uploaded raw data.

### Hendel: predictive gain, coefficient and robustness are different quantities

MRE and LRE mean **mid-range and long-range echolocating**, not medium- and large-bodied bats; see the [original Dryad variable definitions](https://doi.org/10.5061/dryad.xksn02vr1). *P. pipistrellus* is a separate response. The three positive prediction gains coexist with negative fitted resource coefficients in all 65 training folds. They therefore do not demonstrate positive attraction to moths/beetles or direct prey consumption.

Removing each of the 65 plots in turn and rerunning **the entire 64-plot cross-validation** leaves all three mean gains positive in **65/65 deletion variants**. This is not 65/65 favorable heldout plots: the original site-level counts are **40/65, 38/65 and 38/65**, respectively. The deletion ranges are robustness envelopes, not confidence intervals. Penalties 0.05, 0.15, 0.5 and 1.0 preserve these gain signs. The further control-set, DOY-group and elevation-group checks are post-outcome diagnostics within this study.

SRE + moth count has a negative predictive gain (**−0.01199**) despite a positive coefficient. The workbook's 65 plots versus the paper's 64 remain unresolved. Moth and bat sampling deliberately used different nights, and ground-beetle sampling had a different seasonal window. Unmeasured structure, recording and arthropod-proxy explanations remain possible.

### What the portfolio supports

Ducke and Hendel are two original studies with **different response variables** in which local resource indicators can add prediction beyond their specified baselines. They do not replicate the same horizontal-activity effect or provide commensurate effect sizes. Ducke's abundance-matched equal-complexity plant-partition diagnostic has exploratory tail rank **0.055**; dietary specificity remains weak.

The three negative vertical-related comparisons are also heterogeneous. Krauel and Cistrone concern recorded acoustic strata in field insectivore systems. PLOS concerns a **nectar-feeding species** and laboratory target geometry/cues, with real individual XYZ. The latter must not be counted as a third insectivore prey-height test. Their failure to improve these particular predictions is evidence about the frozen comparisons, not proof that resource effects on height are zero. Different denominators, observation processes and validation groups prohibit a pooled average of these gains.

The proposed insectivore contrast in the project discussion—wind/time having more predictive importance for height than resource measures—is retained as an **unconfirmed prospective hypothesis**. The existing studies do not provide a matched wind/time-versus-resource comparison or a diet × predictor interaction. Source-specific weak individual vertical structure in `Tadarida` does not generalize to all insectivores. A pattern noticed after inspecting outcomes cannot confirm Q1.

## 2. Contribution and prior-art boundary

The design's candidate contribution is:

> Test whether independently measured resource information adds transferable prediction of horizontal use, independently supported behavioral state, or height within state, beyond environmental, movement and observation conditions; locate that increment using the same eligible events and prospectively separated nights, places and individuals.

This is a research objective to be demonstrated. It is not a claim of priority or a completed ecological result. Adding a vertical axis, using the probability chain rule, state-dependent movement, or producing a 3D map is already established methodology.

| Prior work | Relevant established result | Boundary relevant here |
|---|---|---|
| [Godoy-Güinao et al. 2023](https://doi.org/10.1016/j.foreco.2022.120668) | Detection-adjusted occupancy/use across four forest strata | Each of 64 cells was assigned one stratum, not a colocated four-camera column; not a directly measured food × individual altitude test. |
| [Karpińska et al. 2024](https://doi.org/10.1002/ece3.11138) | Bird occurrence in six relative vertical × three horizontal tree sectors | The vertical sectors follow tree geometry; they are not fixed absolute-height bins. |
| [Roberts et al. 2026](https://doi.org/10.1111/1365-2656.70326), **Journal of Animal Ecology** | 106-species occurrence modeled with GEDI forest structure and species traits | Forest vertical structure is a predictor; individual bird flight height is not the response. Citing this existing study does not add its bird observation dataset to our analysis. |
| [Klappstein et al. 2026](https://doi.org/10.1111/ele.70414) | 3D integrated step selection with vertical wind and trip-phase interactions | A competitive movement/habitat baseline already exists; 3D-SSF and phase × environment are not new claims. |

The [expanded prior-art audit](PRIOR_ART_3D_FOREST_VERTICAL_AND_HMM_SSF_AUDIT_20261121.md) also covers HMM-SSF utilization distributions, seabird height overlays and LiDAR-aligned bat trajectories. This targeted audit is not an exhaustive proof that no fully matched resource/state/height study exists.

## 3. Model and evaluation contract

### Three targets, not interchangeable results

Keep regional species occurrence, conditional animal use, and recorded-event distributions separate. The existing portfolio mainly predicts recorded activity/composition or conditional movement; a calibrated regional SDM is not yet demonstrated.

For a fixed species and declared observation period, a possible normalized use decomposition is

`p_use(XY,t,i,B,Z | E,R) = p(XY,t | E,R) × w(i | XY,t,E,R) × π(B | i,XY,t,E,R) × φ(Z | B,i,XY,t,E,R)`.

`R` must retain its actual measurement level: plant location, dated resource amount, or an explicitly labeled proxy. Summing/integrating over individual, state and height recovers the horizontal-time marginal. This is a bookkeeping identity, not a causal mediation analysis. Existing source-free prototypes may fix `w(i)`; this expression does not claim that all terms have already been fitted.

Model actual recordings through effort/detection and measurement error. In particular, evaluate recorded height after integrating latent true height under an independently justified sensor/terrain error model. If behavior is uncertain or latent, integrate its uncertainty when scoring observed outcomes; do not treat an unvalidated HMM label as observed feeding. Height-derived visit/state labels cannot predict heldout height.

### Prospective comparisons after source admission

| Scientific component | Matched comparison | Admission condition |
|---|---|---|
| Horizontal use | Environmental/movement/observation baseline versus added resource information | Independently measured opportunity on the same used and available support; an explicit sampling/reference measure |
| State allocation | Same baseline versus added resource in state probabilities/transitions | Behavior independently annotated/validated, or an explicitly limited latent-state claim with uncertainty integrated |
| Height within state | Same XY/time/state/structure baseline versus added resource × height | Verified altitude datum, resource timing, sensor/terrain error and behavior support |
| Residual individuality | Shared versus individual policy after the above variables | Repeated independent bouts; separately reported seen-individual and unseen-individual prediction |

Competitive resource-free 3D movement/habitat and state models are required where the inputs support them. Hold the evaluation events, weights, response definition and reference measure constant. Archive **absolute** scores and paired increments, preprocessing and model provenance; a single favorable delta is insufficient for cross-component integration. All preprocessing and tuning belong inside training folds. Compare equal-complexity alternatives and source/space/time-preserving resource controls where scientifically exchangeable.

Use whole-bat, whole-night and spatial/site holdouts as separate transfer targets, with declared group weighting. Random GPS-fix splits cannot substitute for these targets. A new source/study is required for an external-source claim. The insectivore versus fruit/flower hypothesis requires adequate replication within diet categories; a between-study difference alone cannot identify a diet mechanism.

For Q1, resource and wind/time contributions must be compared prospectively on the **same** source and outcomes with declared ablations and shared support. A weak or negative resource increment without the corresponding wind/time comparison cannot rank their ecological importance.

All seven existing `strict_unestimated` ledger values remain `null`, including the joint individual-resource-behavior link, sensor-calibrated altitude policy, higher-dimensional field gain and external resource-SDM confirmation. Synthetic known-truth tests validate mathematics and numerical behavior only.

## 4. Repository responsibilities

**Working architecture decision for this design:** retain this research program's evidence and experiments in batter; implement a qualified future process model in esdm; export comparable prediction/evaluation records to ODSP. No repository migration or model implementation is performed by this documentation revision.

| Repository | Responsibility | Concrete boundary |
|---|---|---|
| **batter**, existing PR #102 | Bat source admission, original-data adapters, exploratory comparisons, frozen source protocols, empirical evidence and claim limits | Current authoritative research record and development workspace |
| **esdm** | Process → latent ecological state → observation model; training and predictive distributions | Intended model home after input and design qualification, not an assertion that main already contains this bat model |
| **ODSP** | Common ecological-state targets, proper scoring, information increments and transfer/claim evaluation; existing reference learners remain available | Consume forecasts on identical heldout support; do not reinterpret acoustic squared-error gains as nats |

This allocation follows the inspected [esdm README](https://github.com/zuizui0223/esdm/blob/5affa0658123a2702d93e803860ce5c1c435ce7c/README.md), [ODSP README](https://github.com/zuizui0223/odsp/blob/13b884f5cfb94beef36e8e5c5b031559e81b8b4b/README.md), and [existing integration capability matrix](https://github.com/zuizui0223/esdm/blob/5affa0658123a2702d93e803860ce5c1c435ce7c/docs/integration/ODSP_INFORMATION_AXIS_CAPABILITY.md). The matrix requires absolute scores, identical heldout rows, a common proper scoring rule/reference measure and strict model nesting for a new information axis. It does not license importing unmatched source coefficients into one joint model.

**Unlocated original comment:** no matching esdm-versus-ODSP comment was found in the inspected PR threads, repository-scoped issue search or accessible named-document searches. This design records a concrete working decision; it does not claim that an unidentified external comment has been answered or resolved. Protected main and manuscript branches are outside this revision.

## 5. Next source admission: fruit/flower systems

| Candidate | What is already supported | What must be verified before a new fit |
|---|---|---|
| **Goldshtein Stage A** — [source/grain audit](GOLDSHTEIN_OBSERVATION_GRAIN_AND_ACCESS_AUDIT_V2.md) | Published mapping of about **3,600 cactus positions** in foraging fields of **eight** GPS bats, among 17 tracked bats overall | Original archive/file inventory; altitude column/datum; independent plant coordinates and survey coverage; GPS-to-field join; temporal sampling and observation-error support. Stage A is static plant opportunity, not same-night nectar. |
| **Goldshtein Stage B** | Separately observed flower counts on **414 cacti in three fields** | Observed, dated plant/field-level counts must actually match GPS nights and survey coverage. The authors' simulation draws from a flower-count distribution cannot fill this gap. |
| **Panama *Phyllostomus hastatus*** — Isla Colón/Bocas del Toro, 2016 and 2021–2023 | Existing project registry identifies this 3D tracking program; [Calderón-Capote et al. 2024](https://doi.org/10.1098/rsbl.2024.0424). Raw GPS referenced by Movebank [1.282](https://doi.org/10.5441/001/1.282), [1.321](https://doi.org/10.5441/001/1.321), [1.322](https://doi.org/10.5441/001/1.322) | A quantitative dated flower/fruit survey on used **and available** areas; plant/event keys, coverage and behavior/sampling validation. Current public descriptions do not establish that table. |

The latest authenticated Goldshtein archive access receipt is the **2026-11-21 HTTP401**, not a successful source read or a new 2026-11-22 access attempt. Manual acquisition would still require the structural and semantic admission gates. The existing [archive structural gate](goldshtein_user_archive_structural_gate_v1.py) is ready; header hints alone cannot establish a join. Published cactus visits use altitude <20 m and cannot be reused as height-independent states or selection labels.

For Panama, the [official Dryad record](https://doi.org/10.5061/dryad.5qfttdzgj), checked 2026-11-22, lists `README.md` and `stan.zip`, and points raw GPS to Movebank. Its HMM workflow description is not independently validated feeding labels or evidence of a dated food table. The original article explicitly identifies limited resource-availability knowledge. **The source's existence does not make a resource-height fit ready.** A GPS-only seasonal contrast would answer a different question. This Panama candidate is separate from the sparse Panama BIEN botanical-validation cells in esdm.

Source admission proceeds in this order:

1. Authenticate original file/version, inspect schema and resource-survey coverage, and record missing fields before outcomes are fitted.
2. Establish resource level (static position versus measured dated quantity), exact event/field/date joins, altitude datum/error and independent behavioral evidence. Retain all exclusions and support failures.
3. Only if the relevant conditions pass, freeze one matched baseline/resource comparison, holdout roster, weights and controls before opening its new scores. Otherwise retain a source-specific STOP or the explicitly narrower Stage A estimand.

**Closed comparisons:** PLOS, Krauel and Cistrone remain closed after their declared analyses. Reopening their outcomes to seek a positive model is not this next task. Hendel's existing sensitivity analyses are already recorded; this design revision adds none.

**Later:** a qualified implementation/export in esdm/ODSP; stronger resource surveys or independently calibrated field data; broader external transfer. BIEN botanical-source independence and sparse-cell validation remain a separate program, not a substitute for local resource × GPS measurements.
