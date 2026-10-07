# Finite personal core + context-specific realization synthesis v1

## Status

Post-primary mathematical/ecological synthesis. This document combines already-opened analyses across the current public bat archives. It does not convert post-primary diagnostics into confirmatory tests.

## Central question

Can individual bat flight differences be represented by a finite mathematical parameter set, or does every new context require an indefinitely expanding individual-specific description?

## 1. A finite portable personal component is supported in Rhinolophus nippon

Across seven obstacle configurations, the portable movement-policy component is highly compressible.

### One-dimensional sufficiency

Training-only PCA:
- minimal sufficient dimension: **1**
- K = **+0.95785**
- 5/5 bats positive
- p = **0.0006**

Training-only supervised identity subspace:
- minimal sufficient dimension: **1**
- K = **+0.88483**
- 5/5 positive
- p = **0.0021**

The full eight-dimensional endpoint does not outperform the one-dimensional identity representation.

### Interpretable scalar

A transparent FlightIntensity scalar based on total and vertical speed magnitude is supported:
- K = **+0.49656**
- 5/5 positive
- p = **0.0003**

Individual scalar coordinates:

- A: +1.0699
- C: +0.3028
- B: +0.1746
- E: -0.4735
- D: -0.7904

### Rapid estimation convergence

As independent training environments increase:

| environments | held-out MSE |
|---:|---:|
| 1 | 0.5359 |
| 2 | 0.4019 |
| 3 | 0.3573 |
| full non-target set | 0.3409 |

Three environments recover **91.6%** [88.1%, 98.1%] of the finite-data improvement from the one-environment estimate toward the full estimator.

The one-to-three-environment MSE improvement is:
+0.17864, bootstrap 95% CI [+0.05266,+0.33357].

Thus the portable individual component behaves like an estimable finite scalar parameter.

## 2. A single fixed scalar is not the complete realized trajectory rule

The stable scalar predicts average cross-environment differences but does not perfectly preserve pair ordering.

Held-out pairwise magnitude calibration is positive:
- beta = 1.0314;
- r = 0.5548;
- equal-pair sign accuracy = 0.8217.

However, a stricter margin-reliability test fails:
- rho(|predicted difference|, held-out ordering correctness) = +0.2477;
- p = 0.0963.

Large-margin reversals still occur in some individual × environment combinations.

Therefore:

[
individual identity 
eq exact fixed ordering in every context.
]

## 3. A personal noise-scale parameter does not solve the residual

Test:

[
y_{ie}=	heta_i+sigma_i z_{ie}
]

versus theta plus common noise.

Held-out probabilistic gain of individual sigma:
- mean log-score gain = **-0.0782**
- bootstrap 95% CI [-0.3944,+0.2379]
- positive bats = 2/5

Unsupported.

Thus individuals do not reduce cleanly to:
- a personal mean;
- plus a stable personal noise amplitude.

## 4. A shared context-specific affine transform does not solve it either

Test:

[
y_{ie}=gamma_e+alpha_e	heta_i+epsilon.
]

Using other bats in the target environment to estimate alpha and gamma:

- theta-only MSE = **0.3216**
- context-affine MSE = **1.3048**

Affine minus theta improvement:

[
MSE_{theta}-MSE_{affine}=-0.9832
]

bootstrap 95% CI [-2.4045,-0.1832].

Thus environment-specific deviations are not captured by applying the same affine transform to every individual's theta.

## 5. Unregularized low-rank individual × environment completion is not identifiable

The natural extension,

[
h_{ie}=lambda_iphi_e
]

or rank 2,

[
h_{ie}=lambda_{i1}phi_{e1}+lambda_{i2}phi_{e2},
]

was frozen and evaluated on the sparse 5 × 7 bat × environment matrix.

The unregularized matrix completion produces unstable missing-cell extrapolations, including extreme predictions despite low training SSE.

