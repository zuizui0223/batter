# Rhino context-affine theta — deterministic reconstruction result v1

## Status

Deterministic reconstruction from the already-authoritative bat × environment FlightIntensity centroids, using the frozen `CONTEXT_AFFINE_THETA_CONTRACT_V1.md`.

Dedicated workflow run 37640321138 was still queued at the time of reconstruction.

## Target universe

Frozen structural gate:
- Env1–Env4 only;
- 17 held-out bat × environment targets.

## Result

Equal target within bat, then equal bat MSE:

- environment-only peer mean: **1.1727**
- portable theta only: **0.3216**
- context-affine theta: **1.3048**

Primary gains:

[
G_{env}=MSE_{env}-MSE_{affine}=-0.1322
]

bat-cluster bootstrap 95% CI:

[
[-1.0046,+0.5699].
]

Positive bats: **3/5**.

[
G_{theta}=MSE_{theta}-MSE_{affine}=-0.9832
]

bootstrap 95% CI:

[
[-2.4045,-0.1832].
]

Positive bats: **0/5**.

Verdict:

**UNSUPPORTED_CONTEXT_AFFINE_THETA**.

## Interpretation

Using peer bats in the target environment to estimate a shared affine expression transform

[
y_{ie}=gamma_e+alpha_e	heta_i+epsilon
]

does not improve held-out prediction. It is substantially worse than simply carrying the focal bat's training-only theta into the target environment.

Therefore the observed individual × environment deviations are not well represented by one common environment-specific rescaling of the personal axis.

This strengthens the distinction:

- (	heta_i): portable low-dimensional personal component;
- (h_{ie}): context-specific realization not explained by a shared affine transform.
