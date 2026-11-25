# Beyond movement: spatial concentration and limited predictability of foraging-related activity in bats

**Draft V1, 25 November 2026 JST — internal scientific review; not submission-ready.** Proposed standalone manuscript, not a merger of raw data or a replacement of the frozen individuality manuscript. No new empirical fit in this draft. Authors, permissions and data-availability statement to be confirmed. The central estimand is detected foraging-related marks conditional on recorded horizontal movement, not a calibrated functional niche or 3D SDM.

## Abstract

Animal tracking describes where animals move, but spatial use need not describe where particular ecological activities occur. Whether activity-specific distributions are concentrated beyond movement alone, and whether such concentration is predictively persistent, are separate questions. We reanalysed two archived bat GPS datasets with independently recorded feeding-buzz annotations, representing a marine fishing bat (Myotis vivesi; 11 individuals) and an insectivorous aerial hunter (Nyctalus noctula; 22 eligible individuals). We compared the spatial entropy of detected marks with a common temporally stratified recorded-path reference preserving the observed opportunity locations and local mark totals. At a 1-km grid resolution, concentration exceeded the mean rotation reference by 0.328 and 0.135 nats, respectively, corresponding to geometric effective-cell ratios of 0.720 and 0.874 relative to that reference. Positive contrasts persisted at 0.5, 1 and 2 km across four grid origins and two mark weightings. Yet a spatial mark-rate model trained on earlier portions of tracks did not meet the frozen robust criterion for predicting later mark allocation in either cohort. These findings distinguish descriptive activity concentration from transferable spatial prediction. They do not establish that foraging hotspots moved, that actual capture intensity was concentrated, or that species differed systematically: actual audio effort and archive correspondence remain imperfectly known. A layered movement–activity–observation framework clarifies the additional information required to translate movement into estimates of ecological function.

## 1. Introduction

Movement mediates interactions with resources and other organisms. A utilisation distribution describes the geographic distribution of recorded or underlying animal locations; it does not directly distinguish travel, prey pursuit, rest and successful resource acquisition. Behaviour-dependent habitat selection and behaviour segmentation already address important aspects of this problem (Fieberg et al., 2021, doi:10.1002/eap.2470; doi:10.1111/1365-2656.13984). Aerial niche theory likewise recognises environmental and behavioural constraints on animals' use of the airspace (doi:10.1016/j.tree.2025.08.006). We therefore do not claim that behaviour-specific space use or aerial niches are new concepts.

Two empirical questions remain distinct even when behaviour is independently annotated. First, does the spatial concentration of a recorded activity exceed the concentration expected from its temporal association with the recorded movement path? An animal may spend disproportionate time in a cell; a cluster of detected feeding buzzes there could arise without local enrichment of activity. Second, does an activity-specific spatial pattern improve prediction of where subsequent detected marks occur, conditional on the later observed path? Spatial concentration need not imply a stable map, and poor predictive performance does not by itself diagnose a moving resource patch.

Bats provide a useful comparison because synchronized GPS and acoustic annotations permit analyses of detected feeding-related events without declaring slow or tortuous flight to be feeding. Hurme et al. (2019, doi:10.1186/s40462-019-0163-7) assessed GPS segmentation against acoustic records for a fishing bat. Roeleke et al. (2020, doi:10.1111/oik.07158) investigated movement and social information in noctules in contrasting landscapes and explicitly considered spatial concentration of feeding. Our narrower candidate contribution is the comparison of entropy concentration beyond a harmonized, time-conditioned recorded-path reference and its separation from an honest temporal prediction endpoint, using the two archived cohorts. This is reanalysis, not independent validation of the original studies or a claim of first behaviour-specific mapping.

Questions:
1. Does the spatial concentration of detected buzzes exceed a fixed temporally constrained path reference in each archived cohort?
2. Does an earlier detected-mark geography predict later allocation beyond the later recorded path and stratum totals?
3. What would be needed to separate physical accessibility, movement, activity and observation in a model of functional airspace use? Question 3 is conceptual, not a tested causal mechanism.

## 2. Methods

### 2.1 Archived data and sampling units

