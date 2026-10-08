# Synthetic reliability and heteroscedastic false-positive calibration — executed receipt v2

**No biological effects were tested.** Only fabricated cross-session bat-response arrays and simulation null distributions were examined. This is an executed software/statistical method validation, NOT a *Rhinolophus* result.

## Exact execution provenance

- [Official GitHub Actions run 37781644666](https://github.com/zuizui0223/batter/actions/runs/37781644666): `completed/success`.
- Code SHA at run: `a22376aaa12db36cfbf67c568798a7de3cf0905a`.
- Job: `113325933010`, Python 3.13.
- Script: `prospective/reaction_norm_gate/replicated_contrast_synthetic_v1.py --self-test`.
- All synthetic invariance checks and explicit empty-real-source failure guard passed.

## Source-free results

### Five-bat, 1200-replicate × 2 null simulations

We compared exact `5! = 120` permutations of individual S2 labels at nominal one-sided `p <= .05` under **no true repeatable bat challenge-response effect**.

| Simulated condition | Individual noise standard deviations | Null tests | False positives |
|:--|:--|--:|--:|
| Equal independent noise | [1,1,1,1,1] | 1200 | **4.33%** (52/1200) |
| Unequal bat-specific independent noise | [0.3,0.6,1.2,2.5,5] | 1200 | **13.08%** (157/1200) |

The exact permutation conditional reference is not calibrated under this heterogeneous-noise null, despite null expected cross-occasion covariance being zero. These parameter values are illustrative and not measured from any bat. A separately implemented JavaScript 5000-replicate check gave 4.84% (equal noise) versus 10.48% (unequal), with other unequal-noise seeds 10.44–11.54%; differences are expected Monte Carlo variation.

**Scientific limitation:** an observation of `p<.05` from arbitrary bat label permutation CANNOT be treated as confirmatory identity-specific plasticity without verifying label exchangeability or calibrating a prespecified heteroscedastic null. We have **not** implemented/validated a real-data null fitted with bat-specific noise using independent measurements, so this analysis route remains STOP for biological inference.

### Four-occasion synthetic training/test illustration

- All bats share the same challenge response after removing session shifts: held-out gain = **0**, covariance = **0**.
- Perfectly reproducible *fictional* personal challenge response: held-out gain = **+4.666667**, covariance = **+5.6**.
- A permanently assigned, bat-correlated device bias produces **exactly the same observables**, so the positive synthetic gain alone cannot distinguish biology from apparatus.
- Switching the sign of fictional device assignments in the held-out occasions: gain = **−14.0**, covariance = **−5.6**.

These are deterministic constructed controls, not effect estimates or achieved statistical power in actual animals.

## External-source audit

The authors' public source [Nishiumi et al. 2024](https://github.com/Nozomi-Nishiumi/target_tracking_strategy_in_bats) contains 18 experimental labels, 7 bat IDs and recorded dates, but the [categorical-only source gate](PUBLIC_2024_BAT_MOTH_CATEGORICAL_SOURCE_GATE_V1.md) finds a maximum of 3 distinct recorded dates for any bat and no source-verified repeated within-occasion matched challenge/reference geometry. **STOP_NOT_ELIGIBLE** for this particular prospective assay. No numeric flight or ultrasound outcomes were opened.

## Final state

- Code mechanical testing: **PASS**.
- Synthetic false-positive control using **unadjusted label permutation: FAIL** under heteroscedastic individual noise.
- Proposed experimental eligibility and future inference: **HOLD** pending independent bat×challenge×occasion data and a separately validated heteroscedastic reference.
- Bat ecological mechanism, plasticity, learning, adaptive payoff, or field 3D-niche mediation: **NOT ESTABLISHED**.

## V3 independent-variance oracle execution (separate code run)

- [Official GitHub Actions run 37782318423](https://github.com/zuizui0223/batter/actions/runs/37782318423): **completed/success**; job `113328227439`; code commit `46bb83d4665adb90194ebd936e96d409c6a22b21`.
- Added known-pilot-`sigma_i` Gaussian one-sided conditional reference (mathematical derivation in `KNOWN_SIGMA_GAUSSIAN_NULL_ORACLE_V3.md`).
- Each case is still entirely **synthetic**, with 1,200 null replications, 5 fictional bats, Gaussian independent errors and truly known per-bat test-error SDs.

| Null data generation | Unadjusted bat-label permutation rejection | Known independent-sigma Gaussian oracle rejection |
|---|---:|---:|
| Equal SD `[1,1,1,1,1]` | **4.33%** | **4.67%** |
| Unequal SD `[0.3,0.6,1.2,2.5,5]` | **13.08%** | **4.83%** |

**Result:** a Gaussian conditional reference with truly independently known individual variances restores nominal null calibration in this particular construction. It **does not** supply those variances for real bats, account for non-Gaussian distributions, or remove persistent device/context confounds, and it is **not** a calibrated replacement null for the 45-trajectory, four-feature #79 leave-one-configuration-out estimator. `STOP_REAL_DATA_TEST` remains in force.
