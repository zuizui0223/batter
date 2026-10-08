# Executed synthetic four-feature target-blind stress audit v1

**STATUS: COMPLETED SYNTHETIC METHOD CHECK — NO EMPIRICAL BAT REANALYSIS.**
Date 2026-10-08. This note **does not** modify PR #79's original target-blind empirical result (`G=+0.443714; p=0.0003`), its source, its code or frozen JAE work.

## Execution receipt

- [Successful GitHub Actions run 37783687618](https://github.com/zuizui0223/batter/actions/runs/37783687618)
- Job: `113332887465`
- Tested head: `10827eafc6d14a5aa008d571a41f886c8f0a688e`.
- Code: `rhino_four_feature_synthetic_null_v1.py --self-test`.
- Pure standard-library Python 3.13 with **NO Figshare/GitHub API fetch, trajectory XYZ, physiological values or bat outcomes**.
- Four independent normally generated correlated movement feature coordinates (`rho=0.6`). No bat mean tendency, personal history or true bat-by-environment response is injected.

## Precisely emulated aspects

- Five named fictional bats A–E, 7 labelled obstacle environments.
- Number of nonempty bat×environment cells **25**, per-bat environment counts A=5/B=4/C=5/D=6/E=5.
- Total **45** fictitious trial-file entries. Bat/environment cell membership and which cells have two entries are **SCHEMATIC, not the original source arrangement**.
- For compact, controlled variance, replicated fictitious raw entries within each bat×environment cell are set **exactly equal**; this is *not* a naturalistic model of flight-trial variability.
- Four-feature held-out-environment training-only means and sample SDs recomputed in each fold using all non-test-environment fictitious trial entries; personal scalar from four feature z-scores, bat-specific training history predictions, zero baseline, bat- and target-balanced G.
- Original algorithm's **within-environment relabelling of whole bat×environment centroids**, 199 pseudo-random permutations per generated archive (p=(1+exceed)/200).
- One-sided empirical rejection at thresholds 0.05 and 0.01.

## Executed outcomes

| Synthetic null generation | N simulated archives | False rejection at p<=.05 | False rejection at p<=.01 | Mean null G |
|---|---:|---:|---:|---:|
| All bat-specific noise SD = 1.0 | 280 | **13/280 = 4.64%** | 6/280 = 2.14% | −0.135100 |
| Bat-specific SD = [0.3,0.6,1.2,2.5,5] | 280 | **34/280 = 12.14%** | 11/280 = 3.93% | −0.139659 |

The 0.01 results have very few tail counts and only 199 null permutations; do **not** infer exact extreme-tail calibration from these fractions. Under the nominal 5% gate, strong individual-specific dispersion under **zero individual mean** raises false rejection materially. This is a simulation-specific Type-I error, not a measured rate of invalid scientific conclusions in the published literature.

## Why the inference fails

The label-shuffle reference is exact only when the features/centroids assigned to bats within each environment are exchangeable under the **null of no stable personal mean signal**. A stable individual noise amplitude means a low-variance individual's 4D centroid and a high-variance individual's centroid are **not identically distributed**, even though both have mean zero and no cross-environment stable mean. Permuting their labels creates artificial personal histories with incompatible nuisance variances. The resulting conditional reference does not guarantee its stated false-positive rate.

This issue is about inference/reference **calibration**, not the numerical value of G. Both simulated null scenarios have *negative average G*, and this does not overturn the empirically observed positive +0.443714 gain.

## Boundaries, especially PR #79

- This synthetic test **does not** reproduce the original exact bat×environment occupancy matrix, nor real within-cell trial replication, actual four-feature covariance or observed bat SDs, true source measurement error, same-animal physiology, or the original full 9,999-permutation tail.
- The original `p=.0003` is still the executable numerical result **conditional on label exchangeability**, not an independently validated heteroscedasticity-robust p-value. We have no basis to multiply it by a simulated inflation factor or call it false.
- The actual five-bat cluster-bootstrap 95% interval for blind prediction gain `[-0.148938,+1.130310]` includes zero; cross-population generality remains unresolved independent of this new risk.
- Previously derived **known-sigma Gaussian oracle** restores null calibration for a simpler repeated-contrast estimator under externally known independent Gaussian noise, but is **not a ready replacement** for this 4-feature leave-environment-out gain.
- Source eligibility remains `STOP` for independently replicated bat×controlled challenge×occasion data.

## Scientific verdict

**CONFIRMED_SYNTHETIC_EXCHANGEABILITY_VULNERABILITY_IN_FOUR_FEATURE_FORECAST_ANALOG.**

**NOT CONFIRMED: ACTUAL_PR79_TYPE_I_ERROR, NO_REAL_INDIVIDUALITY, BAT_MECHANISM, ADAPTIVE_GAIN.**

Research-program consequence: avoid new causal individuality claims from shuffled labels alone unless a **predeclared, source-supported heteroscedastic null** has been validated under the relevant bat/configuration/measurement structure. Seek independent across-occasion matched contexts rather than more feature scans on the same 45 trajectories.
