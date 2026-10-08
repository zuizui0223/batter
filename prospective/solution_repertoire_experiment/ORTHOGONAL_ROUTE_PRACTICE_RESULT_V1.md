# Orthogonal route-practice identifiability — simulated result v1

## Evidence provenance
**Entirely synthetic design stress test, no tracked bat or animal data.** The hypothesis, seven nested terms, model families, 1000-replicate rule, conditional 9^5 randomization null and numerical parameters were frozen in `ORTHOGONAL_ROUTE_PRACTICE_CONTRACT_V1.md` before opening numerical output. Python 3.13 / NumPy 2.3.5 independent local implementation passed the declared structural checks. The canonical GitHub Actions workflow may still be queued; local results must not be called authoritative Actions outputs until independently reconciled.

## Restricted crossed randomization
N=20 artificial animals, 5 blocks of 4, 4 feasible route labels. Each block has a seed-route permutation S (4! choices), then a practice-route permutation P selected uniformly among the 9 derangements of S, so P_i != S_i. This is **conditionally randomized, not unconditionally independent S and P**. In the exact practice null, S is fixed, there are 9^5=59,049 legal P allocations, and all twenty late choice vectors are held unchanged.

Observed practice-hit H = sum_i sum_{t=1}^8 1[route_{i,t}=P_i]. For each block enumerate 9 derangements, tabulate total H, then convolve the 5 block histograms. A two-block 81-legal-assignment brute-force null matches the convolution exactly.

Important calibration: P excludes S. Under this restricted assignment, conditional expected hit rate is one-third of observed **non-seed** route choices, NOT 25% of all choices. The exact test uses this correct null, not naive random choice.

## Hypothetical mechanisms and results

1000 seeded replicates/model, root NumPy seed 202610081616. All five models use HS=1.2 route-seed bias, fixed route practice choice effect eta=1.8 when enabled, motor-skill physical saving gamma=0.30 when enabled, shared random physical cost shocks in [-0.1,+0.1] and a=eta/gamma=6 cost sensitivity.

| Model | P effect detection under exact 59,049 assignments | Mean P choice fraction | Mean S choice fraction | True P route cost gain |
|---|---:|---:|---:|---:|
| No extra practice effect | 39/1000 = **3.9%** | 16.78% | 50.05% | 0 |
| Practice-induced motor skill CAUSES choice | 1000/1000 = **100%** | 51.00% | 30.05% | +0.30 |
| Practice-induced familiarity causes choice, skill gains coincidentally | 1000/1000 = **100%** | 51.00% | 30.05% | +0.30 |
| Practice improves skill but not route choice | 40/1000 = **4.0%** | 16.63% | 50.05% | +0.30 |
| Practice changes preference but not true cost | 1000/1000 = **100%** | 50.86% | 29.94% | 0 |

One-sided decision: observed practice-hit count greater than exact null expectation and exact p<=0.05. Monte Carlo binomial standard errors for support fractions of 3.9% and 4.0% are 0.61 and 0.62 percentage points respectively. The synthetic 1000/1000 rate is not evidence that future biological detection probability is exactly 100%.

## Independent local validation
- Structural self-test: **PASS** for 9 derangements, 59,049 legal allocations, five-block null normalization and 81-assignment two-block exact-enumeration equivalence.
- Paired-model identity checks: **1000/1000** replicates have identical seed/practice assignments, external physical cost shocks, route-choice arrays, corresponding exact conditional practice p values and independently measured true all-route costs in the two causal twin models.
- Result JSON and local independent replay are saved as `batter_orthogonal_independent_result.json` and `batter_orthogonal_independent.py` for cross-validation. Their outputs are a *local reimplementation*, not the Actions artifact.

## Mechanistic identification boundary
Let a seed route S and an independently assigned-with-exclusion practice route P affect subsequent choice. Let cost improvement gamma and preference eta satisfy eta=a*gamma.

Model 1 (skill-mediated):
`q_i(r) proportional exp(u_ir + HS 1[r=S_i] + a gamma 1[r=P_i] - a D_ir)`, where practice improves actual cost of P by gamma, and that saving is what directly drives choice.

Model 2 (parallel familiarity and physical learning):
`q_i(r) proportional exp(u_ir + HS 1[r=S_i] + eta 1[r=P_i] - a D_ir)`, where familiarity causes route preference directly, while skill gain gamma occurs in parallel and does not mediate the original route preference.

Because eta=a gamma, the joint observable distribution of randomized inputs, actual route use, external cost shocks, all-route physical costs and related test statistics is **exactly the same** under both models for every D. Independent practice assignment identifies a causal total effect on choice **and** a causal total effect on performance. It does not identify the route by which that effect on choice was mediated.

In particular, a cost perturbation D that affects both generators through identical direct cost sensitivity cannot prove historical skill mediation. Intervention on the **learned motor proficiency state** with an exclusion/causal isolation assumption, not just external physical cost, would be needed for mediation-specific attribution; such a safe and isolatable bat-flight intervention is not demonstrated.

## Ecology-first synthesis and next science
The conservative, testable biological statement would be:
- early route history predicts later choice even when feasible paths and current opportunity are equal;
- targeted practice adds further reproducible preference and/or measurable route execution proficiency;
- the long-run preference can persist under common route-state reset;
- whether that practice-related physical advantage is the **proximate carrier of choice**, rather than a parallel correlated effect, remains to be experimentally identified.

To claim ecological adaptive significance additionally require task-aligned comparable reward/energy/risk across all feasible routes and independent perturbation, preferably fitness-relevant. Do not equate persistent route choice, reward responsiveness, speed or collision avoidance alone with natural selection.

This mathematical result should close same-data mechanism hunting; do not use the old five-animal source to fit additional speculative latent factors. Any real design requires separate welfare, apparatus, pilot and preregistration approval and does not overwrite PR #72 or JAE.
