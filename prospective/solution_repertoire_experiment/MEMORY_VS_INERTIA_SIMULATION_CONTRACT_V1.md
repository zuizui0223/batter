# Simulation contract: persistent personal route preference versus transient route inertia (v1)

## Status and firewall
**PROSPECTIVE MODEL-IDENTIFIABILITY STRESS TEST, NOT ANIMAL EVIDENCE.**
This study simulates hypothetical route sequences under fixed generative mechanisms. It reuses the P1 endpoint and exact block randomization from `prospective/solution_repertoire_experiment/` unchanged. It does NOT rerun real bat data, revise the registered P1 question, change JAE, or assert that either mechanism is present in nature. All parameter values, decision criteria, run count and random seeds below are fixed before the first numerical simulation.

## Central question
Can the existing 16-trial early-eight → late-eight route specialization P1 distinguish:
1. **persistent individual strategy** (within-animal route probabilities remain individual-specific across the experiment); from
2. **transient route inertia** (everyone shares the same transition law and has no enduring individual-specific preference, but choices cluster because the most recent route tends to be repeated)?

A causal effect of OPEN-versus-CONSTRAINED acquisition on P1 is NOT necessarily an effect on durable memory. Transient autocorrelation induced by the acquisition treatment would itself be a genuine effect on immediate choices but a different biological mechanism.

## Exact inherited P1
- Four routes `R1,R2,R3,R4`; 20 animals in five randomized four-animal blocks.
- A and B matched families; each animal has one randomly OPEN-acquired and one CONSTRAINED-acquired family, and balanced A/B start order.
- Each family's first common OPEN probe has **16** route observations; early eight estimate `(count+0.5)/(8+4*0.5)`, late eight are held-out scored.
- For each late trial, P1 is log own early probability of observed route MINUS mean log early probability of that route across **all other 19 animals of the same family**, regardless of treatment.
- Equal late-trial mean within animal×family, equal bat mean of `R_open - R_constrained`.
- Exact conditional null enumerates all `4^5=1024` allowed OPEN-family assignments; one-sided p is the fraction of assignments `Delta_perm >= Delta_observed`. P1 positive if `Delta>0 and p<=0.05`.
- No new routes, data-driven clusters, test window change, donor filtering or unrestricted sign flips.

## Hypothetical generative mechanisms, all symmetric at population level
In each replication, each animal and environment family independently draws its stochastic path conditional on treatment assignment.
All route classes begin with equal population probability and equal feasibility.

**IID_NULL**: no identity, no inertia, no acquisition effect: each route independently uniform.

**PERSISTENT_STRONG**: per-animal×family fixed theta drawn from `Dirichlet(kappa_t/4,...,kappa_t/4)` with `kappa_OPEN=4, kappa_CONSTRAINED=40`; all 16 probe and subsequent reopening routes are drawn independently conditional on the same theta.

**PERSISTENT_MODERATE**: as above with `kappa_OPEN=8, kappa_CONSTRAINED=30`.

**INERTIA_MODERATE**: no theta; first probe route uniform; each next route repeats previous with probability `rho_t`, otherwise independent uniform draw, with `rho_OPEN=0.80, rho_CONSTRAINED=0.10`.

**INERTIA_STRONG**: same with `rho_OPEN=0.95, rho_CONSTRAINED=0.10`.

**INERTIA_EQUAL**: same with `rho_OPEN=rho_CONSTRAINED=0.95`; a treatment-null control under strong serial dependence.

Because switching to the OPEN-acquired family changes rho in the two unequal-INERTIA models, those scenarios really do have a treatment effect on transient persistence. They must NOT be called Type-I errors for the randomized P1 test.

The model conditions on the **post-acquisition** common-OPEN process; it does not simulate how acquisition caused the values of kappa or rho, route rewards, disease, aging, obstacles, or animal welfare. Illustrative parameters, not estimates from bats.

