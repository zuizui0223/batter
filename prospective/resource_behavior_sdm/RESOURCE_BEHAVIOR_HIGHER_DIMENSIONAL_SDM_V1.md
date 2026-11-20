# Resource × behavior × vertical space: evidence migration and higher-dimensional SDM v1

**2026-11-20 | prospective research only | parent sources: [esdm PR #244](https://github.com/zuizui0223/esdm/pull/244), [esdm PR #266](https://github.com/zuizui0223/esdm/pull/266), [esdm PR #268](https://github.com/zuizui0223/esdm/pull/268), [batter PR #99](https://github.com/zuizui0223/batter/pull/99), [boids evidence](https://github.com/zuizui0223/boids/blob/main/docs/EVIDENCE_AND_PREDICTION.md).**

**Purpose:** migrate *claims and provenance*, not raw original records, from resource-linked bat SDM work into `batter` and connect them to the independently measured individual vertical-use findings. No inherited frozen JAE/BE article, `esdm` main branch, GPS, GBIF rows, animal IDs, raster or published source material is changed. This draft does **not** assert that adding resources improves the bat SDM.

## 1. Evidence ledger — keep the observation and biological estimands separate

| Source / status | Result that may be carried forward | Bound on inference |
|---|---|---|
| NeoBat original bat–plant literature; source-authenticated, exploratory | 2,571 interactions, 1,931 fruit, 26 candidate primary frugivorous bats, 709 distinct bat–fruit-plant links. With heldout source countries, the documented link-recurrence rate was **46.94%**, vs **40.55%** degree-preserving rewiring (**+6.39 percentage points**, Monte Carlo `p=0.001`); 6/12 countries met the source-only gate. [Parent ledger](https://github.com/zuizui0223/esdm/blob/design/neobat-trophic-sdm-phase1-20261119/docs/replication/NEOBAT_RESOURCE_SDM_STATUS_LEDGER_20261119.md) | **Positive source-network recurrence**, not independently measured fruit supply, functional feeding or SDM predictive gain; source-study nonindependence possible. |
| Source-verified GBIF resource preparation | **85,912** bat records, **367,988** plant records; provenance-backed original downloads. Of 754 initial bat–country pairs, **84** passed original precision- and partner-input gates. **82/84** had at least one documented partner in the same 25-km *recording* cell. | Recorded co-occurrence is not plant abundance, fruiting, use, or a true absence; most records lack coordinate-uncertainty estimates. |
| Botanical recording rank, exploratory [PR #259](https://github.com/zuizui0223/esdm/pull/259) | Of 1,802 preregistered plant×country opportunities, **647** had evaluable rank AUC. Extra abiotic ranking beyond other-plant recording-intensity proxy was **+0.02539 country-equal AUC** (descriptive country-resample interval +0.01534–+0.03733). | **Positive botanical *recording* transfer**, not independently measured presence or fruit resources; source intensity strongly confounded. |
| Original-record source embargo and raster checks [PR #260](https://github.com/zuizui0223/esdm/pull/260), [PR #268](https://github.com/zuizui0223/esdm/pull/268) | Only **35/106** candidate plants had globally trainable datasetKey-disjoint sources across 17 countries. **592/595** fixed plant×country source+raster training inputs passed. Complete 35-plant + bat source + link/N1 intersection: **36/84** original bat×country folds, **11 bat species, 10 countries**. | A **positive feasibility result**, not 35 calibrated ecological plant maps or evaluated M3 models. Data-source disjointness does not ensure observer independence. |
| 106-plant climate-only *shadow* bat source-rank [PR #266](https://github.com/zuizui0223/esdm/pull/266) | **49/51** available folds fitted (original denominator 84 retained). Mean S3–S1 = **−0.00569 AUC**; S3–rewired SN1 = **−0.00800 AUC**. | **No consistent positive gain from published plant identity in this weak proxy.** Not the original fully controlled M3–M1 or M3–N1 ecological test; absence of a true resource effect is not shown. |
| Bat wild vertical/3D identity [batter PR #99](https://github.com/zuizui0223/batter/pull/99) | Full centered-height distribution criterion **5 comparative panels**; tropical terrain-relative vertical fidelity **4/4** panels across **2 species**; positive excess vertical spatial segregation **0/4** source-supported. A separate within-source 8-bat individual-map test gave permutation `p=0.000174`. | Positive **source-specific individual vertical-use predictability**. The 3-D overlap estimator is smoothed and cell-conditioned; no measured physical exclusion, foraging task, food exploitation, causal mechanism or universal bat policy. |
| Behavioral transition [boids evidence](https://github.com/zuizui0223/boids/blob/main/docs/EVIDENCE_AND_PREDICTION.md) | Archived `Tadarida` next-climb-class M1–M0 **+0.01383 nats/transition** in the source extraction; held-out tests of added wind and bat-history did not show robust gains. | Observed conditional prediction can arise under synthetic correlated altitude errors. Not proof of momentum, learned memory, a resource response or a transferable Boids law. |
| Boids driver ablation [v11](https://github.com/zuizui0223/boids/blob/main/docs/RESOURCE_AND_SOCIAL_DRIVER_ABLATION_V11.md) | In known-truth simulation, resource-target differences generated spatial/vertical discrimination **even with social force off**; individual targets and behavioral mixtures could generate vertical identity. | Only a **mathematical sufficiency/counterexample**; resource/identity targets were assigned by the simulator, not independently identified in bats. |

**Additional behavioral boundaries:** `batter`'s H1 original-cue programmes contain specific, often within-site, sensory/social behavioral responses, but neither social-information reliance nor private memory has been jointly fitted with a tagged animal's resource use and vertical space. A 1,342-bat trait database yielded only 45 nonimputed social-group sizes with taxon/diet aliasing ([PR #101](https://github.com/zuizui0223/batter/pull/101)). Do not substitute roost group size for information use or infer a universal memory–social-information tradeoff.

**Crucial incompatibility:** the NeoBat primary fruit-guild species and the published `batter` wild vertical panels are **not an individual- and locality-matched sample**. `Phyllostomus hastatus` is an omnivorous *secondary* taxonomic bridge, not an already successful matched trophic mechanism. The 25-km source grid, 500-m behavior cells, climate climatologies and field tracking times are also different scales. The present results cannot be multiplied as empirical likelihood factors to yield a validated 4-D map.

## 2. Ecological question and predicted separation of dimensions

**Primary question:** Under what conditions does independently observed resource opportunity increase the *transferable prediction* of animal **location, timing, behavior and vertical use**—and when does it change only one dimension while leaving others unchanged?

This resolves the conceptual problem that a species can have:
1. Stable distribution at country/horizontal scale;
2. Different resource-dependent *within-site* timing and behavioral states;
3. Repeatable individual vertical distributions;
4. Extensive 3-D overlap with other individuals.

These can co-occur; none entails active 3-D partitioning. In particular, a 2-D model could show `ΔAUC ≈ 0` even when an appropriately validated conditional `p(z,b,t | x,resource)` carries predictive information.

**Behavior-mixture mediation test:** compare `I(individual; z | XY,time)` with `I(individual; z | XY,time, independently observed behavior)`. The first can be positive and the second exactly zero in a known-truth world where individuals only differ in **how frequently** they forage/commute, not in how they fly vertically *within* each state. Positive residual after proper state conditioning would instead motivate a within-state policy, subject to independent estimation and detector calibration. Neither direction is yet measured in the current `batter` wild panel. Do not infer state from the same height response being tested. **That outcome is a falsifiable prediction, not an observed explanation for the current shadow failure.**

### Probability contract

Keep **three scientific targets** separate:

- **Regional species occurrence/availability:** `P(occupied_s(x,t) | abiotic, resource, access, effort design)`; this requires independent presence/absence or defensible presence-only assumptions and is **not** estimated by the prototype.
- **Conditional use of spacetime/behavior/height:** `p_use,s(x,t,i,b,z) = p_s(x,t | A,G,R) · w_s(i) · π_s,i(b | x,t,R,M,C) · φ_s,i(z | b,x,t,R,A)`; here `A` is abiotic environment, `G` generic plant opportunity, `R` documented-partner opportunity, `M` independent memory/protocol covariates, and `C` independently measured cues. Each component must normalize over its own conditional support.
- **Observed event distribution:** `p_obs(event) ∝ p_use(event) · q(cell,time,state,height,effort)`. `q` is an independently identified detection/recording model. Missing records are **not** inferred absences.

The prototype initially fixes `w_s(i)` independent of place and time; it does **not** fit individual habitat preferences, variable participation, source availability, local abundance, species occupancy, behavioral transition parameters, or feedback from depletion. Those are explicit future modules, not secretly estimated values.

The mandatory mathematical check is that integrating a joint use map over `i, b, z` recovers exactly the model's `p_s(x,t)`. Integrating additionally over time recovers the horizontal use projection. Therefore a vertical behavioral pattern cannot create a spurious horizontal range expansion merely from extra state labels.

### Nested falsification ladder (separately scored)

| Comparison | Estimand | Required observation |
|---|---|---|
| **R0 vs R1** (M0 vs M1) | Out-of-region increment of **generic** plant record/suitability beyond abiotic and effort | Independent plant predictor provenance and matched bat fold |
| **R1 vs R3 vs RN1** (M1 vs M3 vs N1) | Increment of **actual linked partners** beyond generic plants and degree-preserving source rewiring | Same 84-fold accounting; qualified subset; independent fruit-availability proxies; source embargo |
| **B0 vs B1** | Added height conditional on XY and time | Repeated terrain-calibrated 3-D observations; held-out sessions |
| **B1 vs B2** | Increment of **verified behavioral state and time**, not latent post-hoc labels | Externally validated forage/commute/rest labels with matched effort |
| **B2 vs B3** | Increment of **resource-conditioned behavioral/vertical policy** at the same site | Time-aligned fruit surveys/independent resources AND 3-D tracking of the **same species/study** |
| **B3 vs B4** | Residual individual policy after task, availability, habitat and recording are controlled | Repeat individual sessions across contexts, disjoint validation bouts |
| **O** | Increment attributable to detector/GBIF source reporting rather than ecology | Independent effort/paired detection calibration, or STOP |

Evaluate **both** horizontal `Δ log-score/AUC` (only if valid heldout species-label support) and conditional `Δ log-score, calibration` for `(z,b,t)`. Compare R3 against a source-rewired RN1 on the **same** test events and weights; do not report R3 > R1 as partner-specific if RN1 predicts equally well. A higher raw 5-D apparent fit is **not** success without equal-denominator out-of-sample comparison.

## 3. Executable starter, not an empirical validation

`resource_behavior_sdm.py` provides:

- strict `habitat_log_scores(abiotic, generic_plant, linked_plant, beta_*)` — **externally assigned** predictor weights only, no parameter estimation;
- `resource_conditioned_state_policies` — a prespecified, resource-index-dependent softmax for behavioral state allocation, allowing resource changes to alter *conditional height use* while holding total horizontal use fixed; known-truth only;
- strict `joint_use_distribution` for horizontal × time × individual × behavioral state × height;
- marginal projection plus `I(individual;z | cell,time)` **and** `I(individual;z | cell,time,behavior)` mediation diagnostics;
- separate detector-conditioned recorded-event distribution `p_obs`;
- heldout event log-score that does **not** create probability mass for unseen support.

`test_resource_behavior_sdm.py` supplies synthetic unit tests showing that a positive individual vertical-information value can coexist with **identical horizontal use** by individuals, that resource-weight ablations change logits by construction, and that unequal detection changes recorded rates without changing true-use probabilities. These demonstrate **logical possibility and numerical bookkeeping only**, not fitted bat mechanisms or empirical gains.

### Worked known-truth counterexample (simulation mathematics only)

In the exact source-free behavioral-mixture fixture, two equally weighted individuals have **identical horizontal use** and share **both** height bins. They differ only in the proportion of two objectively assigned behaviors: one forages 80% and the other 20%; the *within-behavior* height probabilities are identical for both. The generated marginal (p(high)) is 0.68 versus 0.32. This yields `I(individual;z | XY,time) = 0.06627772` nats but `I(individual;z | XY,time,behavior) = 0`. Thus individual height fingerprints need **not** imply within-state flight differences, competition, or exclusive 3-D space use.

In a separate single-location, two-time resource-policy fixture, an **assigned** resource score change from 0 to 1 with `beta_forage=2` changes `p(forage)` from 0.5000 to 0.880797 and `p(high | time)` from **0.5000 to 0.804638** while keeping the entire horizontal projection at exactly one cell. These are probabilities computed from chosen toy coefficients, **not estimates or replications of wild bats**. This makes the paper's prospective question measurable: resource information might improve *conditional* movement-state/height prediction even if the 2-D distribution metric cannot change.

No raw source coordinates, personally identifying bat labels, copyrighted supplements, fine-resolution spatial arrays or field resource measurements are committed. This is a computational interface to which independently authenticated/fitted predictors can later be attached.

## 4. Immediate empirical gate and STOP conditions

**Next single empirical goal:** produce one audited, matched-bat-fold, out-of-source botanical predictor table for the existing **36/84** strict source/raster prefit folds, keeping the original **84** original eligible fold roster and each STOP. External field abundance/phenology, vegetation and observation effort must be distinguished from GBIF reporting intensity. A 25-km plant map from literature-linked source observations is *not* spatially coobserved fruit use, and a 500-m vertical map must not be declared resource-conditioned without a measured scale bridge.

Then run R1/R3/RN1 heldout on fixed source/time support **before** fitting B2–B4. Any prediction for vertical movement based on unmeasured fruit at the relevant cell/time remains `UNTESTABLE`. No retrofitting the frozen JAE or the unrelated 2019/2020 bat experiment to the plant-guild source.

**Mandatory STOPs:** unmatched taxon or geography; absent local resource/fruit observations; missing effort/detection denominator; source overlap across training/heldout; new outcome-based partner selection; target-group intensity used as true availability; ambiguous height datum; non-independent repeated tracking fixes treated as iid; behavioral state inferred from the same height endpoint; changes in grid/time granularity after opening heldout outcomes.

**No claimed biological result:** no full M3–M1/N1 ecological fit, no out-of-region bat resource transfer, no universal individual movement rule, no Boids/social force inference, no causal individual niche separation, no validated resource-coupled 3-D/4-D SDM. Frozen original manuscripts and results remain intact.
