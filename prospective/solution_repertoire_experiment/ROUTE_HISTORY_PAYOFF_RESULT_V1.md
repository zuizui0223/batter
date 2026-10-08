# Route history, payoff revaluation, and learned skill — simulation result v1

## Status and evidence provenance
**SYNTHETIC MODEL NON-IDENTIFIABILITY RESULT ONLY. NO BAT EXPERIMENT.**

Contract `ROUTE_HISTORY_PAYOFF_IDENTIFIABILITY_CONTRACT_V1.md` was committed at `fc3e7d6` **before** the new synthetic outcomes. Model script `route_payoff_stress_v1.py` and result `ROUTE_HISTORY_PAYOFF_SIMULATION_RESULT_V1.json` were independently executed in Python 3.13 / NumPy 2.3.5. SHA256:

- Script: `fd4c60215482bb31a2c4bffc9bb60ac263e8ac58c2023d7c4245559e78de80de`.
- JSON: `c99fcd90858d8555df4a002c4033fe7373efc49355c362589d5bde16938c1d4f`.

The GitHub file blobs were checked to match the local files byte-for-byte (script `5bf9b0419fc0308b36b04bb9be0e57a51bb56106`; JSON `a5fc10472a173672dfc6ed1ba09a3a6a29d434e0`).

Design: 1,000 synthetic experiments, N=20 artificial animals in five complete four-animal blocks, 4 possible routes, two *independent* balanced within-block randomized assignments (seed S and bonus route B). Each of the S and B route labels has `24^5=7,962,624` legal assignments conditional on the other. Exact tests use integer-histogram convolution, not an approximate subset of assignments. Technical cost-effect calibration uses 1,999 block-respecting Monte Carlo permutations per synthetic experiment. These are simulation test properties, **not biological power estimates**.

## Structural verification
PASS:
- every block has one seed of each of R1–R4 and independently one rewarded path of each kind;
- exact histogram convolution matches direct enumeration of all 576 assignments in two blocks;
- all exact full-null histograms sum to 7,962,624;
- seed-effect and bonus-effect null controls have near-nominal error in the declared simulation;
- choice observations and choice-based randomization results are **identical** under HABIT_PRIOR and SKILL_BENEFIT for every one of 1,000 coupled experiments;
- changing the seeded-path true physical cost by exactly -0.35 changes the measured difference-in-differences technical cost improvement by exactly +0.35 in every paired dataset.

## Choice mechanism
The same choice probability is used in two biologically distinct worlds:

```
q_i(r|bonus) ∝ exp(u_ir + 2.0*I[r=S_i] + (2/0.35)*bonus*I[r=B_i]).
```

- In HABIT_PRIOR, the 2-unit historical preference is a behavioral prior with **no improved actual movement cost**.
- In SKILL_BENEFIT, the same 2-unit preference reflects a true learned **0.35-unit reduction** in the seeded route's physical cost, with cost-to-choice inverse temperature 2/0.35.
- In both, the reward value of B is +0.25 or +0.60 relative to other route rewards.
- An individual's pre-existing route tendency `u_ir ~ Normal(0,.45)` is unrelated to the randomized seed. The models generate exactly the same observable route sequences by paired construction.

Thus choice-only longitudinal data (including reward revaluation) cannot identify **neutral history-dependent preference versus history-dependent performance improvement** under this constructed equivalence.

## Synthetic results

| Frozen endpoint | Mean effect | Supported synthetic runs / 1,000 | Monte Carlo SE of support frequency |
|---|---:|---:|---:|
| E1 randomized seed effect on choice after common motor reset | +0.43779 over 25% | 1000 | observed 0 |
| E2 independent low bonus +0.25 effect on choice | +0.20498 over 25% | 857 | 0.011 |
| E2 independent high bonus +0.60 effect on choice | +0.55455 over 25% | 1000 | observed 0 |
| Seed-null control (stable pre-existing individual biases, no seed effect) | +0.00183 | 52 | 0.007 |
| Bonus-null control (seed bias exists but no bonus effect) | −0.00331 | 44 | 0.006 |
| E3 seed-specific physical-performance gain, **HABIT_PRIOR** | +0.00023 | 40 | 0.006 |
| E3 seed-specific physical-performance gain, **SKILL_BENEFIT** | **+0.35023** | **1000** | observed 0 |

