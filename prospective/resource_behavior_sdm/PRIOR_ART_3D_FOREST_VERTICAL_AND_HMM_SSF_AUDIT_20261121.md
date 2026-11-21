# Verified 3D and forest-stratum prior art: novelty boundaries (2026-11-21)

**Status: SOURCE-BASED LITERATURE AUDIT, NOT ORIGINAL ANIMAL DATA / NOT A FITTED 5D MODEL.** This is a negative/limiting result for broad novelty language and a positive, narrower research target. The search is not a systematic review or proof of absence of other papers. Protected batter main, frozen JAE/BE, and esdm main are unchanged.

## New hard near-prior examples

| Study and inspectable source | What was actually modeled | What cannot be claimed new | What was NOT shown in the inspected source |
|---|---|---|---|
| **Schneider et al. (2026)**, Marine Ornithology 54:215–240, DOI https://doi.org/10.5038/2074-1235.54.1.1695; preceding **Wallach et al. (2025)** official California Energy Commission report https://tethys.pnnl.gov/sites/default/files/publications/Wallach-et-al-2025-CEC-500-2025-037.pdf | Integrates 2-D at-sea density for **44 seabird taxa**, flight-group probability of flying **above 10 m ASL** as a function of wind speed (mixed-effects logistic), and spatially/time-resolved windscape into spatially explicit density above/below threshold. Official 2025 report confirms 2D density cross-validation; this is a height-threshold overlay, **not necessarily continuous p(z)** | **2D density multiplied by conditionally predicted vertical-use probability**; 3-D spatial maps and a flight/meteorological environmental layer | No directly sampled *local prey* + bat state/individual repeated within-study GPS AGL fit in described framework; no stated source-matched continuous individual conditional height heldout gain |
| **Godoy-Güinao et al. (2023)**, Forest Ecology and Management 529:120668, DOI https://doi.org/10.1016/j.foreco.2022.120668 | Forest-floor, understory, lower- and upper-canopy **four observation strata (0–32 m)**, **16 cameras per stratum** (64 total); 24 vertebrate taxa detected including 17 bird species; detection-adjusted occupancy models for seven taxa | 3-D terrestrial forest occupancy/vertical stratification and **imperfect detection adjustment** | No same-bat-night measured food and GPS height; no individual repeated resource-conditioned altitude policy |
| **Karpińska et al. (2024)**, Ecology and Evolution 14:e11138, DOI https://doi.org/10.1002/ece3.11138 | Six *relative tree sectors by height* × three positions relative to trunk = **18 sectors**. Forest bird species presence/absence per sector analyzed by binomial GLMM for ten common species; six plots and 24 pooled tetrads | Terrestrial forest bird **height-sector-specific probability of occurrence** | Tree-relative categories rather than continuous absolute AGL; no regional SDM or measured food × GPS height joint holdout; observation visibility may vary by forest stratum |
| **Re et al. (2025)**, Diversity 17:16, DOI https://doi.org/10.3390/d17010016 (online 2024-12-27) | Urban Brisbane bird activity **observed height bins as response**, with LiDAR building/vegetation height, cover, feeding-level trait subsets in **cumulative link mixed models** | Directly predicting terrestrial **bird height use from structural predictors**, including trait-specific height association | No validated regional horizontal SDM projection or food/behavior/individual vertical joint model described; no evidenced independent whole-individual holdout |
| **Coddington et al. (2023)**, Ecosphere 14:e4720, DOI https://doi.org/10.1002/ecs2.4720 | Eighteen Amazonian mixed bird flocks followed in XY across five forest types; 3D LiDAR foliage density stratified at 0–5, 6–15, 16–25, >26 m; **separate later foraging-height measures** of obligate flock-followers from three flocks | Forest-stratum structural predictors, actual foraging-height characterization and behavioral horizontal-use analyses already exist | Vertical observations were made in later years, not a guaranteed same-event 3D moving-resource joint sample |
| **Roberts et al. (2026)**, Journal of Animal Ecology, DOI https://doi.org/10.1111/1365-2656.70326 | Broad-scale **106-species horizontal bird occurrence** models with GEDI vertical foliage-height diversity and traits; foraging traits associated with structural response. Bird observations derive from a dataset not adopted by this project. | Large-area forest-bird SDM with vertical forest *structure as a predictor* and links to foraging traits | Bird **height** is not the response; vertical structure metrics are 2-D grid covariates. Do not represent this as an observed 3D animal-use density |
| **Klappstein, Thomas & Michelot (2023)**, Movement Ecology 11:30, DOI https://doi.org/10.1186/s40462-023-00392-3 | Joint HMM + state-dependent SSF with transition covariates, individual drivers and habitat selection. **Explicit simulated utilisation distributions**: zebra example simulated **five tracks of 100,000 fixes** using learned transition/SSF parameters. Describes food as a potential predictor of **state transition OR within-state choice** | A state-based resource-dependent movement model, state uncertainty integration, **and mapping space-use distributions** are already established. Earlier phrase "HMM-SSF does not produce a distribution" is **incorrect** | Illustrative model is horizontal (2D); no measured repeated-bat food × continuous vertical AGL model, or proof of general ecological partner gain |