Hurme cohort: source article doi:10.1186/s40462-019-0163-7 and data doi:10.5441/001/1.kk3bg2f4. Scheduled GPS sampling 15 s and scheduled audio 0.5 s every 5 s; annotations count manually evaluated buzzes assigned near fixes. The source V40–42 receipts show 14,328 unique archived events (698 buzzes) and 14 eligible deployments from 11 individuals (13,855 fixes, 602 positive fixes, 693 buzzes). Deployment is the analysis track, not a reconstructed original trip. The published analysis subset (12,038 fixes and 688 buzzes) is not exactly reconciled; no ad hoc roost boundary or trip reconstruction is used. Archive licence CC BY-NC 4.0; cite original data and confirm reuse terms before publication.

Roeleke cohort: source article doi:10.1111/oik.07158 and published data reference doi:10.4228/ZALF.DK.112. The authorized public GeoJSON export used in V48–52 has SHA256 a2a3a9cc02b718e729aba4342a81d0e025c4809234b8dd6b7f88fc1ecc815186, 5,627 distinct events, 27 animals/tags and two sites, of which 22 individuals satisfy the count and track gates (5,227 fixes, 1,079 positive fixes, 1,272 marks). Nominal article GPS cadence was 31 s with noncontinuous audio (1.5 s per 10 s). Export timestamps resolve only minutes, and month labels (July/August) do not reconcile with article (July) and repository description (May). Exact first-trip correspondence and within-minute sequence are not verified; original V46–50 admission failures are preserved. The V52 analysis is a new, post-diagnostic archived-cohort comparison with minutes treated only as recorded ordering keys. It is not a reconstruction of the original article sample. No pooling of species or assertion that all GPS records describe active flight.

Tracks require at least 100 valid fixes and 10 positive-mark fixes. Hurme deployments are weighted equally within individuals; individuals are weighted equally within each separate cohort. Technical points and rotations are not independent biological replicates. Distinguish scheduled audio windows from actual recording success. A zero mark is a non-detection, not confirmed absence of feeding. Buzzes are activity indicators, not successful captures or prey biomass.

### 2.2 Recorded-path reference and concentration

For a track let P_c be the proportion of recorded GPS locations in cell c; Q_c the proportion of recorded marks in that cell; and R_c = sum_k (M_k/M) (N_kc/N_k), where k indexes temporal strata, M_k is the observed stratum mark total, M is total marks, N_k is fix count and N_kc is cell fix count. R represents observed GPS opportunities reweighted by observed temporal mark totals, not counterfactual accessible habitat. Shannon entropy H(A) = -sum_c A_c log A_c with zero terms omitted. C = H(R)-H(Q) measures concentration relative to R. Concentration is different from spatial displacement or general divergence; Jensen–Shannon divergence is separately retained.

V52 harmonized reference: collapse both datasets to occupied-minute bundles without inventing an order within minutes. Preserve track boundaries; stratify by recorded hour, segment separated by gaps >3 minutes, and bundle size. Use 499 seeded cyclic bundle rotations and within-target-minute allocation (seed 41025); preserve stratum mark totals, the recorded path, and bundle support. Count-mark and binary-positive-fix weights use the same paired reference scheme; one binary positive does not mean one successful foraging event. More than 99% of count marks lie in rotatable strata in both cohorts. Grid partition uses EPSG:6933, predeclared 1 km primary and 500 m/2 km secondary scales, four half-cell origin shifts. Use the exact implemented estimator and fixed origin criteria from V42/V52, not a new test. Report equal-individual excess E = C_obs - mean(C_ref), omission sensitivity and origin robustness. Geometric effective-cell ratio is exp(-E), because the effective count is exp(H). It is a ratio to the geometric reference and not a percentage of physical habitat area, volume or prey abundance. The reference is a structured descriptive benchmark, NOT an exchangeability-calibrated randomization null; report no formal permutation p-value or confidence interval from these rotations.

Native Hurme V42 results predate V52 and provide a same-cohort check only. V52 repaired a missing-symbol implementation failure without changing the design. This chronology is reported openly; V52 is not a pristine prospective external replication.

### 2.3 Earlier-to-later conditional forecast

