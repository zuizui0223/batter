# Known-Gaussian GPS AGL observation error × resource-conditioned 3D height: source-free audit v1

2026-11-21, batter Draft PR #102. **Five preregistered synthetic scenarios only**; no original Goldshtein bat heights, flower amounts, or real 3D ecological effect were estimated. Do not cite these numbers as measured resource responses. Original ssf3D continuous-space sampled-control fitting is a separate uncompleted benchmark; this script tests the *complete enumerated discrete XY × Z* candidate lattice, **not** a q-sampled control riskset.

## Why this changes the model

The existing M0–M3 riskset evaluator used one discrete "observed choice" that implicitly reveals the true altitude bin. Real GPS altitude is a **noisy observation of latent altitude**, not a verified bin. For each sampled flight fix with observed horizontal cell x and continuous measured AGL y, the new [error-convolution evaluator](gps_height_error_likelihood_v1.py) fits:

    p(x,y | context, R, sigma)
        = sum_{z in candidate heights for x} p_choice(x,z | context,R)
            Normal(y; z, sigma^2).

Here sigma is **independently calibrated** GPS-altitude uncertainty, not fitted to the withheld flight outcome. Horizontal observation is treated as error-free at the prespecified coarse XY scale. The predictive log density decomposes exactly into
log p(x) + log p(y | x); all nested models evaluate the **same continuous observed y**, with the same Gaussian density units. A latent true z label is forbidden in the accepted training schema. Training uses BFGS on mixture log likelihood with train-only feature scaling, equal-bat-night weighting and ridge regularization; the comparator first hard-bins y to the nearest candidate z for training, but is **also evaluated on the same continuous observed y** via the same convolved density. No direct causal identity is inferred.

**Data eligibility is strict:** original GPS fix, regular sampling, known AGL datum, independently calibrated positive finite sigma, complete fixed XY×Z candidate grid not derived from the test outcome, independent actual resource proxy, and a source-specific separate archive/schema check. A dated true-flower hypothesis additionally requires night-matched direct flower observations and verified effort. Do not interpret simulation-set provenance flags as real source authentication.

## Executed original source-free numerical experiment

The precommitted [5-scenario runner](gps_height_error_sensitivity_sourcefree_v1.py) and dedicated [GitHub Actions workflow](../../.github/workflows/resource-behavior-gps-height-sensitivity.yml) produced a run-traceable artifact (Actions #44889812634, artifact "gps-height-error-five-synthetic-scenarios-v1", GitHub artifact ID **14701144217**) before these outcomes were summarized here.

Generator: 6 fictional bats, 2 nights each, 5 steps per night = **60 simulated step observations clustered within six animals** (not 60 statistically independent bats). Two full artificial sites are withheld successively; within each site three bats are held out together. Original simulator true choices generate a noisy GPS observation and the latent true step index is then **deleted** before model fitting. The independent standard-normal deviates, seed 20261121, are reused across sigma conditions for paired sensitivity. Model M2−M1 adds resource×candidate height. Scores are equal-site means in nats per recorded XY+continuous AGL observation. Environmental site and independence structure are simulated, not real survey designs.

| Generator / sigma (m) | M2−M1 conditional height gain, sensor-aware | M2−M1 conditional height gain, hard-bin learned | M2 sensor-aware minus hard-bin **overall joint** predictive log density |
|---|---:|---:|---:|
| True resource×height, 0.5 | **+0.067275** | +0.067275 | approximately 0 |
| True resource×height, 11 | **+0.069186** | +0.069679 | +0.002353 |
| True resource×height, 25 | **+0.030019** | +0.033408 | **+0.042272** |
| True no resource effect, 11 | +0.000165 | +0.000592 | −0.000422 |
| True resource×height, σ=11 with XY-dependent 0.6×/1.7× observation SD | **+0.065389** | +0.069036 | +0.003664 |

The final scenario uses sigma=6.6 or 18.7 m by candidate XY and assumes these varying errors are **independently known**; it is not an estimate of how vegetation modifies satellite GPS error. Outcomes depend on this fixed illustrative generator. Zero-noise equivalence is approximated with σ=0.5m (not exactly σ=0).

**Important contrast:** A larger nested "increment" does not make that model better absolutely. At 25m, the hard-bin-trained M2 has a nominally larger M2−M1 *within-horizontal increment* (+0.0334 vs +0.0300), but the **sensor-aware M2 itself** has higher heldout joint observed-data log density by +0.0423. The latter comparison uses identical test targets and source folds. One can report both, but not cherry-pick the largest incremental score as absolute superiority.

These results support **software ability to represent height observation error and assess nested resource prediction**, not robustness of any actual wild-bat resource effect. Published Goldshtein et al. (2020) reported roughly 11m vertical GPS SD, but the 11m value here is an illustrative *input*; this project has not independently verified the exact tag-, terrain-, fix- or bat-level error distribution. Gaussian homoscedasticity, errors correlated with canopy, XY error, altitude non-Gaussian tails, bias and changing datum are untested.

## Fail-closed tests and boundaries

Source-free unit tests [test_gps_height_error_likelihood_v1.py](test_gps_height_error_likelihood_v1.py) check normalization/decomposition, matched scoring denominators across the two training approaches, whole-site holdouts, permitting noise-induced negative measured AGL without making true candidate AGL negative, impossible/zero or uncalibrated sigma, height-defined resource covariates and latent true endpoint/height label leakage, and independence of state labels. Both synthetic and source-free CI use Python 3.10–3.12.

**Unresolved:** the known-q sampled 3D control likelihood from the earlier implementation is **not yet mathematically integrated with this latent-height observation-error likelihood**. Simply convolving per sampled-candidate choice labels with an error kernel is not generally equivalent to a continuous 3D step process. The present module explicitly returns q_sampled_control_correction_integrated = false. A real calibrated 3D usage density additionally requires spatially valid availability, sensor likelihood, modelled detection and, for regional species SDM, separate occupancy/abundance inference.

**Primary empirical gate remains:** official Goldshtein Mendeley dataset https://doi.org/10.17632/jxghjjsttw.1 exists, but original archive/API remained HTTP401 in the source runner; 3,600 mapped cactus locations are not the same as 414 repeatedly monitored flowering cacti. The source's same-night GPS fix × dated real bloom join is unverified. Never replace with model-imputed flower counts; never use the paper's altitude<20m visit label as a predictor of altitude. No original wild-bat resource-conditioned height prediction is reported.

Original software test artifact: https://github.com/zuizui0223/batter/actions/runs/44889812634 . Current JAE/BE submissions and batter/esdm main unchanged; keep PR Draft.
