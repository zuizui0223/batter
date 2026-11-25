# Supplement S1. What the paired recorded-label contrast does and does not identify

This is an analytical interpretation of the existing estimator, not a newly fitted model or a claim of statistical novelty. All data and predictions remain unchanged.

## S1.1 Exact invariance of the model score

For a fixed provider-year-block and two different recorded cells x,y, with labels s,t, define the double difference Df = f_s(x)−f_t(x)−f_s(y)+f_t(y). The model score log sigmoid(Df) is unchanged by adding arbitrary species intercepts a_s or a common cell term b(x) to f_s(x). Both cancel exactly. Consequently this estimator targets relative recorded-label association, not abundance, absolute cell suitability, or baseline occurrence probabilities. A scalar environmental coefficient shared identically by all species also cancels. The predictive value of R50 therefore concerns species-differential responses in this fitted score, not a universal increase in suitability.

## S1.2 When observation terms cancel — a conditional illustration

Let p_s(x) denote the marginal probability of a recorded species-cell label in a stratum, not its latent biological occupancy. In an idealized setting with independent label indicators across distinct cells, the expected weight of the recorded orientation (s at x, t at y) is p_s(x)p_t(y); the swapped expected weight is p_t(x)p_s(y). Both orientations can appear in our composite construction. On positive common support the log ratio of these expected weights is the double difference D(log p).

Suppose, as an additional substantive assumption, that p_s(x)=A_s B(x) U_s(x), with positive factors giving valid probabilities. Then D(log p)=D(log U): source-specific species factors A_s and species-common cell factors B(x) cancel. But species-by-cell observation interactions need not cancel. Without the factorization, matching data provider, year and block does not identify D(log U). This result describes an idealized ratio of expected orientation weights, not an exact independent likelihood for the capped and block-weighted empirical pair sample. It must not be used to claim equal effort, detection adjustment or causal selection.

## S1.3 Why multiplicity deduplication is not a detection correction

Even if raw recording intensities factorize as mu_s(x)=A_s B(x) U_s(x), probabilities of at least one detected record under independent Poisson sampling are p_s(x)=1−exp(−mu_s(x)). This nonlinear mapping generally breaks the factorization; approximate cancellation is possible in the rare-record limit but is not guaranteed. Hence removal of duplicated label occurrences controls multiplicity, not heterogeneous detection.

A numerical counterexample, explicitly illustrative and not from the bat data: U_s(x)=U_s(y)=U_t(x)=U_t(y)=1, A_s=1, A_t=0.2, B(x)=10 and B(y)=0.1. Then the raw intensity cross-product ratio equals 1, but the deduplicated label orientation ratio is

(1−exp(−10))(1−exp(−0.02)) / [(1−exp(−0.1))(1−exp(−2))] = 0.240636.

The log ratio is -1.424470 despite identical biological use for both species at both cells. This is one way a profile-related sampling gradient could influence observed sorting without true niche differentiation.

## S1.4 Relation to multidimensional SDM

The fitted response f_s(x) ranks recorded-label orientations on the existing common support. It is invariant to species and cell intercepts and cannot identify even a calibrated horizontal occupancy probability; the original 20-species target-group SDM was not fitted. A horizontal biological intensity Lambda_s(x), if independently identified, would still leave the altitude distribution q_s(z|x) unconstrained. Any normalized q_s yields the same horizontal marginal of lambda_s(x,z)=Lambda_s(x)q_s(z|x).

An independent structural proxy check can evaluate the environmental part of this chain (GVSM R50 versus ALS-derived H50/H95) without validating bat altitude or biological detection. The northern stress test simultaneously changes provider, geographic conditions and GVSM extrapolation status, so an environmental proxy validation alone cannot causally explain the failed northern transfer.

The appropriate contribution of the present paper is held-out predictive information in a vertically informed **recorded-label model**, with clearly tested transfer limits. No extrapolation to actual airspace utilization, PAVD or successful feeding.