This is a numerical identifiability STOP, not a biological rejection of low-rank interaction.

The current archive is too sparse to identify that interaction without regularization, measured environment covariates, or denser crossing of the same individuals across configurations.

## 6. Independent learning data show stable personal information with plastic expression

In the independent Yamada naive-to-familiar dataset:

Overall personal speed-state persistence:
- K = +0.5277
- p = 0.0052
- 12/14 bats positive.

So learning does not simply overwrite individuality.

But condition-specific expression differs sharply descriptively.

Permeable / larger learning shift:
- alpha ≈ **0.002**
- p ≈ 0.498

Reflective / smaller learning shift:
- alpha ≈ **0.800**
- p ≈ 0.0022

Direct alpha contrast:
- delta alpha ≈ +0.798
- p = **0.0997**

Thus context-dependent expression is plausible but not yet statistically established as a between-condition effect.

## 7. Species contrast: Miniopterus does not show the same portable individual core

For *Miniopterus fuliginosus*:

Unsupervised PCA dimensionality scan:
- d = 1 through 8: **no supported dimension**

Training-only supervised identity subspace:
- d = 1 through 3: **no supported dimension**

Even though Miniopterus PC1 captures about 59% of overall behavioural variance, it does not carry stable cross-environment individual identity.

Therefore:

[
low-dimensional behaviour

eq
low-dimensional individuality.
]

The current contrast is:

[
Rhinolophus:
	ext{stable one-dimensional portable individual component}
]

versus

[
Miniopterus:
	ext{no detected portable linear individual component}.
]

This is not evidence that Miniopterus is infinite-dimensional; stronger plasticity, nonlinear individuality, or limited data remain alternatives.

## 8. Current minimum mathematical model

For *R. nippon*, the evidence is best summarized by:

[
oxed{
mathbf{x}_{i,e,t}
=
oldsymbol{mu}_{e,t}
+
	heta_imathbf{v}
+
mathbf{h}_{i,e,t}
+
oldsymbol{epsilon}_{i,e,t}
}
]

where:

- (	heta_i): finite, portable, approximately one-dimensional personal control coordinate;
- (mathbf v): common movement-intensity direction;
- (oldsymbol{mu}_{e,t}): common environment / learning operating point;
- (mathbf h_{i,e,t}): task-specific personal realization;
- (epsilon): trial-scale residual variation.

The first term that is truly individual and portable is low-dimensional and convergent.

The unresolved mathematical object is (h_{i,e,t}), not theta.

## 9. Answer to the “pi / non-convergent formula” hypothesis

The strongest version is not supported.

For *R. nippon*, the personal component does **not** require an indefinitely expanding coefficient list:
- d=1 is sufficient;
- scalar magnitude transfers;
- theta estimates stabilize rapidly with independent contexts.

The difficult part is that a low-dimensional personal parameter interacts with a context-specific internal/task state.

A closer analogy is therefore not pi.

It is a state-space system with a stable parameter and a changing latent state:

[
	heta_i=	ext{stable parameter},
]

[
h_{i,e,t}=	ext{context-dependent state}.
]

The realized trajectory may remain difficult to predict far into the future even when the personal parameter itself is finite and recoverable.

## 10. Current data ceiling

With the existing public Teshima matrix, the next unknown cannot be cleanly solved by adding more post-hoc linear dimensions.

To identify (h_{i,e,t}), the highest-value data are:

1. denser repeated crossing of the **same individuals × many environments**;
2. quantitative obstacle/environment descriptors;
3. known temporal reset/reconfiguration order;
4. repeated observations after reset to estimate re-formation of the task-specific state.

That would allow direct tests of whether:

[
h_{i,e,t}=f_i(E_e,history_t)
]

is itself a low-dimensional learned reaction norm.

## Bottom line

> **The portable individual difference is mathematically compressible and convergent; the unresolved complexity sits in context-specific realization, not in an infinite personal fingerprint.**
