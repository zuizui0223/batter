# Theta correspondence audit v1 — post-outcome correction and new randomization test

## Status and evidential firewall
Generated after the scalar theta, held-out calibration, and learning-curve outcomes were already seen. This is **post-outcome diagnostic**, not an independent preregistered confirmation. Prior frozen outputs remain unchanged and recoverable.

## Part A — mathematical audit (exact, outcome-independent)
The frozen learning-curve method averages squared error over **every** size-m subset S of N observed training environments. With y the held-out scalar, training mean xbar, and training sample variance s² (denominator N-1):

mean_{S: |S|=m} (y - mean(x in S))²
= (y - xbar)² + (N-m)*s²/(N*m).

Consequences fixed before this audit:
1. MSE_1 >= MSE_2 >= MSE_3 >= MSE_full by construction, for any data.
2. A strictly positive MSE_1-MSE_3 needs only nonzero training variance; it is not evidence for temporal or stochastic convergence to a stable biological parameter.
3. The individual "fraction to full" is 1-(N-m)/(m*(N-1)), depending only on the count N, not on the observed y or on genuine biological persistence.
4. Hence the 91.6% aggregate is not an independent convergence estimate; this audit supersedes that interpretation, without invalidating other identity-transfer or magnitude-calibration tests.
5. With only 4–6 observed environments per bat, a limiting parameter as N→infinity is not identifiable from these data.

## Part B — actual held-out bat-identity predictive gain
Use the 25 bat×environment scalar centroids from the authoritative FlightIntensity analysis, reconstructed without value changes from its frozen upstream script:
prospective/task_reset_lockin/flight_intensity_scalar_v1.py.

Bat set A–E; environment incidence is frozen by the source archive.
For each bat i, target environment e:
- training theta_i,-e is the equal-environment mean from the other observed environments of the same bat;
- prediction target y_ie is the environment-standardized FlightIntensity centroid;
- zero baseline is 0 (the null location under prior within-environment standardization);
- target gain g_ie = y_ie² - (y_ie - theta_i,-e)².

Primary G: equal target environments within bat then equal bats, mean g.
Report MSE_personal, MSE_zero, R²=1-MSE_personal/MSE_zero, bat-specific G and bat R².
This is distinct from the algebraically guaranteed subset-learning-curve improvement.

## Null
Within each environment independently, permute its complete bat×environment scalar-centroid values among the **observed bat labels for that environment**. Thus:
- exact environment occupancy (which bat labels occur) fixed;
- exact environment value distributions fixed;
- bat-wise number of available environments fixed;
- correspondence of the same bat across environments broken;
- own history and held-out personal predictions recomputed after each permutation.

B=19,999, seed=20261008111.
One-sided p=(1 + #{G_perm >= G_obs})/(B+1).
No optional dropping of outliers or bats after opening.

## Robustness (descriptive only)
- Equal-bat contribution table (five bats).
- Five leave-one-bat-out programme-level gains, same estimator, no reclassification.
- Bat-cluster bootstrap (B=9,999, seed=20261008112) 95% percentile CI for G, reflecting only five biological units.
- Verify Part A identity to tolerance 1e-10 for every target at m=1,2,3 on the extracted centroid values.

## Interpretation
If G>0 and permutation p<=0.05, own identity predicts held-out context-standardized flight intensity better than no personal identity at the species/context-centred baseline, even though the subset MSE convergence result was tautological.

If G is unsupported, one-dimensional identity scores and pairwise calibration remain separate endpoints, but the mean-value personal scalar is not supported as an absolute predictor beyond the zero baseline.

A positive G for the population is not the claim that all five bats have stable personal scalars. Non-positive bat-specific gains must be reported, without selective exclusion.

This does not identify a unique dynamical equation, ontogenetic origin, universal biological dimensionality, or time-series convergence of theta. Environment identity here is an obstacle **configuration**, not ordered time.