V53 uses the exact V52 cohorts but a distinct frozen endpoint. Within each track split ordered occupied minutes at their midpoint, discard five occupied minutes immediately before and after the split, and require at least 40 fixes and five positive fixes in each retained part. Use 1-km grid, four origins, and a fixed training rate multiplier m_c = (K_c + 5)/(E_c + 5), where K is observed training count and E is expected count from the training-only stratum-weighted GPS reference; unseen cells have multiplier 1. In later strata, conditional on their observed paths and mark totals, normalize the training multipliers across available recorded fixes and score log probability against uniform allocation. Average equal individuals; compare with 499 reference training rotations and frozen origin, weighting and omission criteria. The model conditions on the later realised path and detected total; it does not forecast path, activity totals, true capture or a species occurrence surface. Report eligible samples, overlap of test cells with training cells, both count and binary results and all failed gates.

### 2.4 Proposed integration (not a fitted model)

Let U_i(x,t) represent actual movement/use intensity and a_i(x,t) activity-event rate per unit use. A latent functional event intensity is F_i(x,t)=U_i(x,t)*a_i(x,t). If event attribution is correct and there is no localization error or false-positive mark, observation intensity is D_i(x,t)=q_i(x,t)*F_i(x,t), with q detection probability. A spatial or temporal GPS reference is not necessarily U; incomplete fix support must be modelled separately. Physical accessibility A_i, movement histories, environment and resources can enter a normalized transition model for U; resource and behavioural state can enter a. A product representation by itself does not identify mechanisms. Changing a by a positive multiplicative function and changing q inversely leaves D unchanged wherever admissible. Conditional support and independent detection information are required.

A separate source-free sensitivity result (roost branch V57) bounds latent event share for a predefined subset S, with observed share d and max(q)/min(q) <= Gamma (positive support, no false positives, correct attribution). Then F(S) is in [d/(d+Gamma*(1-d)), Gamma*d/(Gamma*d+1-d)]. Compared with a fixed reference share r, strict enrichment is robust only if observed odds(d)/odds(r)>Gamma. This is a partial-identification illustration, not a calibrated bound on these cohorts; entropy excess cannot be converted into an empirical Gamma. No evidence of true functional enrichment follows without independent observation bounds.

## 3. Results

### 3.1 Concentration recurs in two distinct archived cohorts

|Grid|M. vivesi excess (nats)|Positive individuals|N. noctula excess (nats)|Positive individuals|Passing origins, each cohort|
|---|---:|---:|---:|---:|---|
|500 m|0.30686734|10/11|0.14454241|17/22|4/4|
|1 km|0.32842527|11/11|0.13480788|19/22|4/4|
|2 km|0.27400472|11/11|0.11444867|18/22|4/4|

At 1 km observed C / reference mean / q95 were 0.90600011 / 0.57757484 / 0.65106595 for M. vivesi and 0.43570360 / 0.30089572 / 0.34973320 for N. noctula. Leave-one-individual excess ranges were [0.26823556, 0.35826078] and [0.11806420, 0.15546162]. Binary-positive excess at 500 m, 1 km and 2 km was 0.32008783, 0.33691182, 0.27356310 and 0.13628922, 0.12628558, 0.10393771 respectively, with all origins passing. At primary resolution exp(-E) was 0.720 and 0.874. These are separate cohort results, not a formal interspecific effect-size contrast. JS divergence did not show common robust support and is retained as a non-supporting endpoint.

### 3.2 Concentration is not sufficient evidence for predictive geography

|Cohort|Eligible animals|Training/test fixes|Training/test marks|Count gain nats/mark|Reference q95|Binary gain|Passing origins count/binary|
|---|---:|---:|---:|---:|---:|---:|---|
|M. vivesi|7 (9 deployments)|4961/5141|308/190|+0.01034210|0.00884366|+0.00697500|1/4; 1/4|
|N. noctula|20|2148/2121|750/371|-0.00126687|0.00563127|-0.00206869|0/4; 0/4|

M. vivesi count score positive in 5/7 individuals; binary reference q95 0.00775532. Test-fix fractions in training cells range 0.255–0.308 and 0.295–0.362, respectively, depending on origin. Neither cohort satisfies the robust V53 criterion. This is not a formal equivalence result, nor a direct test of hotspot motion, resource depletion or absence of spatial memory.

## 4. Discussion

The central result is that event-weighted space use and movement opportunities provide distinct descriptions of animal use, even after a common temporally constrained path reference. The contrast recurs in two archived species with different feeding ecologies, but does not establish universality, causal dietary differences or successful predation intensity. Original Roeleke work already predicted habitat-dependent spatial concentration; the narrower new analysis is the common concentration-versus-path estimand plus a separate forward prediction endpoint. The failure of robust predictive transfer should be interpreted with low spatial overlap and incomplete observation effort, rather than as evidence that all activity hotspots are ephemeral.

