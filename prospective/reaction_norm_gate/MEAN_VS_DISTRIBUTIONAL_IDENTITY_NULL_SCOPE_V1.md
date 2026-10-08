# Critical null-scope correction: mean policy versus full-distribution individuality

**Scientific scope:** mathematical interpretation audit only; no new bat outcomes opened or reclassified.

The earlier "12.14% false positives at nominal 5%" simulation uses a **specific mean-identity null**:

```
H0_mean: for every bat i and configuration e,
         E[Y_ie | e, i] = mu_e,
         but Var(Y_ie | e, i) may differ among bats.
```

Under this H0_mean, the simulation generates **zero stable individual mean**, but stable heteroscedastic `sigma_i`. The *null being scientifically tested* is absence of a repeatable **mean flight-intensity shift**. Bat-label permutations do not preserve this null, so their rejection probability can exceed 5%. This is a calibration failure **for a mean-policy claim**.

However, a *stronger and different null* is

```
H0_exchangeability: the entire conditional distribution
                    Law(Y_ie | e, i) is identical across bats.
```

Under H0_exchangeability, bat-specific sigma differences ARE genuine persistent differences in the conditional distribution. Our unequal-sigma simulator does **not** satisfy H0_exchangeability. Thus rejecting a valid test of *full exchangeability* under this data generator would NOT necessarily be a false positive. We must never say "there is no individuality of any kind" merely because the means are zero. Variance-specific individuality might be biological (or measurement/quality differences), and a mean-oriented personal-history predictor may respond to it in a nontrivial way.

## Why this matters for the two bat-programme endpoints

- PR #79 target-blind **scalar MSE gain** is an *absolute future-forecasting* statistic. Its observed gain is +0.443714 and the original within-configuration label permutation gives p=.0003 under exchangeable-label reference. The observed gain is unchanged. The simulation documents that an exchangeable-label null is **not calibrated to H0_mean with arbitrary bat-specific noise variance**. It does **not** refute the possibility of a full-distribution individuality test or automatically undo the original nominal exchangeability test.
- The field JAE 3D vertical-use shape result, and laboratory multidimensional cross-configuration correspondence primary, are **separate statistics/biological questions**. None is numerically reassessed by this 4-feature toy. Do not carry its 12.14% number over to their p-values.
- A prospective mechanistic claim ("the bat carries a stable *mean* flight-policy parameter theta_i") must distinguish (a) individual location, (b) individual scale/variance, (c) individual response slopes, and (d) device/measurement distribution differences.
- The whole-cell sign-flip oracle in `CELLWISE_SIGNFLIP_KNOWN_ENVIRONMENT_CONTRACT_V1.md` addresses H0_mean under known shared environmental centering, independent centrally symmetric whole-cell residuals; it **does not** test H0_exchangeability and cannot guarantee valid bat-wide policy conclusions without independent source calibration.

## Current statement authorized

> The mean-policy interpretation of conditional identity-label permutation can be anti-conservative under bat-specific heteroscedasticity. The same simulator may nevertheless contain genuine *variance* individuality. Existing realized personal-history forecasting remains a descriptive effect, with unconfirmed mean-specific inference across independent bats.

This is why the decisive next empirical measurement must independently estimate individual variance and sensor offsets, not just accumulate more bat label permutations.
