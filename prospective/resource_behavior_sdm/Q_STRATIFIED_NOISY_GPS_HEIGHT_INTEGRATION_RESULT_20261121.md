# Integrated nonuniform candidate q × noisy GPS height: two-world results and MC accuracy audit

2026-11-21. Branch prospective/resource-behavior-higher-dimensional-sdm-v1-20261120, draft PR #102. **SOURCE-FREE SIMULATION ONLY**. No original Goldshtein GPS/flowers, no real resource × AGL gain, no continuous-space ssf3D fit, no species SDM or causal inference.

## The nontrivial mathematical change

Earlier modules treated:
1. known true chosen 3D candidate among one observed and K q-sampled independent controls — a conditional **selected-label likelihood** with offset log(reference / q); or
2. continuous observed GPS AGL with Gaussian error and exact enumerated 3D candidate support.

These are **different observation experiments**. A noisy GPS height does NOT reveal which latent z is the "observed choice" among q-sampled alternatives. Simply applying a Gaussian convolution to the first module's chosen candidate would incorrectly condition on hidden truth and/or use an observation-dependent proposal.

The new [q_stratified_noisy_height_bridge_v1.py](q_stratified_noisy_height_bridge_v1.py) implements a coherent **third** experiment: given measured coarse horizontal cell x and noisy AGL y, independently sample a fixed number K_x of latent altitude candidates from a known, positive, prespecified q(z|x) **before seeing observed x,y**, with prespecified reference μ(x) μ(z|x). The **same controls** are used in M0/1/2/3. For any model linear predictor η(x,z), construct

    W_x(z_k;θ) = [μ(x)/K_x] [μ(z_k|x)/q(z_k|x)] exp(ηθ(x,z_k))
    A_x(θ) = sum_{k=1}^{K_x} W_x(z_k;θ)
    B_x(y;θ) = sum_{k=1}^{K_x} W_x(z_k;θ) Normal(y|z_k,σ²).

Then

    p_hatθ(x,y) = B_x(y;θ) / sum_{x'} A_{x'}(θ)
    log p_hatθ(x,y) = log p_hatθ(x) + log p_hatθ(y | x)

where p_hatθ(x) = A_x / ΣA and p_hatθ(y|x)=B_x/A_x. The exact decomposition is **conditional on the finite q sample and coarse XY observation**; it is not species occurrence or abundance. It is **self-normalized importance quadrature**, consistent for the specified finite reference domain with adequate sampling, but biased at finite K. It is **not** the case-control selected-label likelihood and not the published ssf3D continuous normalizer.

Code reuses original training-only standardized M0–M3 covariates, equal bat/night weighting, Gaussian measurement-error likelihood, ridge-BFGS fit and whole-site/bat/night holdout. The separately source-validated offsets are injected into the existing GPS-error likelihood; the original complete-grid admission **explicitly rejects unverified offsets**.

## Synthetic empirical-looking gains are NOT field effects

