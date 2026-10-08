# Audit of the alleged 92% convergence of personal theta

## What was previously claimed

The prior `THETA_CONVERGENCE_CONTRACT_V1.md` reported a training-subset learning curve with 3 environments recovering ~91.6% of the difference between m=1 and the full non-target-environment mean.

The workflow is reproducible. However, the interpretation **FINITE_SCALAR_RAPID_CONVERGENCE** is not warranted by this endpoint alone.

## Exact finite-population identity

For one held-out target `y`, let the `N` available training-environment centroids be `x_1,...,x_N`, and let `S^2` be their sample variance with denominator `N-1`.

Enumerate uniformly all training subsets of size `m`. Let `xbar_S` be the mean over one subset and `xbar` the full training mean.

Then, without any stochastic assumptions and for **arbitrary** training values,

```
E_subsets[(y - xbar_S)^2]
    = (y - xbar)^2 + (1/m - 1/N) S^2.
```

Proof: `E(xbar_S)=xbar`, the cross term is zero, and sampling without replacement gives `Var(xbar_S)=(1/m-1/N)S^2`.

Therefore,

```
MSE_1 - MSE_3 = (2/3) S^2 >= 0
```

for every target with N>=3.

The *sign* of the frozen `MSE_1-MSE_3` statistic was determined by sampling variance. It is positive whenever the training environment values vary, even if no persistent biological theta exists.

More importantly, the previously emphasized fraction toward the full training mean obeys

```
F_m = 1 - (N-m)/(m*(N-1))
```

independently of `y` and independently of whether the animal has a stable latent parameter.

At m=3 the observed individual fractions exactly match the identity:

| bat | available non-target environments N | mathematically forced F_3 | reported |
|---|---:|---:|---:|
| A | 4 | 0.88889 | 0.889 |
| B | 3 | 1.00000 | 1.000 |
| C | 4 | 0.88889 | 0.889 |
| D | 5 | 0.83333 | 0.833 |
| E | 4 | 0.88889 | 0.889 |

The pooled ~0.916 is an aggregation of these design-determined fractions with variance weights. Its bootstrap interval does not test genuine temporal or cross-environment stability.

## Corrected interpretation

- **Retain**: training-only cross-environment identity transfer, independent scalar pairwise calibration, and marginal positive held-out R² where tested.
- **Withdraw as independent evidence**: the claim that 91.6% proves a finite latent law or biological convergence.
- **Separate**: finite-dimensional linear *representation* from *identifiability* of a stationary, finite-dimensional generative law.
- **Stop**: interpreting a failure in Miniopterus as high/infinite dimensionality; matched-support positive controls show poor detection power under its sparse 19-trajectory panel.

The next frozen check uses label-disrupted individual histories as the null. This asks whether true cross-environment correspondence improves held-out scalar prediction beyond what averaging alone guarantees.

## Statistical caveat

The existing z-score transformations are calculated from all trajectories within the held-out obstacle environment. Those are label-free but transductive: the prediction is conditional on knowledge of the target environment's sample-level feature center and scale, not an unconditional deployment forecast into an entirely unobserved environment.

The new test retains those published preprocessing rules for comparability and labels its estimand accordingly.
