# Rhino theta convergence result v1 — deterministic reconstruction

## Status

**POST-PRIMARY MATHEMATICAL-STRUCTURE DIAGNOSTIC.**

The convergence contract was frozen before this learning-curve calculation was opened.

This result was deterministically reconstructed from the authoritative FlightIntensity theta-summary artifact:

- source workflow run: **37211528747**
- source artifact: **11306753000**
- source artifact file: `FLIGHT_INTENSITY_THETA_SUMMARY_V1.json`
- convergence contract branch: `post-freeze/rhino-theta-convergence-v1`

The source artifact contains the exact bat × environment scalar centroids needed by the frozen convergence estimator.

## Individual scalar positions

The transferable scalar is:

[
FlightIntensity =
[z(v_{med})+z(v_{90})+z(|v_z|_{med})+z(|v_z|_{90})]/4.
]

Equal-environment personal positions:

| bat | theta_i | between-environment SD | environments |
|---|---:|---:|---:|
| A | **+1.0699** | 0.3061 | 5 |
| C | **+0.3028** | 0.8319 | 5 |
| B | **+0.1746** | 0.6104 | 4 |
| E | **-0.4735** | 0.3943 | 5 |
| D | **-0.7904** | 0.1613 | 6 |

Descriptive order:

[
A > C approx B > E > D.
]

The B–C separation is a near-tie and is not stable environment by environment.

## Convergence learning curve

Targets: 25 bat × environment observations from all five bats.  
Every target has at least three independent non-target environments.

For each target, theta was estimated from every possible subset of 1, 2, or 3 training environments and used to predict the held-out environment.

| training environments | MSE | CV R² vs zero baseline | mean subset-theta SD |
|---|---:|---:|---:|
| 1 | **0.5359** | **0.1547** | **0.3823** |
| 2 | **0.4019** | **0.3660** | **0.2145** |
| 3 | **0.3573** | **0.4364** | **0.0985** |
| all available | **0.3409** | **0.4623** | — |

Thus estimator spread collapses strongly as independent environments accumulate.

## Frozen convergence contrast

[
Delta_{1	o3}=MSE_1-MSE_3=+0.1786.
]

Cluster bootstrap over biological bats:

- 95% CI: **[+0.0527, +0.3336]**.

So the reduction in held-out prediction error from one to three training environments is supported under the frozen rule.

## Distance to the full-training estimator

Frozen fraction-to-full statistic:

[
1-rac{MSE_m-MSE_{full}}{MSE_1-MSE_{full}}.
]

Results:

- 2 environments: **0.6870**, bootstrap 95% CI **[0.6609, 0.7360]**
- 3 environments: **0.9160**, bootstrap 95% CI **[0.8811, 0.9814]**

The frozen rapid-convergence threshold was 0.80.

Therefore three training environments recover about **91.6%** of the reducible gap between a one-environment estimate and the full-training estimate.

Verdict:

**FINITE_SCALAR_RAPID_CONVERGENCE**

## Individual convergence

Fraction of the one-environment-to-full gap recovered by three environments:

- A: 0.889
- B: 1.000
- C: 0.889
- D: 0.833
- E: 0.889

The scalar is not equally predictive in absolute terms for every bat. B and C show substantial environment-dependent deviation around their personal mean, whereas A and D are much more stable. Thus the result is not "each bat is a constant."

The supported structure is instead:

[
y_{i,e}=	heta_i+h_{i,e}+epsilon_{i,e},
]

where (	heta_i) is a recoverable personal scalar and (h_{i,e}) is an environment/task-specific deviation.

## Relation to latent dimensionality

The separate frozen dimensionality diagnostic already showed:

- unsupervised training-only PCA: **minimal sufficient d = 1**, K = +0.9578, 5/5 positive, p = 0.0006;
- supervised training-only identity subspace: **minimal sufficient d = 1**, K = +0.8848, 5/5 positive, p = 0.0021;
- full 8-D K = +0.9436.

One PC explains only about **46.7% of total behavioural variance**, yet is sufficient for cross-configuration individual identity.

Thus individual identity is substantially lower dimensional than total trajectory variation.

## Mathematical interpretation

For this *R. nippon* system, the strongest current model is not an irreducibly high-dimensional or non-convergent trajectory fingerprint.

A compact representation is:

[
mathbf{x}_{i,e,t}
=
oldsymbol{mu}_e
+
	heta_imathbf{v}
+
mathbf{h}_{i,e}
+
oldsymbol{epsilon}_{i,e,t}.
]

- (oldsymbol{mu}_e): task/environment;
- (	heta_i): stable one-dimensional personal policy position;
- (mathbf{v}): shared movement-intensity direction;
- (mathbf{h}_{i,e}): task-specific personal realization;
- (epsilon): trial-scale variation.

This does **not** imply that complete XYZ trajectories are one-dimensional. It says that the portable individual-difference component is approximately one-dimensional in the measured movement-policy space.

## Claim ceiling

This result supports a finite, rapidly estimable scalar personal parameter over the observed obstacle configurations.

It does not establish:
- a unique differential equation for flight;
- a neural or genetic scalar;
- lifetime stationarity;
- universality across bat species;
- deterministic prediction of the next XYZ coordinate.
