# Frozen post-outcome diagnostic — target-configuration-blind rank-two forecast

## Evidence tier and provenance
**POST-OUTCOME SENSITIVITY ONLY**. Both the 8-D transductive rank-one/rank-two outcome and the four-feature target-blind scalar outcome were already opened before this test was designed. No result here is independent confirmation or a new preregistered trial. Freeze this mathematical test before calculating its numeric outcome; do not change models, thresholds, individuals, units or features after opening.

Data: the original 45 feature-valid *Rhinolophus nippon* trajectories, five individuals A–E, configurations Env1–Env7, 25 bat×configuration cells, extracted by the frozen `rhino_configuration_identity_primary_v1.py` from Figshare article 29209493. An identical 45-row **validated feature inventory** is deposited as GitHub Actions run 37205598790, artifact 11304089545, ZIP SHA256 `d6d3d3e8baa08c0417b77b0b32334859285200ae1a8b3e42c87f0aaee8e60b88`. The eight features and source values are fixed.

## New test question
Does a second **training-only** personal kinematic axis add out-of-configuration predictive information over the first axis for the identical 8-feature held-out movement phenotype, when NO feature value or empirical reference from the held-out obstacle configuration contributes to the predictor?

This closes a semantic gap between the transductive rank-two nested-prediction test and the four-feature cold-start test.

## Units and structures
- Input features: median speed, p90 speed, median absolute vertical speed, p90 absolute vertical speed, median absolute horizontal turn rate, p90 horizontal turn rate, path efficiency, vertical range. Use all eight. No feature deletion/selection.
- 45 trajectories, 25 bat×configuration cells, 7 environments and bats A–E. All structural requirements must be met, otherwise STOP.
- Whole bat×configuration trial clusters remain intact for permutation; replicate trajectories are not treated as biological replicates.

## Target-blind leave-one-configuration-out folds
For each held-out configuration e:
1. Compute 8-dimensional mean and sample standard deviation **using every trial in the other six configurations only**. Use pooled training trials, `ddof=1`; reject nonfinite or nonpositive SD. Hold the same reference fixed for every bat and rank within this fold.
2. Standardize the training trajectories with the frozen training-only means/SD. Compute a bat×training-configuration centroid by averaging all its standardized trajectories, then an eight-dimensional bat centroid by **equal weighting the eligible training configurations**.
3. Require all five bats with >=2 separate training configurations in every fold.
4. Build a 5×8 matrix from the five bat centroids. Center by the **equal-bat** training centroid mean. Fit deterministic SVD *only on these five training centroids*, not on any target data or bat labels from the target configuration.
5. Rank-r bat prediction, r in {0,1,2,3,4}: `p_i,e,r = grand + V_r V_r^T (bat_centroid_i - grand)`. Rank zero equals the grand mean; all other ranks are nested projections of the **same** bat centroid under the same training-only SVD.
6. Standardize the held-out trajectory's eight features with the saved **training-only** mean and SD. The held-out raw features are accessed only for scoring the prediction, never to change reference means/SD, PCA axes, training selection or the predicted values.

## Same-endpoint held-out loss
For each rank:
`L_r=mean_bats(mean_target_configurations(mean_target_trajectories(mean_features((z_target-p_i,e,r)^2))))`.
The main difference is `Delta_{2|1}=L_1-L_2`. Also report `Delta_{1|0}=L_0-L_1`, `Delta_{2|0}=L_0-L_2`, and all rank losses 0–4. This is quantitative forecasting, not identification accuracy. All ranks have the **same** 45 target trajectories, 8 features, 25 biological cells and folds.

## Bat-correspondence null
Within each environment independently, randomly reassign complete physical bat×environment clusters among the exactly observed bat labels in that environment, preserving all trial values, cluster sizes, configuration membership, target support, and the training-only environment reference.
For each permutation recompute training bat centroids, SVD and held-out losses at every rank. The statistic is the same mean `L_1-L_2`.

Use exactly B=9,999 permutations with `numpy.random.default_rng(20261008171)`. One-sided `p=(1+num(null>=Delta_obs-1e-12))/(9999+1)`. Demand all 9,999 valid without dropping permutations.

## Cluster uncertainty and frozen decision
Bat-cluster bootstrap B=9,999, seed `20261008172`; sample five biological bats with replacement and average bat-specific rank losses, then calculate the contrast; report percentile 95% CI.
Support under the **descriptive pre-fixed post-outcome rule** requires:
- Delta_{2|1} > 0;
- one-sided permutation p<=0.05;
- at least four of five bat-level Delta_{2|1} >0;
- 95% bat-cluster bootstrap lower bound >0.
Report all individual changes irrespective of outcome.

## Pre-result invariance and provenance gates
1. From the 45-row archived source, recalculate the earlier within-configuration four-feature scalar and verify original G=+0.293072, MSE_zero=0.633974, MSE_personal=0.340902 to tolerance 2e-5.
2. Synthetic target-configuration mutation must not alter training means/SD, training centroids, rank predictions or SVD axes for that held-out configuration. Test this before opening real scores.
3. Source ZIP SHA256 must equal the identifier above when running from the archived-feature file.
4. Numeric result must be presented as archived-feature reimplementation only; the companion GitHub Actions run remains separate until it itself finishes.

## Interpretive ceiling
- Positive: the second low-rank axis adds target-blind incremental **8-feature** movement-phenotype prediction within the observed five-bat sample. It does not imply fixed lifelong traits, a universal mathematical equation, a cause (morphology/learning), or prediction of an exact 3-D route.
- Negative: earlier target-inclusive (transductive) rank-two gain cannot be transported to target-blind prediction under these same exact features, folds and loss. The previous calibrated identity tests remain unchanged.
- Bat-label correspondence p values are conditional on the observed data, whereas inference to an unobserved population has only five biological units.
- Do not change the model after seeing any output. No further within-archive dimension-search rescue.