The 1,000/1,000 frequencies are properties of these strong *hypothetical* effects; zero empirical MC-SE does **not** mean universal detection probability of 100%.

## History versus payoff response in conflict animals
Among artificial individuals with randomized `S_i != B_i` (mean 15.096 out of 20):

| Bonus magnitude | Prob. choose historical seed | Prob. choose bonus route | True regret per route choice: HABIT | True regret: SKILL |
|---|---:|---:|---:|---:|
| +0.25 | 0.5314 | 0.3125 | 0.1718 | 0.0859 |
| +0.60 | 0.1985 | 0.7462 | 0.1522 | 0.0828 |

Regret is the difference between maximum feasible net payoff and predicted payoff of route choice under each model's **true synthetic cost matrix**. It is expressed in invented comparable utility units, not observed metabolism, individual fitness or measured bat performance.

When the reward advantage is +0.25 but historical skill can save 0.35 cost units, favoring the remembered path can be net efficient. When bonus rises to +0.60, switching toward the now better rewarded route can be net efficient instead. The same choice probabilities have different actual performance implications in the two underlying worlds.

## Falsifiable biology and next design

Original PR #72: randomized solution *opportunity* changes short-window route organization; no claim about lasting memory from P1 alone.

PR #81 and parallel history reset: common first-order route inertia can be distinguished from stable personal state by standardizing the final route state, but matched delayed outcomes still cannot prove a newly created propensity.

PR #82: independently randomized which-route seed can identify a specific causal *experience-to-choice* effect beyond pre-existing fixed route propensity.

**This prospective branch:** beyond choice, we also need an independent counterfactual *route performance* assay:

1. Pre-randomization baseline: each bat's success, route time and task-aligned movement costs on all four routes, under balanced forced-route presentations.
2. Randomize initial **seed route** independently of physical route identity/fitness and reward assignment; apply standardized safe exposure.
3. Assess route preference after a common immediate route-state reset with equal current opportunity.
4. Independently randomize the better-rewarded route; ensure bonus knowledge, handling, route attractiveness, time, order and fatigue are controlled. The current low/high simulated contexts are **counterfactual test settings**, not a finalized repeated-measures animal schedule.
5. **Only after primary choice testing**, measure matched repeated isolated-route physical performance again for *all four feasible routes* under blinded tracking; otherwise measuring unchosen routes during primary history tests alters personal experience. Independently measured pre/post route-specific improvement under assigned S is essential.
6. Analyze seed-by-route gain via an animal-level blocked randomization test, preserving each randomized S assignment. Assess biologically comparable intake/time/error or energy costs before interpreting net payoff. If only latency/3D path-length proxies are available, stop short of an energetic or evolutionary adaptation claim.

### Interpretation matrix
- Choice seed effect + no seed-specific performance improvement: history affects choice without a detected motor-skill benefit; could be neutral history, familiarity, affect or sensory bias—not proof of maladaptive habit.
- Choice seed effect + experimentally attributable route-specific performance improvement: compatible with skill-mediated adaptive matching; need quantify cost relative to rewards and task risks.
- Choice shifts after independent reward revaluation: shows reward responsiveness under the tested schedule, but does not by itself identify neural goal-directed control.
- Value revaluation has no choice effect: compatible with inertia, costly switching, or perception/learning failures. It does not establish a true habit without independent reward-knowledge manipulation.

## Scientific originality boundary
Reward devaluation, habit formation, habitual route fidelity and route learning all have prior art. Relevant prior studies:
- Bouton, 2024, *Habit and persistence*: https://doi.org/10.1002/jeab.894.
- Model based control can give rise to devaluation-insensitive choice: https://www.sciencedirect.com/science/article/pii/S277239252300010X.
- DREADD bat flight compensations under sensory perturbation: https://pubmed.ncbi.nlm.nih.gov/39549701/.
- Movement-ecology integration of motion/navigation/internal state: https://pmc.ncbi.nlm.nih.gov/articles/PMC5983048/.

The only prospective contribution here is the proposed **orthogonal randomized route experience × route payoff × independently measured within-individual physical performance** test. No fitness, ecological-trap or wild niche causation is established until new animal observations exist.

## Scope firewall
Do not merge this exploratory branch into frozen JAE or PR #72; do not run animals without new ethical, welfare and engineering approval. The `payoff` repository models *heritable architecture* payoffs; its evolutionary-game results do not directly apply to individual acquired flight routes.