## Critical corrections to the former novelty story

1. **Do not claim original p(x) × p(z|x)**. It is a conditional factorization and already implemented at height-threshold level in the 3D seabird work.
2. **Do not claim first terrestrial/forest vertical animal SDM**, nor that forest bird studies predict only 2D occupancy. Chilean four-stratum occupancy and Polish 18-sector bird GLMM directly model vertical strata. Urban birds predict height bins. One can say **no matched full integrated test established among THIS inspected subset**, not that no research worldwide exists.
3. **Do not claim HMM-SSF never produces a distribution map**. The 2023 paper computes simulated utilisation distributions and explicitly discusses food controlling state transitions versus choice. Any state model added here is an extension/use of prior mathematical infrastructure, not invention of state-dependent selection.
4. **Do not treat LiDAR foliage-height diversity as the same response as measured animal AGL**. Roberts 2026 and Coddington 2023 are structural-predictor studies, distinct from direct vertical occurrence/height models.
5. **Do not claim integrating published pieces equals a demonstrated novel ecological mechanism**. A five-factor probability decomposition is bookkeeping. Added empirical prediction must be estimated with original joined field events and matched denominators.

## Researchable novelty, only if original sources permit

Question: **Does directly observed resource opportunity alter (a) the occupancy/use of horizontal cells, (b) state switching, and/or (c) the conditional vertical-use distribution *within* state? Do these effects transfer to nights, sites and individuals not in model fitting, beyond horizontal habitat and recording/detection?**

Maintain explicit targets:
- **Occurrence versus use:** Regional species occurrence is not equal to utilization density or acoustic activity. A partition of an arbitrary p_use(x,t) is not a calibrated species SDM.
- **Normalized conditional use**: p_use(x,t,i,b,z|E,R) = p_use(x,t|E,R) × w(i|x,t,E,R) × pi(b|i,x,t,E,R) × phi(z|b,i,x,t,E,R). Summing i,b,z returns p_use(x,t|E,R) when all terms normalize. This **chain-rule identity is not a novelty claim**.
- **Detector model**: p_obs proportional to p_use × q(effort,detector,behavior,location,height). Detection corrections already exist in forest-stratum occupancy; their use is not new, but can be *essential* to a valid joint comparison.
- **Scientific B0/B1/B2/B3 ladder**: shared heldout original events: XY/time/terrain/XY-only motion -> independently supported habitat/structure -> independent resource -> state-specific height -> residual individual differences (as data permit). Avoid post-hoc height-defined foraging states; use state uncertainty from models that never train on heldout height outcomes.
- **Cold-start individual versus seen individual** must be different estimands; unseen animal random effects integrated over training posterior, never smuggled in via test labels. Whole-night/site/bat holdouts are mandatory to claim transfer; no GPS fix-level p-values.
- **Claim the new principle only after gain**: empirical predictor gain and its location (horizontal vs state mixture vs within-state height); not simply "3-D map" or "factor multiplication".

## Existing project evidence and non-claims

- Brazil Ducke: captured bat guild composition improved by independent plant-category composition in whole-block evaluation (+0.028769 nats in original source), but plant subset identity not a validated consumed/non-consumed causal control.
- Germany Hendel: user-uploaded original, within-study whole-site holdout positive for **specific** prey-proxy/acoustic-activity channels; response and scores distinct from Ducke. Some positive predictive resource signals had **negative conditional ridge coefficients**. Does not show consumption or positive attraction.
- Wild bat panel: repeatable centered-height shape / individual vertical-use identity established in sources without local resource mapping; no assumption that identity equals partitioning.
- Goldshtein original 2020: ~3,600 mapped cactus locations for eight GPS bats versus separate **414 repeated monitored open-flower cacti** in three fields; official Mendeley API source receipt HTTP 401. Same-night resource×height event join NOT VERIFIED. Source-defined cactus visits use height <20m, a prohibited response-derived covariate.
- **Original joint field gain conditional on food + behavior + bat AGL**: **NOT ESTIMATED**. **Regional ecological M3–M1/N1**: **NOT ESTIMATED**. Keep PR DRAFT and exclude methods or results claims of completed 5D SDM.

## Access provenance / limitations

