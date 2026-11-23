# Novelty / prior-art kill-switch for a physical air-volume bat SDM (2026-11-23)

**Status:** explicit pre-empirical novelty boundary. The engineering branch passed 10 known-truth synthetic tests in [Actions #45097642395](https://github.com/zuizui0223/batter/actions/runs/45097642395), artifact 14783384541. **No real matched, calibrated LiDAR+3D bat source has been fitted**, and the positive artificial clutter coefficient / heldout synthetic logscore is not a biological result. JAE main remains untouched.

## Where originality is ALREADY GONE

1. **3D LiDAR vegetation descriptors predicting bat habitat**: Froidevaux et al. (2016), *From field surveys to LiDAR: Shining a light on how bats respond to forest structure*, *Remote Sensing of Environment*, DOI **10.1016/j.rse.2015.12.038**. LiDAR forest structure and guild/wing/echolocation-related habitat use are prior art. "LiDAR predicts bats" is not new.
2. **Aligned in situ 3D bat flight tracking, vegetation voxels and distances to clutter**: Hermans et al. (2023), *Movement Ecology*, DOI **10.1186/s40462-023-00387-0**. Their co-registration, nearest-vegetation distances and voxelization already exist, with examples of trunk flight and light-related vegetation distance. "Overlay bat positions with voxelized trees" is not new. The full co-located data [DataverseNL 10.34894/CHW0HB](https://doi.org/10.34894/CHW0HB) are restricted, *not* source admitted.
3. **3D vegetation preference from movement tracking**: *Spaceborne and UAV-LiDAR reveal hammer-headed bat preference for intermediate canopy height and diverse structure in a Central African rainforest* (2025), *Movement Ecology*, DOI **10.1186/s40462-025-00552-7**. Individual and population level GPS/SSF landscape analyses using 10m UAV-LiDAR and GEDI; selection for canopy height/gaps and structural complexity already documented. "Bats select open airspace near canopy gaps" is not a new conclusion.
4. **3D animal movement, habitat selection, 3D step selection functions**: *Three-Dimensional Correlated Random Walks for Animal Movement and Habitat Selection* (Klappstein et al. 2026), *Ecology Letters*, DOI **10.1111/ele.70414**. A general 3D correlated random walk / SSF exists, including barriers and vertical resources. "First 3D animal habitat selection model" is FALSE. A fair comparison to 3D SSFs is required if original 3D tracks permit it.
5. **Different observations linked through one latent spatial intensity with detection probability**: *Integrated species distribution models: combining presence-background data and site-occupancy data with imperfect detection*, *Methods in Ecology and Evolution* 2017, DOI **10.1111/2041-210X.12738**. Integration and thinned Poisson point processes are prior art. The **intSDM R package** (2025) already supports Poisson, presence-absence and presence-only observations with process-specific detection bias. "First integrated observation-process point process" is FALSE.
6. **Airspace as ecological habitat and 3D movement analysis**: Nilsson et al. (2025), *Animal niches in the airspace*, *Trends in Ecology & Evolution*, DOI **10.1016/j.tree.2025.08.006**, plus *Movement in 3D: Novel Opportunities for Understanding Animal Behaviour and Space Use* (2024), *Ethology*, DOI **10.1111/eth.13529**. "The atmosphere is a habitat" and 3D utilization distribution are prior ecological concepts.
7. **Airborne LiDAR custom structural habitat metrics**: *Using the full potential of Airborne Laser Scanning (aerial LiDAR) in wildlife research* (2024), *Wildlife Society Bulletin*, DOI **10.1002/wsb.1532**. Custom vegetation metrics and multiscale height habitat modelling already articulated.

These papers do not prove that the **exact** combined prospective question below has been answered. They DO mean this study cannot truthfully claim a first for any ingredient, or a universal answer simply by composition. This ledger is an inspectable literature scope, **not** an exhaustive systematic review through 2026 and not a priority claim without a final systematic search.

## One differentiating falsifiable field question (conditional prospective hypothesis)

> **Does a physically surveyed, detector-calibrated *free-air-volume* clutter model transfer to entirely unobserved forest sites and improve prediction of bats' height-resolved observed activity over the best 2D/vertical-only controls?**

**Scientific novelty, if established:** out-of-forest **volume-conditional niche prediction** that explicitly separates measured *free-air volume*, vegetation proximity and microphone visibility/detection. It is **new ecological predictive evidence** if neither the Hermans descriptive 3D tracking precedent, the hammer-headed bat LiDAR/SSF habitat result, nor a calibrated integration framework already shows the same endpoint with equivalent independent holdouts. It is NOT an assertion of new statistics or mathematically new point processes.

### Model comparison ledger fixed before accessing any eligible field outcome

Same species/guild identity; same observation event definition; same sampled forests, same detector footprint K, same recording exposure, same heldout observed counts, same air/vegetation/unknown mask; no model may use heldout counts for background, source q or regularization.

- **B0 strongest 2D competitor**: x–y environmental occupancy/activity intensity with a **training-only learned vertical allocation prior conditional on source sampled heights**. Not "no height information": give 2D a fair estimated vertical prior (e.g., training histogram/spline with source exposure K); maintain the same measurement model for heldout observations.
- **B1 3D height-only**: common absolute/relative height / canopy height function, evaluated on verified available air volume, same effort/K and number of constraints.
- **B2 3D structure**: all B1 features + the specifically preregistered nearest vegetation distance, foliage clutter and boundary distance, if their survey-derived values are available on *certified free air* and measured with a source-specific ray visibility model.
- **B3 if 3D trajectories available**: a fair 3D movement/step-selection baseline to separate actual flight movement autocorrelation / central-place / inertia from apparent habitat selection. Do not count each autocorrelated acoustic localisation as an independent individual or site.
- **Detector sensitivity**: compare calibrated K vs correctly declared uncertainty/sensitivity intervals. A positive B2−B1 that disappears under plausible q estimates does **not** identify selection for vegetation proximity.
- **Calibration and heldout**: entire **forests/plots** (not random voxels/tracks from the same setup), independent hardware or site effects where possible, block by recording night/track to avoid pseudoreplication, evaluate proper original observation-space predictive logscore and 3D pattern calibration (height and near-clutter conditional densities), and report site-level intervals, not call-level falsely narrow intervals.

### Three red-line claim gates

- **Gate A — true volume**: have original same-CRS bat event XYZ or source-described 3D kernel footprint, original LAS/LAZ point classification and independent scanner visibility mask, source survey geometry, and original site + session/exposure IDs. LiDAR no-return alone **cannot be treated as air**.
- **Gate B — observational identifiability**: source-specific q measured/limited independently, or an original repeated/localisation design with a justified identifiable observation operator K; avoid multiplying simultaneous detector observations that see the same original call as independent Poissons. K rank / structural condition must be evaluated. A prior or low-dimensional smoothness assumption may regularize but cannot make a nonidentifiable unconstrained λ "observed".
- **Gate C — ecological transport**: at least 3 genuinely heldout forest sites (desired design criterion, not a guarantee of sufficient power) and a locked prospective B0–B1–B2 outcome. Require directionally consistent and meaningful improvement at source-site level with uncertainty excluding negligible/no gain *before any broad cross-forest biological claim*. No gain → publication target is methods + negative boundary, **not** an ecological discovery.

These thresholds are the **study's required prospective minimum bar**, not demonstrated findings. No number of synthetic successes can pass Gate C.

## A reviewer-grade falsification: hidden q can create an apparent clutter niche

Suppose genuine activity is uniform in two equal-volume known-air habitats (near vegetation and open air): `lambda_near=lambda_open=100` events/m³/h. If detection probability is `q_near=.2` and `q_open=1.0`, expected detected events become `20` and `100`. A detector-naive model falsely infers `lambda_open/lambda_near=5` and reports a strong **open-air niche**. The correct K with calibrated q recovers `lambda_open/lambda_near=1`.

The same observed data can be explained by a true open-air preference and equal q. Thus the "strong clutter effect" is not biologically identifiable from detected counts alone. This precise synthetic contrast should live next to the true air-volume model CI and be treated as a hard adversarial counterexample, not a new ecological result.

## Coherent relationship to pre-existing batter conclusions

The batter JAE program has positive **individual-centered vertical shape identity**, but no supported need for persistent between-individual spatial partition. That result addresses persistence of individual distributions under coarse horizontal standardisation. A prospective air-volume model addresses **habitat-supported intensity and transport between forests**, an independent population/species or acoustic guild level. It must not silently reinterpret individual-level identity as species-specific clutter selection.

Similarly the ODSP #306/#307/#308 source projects represent recorded height information, bat–plant functional layer labels and mixed 62-study broad-taxon vertical transfer, not actual registered 3D air-volume niche models. Their outcomes must not be pooled as replication of this new physical-space hypothesis.

## Honest paper titles by tier

- **NOW (source-free methods)**: *Observation-aware point processes for bat airspace: a synthetic framework and identifiability limits*. No first/unprecedented/new-ecological-phenomenon language.
- **IF Gate A/B + prospective real plot prediction succeeds**: *Predicting bat use of forest airspace from vegetation geometry under explicit acoustic detection*.
- **IF independent multi-forest transfer Gate C succeeds**: *Clutter-defined airspace niches predict bat activity across unseen forests* — only if previous work did not already establish equivalent outcome; check competing current literature again.
- **IF non-transfer**: *Where three-dimensional forest structure fails to generalize bat space-use predictions*.

**Current reality:** code + ten synthetic tests PASS; 0 original matched calibrated LiDAR × bat XYZ field sources admitted; Hermans original is restricted. **No empirical novelty claim is presently supported**. The main practical blocker is obtaining or producing a paired calibrated multi-site source, not adding more model terms to synthetic proof.