## Mechanism discriminator — proposed S2 *planning* variant (NOT an alteration of original S2)
To evaluate whether the already-planned 'suppression → exact reopening' can distinguish mechanisms, independently model an **8-trial forced canonical R1 block after the fixed P1 16-trial probe**, followed by **8 R1/R2/R3/R4 reopening trials** in each animal's OPEN-acquired family. All routes remain mechanically feasible after reopening.

- In fixed-theta models, imposed R1 expression does not change theta and reopened routes sample the same theta.
- In transient Markov models, the forced block sets the state to R1, and reopening begins from the same R1 state for every bat; the transition kernel remains common to all (though shared treatment-specific rho may persist).
- Reuse *only* the original eight early-probe trials from the OPEN-acquired family as predictive personal history, with the same alpha=0.5. Do not use suppression flights, late P1 target flights, or reopening targets to build the personal probability model.
- For this **new hypothetical S2 statistic only**, compare self early distribution against the other OPEN-acquired animals *within the same family* (10 animals per family under the matched-block assignment). This ensures donors share acquisition treatment; it is intentionally distinct from P1's all-family donors.
- Score mean self log probability minus mean other log probability over eight reopening trials, first by individual then equally across 20 OPEN-acquired families.
- The identity-correspondence null independently permutes early profile labels among OPEN-acquired individuals within A and B family; it retains target sequences, family, treatment, donor group, routes and sample sizes. **999 permutations**, seed below, conditional one-sided p with +1 adjustment.
- S2 signature: `mean advantage > 0 and permutation p<=0.05`. It would indicate retained individual correspondence over the forced-route block but would not by itself identify learned memory rather than stable morphology or individual-specific Markov response parameters.
- Original PR #72's S2 is already prospective but not fully numerically fixed; the 8 forced + 8 reopening counts are solely a simulated **proposed pilot option**, not a change to the frozen P1 or a confirmed experimental commitment.

## Monte Carlo protocol
- Exactly **1000 independent synthetic experiments per scenario**, 6 scenarios = 6000 total (no stopping early for good p).
- Root seed `202610081337` (numpy PCG64) with deterministic per-replicate substreams. S2 correspondence permutations use the same replication stream after path generation.
- Every experiment draws one of the 1024 allowed blocked assignments uniformly.
- For each replication report P1 Delta and exact conditional p; proposed S2 retained advantage and label-permutation p.
- Aggregate the fraction P1-positive, the fraction S2-positive, and fraction both positive under each scenario, plus mean P1 Delta and mean S2 advantage. Use binomial Monte Carlo standard errors, not retrospective biological power or new empirical p values. Report `P(S2+ | P1+)` as a descriptive ratio of simulation counts, or undefined if no P1 successes.
- Synthetic invariant checks before computation: (a) 1024 unique assignments with required balance; (b) exact null distribution has 1024 entries and includes the observed assignment; (c) P1 score agrees with reference definition on a deterministic toy route fixture; (d) if forced final R1, post-reset Markov path no longer depends on early probe route when rho same across bats; (e) P1 donor pool all same-family bats versus proposed S2 within-treatment donors.
- Program must emit immutable JSON with settings, scenario totals and diagnostics; never overwrite with new parameter choices without a new version.

## Interpretation ceiling
- P1 positives in persistent and transient-inertia models demonstrate **mechanistic non-identifiability from 16 consecutive free choices** under those illustrative mechanisms, not that P1 is statistically invalid.
- If the fixed-route interruption sharply discriminates, this motivates completing the existing S2 prospective schedule and a balanced sham control, **before any animal outcomes**. Forced-route exposure can itself induce relearning; it does not perfectly isolate memory without a control or assumptions.
- No P1-only result proves learned memory, persistent personal flight 'law', optimality, or fitness consequences.
- Do not label simulated rejection fractions as observed bat evidence, and never count synthetic replications as biological samples.