- Schneider 2026: verified journal landing page and abstract (online 2026-05-07). The large full-journal PDF (approx. 25 MB) was not accessible through the browsing PDF reader; technical components verified against the detailed **2025 public project report**. Do not claim to have checked every equation of the final 2026 paper.
- Karpińska 2024, Klappstein 2023, Coddington 2023 and Re 2025: full HTML methods inspected. The Karpińska PDF page containing binomial GLMM details was also visually verified.
- Godoy-Güinao 2023: publisher full abstract and methods excerpt, plus bibliographic record inspected; the full original PDF text was not necessary for the conservative stratum-occupancy claim.
- The search was targeted to directly relevant marine flight height × XY, terrestrial forest/urban vertical height/occupancy, and HMM-SSF behaviour/space use; it is **not exhaustive** or a field-wide novelty certification. In particular, the lack of a found integrated model does not prove none exists.


---

## Stronger newly verified numerical and bat-specific prior art (added 2026-11-21)

**Klappstein et al. (2026), Ecology Letters 29:e70414, 3D-SSF.**
DOI https://doi.org/10.1111/ele.70414; full publisher HTML https://onlinelibrary.wiley.com/doi/full/10.1111/ele.70414
- First published **2026-07-01**; 3-D correlated random walks, integrated step-selection function, movement constraints, individual step availability and vertically stratified **wind** in real Antarctic petrel telemetry. Models 3-D flight movement and habitat selection jointly, rather than just thresholding a 2-D presence surface.
- The paper itself proposes future **3-D HMM-SSFs**, individual random effects and measurement error models as extensions; it does not establish those combined components empirically. The underlying model assumes regular tracking intervals and sufficiently precise 3-D measurements; vertical error can be a major issue in bat data.
- Authors publish a functional but under-development **R package ssf3D** at https://github.com/NJKlappstein/ssf3D with processing, fitting and correlated random walk simulation vignettes; Zenodo data/code https://doi.org/10.5281/zenodo.17553938. Repo README still cites 2025 preprint although the peer-reviewed article is 2026. This is **direct numerical prior art**. No new "first 3-D SSF" or "first joint 3-D movement + environmental selection" claim can be made here.

**Hermans et al. (2023), Movement Ecology 11:25, direct bat 3D x LiDAR.**
DOI https://doi.org/10.1186/s40462-023-00387-0
- Aligned mic-array-localized **3-D bat trajectories** to LiDAR vegetation point clouds. Acoustic source foraging guilds; 138 array-nights, average 6,822 localized 3-D positions per array night. Quantified stereotyped pipistrelle flight around trunks (multiple nights), and vegetation/light-post distance.
- Critically, mic-array tracking **did not determine whether the same bat returned across nights**, so individual-specific repeatability and individual cold-start transfer cannot be inferred. No independent same-night true food availability or bat-species distribution SDM. But **the empirical 3-D bat flight × fine vegetation structure join is established prior art**.

**Erasmy et al. (2021), Ecology and Evolution 11:17273–17288, bats at vertical strata.**
DOI https://doi.org/10.1002/ece3.8363
- Forest interior/gaps and **three acoustic recorder heights** over reproductive seasons; species/guild- and habitat-conditional vertical bat acoustic activity. NOT novel to assess forest bat vertical activity as a function of vegetation context and season. As height is sensor stratum and acoustics are detected passes, these are not individual repeated GPS use probability without an observation model.

**Lennox et al. (2025), Ethology 131:e13529, review**, DOI https://doi.org/10.1111/eth.13529: surveys already extant 3D UDs, 3D movement and habitat-selection methods. This is contextual methods prior art, not an empirical 5-D result.

### Revised short claim gate: methodological originality is NOT available merely from adding z

- **No originality:** A 3D-SSF, 3D movement-environment selection, LiDAR-aligned 3D bat tracking, vertical-layer bat/forest bird occurrence, height-from-structure prediction, HMM state-dependent use and simulation-based UD, or horizontal density × height probability.
- **Unproven candidate empirical advance:** independently measured true-food availability (not proxies), independently defined behavior (not height-derived labels), repeated individual 3D AGL under joint survey support; whole-animal, night, site and source heldout **increment for resource-conditioned altitude and state allocation** beyond competitive 3D-SSF and resource-free vertical benchmarks, while maintaining an explicitly calibrated horizontal species distribution/use marginal.
- **Prior art baseline priority:** 3D SSF from ssf3D is the mathematically nearest **movement and habitat selection competitor**; Klappstein 2023 HMM-SSF is the nearest state-switching competitor; Schneider 2026 is the 2D-to-vertical abundance overlay competitor; Hermans 2023 is the finest direct forest-bat 3D vegetation data competitor. All must be cited and benchmarked where matching data exist. A synthetic proof that probability factors normalize is not an ecological or computational novelty.
- **Still STOP:** No original Goldshtein direct resource × AGL same-night matched table verified. The data and observation-process differences between Ducke, Hendel, main batter tracks and ssf3D's Antarctic petrels prevent combining their coefficients into a single new joint bat 3D effect.
