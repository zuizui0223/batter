# Exact two-number predictability threshold for individual flight-intensity scalars

## Status

Exact algebraic interpretation of an already-opened held-out result; **not a new biological hypothesis test**.

## Setup

For bat i, observe n distinct configuration-wise flight-intensity centroids `y_1,...,y_n`, with:

- `theta_i` = their arithmetic mean;
- `s_i²` = their sample variance (denominator n−1);
- leave-one-environment-out prediction of target `y_e` by the mean of other contexts.

For the no-personal-information baseline, predict the within-environment standardized reference 0.

## Exact result

The two cross-environment MSEs satisfy:

\[
MSE_{\rm self,i}=\frac{n_i}{n_i-1}s_i^2,
\]

\[
MSE_{0,i}=\theta_i^2+\frac{n_i-1}{n_i}s_i^2.
\]

Hence the personal forecast is better than zero **if and only if**:

\[
\boxed{
\theta_i^2>
\frac{2n_i-1}{n_i(n_i-1)}s_i^2
}.
\]

The observable held-out gain is exactly:

\[
\boxed{G_i=\theta_i^2-c(n_i)s_i^2,\quad
c(n)=\frac{2n-1}{n(n-1)}}.
\]

The scalar coordinate alone is insufficient to specify its *predictive reliability*; one additionally needs its environment-dependent spread and observed number of configurations.

## Exact application to the five bats

| bat | n | theta² | c(n) s² | G_i | self history vs zero |
|---|---:|---:|---:|---:|---|
| A | 5 | 1.144645 | 0.042153 | +1.102492 | improves |
| B | 4 | 0.030497 | 0.217339 | −0.186842 | worsens |
| C | 5 | 0.091686 | 0.311410 | −0.219724 | worsens |
| D | 6 | 0.624759 | 0.009546 | +0.615213 | improves |
| E | 5 | 0.224194 | 0.069975 | +0.154219 | improves |

Numerical verification against the authoritative held-out result is accurate to floating-point error below 3e−16.

## Interpretation

This identity clarifies why a stable species-level scalar identity can coexist with weak or negative absolute predictions for some individuals.

- A and D have large mean separation from the standardized cohort reference relative to their environmental variation.
- E has moderate separation and variance.
- B and C are near the cohort reference and have comparatively large contextual variation, so a per-bat sample mean is a poorer forecast than zero over their observed configurations.

At the **summary-prediction level**, the observed distinction between predictable and unpredictable bats is fully described by \((\theta_i,s_i,n_i)\).

## Claim ceiling

This is an **identity of the estimator**, not proof that bat flight dynamics or environmental plasticity is fundamentally governed by two parameters. The estimated spread `s_i` includes contextual response, sampling noise, unequal trial counts and within-environment reference-composition effects.

The next biological question is whether \((\theta_i,s_i)\) themselves replicate in **new, matched obstacle configurations** (same identified bats, balanced co-observation, and fixed feature normalization).

The identity cannot establish asymptotic convergence, a unique differential equation, learning, or genetic control.