A functional distribution can be represented as the product of use and an activity rate, while observed marks additionally depend on detection and spatial assignment. The framework highlights where standard movement and occurrence distributions may be insufficient for conservation or ecosystem-function inference. In particular, a feeding attempt is not necessarily capture or energy acquisition. Stidsholt et al. (2023, doi:10.7554/eLife.84190) already distinguished attack and capture and contrasted hunting tactics; their evidence motivates independent validation with successful feeding, not a novelty claim for that distinction.

### 4.1 Cross-branch integration: contextual evidence, not pooled empirical results

Separate batter analyses demonstrate layer-specific questions and do not jointly fit the movement–activity model:
- Terrain V29/V34: four taxa, five panels, 5,868 conditional movement windows; directional gain positive in 5/5, vertical gain positive in 4/5. Known realised chord length and elapsed time; no independent calibration of 3D coordinates. Neither direction nor vertical gain estimates the event-rate field.
- Individuality PR #99: centred vertical distribution-shape correspondence in five of six panels; no supported additional smoothed segregation in four tropical panels (two species). Session-centred smoothed overlap is not measured physical shared airspace. New detected-mark cohorts do not link these same individuals to functional segregation. No reuse of the prior paper's results as new evidence.
- Resource analyses: Hendel plot-heldout acoustic activity log-score gains with moth count for MRE +0.10990 and P. pipistrellus +0.16283, and beetle richness for LRE +0.13708. Fitted resource coefficients negative in these examples; not attraction or consumption. Ducke composition +0.0261067 nats/plot, abundance-matched label comparison plus-one 0.055. Cistrone and Krauel vertical recorder-stratum additions negative; no demonstrated resource–height mechanism.
- Flight energetics: conditional wind/time/energy geometry is an independently derived theoretical scenario; the Carollia computed inequality response depends on active constraints and the power model, not field range observations. Do not infer wing-mediated functional niche partition.
- Cave assemblage AR clustering and mass dispersion are exploratory community-level patterns and not a test of individual behaviour, ecological functions or causal filtering. Exclude from main results.
- Air-volume V57 explicitly separates detection from functional support. Present as a conceptual observation limitation (or short appendix); no calibrated field estimate, no claim of 3D functional-space reconstruction.

These outcomes motivate layered constraints, but the main empirical dataset cannot estimate cross-layer causal paths. Do not combine scores across units, count panels as independent species, or interpret the additive conditional log-score decomposition as ecological feedback.

### 4.2 New hypothesis: functional segregation without movement segregation

Among individuals that share comparable movement opportunities, independently verified activity-event distributions may be more distinct than their use distributions. If so, activity-specific segregation can arise without strong movement partition. Current V52 within-individual concentration is NOT evidence of between-individual segregation. Different hotspots may be shared by all individuals. A future independent dataset must provide simultaneous/repeated animals with overlapping support, calibrated location and event detection, and a prospective pair-level contrast relative to a matched individual-specific path reference. Resource and time differences must be addressed, and repeated pair membership handled at animal/site/night level. No further outcome-adaptive changes to the V52/V53 cohorts.

### 4.3 Scope and publication boundary

Use horizontal detected marks, not 'true functional niches' as the validated response. Do not claim 3D functional SDM, successful predation, competitive release, habitat preference, causal mechanisms, stable or moving true hotspots, or taxonomic generality. The source provenance mismatch and unmeasured actual recording effort are substantial limitations, not supplementary footnotes. Prior literature on state-specific habitat selection and activity-dependent distribution is extensive; complete targeted novelty search before submission. Prefer Movement Ecology as provisional first target given the movement/behaviour and conditional prediction question; JAE only after additional independent field evidence or a clearly stronger general ecological mechanism. No submission or author contact.

## Figures and supplement plan (not yet generated)

1. Conceptual decomposition: recorded movement reference, detected mark distribution and latent activity/observation layers; clearly labelled conceptual, no invented source maps.
2. V52 count and binary concentration excess, three spatial resolutions, two cohorts. Show four-origin robustness and omission sensitivity, not rotation intervals as sampling confidence intervals.
3. V53 forward gains vs same-cohort training rotation q95, binary/count and train-cell overlap. Show both failures explicitly.
4. Optional conceptual next test: movement overlap vs function overlap, not empirical result; keep conceptual if needed, otherwise supplement.

