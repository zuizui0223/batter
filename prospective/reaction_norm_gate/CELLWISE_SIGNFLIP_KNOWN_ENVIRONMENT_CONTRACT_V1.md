# A variance-preserving alternative to bat-label permutation (pre-output method contract)

**STATUS:** SYNTHETIC-ONLY CALIBRATION. No real bat endpoints may be opened or recomputed. This is a child test of the four-feature synthetic #79 analog, not an independent confirmation of bat identity, learning or niche mechanisms.

## Target and misconception to avoid

The original #79 null relabels observed bat centroids among the co-observed bats within each configuration. This is **not** a valid null for `no stable bat-specific *mean*` if each bat retains a distinct noise scale: under that mean-null bats are not label-exchangeable, because noise scale is itself identity-linked. The earlier 4-feature simulation reproduced nominal 5% false rejection at ~12.14% for one heterogeneous Gaussian design. This does NOT imply that there is no biological variance individuality or that the archive's realized G is spurious.

Here we test a **different** null transformation, defined before opening its synthetic test outputs. It preserves both the individual-specific 4D error magnitudes and feature correlation.

## Source-free model

For observed bat i, configuration e, four-feature cell centroid:
```
Y[i,e] = mu[e] + theta[i] + sigma[i] * epsilon[i,e]
```
where `mu[e]` is a **known, externally prespecified** four-feature shared environment vector, sigma[i] can be arbitrarily individual-specific, and each independent `epsilon[i,e]` is jointly centrally symmetric in 4D under the **H0: theta[i] = 0** mean-identity null. Correlation within the four-vector is allowed. Independence between bat×configuration cells and symmetry around externally known `mu[e]` are required; simply assuming individual trajectories are independent is not enough.

### Sign flip algorithm
1. Keep the same synthetic bat×configuration occupancy (5 bats/7 environments/25 cells) and exactly 45 synthetic trial entries, with schematic original occupancy and artificial within-cell duplicate records.
2. For each of the 25 **whole four-feature cell residual vectors** `r[i,e] = Y[i,e] - mu[e]`, draw one independent Rademacher sign `s[i,e] ∈ {-1,+1}` and form `Y* = mu[e] + s*r`. All replicated trial entries in that cell receive the **same** sign; no frame or individual feature may be flipped separately.
3. In **every** synthetic reference, refit the training-only four-feature mean and sample SD using the 45 artificial trial rows outside the held-out configuration; then recompute scalar, personal-history forecast, zero-baseline MSE and bat-equal G. Do not reuse fold scales from the observed draw.
4. Null Monte Carlo one-sided `p = (1 + count(G* >= observed G))/(B+1)`, B=199 sign-flips per simulated dataset; compare with B=199 old within-environment label permutations.
5. Primary methodology contrast: empirical null rejection rate at one-sided 0.05 for two **fixed** synthetic generative scenarios: equal independent Gaussian bat SD=1 and heterogeneous bat SD=[0.3,0.6,1.2,2.5,5]. Both include the same nonzero known task-wide environment means and same within-cell four-feature correlation rho=0.6.
6. Additional deliberately invalid stress scenario: heteroscedastic **asymmetric** noise (centered exponential mixture with four-feature correlation): whole-cell sign symmetry fails. The sign-flip method is not claimed valid there.
7. A separate **fixed personal mean** scenario (illustrative power) may be reported but may not be used to select a null-test variant or effect threshold.

### Calibration check
The test is meaningful if the known-mean, centrally symmetric heteroscedastic sign-flip null stays near nominal 5%, whereas bat-label permutation may not. Monte Carlo fluctuations are expected. A positive result must always be labeled `PASS_SYNTHETIC_ORACLE_ONLY`.

### Why this is not yet a deployable bat-data test
In the actual experiment `mu[e]` is **unknown**, must be estimated, and the bat×environment design is sparse. Plugging a same-sample mean of 2–5 bats into the sign-flip center is **not** an exact null. There can also be time-of-night covariates, device offsets, repeated trajectories from correlated behavioral bouts and skewed errors. No claim of sign-exchangeability from real bats has been verified.

**STOP for empirical reinterpretation** until (i) shared environmental means and error symmetry are established by independent calibration or a separately justified model, (ii) bat-specific noise estimation and interval uncertainty are handled, and (iii) a new dataset or uncontaminated held-out evidence is available.

This script is a technical falsification of an attractive but invalid exchangeability assumption; it is not a new ecological discovery.
