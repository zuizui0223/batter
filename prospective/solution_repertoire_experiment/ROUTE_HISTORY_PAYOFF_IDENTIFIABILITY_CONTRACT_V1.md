# Route-history × payoff-revaluation × biomechanics discriminator (v1)

## Status and firewalls

**PROSPECTIVE SYNTHETIC DESIGN TEST, NOT EXPERIMENTAL BAT EVIDENCE.** This is a separate proposed experiment on branch `prospective/route-history-payoff-revaluation-v1`, descending from PR #82. It does not alter the frozen JAE manuscript, PR #72's randomized opportunity primary/P2, PR #81, or previous source outcomes. No bat or human data are opened. No trial burden is authorized.

## Ecological question

A bat can keep using the path it experienced first even when another path offers a higher apparent food reward. Does that indicate counterproductive historical lock-in, or an **acquired skill** that makes the historically used path cheaper/safer, so the same choice is rational on a *net benefit* basis?

This is the necessary third layer after:
- opportunity changes short-window specialization (PR #72);
- short memory can mimic stable preference (PR #81);
- an arbitrary randomized route seed can create a route-specific delayed causal signal (PR #82).

In behavioral learning, reward-devaluation sensitivity and habit are established topics. This experiment does not claim to invent value reversal or habits. The distinctive question is whether **the same history-caused route persistence has different ecological value depending on unobserved experience-dependent flight proficiency**.

## Exact observational-equivalence claim

Four equally feasible route labels r∈{0,1,2,3}. Random route seed S_i and randomly rewarded route B_i are assigned independently, as one of each label in each four-bat randomization block.

A fixed behavioral distribution is

```
q_i(r|bonus) ∝ exp[u_ir + h * 1(r=S_i) + a * bonus * 1(r=B_i)]
```

where u_ir is stable route bias unconnected to seed, h=2.0, a=2.0/0.35 and `bonus ∈ {0,0.25,0.60}`.

Two different true biological processes give **the same observed q**, even across two reward magnitudes and post-reset choice tests:

- **HABIT_PRIOR**: h is a value-blind choice prior / long-lived history bias; first experience changes tendency to choose S but does *not* lower true route energy/time cost.
- **SKILL_BENEFIT**: h represents a real history-acquired decrease of 0.35 synthetic comparable payoff/cost units on the seeded path; the animal's inverse utility scale is a=2/.35, so the seeded-route skill saving creates exactly the same +2 choice utility.

Couple the two worlds to use identical S, B, u and choice draws. Every route sequence, seed-hit statistic, reward-tracking statistic and associated randomization p must match **exactly** across the two worlds. This is an identification theorem by construction, not an observed bat result.

A route-choice-only assay cannot tell which process generated the data. The difference is in **measured route-specific performance, not choices**. The real-world interpretation of 'skill' requires an independently validated physical metric and comparable utility/energetic units.

## Locked synthetic architecture
- N=20 hypothetical animals, five complete four-animal blocks.
- Each block independently randomizes a permutation of 4 seed routes S and another independent permutation of 4 rewarded routes B. There are `24^5=7,962,624` balanced assignments for either factor conditional on the other.
- For each synthetic experiment, common R1 motor-state reset precedes baseline free choice (as in previous proposed diagnostics), but the two worlds are compared only after reset; motor-state persistence is not the active mechanism in this new comparison.
- Base period: eight free choices under equal reward (`bonus=0`).
- Low bonus: eight free choices with B-route bonus +0.25.
- High bonus: eight free choices with B-route bonus +0.60.
- The low/high outcome arrays are **separate synthetic potential measurement contexts** using the same personal utility; a future animal experiment cannot assume these would be observed without order, washout, novelty or carryover. Required controlled experiment would randomize bonus-dose/order or cohorts before real outcome.
- Personal stable unrelated route utility `u_ir ~ Normal(0,0.45)` independently per animal×route; it is not labeled innate versus learned.
- In each synthetic replicate draw route choices from the above softmax. The two worlds share exactly the same choice arrays.
- Before any seeding, generate true physical route cost `c0_ir = 1 + common_individual_i + route_effect_ir`, with `common_individual~Normal(0,0.07)`, `route_effect~Normal(0,0.025)`.
- HABIT world post-training true cost `c1_ir = c0_ir`.
- SKILL world post-training true cost `c1_ir = c0_ir - 0.35*1(r=S_i)`.
- For each bat/route, acquire two independent technical measurements before seed and two after choice probes, each Gaussian noise SD 0.20, using the *same* noise realizations across the two coupled worlds. The post measurements are a **hypothetical forced counterfactual performance assay after primary choices**, which must not contaminate the earlier choice test. No claim about animal-safe trial burden.
- Net synthetic value of choosing r under bonus Δ is `Δ*1(r=B_i) - c1_ir`, in the same arbitrary utility-linked units only. True cost and reward are never assumed calibrated for real bats. Regret is max net value among four possible routes minus expected net value given q_i under each condition.

## Three frozen synthetic endpoints

**E1 assigned-route history:** fraction of eight baseline choices that use assigned S, minus 0.25. Exact within-block seed-route permutation p from the `24^5` conditional randomization space by integer-histogram convolution. Treat as planned seed causality test; use upper-tail exact p <=.05 and observed excess >0.

**E2 randomized payoff tracking:** fraction of 8 bonus-context choices that use assigned B, minus 0.25. Compute separately for low and high; exact within-block B-route permutation p, holding S fixed. Planned separate follow-up; no claims of confirmatory family-wise control from these synthetic tests. For a real trial, specify gate/multiple-testing plan prospectively.

**E3 randomized seed-specific technical cost improvement:** let `d_ir = mean_post_measured_cost_ir - mean_pre_measured_cost_ir`. Then per bat improvement `g_i=mean_{r≠S_i}d_ir - d_i,S_i`. Aggregate `G_cost=mean_i g_i`. Its permutation calibration independently reassigns S within each block for the observed 20×4 d-matrix, with B=1,999 Monte Carlo assignments and +1 upper-tail correction, seed derived from each replicate's independent `SeedSequence` stream. Under no seed-specific skill, the expectation is 0. Under the model skill γ=0.35, expectation is +0.35. No feature deletion or post-hoc selective forced flights.
  
Report positive detection fraction for E1/E2/E3, mean observed effects, binomial Monte Carlo errors (1,000 experiments); report diagnostic E1 & E3 co-support as separate synthetic planning outcome. Compute and report mean **true** regret over conflicting seed/bonus assignments (`S≠B`) for low and high bonus and both worlds.

## Monte Carlo and checks

- 1,000 independently seeded synthetic experiments, root NumPy PCG64 `202610081510`; NumPy version 2.3.5, Python 3.13 preferred for exact replay.
- Every replication has both coupled HABIT_PRIOR and SKILL_BENEFIT worlds, sharing route choices. Use independent streams for routes/measurement/permutation to avoid accidental matching claims.
- Optional calibration controls in exactly the same synthetic experiments:
  * NO_SEED: use h=0 for behavior and no skill cost; E1 should be near nominal .05.
  * NO_BONUS: use Δ=0 for behavior after B assignment (but still B labels randomized); E2 should be near nominal .05.
  Both share pre-generated S/B and independently drawn routes; use separately seeded streams.
- For each exact 24^5 seed or bonus test, enumerate 24 possible mappings per block, histogram integer seed-hit counts (0..32 per block), convolve across five blocks. Verify total assignments 7,962,624 and null expected hit rate 0.25. Brute force 24²=576 two-block permutations matches convolution exactly.
- For E3, legal randomly sampled seed assignments must be permutations per block; verify p calculation, sign and that assigned S exerts no influence on pre measurements.
- Observational equivalence check MUST assert byte-identical choice arrays and exact-identical E1/E2 effects/p values between HABIT and SKILL for *every* replication, including bonus contexts.
- No optional exploration of other h, a, gamma, Δ, flight count, noise or N under v1. A new hypothesis requires a new version.

## Interpretive ceiling

- This is a **mathematical/data-generating-model counterexample**, not evidence that actual bats habitually choose inefficient routes or learn useful motor skill.
- A learned route can be net efficient even when another currently available route gives more food reward, because the learned path may save energy or reduce errors; conversely, high fidelity may incur avoidable cost.
- Without measuring all feasible route costs under a standardized counterfactual trial, route-reward choice data cannot identify ecological net gain.
- Actual adaptive significance would require real calibrated reward gain, movement energy, time, risk and ideally fitness relevance. Time or 3-D route length alone is not fitness.
- The hypothetical pre/post all-route cost assay may itself change familiarity and memory; real work needs a **new independently welfare-approved cohort/protocol**, safe run numbers, balanced sham, blinded tracking/processing and preregistered contrasts.
- The `payoff` repository concerns *heritable architecture-level payoff games*, not these proximate bat behavior choices. Neither its evolutionary/fixation results nor `adaptive-gain`'s adaptive measurement theorem can be imported as proof about bats.
