# Conditional independent-sigma Gaussian reference: derived oracle and limitations v3

## Evidence tier
**Analytic derivation + synthetic null calibration only.** This is not an estimated bat-level effect and not an implemented field-ready heteroscedastic procedure. Supersedes neither #79 nor the need for crossed 3D flight data.

## Problem
For the simple repeated-contrast statistic
`C = Cov_i(x_i, y_i)`, where x_i is a training-night challenge contrast and y_i is the independent held-out test-night challenge contrast, raw bat-identity permutations require exchangeability across biological bats. Under H0 where x and y are independent **but each bat has a different stable noise variance**, this exchangeability fails. The executed synthetic negative control in Actions 37781644666 found 13.08% rather than nominal 5% false positives under the one specified heterogeneous-noise setting.

## Conditional Gaussian oracle

Define `a_i = x_i - mean(x)`. Under the **strong and externally verified** H0 assumptions:

- all test occasions are genuinely independent of training data conditional on pilot calibration;
- `y_i` are independent across bats, with **zero true individual test response after shared-occasion effects**;
- `Var(y_i) = sigma_i²` is known from a **separate source not sharing the held-out observations**;
- errors are Gaussian and there are no persistent assigned-device, bat-specific history or order effects;

then the cross-session numerator `T = sum_i a_i y_i` obeys:

```text
E[T | x] = 0
Var[T | x] = sum_i a_i² sigma_i²
Z = T / sqrt(sum_i a_i² sigma_i²) | x  ~  N(0,1).
```

Centering all test `y_i` again leaves T unchanged because `sum_i a_i=0`. Thus an exactly calibrated *conditional* one-sided test is `p = 1-Phi(Z)` with externally known individual noise variances. The statistical model is more constrained than the label-shuffle null; its validity is **assumption-dependent**, not distribution-free.

For a mean of `m` independent held-out occasions, `sigma_i²` must represent the actual variance of that mean, including independent occasion noise and any within-bat/session correlation. Do not simply divide by m when occasions are dependent.

## Properly narrowed scientific interpretation

- A demonstration where the known-sigma reference restores nominal size is evidence of a **remediable statistical calibration problem under an oracle Gaussian model**, not a solution to real-world individual effect identifiability.
- In practice, `sigma_i` is usually unknown and can differ by configuration, sensor, period or bat. Estimating it from the two test responses and pretending it was fixed is circular and will invalidate this exact reference. A future fit needs independent pilot replication, explicit variance-estimation uncertainty and fresh simulation validation under realistic deviations.
- A persistent device bias or stable bat×session confound can produce strongly positive C even with perfectly calibrated independent *noise*; it violates the structural mean-zero assumption and must be solved by randomization, crossover and external measurement.
- Even a credible statistically repeatable bat-specific reaction norm cannot establish acquired skill, ecological reward or wild 3D-niche mediation. All require separate independently observed outcomes and causal/external evidence.

## Code status
`replicated_contrast_synthetic_v1.py` includes `independent_sigma_gaussian_p` and side-by-side equal- and unequal-noise null calibrations. The independent verification is synthetic; do not interpret it as enabling any source reanalysis while source-structure gate and independent sigma estimation remain unresolved.
