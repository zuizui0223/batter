# Rhino low-rank individual × environment interaction contract v1

## Status

**POST-PRIMARY MATHEMATICAL-STRUCTURE DIAGNOSTIC. NOT CONFIRMATORY.**

Frozen after:
- a rapidly convergent one-dimensional personal mean parameter theta was supported;
- simple held-out margin reliability was unsupported;
- an individual-specific variance parameter sigma did not improve held-out probabilistic prediction.

No low-rank interaction outcome has been calculated before this contract.

## Question

Can the remaining individual × environment term be represented by a small number of structured reaction axes?

Start from

[
y_{ie}=mu+	heta_i+gamma_e+h_{ie}+epsilon_{ie},
]

where:
- (y_{ie}) is the bat × environment mean FlightIntensity;
- (	heta_i) is an individual main effect;
- (gamma_e) is an environment main effect;
- (h_{ie}) is the remaining individual × environment interaction.

Test:

### M0 — additive model

[
h_{ie}=0.
]

### M1 — rank-1 interaction

[
h_{ie}=lambda_{i1}phi_{e1}.
]

### M2 — rank-2 interaction

[
h_{ie}=
lambda_{i1}phi_{e1}
+
lambda_{i2}phi_{e2}.
]

If M1 predicts held-out cells better than M0, one extra personal reaction coefficient is sufficient for the structured interaction.

If M1 fails but M2 succeeds, two interaction coefficients are required.

## Data

Use exactly the already-defined *Rhinolophus nippon* FlightIntensity bat × environment centroids from the seven obstacle configurations.

No pulse variable, route coordinate, morphology, or target-specific tuning enters this diagnostic.

## Cross-validation unit

Leave one observed bat × environment centroid out.

A target cell is evaluable only if, before removal:

- the focal bat occurs in at least 4 environments, leaving >=3 training environments;
- the target environment contains at least 3 bats, leaving >=2 other bats after the target is held out.

These gates are structural and frozen before outcome opening.

Expected target universe from the known incidence pattern:
**23 bat × environment cells** (Env1–Env6; Env7 is structurally excluded).

## M0 fitting

On all non-target observed cells, fit by ordinary least squares:

[
y_{ie}=mu+	heta_i+gamma_e.
]

Use an intercept plus treatment-coded bat and environment indicators.

All categories needed for the target must be present in training.

## M1 / M2 interaction fitting

1. fit M0 on the training cells;
2. calculate training residuals;
3. fit a rank-r factorization to observed training residuals only:

[
r_{ie}approx L_i^	op F_e.
]

For r = 1 or 2.

Implementation:
- deterministic zero-filled residual-matrix SVD initialization;
- alternating least squares on observed cells only;
- ordinary least-squares row and column updates;
- normalize factor columns after each complete ALS cycle;
- maximum 1,000 cycles;
- convergence when training SSE improvement is <1e-12 relative scale.

No ridge penalty or post-outcome hyperparameter is allowed.

Prediction for the held-out cell:

[
hat y^{(r)}_{ie}
=
hat y^{(0)}_{ie}
+
hat L_i^	op hat F_e.
]

## Primary endpoints

For each model compute held-out squared error.

Aggregate:
1. mean target error within bat;
2. equal mean across bats.

Report:
- MSE0;
- MSE1;
- MSE2.

Primary improvements:

[
Delta_1=MSE_0-MSE_1
]

[
Delta_2=MSE_0-MSE_2
]

and incremental:

[
Delta_{2|1}=MSE_1-MSE_2.
]

## Uncertainty

Cluster bootstrap biological bats with replacement.

- B = 9,999
- seed = 20261007941

Report percentile 95% CIs for all three improvements.

A rank r is supported relative to M0 only if:
- (Delta_r>0);
- bootstrap 95% lower bound > 0;
- at least 3/5 individual bats have positive within-bat improvement.

Minimal sufficient interaction rank:
- 1 if rank 1 is supported;
- otherwise 2 if rank 2 is supported;
- otherwise none.

Rank 2 cannot replace rank 1 merely because its point estimate is larger.

## Interpretation

### Rank 1 supported

A compact model is:

[
y_{ie}=mu+	heta_i+gamma_e+lambda_iphi_e+epsilon.
]

Each individual's cross-environment behaviour is then described by:
- a baseline personal coordinate (	heta_i);
- one reaction coefficient (lambda_i).

### Rank 2 supported but rank 1 not

The interaction remains low-dimensional but needs two personal reaction coordinates.

### Neither supported

The residual individual × environment structure is not predictively compressible by a rank-1 or rank-2 linear reaction architecture in this archive.

That is not evidence of infinite mathematical dimensionality; nonlinear structure and limited data remain alternatives.

## Claim ceiling

This is matrix interaction compression, not identification of physical environment variables.

The latent environment scores (phi_e) are not automatically obstacle complexity, sensory uncertainty, or learning state.
