# Memory versus inertia — P1 identifiability simulation result v1

## Evidence status and chronology
**SYNTHETIC MECHANISM-STRESS TEST — NOT EMPIRICAL BAT EVIDENCE.** The simulation contract was committed first at `02a8d58`, before scenario outputs were computed. The initial software dry run used one PRNG stream per scenario, contrary to the frozen contract's per-replicate substreams; that exploratory software output was **superseded**, without tuning any biological parameters or decision thresholds. The authoritative simulation uses independent `numpy.SeedSequence.spawn(1000)` substreams per scenario and all contract-frozen parameter values. This implementation correction is disclosed explicitly.

Source design: current prospective PR #72, not wild 3-D tracking or the prior frozen JAE paper.

## Structural and endpoint fidelity
- 20 virtual bats, five complete four-animal blocks; A-start vs B-start balanced within block.
- Four route classes; early 8 choices and held-out late 8 choices per bat×family; alpha=0.5.
- Exactly 1,024 legal restricted treatment assignments (four per block), exhaustive one-sided P1 randomization.
- Frozen family P1 score uses **all 19 same-family conspecifics** as donors, regardless of OPEN-acquired label.
- The proposed post-suppression S2 uses only the 10 OPEN-acquired conspecifics per physical family as its own distinct treatment-matched donor pool.
- Simulated suppression sets all bats' most recent route to canonical R1 for eight forced flights; then eight OPEN flights are generated. P1 is evaluated on the original 16 flights *before* this interruption, unchanged.
- For proposed S2, early OPEN-family first-eight history predicts first eight post-reopening choices. Correspondence permutation: 999 random label permutations independently within the two OPEN-acquired matched-family groups, one-sided +1 adjustment.
- Deterministic tests: 1,024 unique balanced assignments PASS; optimized P1 equals literal direct formula at 1e-13 tolerance PASS; baseline all-R1 identity score zero PASS; true assignment included in exact permutation support PASS.

## Six illustrative generative scenarios
All six scenarios were specified before simulation, each with **1,000 independent synthetic experiments**, root PCG64 seed `202610081337`.

- IID_NULL: every route independent uniform, both acquisition treatments identical.
- PERSISTENT_STRONG: individual-specific route vector drawn from symmetric 4-route Dirichlet with total concentrations kappa_OPEN=4, kappa_CONSTRAINED=40; same personal vector generates both the original probe and reopening.
- PERSISTENT_MODERATE: kappa_OPEN=8, kappa_CONSTRAINED=30.
- INERTIA_MODERATE: every bat has the same first-order switching law, with no personal route preference; repeat previous route with rho_OPEN=0.80, rho_CONSTRAINED=0.10, otherwise draw an independent uniform route.
- INERTIA_STRONG: rho_OPEN=0.95, rho_CONSTRAINED=0.10; no persistent personal theta anywhere.
- INERTIA_EQUAL: rho_OPEN=rho_CONSTRAINED=0.95; negative-control test with high temporal dependence but no acquisition treatment effect.

The actual one-step route-repeat probability under the Markov mixture is `rho+(1-rho)/4`. Thus rho=.95 means 0.9625 immediate repetition. Such high inertia is **illustrative and extreme**, not a measurement of real bats.

## Monte Carlo result

| scenario | mean P1 Delta | P1 positive, exact randomization p<=.05 | mean proposed S2 score | proposed S2 positive, correspondence p<=.05 | both positive | S2+ conditional on P1+ |
|---|---:|---:|---:|---:|---:|---:|
| IID_NULL | +0.004 | 5.9% (59/1000) | -0.003 | 4.4% | 0.3% | 5.1% |
| PERSISTENT_STRONG | +0.279 | 82.6% (826/1000) | +0.524 | 100.0% (1000/1000) | 82.6% | 100.0% |
| PERSISTENT_MODERATE | +0.127 | 34.6% (346/1000) | +0.299 | 98.9% | 34.4% | 99.4% |
| INERTIA_MODERATE | +0.068 | 8.7% (87/1000) | +0.000 | 3.9% | 0.6% | 6.9% |
| **INERTIA_STRONG** | **+0.818** | **95.8% (958/1000)** | **+0.005** | **4.3%** | **4.0%** | **4.2%** |
| INERTIA_EQUAL | +0.010 | 5.1% (51/1000) | +0.003 | 4.3% | 0.2% | 3.9% |