Source-free original run [GitHub Actions #44891053058](https://github.com/zuizui0223/batter/actions/runs/44891053058), artifact **14702001629**, stores the first two-world receipt. 6 fictional bats, 2 nights × 4 steps each = 48 fictional recorded XY+noisy AGL positions, two full-site holdouts, 24 q-sampled altitudes per XY, opposite site q tilts ±1.7, assumed observation σ=11m (not verified field calibration). q and source supports are independently constructed.

| Designed truth | Corrected M2−M1 conditional height gain | Naive q-sampled M2−M1 conditional height gain | Corrected M2 absolute joint log density | Naive M2 absolute joint log density |
|---|---:|---:|---:|---:|
| True resource×height effect ZERO | +0.002493 | −0.056657 | −6.241627 | −7.071209 |
| True resource×height effect nonzero | +0.070349 | +0.023772 | −7.153291 | −7.124888 |

Gains are nats per **synthetic recorded observation**, equal source-site averages, NOT independent-bat tests or inferential p-values. The nonzero true-effect world exposes a crucial limitation: **corrected M2 conditional-height increment is higher while corrected M2 total absolute log density is slightly worse** (−7.153 vs −7.125) at K=24, consistent with inadequate finite Monte Carlo coverage. Never select one numerator contrast as proof of overall model superiority.

## Source-free precommitted MC accuracy check: complete-grid ground truth

A separate fixed-K protocol was committed *after the above two-world outcome was already seen* and before opening the new grid: [Q_NOISY_HEIGHT_MC_CONVERGENCE_FREEZE_V1.md](Q_NOISY_HEIGHT_MC_CONVERGENCE_FREEZE_V1.md). It is post-outcome methodological robustness, not preregistered experimental evidence.

[GitHub Actions #44891213983](https://github.com/zuizui0223/batter/actions/runs/44891213983), artifact **14702280601**, replayed synthetic source world with identical recorded XY+noisy AGL observations for K_x = 12, 24, 96, 384, 1536 per XY. Crucially **no model is refitted** in this accuracy experiment: all methods use the exact same frozen beta = [0,0,0,0,0,−0.08,+0.12,+0.45] and compare predictive log densities against complete reference-grid calculations (2 XY × 3 Z).

| q samples per XY | Corrected mean absolute log density error | Uncorrected error | Worst event's sampled Z coverage | Minimum importance effective sample fraction |
|---|---:|---:|---:|---:|
| 12 | 2.9964 | 3.3269 | 1/3 | 0.133 |
| 24 | 2.1731 | 2.6052 | 1/3 | 0.123 |
| 96 | 0.8233 | 1.6409 | 2/3 | 0.133 |
| 384 | **0.0815** | 1.0461 | 3/3 | 0.149 |
| 1536 | **0.0501** | 1.0881 | 3/3 | 0.149 |

Unit: nats per synthetic recorded XY+height observation, equal-bat mean **absolute** discrepancy from exact full-grid joint log density. When K_x becomes large, corrected integration approaches the exact result; naively uncorrected q-weighting retains severe systematic discrepancy. **No universal threshold K=384 is justified** by one q distribution and three Z levels. Effective sample *fraction* can remain low even with many control points; actual ESS increases with K. Missing height classes at K≤96 make low-sample model results unreliable even when algebraically corrected.

In this one generator the corrected error decreased across tested K, but the sequence is not a theorem of monotone convergence and finite MC estimates are not independent across repeated attempts. The 11m observation SD is illustrative and Goldshtein GPS measurement error remains externally uncalibrated in this project.

## Admissibility hard STOPs

- Independently measured original GPS XY & recorded altitude, verified AGL datum, sensor error distribution independent of heldout response, original regular fix timestamps, pre-response q(z|x) with positive coverage over the entire source-supported Z domain and traceable reference μ.
- q-sample **independent of the observed current XY and noisy GPS height** (stratification across eligible XY is predeclared); no observed latent true z/visit label (Goldshtein's visit uses height<20m).
- Original measured local resource from independent survey, fixed spatial/time footprint. Direct timed flowers require actual matched night and effort; mapped cactus positions alone are habitat opportunity, not actual nightly nectar. No missing resource imputation as zero, no simulated bloom counts presented as observed.
- Control duplicates okay for Monte Carlo integration. q_z and μ_z for *every* Z support cell must be recorded and normalized, candidates checked against their full source catalog; self-declared booleans cannot authenticate the original dataset. Return NULL and STOP when source survey, q positivity, sensor support, or original file authenticity cannot be independently verified.
- No single random K or positive simulator conditional-height gain is an empirical bat effect. No fix-level p-values. A real continuous-space SSF requires appropriate full movement kernel, measurable q reference over physically accessible 3D regions, actual sensor likelihood and observation effort/detection. Its scores are **not** directly commensurate with this finite-domain method or regional species occupancy AUC.

Tests: [test_q_stratified_noisy_height_bridge_v1.py](test_q_stratified_noisy_height_bridge_v1.py) pass complete grid q=μ equivalence, finite q candidate duplicates, noise/error log-score decomposition and original height/proposal/date eligibility STOP. Original full battery source-free CI on the fixed source-free implementation succeeded [run #44890987054](https://github.com/zuizui0223/batter/actions/runs/44890987054).

**Empirical status:** Goldshtein [Mendeley Data 10.17632/jxghjjsttw.1](https://doi.org/10.17632/jxghjjsttw.1) original content remains unavailable from official GitHub source metadata API (prior authenticated result HTTP401). Original per-fix bat AGL and directly dated flowering resource join have not been inspected. Real M2−M1 and M3−M2 resource-conditional height gains remain NOT ESTIMATED. Keep PR Draft; no changes to main, JAE/BE frozen release, or esdm main.