Supplement S1 data source licenses, hashes and failed admission/repair chronology. S2 full origin/reference/individual aggregate scores, exact code and seeds. S3 observation and partial identification derivation with synthetic illustration. S4 cross-branch evidence ledger only if needed to explain motivation; frozen individuality results not republished as fresh findings.

## Reproducibility pointers

V52 contract and failed-run repair: trait-wind branch docs/FUNCTIONAL_SPACE_V52_COMMON_MINUTE_REFERENCE.md (blob 9d76aca6d6b657b198c45fda3c4ddd20cc95c65c), docs/FUNCTIONAL_SPACE_V52_IMPLEMENTATION_REPAIR.md (blob 048284c3fc7bac86ba9cafb88889d1935f8ccbb2). V52 successful run 45556390387 artifact 14995603320, SHA256 7daf965b5a4ddfd4be678e1872cca25c77c30fb1309b46df1cb5eeedfc98779b.
- [V52 results/forward contract](https://github.com/zuizui0223/batter/blob/prospective/trait-wind-roundtrip-20261124/docs/FUNCTIONAL_SPACE_V52_CLOSEOUT_V53_PREDICTION.md)
- [V53 results and V54 structural gate](https://github.com/zuizui0223/batter/blob/prospective/trait-wind-roundtrip-20261124/docs/FUNCTIONAL_SPACE_V53_CLOSEOUT_V54_3D_SUPPORT.md) (blob 8db40a20f45ec57c09dae2c4ee2b436230c9e28f); run 45559784386 artifact 14996359555 SHA256 07405a359e236952b68b5f0a765459f8a47dce02cc7c4c9915a2668e977f55c1.
- [V51 archive provenance](https://github.com/zuizui0223/batter/blob/prospective/trait-wind-roundtrip-20261124/docs/ROELEKE_V51_PROVENANCE_DIAGNOSTIC.md) (blob 797da2a9c3192ee0e660ad5e9725e73dd9af1994).
- [Cross-branch evidence](https://github.com/zuizui0223/batter/blob/prospective/roost-3d-connectivity-fd-20261124/INTEGRATED_3D_MOVEMENT_EVIDENCE_V1_20261124.md).
- [V57 bounds](https://github.com/zuizui0223/batter/blob/prospective/roost-3d-connectivity-fd-20261124/AIRSPACE_V56_CLOSEOUT_V57_FUNCTIONAL_SUPPORT_BOUND.md).
- [Earlier individual manuscript PR #99](https://github.com/zuizui0223/batter/pull/99).

## References (initial prior-art check; complete bibliography pending)

- Hurme E et al. (2019). Acoustic evaluation of behavioral states predicted from GPS tracking: a case study of a marine fishing bat. Movement Ecology 7:21. https://doi.org/10.1186/s40462-019-0163-7
- Roeleke M et al. (2020). Landscape structure influences the use of social information in an insectivorous bat. Oikos 129:912–923. https://doi.org/10.1111/oik.07158
- Fieberg J et al. (2021). Conceptual and methodological advances in habitat-selection modeling: guidelines for ecology and evolution. https://doi.org/10.1002/eap.2470
- Accounting for behaviour in fine-scale habitat selection: a case study highlighting methodological intricacies (2023). https://doi.org/10.1111/1365-2656.13984
- Animal niches in the airspace (2025). https://doi.org/10.1016/j.tree.2025.08.006
- Stidsholt L et al. (2023). Echolocating bats prefer a high risk-high gain foraging strategy to increase prey profitability. eLife 12:e84190. https://doi.org/10.7554/eLife.84190; data https://doi.org/10.17632/smx7n93syw.1.

## Release gates

V1 is an internal evidence-bounded manuscript draft, not a claim of submission readiness. Before submission: independently audit original aggregate score artifacts and source permissions; verify V52 code/metrics and support, build source-safe figures, resolve or transparently delimit archive correspondence, complete literature search, and ideally obtain an independent eligible third source with actual audio effort and aligned full paths. Preserve main, all original branches and historical negative endpoints. No raw locations or IDs redistributed.