Binomial Monte Carlo SE for key 95.8%: 0.63 percentage points; for 82.6%: 1.20 pp; for 4.3%: 0.64 pp. For 1000/1000 the observed Monte Carlo standard error formula reports zero but this does NOT establish 100% detection probability in the underlying simulation distribution.

## What the simulation establishes
The same validated P1 route-choice endpoint is highly responsive under **two mutually different hypothetical mechanisms**:
1. a stable individual-specific route-distribution vector, and
2. exclusively transient *first-order* path inertia shared by all animals, with stronger inertia under OPEN-acquisition history.

Thus even an exactly randomized positive P1 would establish an effect of prior solution-opportunity exposure on subsequent route organization **but does not identify long-lasting personal policy as the mediator**. INERTIA_STRONG is NOT a Type-I error against the randomized treatment null; the simulated acquisition treatment genuinely changes immediate serial dependence.

The proposed post-suppression identity test sharply distinguishes the **two stated idealized models**: forced R1 synchronizes a common Markov state and destroys correspondence between early individual routes and post-reopening routes, but a stable latent theta still predicts post-reopening route preference. The simulation is not an observational claim.

## Analytical reason for the trap
For the symmetric four-route Markov kernel
`P(next=r | current=s)=rho*1[r=s]+(1-rho)/4`,
one has
`P(X_(t+l)=X_t)=1/4+(3/4)*rho^l`.
At rho=.95 the same-route probability is ~0.748 after eight transitions and ~0.580 after sixteen, even though every bat shares **exactly the same transition parameters**. Repeating one route for an eight-trial early/late split can therefore resemble a private strategy.

After all animals have been **forced to R1** for the intervening block, the Markov process's next state depends only on R1 and the common rho, not on the bat's identity or original personal route. This yields no *cross-reset* individual mapping under the defined inertia model.

## What is not established
- Simulated high P1 rejection rates are not measured effect sizes or actual power for natural bats.
- The opportunity-dependent inertia model does not specify *how* twelve acquisition trials produce rho=.95; it shows a nonidentifiability counterexample, not a validated physiological mechanism.
- Positive S2 could reflect **stable morphology, sensory bias, site preference or stable individual-specific response rules**, rather than a learned memory for specific routes.
- Negative S2 could result from forced-block-induced rewriting of a genuinely persistent policy, imperfect re-opening, fatigue, long experimental intervals or noisy low-n estimates.
- S2 here is an **unregistered numerical proposed variant**, not a new primary or an amendment to existing PR #72's qualitative S2 proposal. Its eight forced + eight reopened flight counts require engineering/welfare review and explicit pre-outcome freezing.
- The existing experimental plan currently lacks a paired **sham interruption**. Adding it prospectively would help distinguish true route-state resetting from generic exposure/retraining and order effects, but adds trial and welfare burden.

## Next ecological discriminators, not more same-data model fitting
1. Keep P1 as the already-frozen causal test of whether **acquisition opportunity changes route specialization**; explicitly avoid calling it a memory-formation assay by itself.
2. Engineer and preregister S2 *before animal data*: pre-suppression own-history profile predicts post-reopening routes when the last 8 route exposures were all R1. Use same treatment-matched family donor pools and identity correspondence null; ensure pre-specified first reopening window.
3. Consider a matched sham interruption control or orthogonal reset manipulation **only after feasibility review**; a single forced-route block cannot logically separate all classes of persistent internal state.
4. To support the large ecological theory, link manipulated history to the maintained spatial strategy **and** to resource use, energetic performance or equivalent payoff. This study itself tests neither fitness nor wild spatial partitioning.
5. Keep JAE and the original PR #72 primary, randomization, sample-size and attrition gates unchanged.

## Reproducibility
The local deterministic implementation is `memory_vs_inertia_simulation_v1.py` and the full machine result is `MEMORY_VS_INERTIA_SIMULATION_RESULT_V1.json`. Preserve all six model assumptions, the 1,000 repetitions per scenario, independently spawned per-replicate RNG streams, P1 1024-assignment exact null and S2 999-label-permutation null. The code and JSON should accompany this note as archived artifacts. No optimization against synthetic results is permitted.
