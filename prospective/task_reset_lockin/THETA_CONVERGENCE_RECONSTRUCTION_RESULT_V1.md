# Rhino theta convergence — deterministic reconstruction v1

## Provenance

This result reconstructs the frozen `THETA_CONVERGENCE_CONTRACT_V1.md` statistics from the already-authoritative bat × environment FlightIntensity centroids.

Source artifact:
- workflow run: **37211528747**
- artifact: **11306753000**
- artifact name: `rhino-flight-intensity-theta-summary-v1`

The source artifact contains the exact environment-level FlightIntensity centroids for bats A–E. No trajectory values, target outcomes, thresholds, or model choices were changed after the convergence contract was frozen.

The dedicated convergence workflow run 37620420211 was still queued when this deterministic reconstruction was made.

## Target support

- bats: **5**
- held-out bat × environment targets with >=3 other observed environments: **25**
- training subset sizes compared: **m = 1, 2, 3**
- all subsets of the available non-target environments were enumerated for each target

## Learning curve

Equal target-environment within bat, then equal bat aggregation:

| training environments m | held-out MSE | held-out R² vs zero baseline | mean subset-estimate SD |
|---:|---:|---:|---:|
| 1 | **0.5359** | **0.1547** | **0.3823** |
| 2 | **0.4019** | **0.3660** | **0.2145** |
| 3 | **0.3573** | **0.4364** | **0.0985** |
| all non-target environments | **0.3409** | **0.4623** | — |

Thus prediction error decreases monotonically as independent environments are added.

Primary convergence contrast:

[
MSE_1 - MSE_3 = mathbf{+0.17864}.
]

Bat-cluster bootstrap, B=9,999, seed=20261007601:

- 95% CI: **[+0.05266, +0.33357]**

Therefore the frozen positive convergence criterion is supported.

## Fraction of finite-data asymptote recovered

Using the full non-target-environment estimate as the archive's lowest-variance finite-data reference:

- m=2: **0.6870**, bootstrap 95% CI **[0.6609, 0.7360]**
- m=3: **0.9160**, bootstrap 95% CI **[0.8811, 0.9814]**

The frozen descriptive rapid-convergence threshold was 0.80.

Therefore:

> **three independent environments recover about 92% of the improvement from the one-environment estimate toward the full-training scalar estimate.**

## Parameter-estimate stabilization

Mean SD of subset-based theta estimates:

- m=1: **0.3823**
- m=2: **0.2145**
- m=3: **0.0985**

This is a ~74% reduction in estimator spread from one to three environments.

## Interpretation

Together with the already-opened dimensionality and calibration results:

1. one latent linear dimension is sufficient for held-out cross-configuration individual identity;
2. a transparent FlightIntensity scalar captures a substantial fraction of that identity;
3. pairwise individual ordering is stable across configurations;
4. held-out pairwise magnitude calibration is positive;
5. and now the scalar estimate itself shows a rapidly stabilizing learning curve as more independent environments are observed.

This is substantially more consistent with an **estimable finite personal parameter** than with an irreducibly high-dimensional or non-convergent individual fingerprint.

A compact descriptive representation is:

[
x_{i,e,t} = mu_e + 	heta_i v + h_{i,e} + epsilon_{i,e,t},
]

where (	heta_i) is the portable low-dimensional component and (h_{i,e}) captures environment-specific realization.

## Relation to the “pi” analogy

This result argues against the strong version of the analogy.

The difficulty is not that each individual requires an endlessly expanding list of coefficients.

For this *Rhinolophus nippon* system, the observed cross-environment individual component is compatible with a **one-dimensional parameter whose estimate rapidly stabilizes with repeated independent environments**.

What remains non-convergent at the trajectory level can arise from environment-specific route realization and trial-scale stochasticity even when the personal parameter itself is low-dimensional.

## Ceiling

This does not establish:
- a unique equation of motion;
- lifetime stationarity of theta;
- a neural/physiological scalar;
- universality across bats;
- that every aspect of individual behaviour is one-dimensional.

It establishes a much narrower but strong mathematical statement:

> **the transferable individual component measured here behaves like a finite, low-dimensional, recoverable parameter.**


## Individual-level convergence

The population-level learning curve is not driven by one or two bats.

Held-out MSE by bat:

| bat | m=1 | m=2 | m=3 | full | fraction to full at m=3 |
|---|---:|---:|---:|---:|---:|
| A | 0.1873 | 0.1405 | 0.1249 | 0.1171 | 0.889 |
| B | 0.7452 | 0.5589 | 0.4968 | 0.4968 | 1.000 |
| C | 1.3840 | 1.0380 | 0.9227 | 0.8650 | 0.889 |
| D | 0.0521 | 0.0391 | 0.0347 | 0.0321 | 0.833 |
| E | 0.3110 | 0.2333 | 0.2073 | 0.1943 | 0.889 |

All five individuals show monotonic MSE improvement from one to two to three training environments.

Thus the convergence pattern is individual-level, not merely an aggregate effect.

The individuals differ mainly in **how noisy their environment-specific expression is**, not in whether the scalar estimate converges:
- A and D are comparatively stable;
- B and C show larger environment-to-environment variability;
- nevertheless all five move toward their full-training estimate as independent environments accumulate.

This supports a useful distinction:

[
\theta_i = \text{stable personal coordinate}
]

while

[
y_{ie}-\theta_i = \text{environment-specific expression / residual}.
]

The residual variance differs among individuals even when the portable parameter is one-dimensional.
