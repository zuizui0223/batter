# Whole-cell variance-preserving sign-flip: executed synthetic calibration v1

**2026-10-08. This is a source-free statistical method result; NOT a new bat ecological observation.**

## Provenance and execution
- Pre-result theoretical/synthetic contract: `CELLWISE_SIGNFLIP_KNOWN_ENVIRONMENT_CONTRACT_V1.md`, committed `e7d6c4fd13318dbdb02aae33aa3a10b08f787c29`.
- Script: `whole_cell_signflip_synthetic_v1.py`; scripted GitHub Actions workflow committed at `02709ac653440b073d8f7de90803b7d5071bd7d7`.
- [Official successful workflow run 37784689642](https://github.com/zuizui0223/batter/actions/runs/37784689642), job `113336310621`; Python 3.13 compile/self-tests completed; no real-data files opened.
- **Entire dataset fabricated**: 5 fictional bats, 7 fictional obstacle contexts, 25 nonempty bat×context cells, 45 synthetic repeated trial-file rows. The cell occupancy is schematic, NOT the original tracking archive's exact source layout; synthetic same-cell records are duplicates. Four correlated fabricated features per cell; within-vector correlation approximately rho=0.6 by construction.
- 160 independently simulated synthetic archives per scenario; 199 randomized transformations per archive; `p=(1+number_of_null_scores>=observed)/(199+1)`. Two algorithms recomputed exactly the same mean-history held-out score; sign-flip oracle re-fitted training-only feature means and SDs in each null transformation.

## Executed outcomes: false rejection under H0_mean (theta_i = 0)

| Simulated noise | Individual SD profile | Bat-label shuffle at nominal 5% | Known-task-mean, whole-4D-cell sign flip at nominal 5% |
|:--|:--|--:|--:|
| Gaussian, symmetric | all 1.0 | 4/160 = **2.50%** | 6/160 = **3.75%** |
| Gaussian, symmetric | [0.3,0.6,1.2,2.5,5.0] | 22/160 = **13.75%** | 11/160 = **6.875%** |
| Centered-exponential, asymmetric | [0.3,0.6,1.2,2.5,5.0] | 30/160 = **18.75%** | 17/160 = **10.625%** |

Additional tail indicator at nominal 1%:
- Equal Gaussian: both 0/160.
- Unequal Gaussian: label 10/160=6.25%; sign 1/160=0.625%.
- Unequal asymmetric: label 15/160=9.375%; sign 6/160=3.75%.

These percentages are stochastic measurements from **fixed toy simulations**; sample size 160 and 199 Monte Carlo draws limit precision, especially in the extreme p-value tail. Do not use them as universal type-I error rates or a multiplicative correction of any real bat p-value.

## Mathematical interpretation

If the external shared environment means `mu_e` are known, bat×context four-vector residuals are conditionally **jointly sign-symmetric around zero**, and the 25 cell vectors are independent conditional on their configuration, the null distribution is invariant under changing the sign of any **entire cell vector** while retaining bat, context, feature correlations and each cell's residual amplitude. Such transformations do not require identical `sigma_i`; hence in this oracle construction the sign-flip test targets the null of no stable **individual-specific mean**, while accommodating individual-scale differences. The Gaussian heteroscedastic case shows substantial improvement relative to label relabelling, though the 6.875% estimate itself has Monte Carlo uncertainty.

The asymmetry stress case was intentionally **outside** those invariance assumptions; its elevated sign-flip false rejection (~10.625%) is direct evidence that this is **not** a safe drop-in replacement when residual symmetry fails. The null also fails if `mu_e` is estimated from the same sparse bat data without appropriate adjustment, or if long-lived sensor, same-night dependence or individual-state effects violate residual independence and centering.

## Null-scope boundary

We are testing `H0_mean` where `theta_i=0` and `sigma_i` may differ. Such heterogeneous sigma is already **distributional individuality**, not a complete absence of every individual-specific property. The original cross-configuration identity tests may pursue a broader exchangeability/null and are not numerically refuted by this simulation. See `MEAN_VS_DISTRIBUTIONAL_IDENTITY_NULL_SCOPE_V1.md`.

## Consequences and STOP decision

1. **Validated as a synthetic principle:** preserving nuisance variance and within-feature dependence helps to avoid false declarations of portable individual mean shift in one defined symmetric, heteroscedastic null.
2. **Demonstrated failure condition:** asymmetric residual distributions invalidate this sign-flip oracle even with externally known mu.
3. **NOT solved:** real bat per-environment shared means are unknown, real residual symmetry and session independence unverified, bat-to-sensor effects unseparated, and support is limited to 5 bats. No method is now authorized to replace PR #79 p=.0003 using the old observations.
4. **Source gate unchanged:** none of the separately screened public datasets currently satisfies the independent bat×controlled context×repeated occasion structure needed to verify personal reaction norms and foraging payoff.
5. **Ecology priority:** obtain independently verified repeated contexts, device crossover and prey/target performance for any future causal claim. Do not promote another synthetic benchmark into proof of learned 3D strategy or spatial niche adaptation.

**Verdict: PASS_SYNTHETIC_VARIANCE_PRESERVING_ORACLE_UNDER_SYMMETRY; FAIL_GENERALITY_UNDER_ASYMMETRY; STOP_EMPIRICAL_MEAN_POLICY_RECLASSIFICATION.**
