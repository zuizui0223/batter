# Exact paired-assignment Fisher sharp-null synthetic audit — executed V5

**Evidence tier:** Design-based mathematics and explicitly fabricated observations ONLY. No biological bat records; no new actual treatment or flight result. The existing five-bat Rhino/JAE/BE results are unchanged.

## Frozen prior contract and reproducibility

- Pre-outcome design contract: `RANDOMIZATION_FIRST_PAIRED_3D_CAUSAL_CONTRACT_V5.md`, committed `390d46f0238adcc15d0f9805349d721d0a189203` before synthetic output.
- Source-free implementation: `paired_assignment_randomization_synthetic_v5.py` (standard-library Python 3.13).
- Initial test `37792016278` was successful but revealed a **test-code counterexample bug**: it reused a no-effect reference after injecting a common effect and erroneously returned p=0. This was fixed by reconstructing observed challenge/control slot outcomes and recomputing Fisher's sharp-null imputation **before this authoritative run**, without changing the no-effect calibrations.
- **Authoritative** [GitHub Actions run 37792159876](https://github.com/zuizui0223/batter/actions/runs/37792159876) completed **SUCCESS**, head `cb518bf4d1ecbfa113d08266ad9ee5d92edbf878`, job `113362107653`. Compile, enumeration, mathematical invariance and absent-real-source failure guard all passed.

## Synthetic design and exact calculation

- **Five fictional bats**, each with 3 fictional independent pair blocks: **15** matched bat×session pairs.
- Each pair has two potential independent opportunity slots and a genuinely fair coin allocation of whether challenge occurs in first or second slot.
- Under the **sharp null** Y_isj(1)=Y_isj(0) for every bat/session/slot, each outcome stays fixed under treatment reallocation.
- Individual baseline amplitudes, night-specific context baselines, and fixed unequal potential noise/slot differences were arbitrary; **no assumption of exchangeable bats or normally distributed equal errors** is needed for the assigned randomization null.
- Entire legal randomization space: `2^15=32768` allocations, **fully enumerated**, without Monte Carlo approximation.
- Statistic: equally bat- and session-weighted signed treatment-minus-control within-pair contrast; one-sided randomization tail including all ties.

## Authoritative exact design-null error rates

| Nominal alpha | Rejections / 32768 equally likely assignments | Exact conditional false-rejection proportion |
|:--|--:|--:|
| 0.01 | **316/32768** | **0.964355%** |
| 0.05 | **1608/32768** | **4.907227%** |
| 0.10 | **3202/32768** | **9.771729%** |

All are <= the corresponding nominal alpha as required by Fisher's sharp-null randomization argument. The calculation is for one **fixed synthetic no-effect potential-outcome schedule** with *all* possible randomized assignments. It is not a test of any bat source.

The arbitrary additive personal intercept and shared occasion context mean were both perturbed by very large fixed values, leaving all signed slot contrasts, statistics and reference support unchanged. Thus a genuinely randomized *treatment* comparison does not require prior identification of those means in this particular paired design.

## Counterexample preventing an ecological overclaim

Synthetic intervention with an **identical constant effect +100 for every bat and block**, i.e., literally **ZERO individual treatment-effect heterogeneity**, generated `p = 1/32768 = 0.000030517578125` against the no-effect sharp null when the proper observed-outcome-imputed reference was used. This is a deliberate illustration, not biological evidence.

**Consequently, a significant causal opportunity main effect is not proof of individual-specific response rules.** A separately repeated/cross-validated reaction-norm estimand, multiple independent bat/session blocks, calibrated sensor/noise structure and task performance measures would still be necessary. Identical task success differences from route opportunity do not imply route choice was causally mediated by skill, learning or spatial overlap.

## Remaining constraints / decision

1. **Actual random assignment** is indispensable. The earlier 45 *Rhinolophus* trajectories were observational across configurations and cannot be retroactively labeled randomized challenge/control pairs. No V5 p-value can be assigned to those bats.
2. Sharp no-effect is **not** the weak null of average zero and not the null of no individual-effect heterogeneity; those require distinct inferential machinery and, in particular, more independent subject-level replication.
3. Matched slots need opportunity geometry, acoustic signal path, target reward, latency, physiological carryover, context order and apparatus conditions verified to be comparable. Prior #93 physical bench gate remains essential if route availability and masking change the acoustic path.
4. Short-term route persistence may arise from inertia and no independent learning or adaptive benefit can be inferred without separately manipulated history and functional endpoints.
5. Five fictional bats and 3 artificial occasions are sufficient only to illustrate the exact proof. They do **not** establish an empirical N/power threshold for real reaction norms or a feasible bat protocol. Published studies would require ethics, site calibration and adequately designed new independently collected data, none supplied.

**Conclusion:** `PASS_EXACT_DESIGN_BASED_SHARP_NULL_SYNTHETIC` with a strict `NO_BIOLOGICAL_EFFECT_ESTIMATED` and `INDIVIDUAL_RESPONSE_CAUSAL_MECHANISM_UNRESOLVED` firewall. For this source-constrained programme, close additional same-source randomization substitutions here.
