# Amendment v2: heteroscedastic label-null failure, 4-occasion evaluation, and sensor crossover

**Status:** prospective methodology; no new bat data accessed, no change to JAE, 45 Rhino observations, or the #79 audited empirical results. This amendment was written after discovering a **synthetic false-positive vulnerability** in the originally proposed exact bat-label correspondence test, and *before* any eligible new biological response data.

## Why we must not simply use p<.05 from the first two-occasion demonstration

The initial illustrative estimator `Cov_i(Delta[i,S1], Delta[i,S2])` has a valid zero **expectation** under independently repeated mean-zero individual expression noise (even with different individual variances). However, relabelling entire bat contrasts on S2 is a valid null-randomization procedure **only when labels are exchangeable under the specified null**. It is **NOT exchangeable** if independent bats have persistent, unequal session noise variances (heteroscedasticity).

Synthetic stress test using **five fictional bats** with no stable individual response:
- All bat residuals are independently Gaussian, mean zero, independent between occasions and conditions; sigma fixed per bat.
- Homoscedastic negative-control null: sigma `[1,1,1,1,1]`.
- Heteroscedastic negative-control null: sigma `[0.3,0.6,1.2,2.5,5.0]`.
- Per replicate, compute the exact 5! = 120 bat correspondence relabellings, one-sided `p<=0.05`, and count null rejections.

A separate seeded JavaScript implementation (5,000 synthetic replications per group) returned:
- equal sigma: **0.0484** false-positive fraction;
- unequal sigma: **0.1048** false-positive fraction;
- independent unequal-sigma seeds: **0.1154**, **0.1044**.

These are synthetic-method-specific numbers, **not animal results**, not a universal false positive rate for every heteroscedastic setting. Python CI adds a second independent demonstration with a separately declared deterministic RNG; its values must be recorded from the executed job rather than copied from the JS implementation.

**Consequence:** The old positive exact-label p is **not** acceptable as a standalone confirmatory personal-plasticity finding in a new biological dataset. Under bat-specific heteroscedastic noise it can materially exceed the advertised Type-I error. A corrected inferential route must derive its critical reference from the **specified heteroscedastic null**, with session nesting, bat-level sampling uncertainty, sensor crossing and all eligibility/parameter estimation rules locked before opening response outcome values. Do not merely tune the null after looking at p.

## Literature constraints

- Dingemanse et al. 2010, *Trends Ecol Evol*, doi:10.1016/j.tree.2009.07.013: individual reaction norms and personality/plasticity are established prior art.
- van de Pol 2012, *Methods Ecol Evol*, doi:10.1111/j.2041-210X.2011.00160.x: accurately estimating heterogeneous slopes is data hungry; when individuals share environment per occasion, only two individual-level measurements should be avoided. Their sample-size heuristics cannot be applied blindly to this bat experiment but decisively argue against interpreting our 2-occasion toy demonstration as adequate biological replication.

## Revised empirical source gate

For **prospective confirmatory individual response** the preferred analysis-ready support is:
1. **At least four genuinely separate occasions per bat**, each with predeclared challenge and reference measurements. First 2 independent occasions train the bat contrast and last 2 evaluate it. This is a *minimal out-of-occasion train/test split*, not a power assurance; several more occasions and independently sampled bats may be needed, as determined by simulation-based design precision and a real study plan.
2. Unambiguous animal IDs, source calibration and sensor/device ID. Cross devices and processing batches across bat×condition×occasion, or demonstrate independent sensor-bias cancellation with physical calibration. A permanently assigned device whose condition-specific bias is constant can make `C>0` with **zero biological individuality**, even in infinite repeated trials.
3. Independently verified context geometry and challenge manipulation, randomized/counterbalanced order, matched rewards, with bat-by-session recording unit; individual-level independent biological replication is bats, not frames.
4. Predeclare exact phenotype, numeric contrast, session pairing, missing-data gate, device exclusions, model complexity, and effect threshold. Do not retrofit a positive response feature from the same five Rhino recordings.
5. Primary validation: predict held-out bat-specific challenge contrast in independent evaluation occasions using **only earlier training occasions**, controlling shared session and context means. Compare against both a common-response baseline and an explicitly heteroscedastic H0 with per-bat noise (variance estimated without test-session leakage). Report incremental predictive gain with cluster uncertainty, calibration under heteroscedastic null, each bat, and evaluation-context failures.
6. Accompany individual response prediction with causal history manipulation only if learning is the claim. Functional benefit (success/energy/cost) is an independently specified outcome, not inferred from response persistence.

**STOP** if no repeated bat×challenge×occasion crossing, insufficient new bats to support meaningful inference, fixed bat-device confounding without controls, context-selection after outcome exposure, or independent test sessions lacking.

## Synthetic target scenarios and interpretations

| Scenario | Held-out individual response after 2 training occasions | Meaning |
|---|---|---|
| Shared challenge response; very different individual *means* | no additional individual gain | No stable response heterogeneity required |
| Stable individual challenge coefficient | potential positive gain on different occasions | Response repeatability, NOT learned origin/adaptive value |
| Heteroscedastic independent response noise | no reliable expected personal gain; naive exact label p can be anti-conservative | Must use heteroscedastic null |
| Same condition-specific device bias forever assigned to bat | falsely positive gain and covariance | Need device crossovers/independent calibration |
| Device assignment swapped across train/test | conditional fixed-device signature can reverse | Shows why sensor crossover is an identifiability gate |
| Slow-moving within-bat physiological state lasting across study | apparent durable response even without long-term personal attractor | Need reset/long time gaps, biological state covariates |

## Ecological claim ceiling

A reproducible personal challenge response would be a possible **proximate carrier** of individuality during co-use of 3D space, but it does not show that bats allocate space to avoid one another, that they learned this controller, that the same controller shapes wild vertical niche distributions, or that it improves lifetime fitness. The next publication-worthy causal result needs a distinct **functional consequence** and credible ecological task mapping. This branch supplies an explicit stop/eligibility rule rather than a positive bat discovery.
