# Randomized route-seed mechanism discriminator — analytical result and synthetic audit v1

## Status
**NO EMPIRICAL ANIMAL DATA.** This is a mathematical identifiability result and independently reimplemented simulation of a *proposed distinct future experiment*. The original PR #72 main P1/P2, JAE v0.4.0, PR #81 P1-vs-inertia and the separate proposed matched dual-family reset remain unchanged.

### Provenance
- Frozen theoretical + simulation contract: commit d102328, followed by pre-output scenario-count correction commit 0acd81 (six -> seven).
- GitHub implementation: \`randomized_route_seed_simulation_v1.py\`, committed at 3141b3 before opening these numeric outcomes.
- Independent local Python 3.13.5 / NumPy 2.3.5 implementation: SHA256 \`5bea80712c3aaa3d38712d68ec0d24bc77bc51ab1a1b232117a8f371c523834e\`.
- Independent local JSON: SHA256 \`019a3ac97c7aeeb3d7762165ae0ea4c584e2dc05544689d5f9c07d00e357331c\`.
- Seed: 202610081401, 1000 synthetic experiments per model, seven fixed models; independent substreams across models and replicates. GitHub Actions result, if any, must be independently compared with this reconstruction and cannot be claimed to have passed before the workflow finishes.

## Structural exact-randomization result
Five four-animal blocks, one individual randomly assigned each of 4 routes per block:

\[
N_{\mathrm{legal}}=(4!)^5=7,962,624.
\]

For every individual's eight post-reset OPEN flights, let \`c[i,r]\` count choices of route r; let \`S[i]\` denote independently randomized seed route. The fixed primary score is

\[
T=\frac{\sum_i c_{i,S_i}}{20\times8}-\frac14.
\]

All \`24^5\` legal assignments are assessed **exactly without Monte Carlo approximation** by enumerating 24 mappings per block, tabulating the integer seed-hit counts within each block, then discrete-convolving the five histograms. Each local histogram sums to 24; the global histogram sums to 7,962,624. A 2-block brute-force enumeration of 576 allocations reproduces the convolution exactly. One-sided p is exact upper-tail probability including ties.

The effect is about **which random route was experienced**, not the previous identity-recognition advantage after its route has been freely selected. The random seed is causally orthogonal to prior individual morphology or route preference under valid no-interference randomization.

## Scenario results

| Hypothetical generator | Seed-hit rate | Mean T (above chance .25) | Exact-test support /1000 | Rejection fraction | Monte Carlo SE |
|---|---:|---:|---:|---:|---:|
| TRAIT_ONLY (pre-existing stable b_i) | 0.250438 | +0.000438 | 50 | 0.050 | .00689 |
| TRAIT_WITH_ROUTE_ASYMMETRY | 0.255013 | +0.005013 | 48 | 0.048 | .00676 |
| GATED_PREDISPOSITION (strong fixed bias, no seed influence) | 0.251438 | +0.001438 | 49 | 0.049 | .00683 |
| MARKOV_WITH_RESET (same R1 start, rho=.95) | 0.248763 | -0.001238 | 34 | 0.034 | .00573 |
| HISTORY_IMPRINT_WEAK (lambda=.15) | 0.363981 | +0.113981 | 532 | 0.532 | .01578 |
| HISTORY_IMPRINT_STRONG (lambda=.35) | 0.513563 | +0.263563 | 999 | 0.999 | .00100 |
| MARKOV_NO_RESET (initial current route S_i, rho=.95) | 0.853000 | +0.603000 | 1000 | 1.000 | 0 (empirical fraction boundary) |

### Mathematical self-consistency
The *hypothetical imprinting* models are defined as

\[
b_i\sim \operatorname{Dirichlet}(.35,.35,.35,.35),\quad
q_i=(1-\lambda)b_i+\lambda e_{S_i}.
\]

With a balanced independent seed and four routes,

\[
E[T]=\left(1-\frac14\right)\lambda=\frac34\lambda.
\]

Hence the precomputed theoretical expectations are 0.1125 for lambda=.15 and 0.2625 for lambda=.35; observed simulated means 0.113981 and 0.263563 agree within simulation noise. These effects are **put in by the generator**, not evidence that any bat learns with these values.

The diagnostic no-reset Markov generator has no stable individual theta but a recent route state equal to its assigned seed. It demonstrates that **even randomized seed effects can be carried by short-term motor inertia** unless the immediate state is standardized before delayed testing.

### Null credibility
The first four models have no causal seed effect on reopened choices. Their exact-test support fractions are 0.050, 0.048, 0.049 and 0.034, consistent with nominal one-sided 0.05 and discreteness. Even strong pre-existing individuality and route attractiveness do not create a persistent spurious seed association when seed routes are balanced independently.

## A deeper identification theorem beyond the reset audit

Consider a learned-state model in which post-randomization experience T produces a latent personal parameter \(\theta_i(T)\) with law H, and future trajectory/route observations Y have conditional law F(Y|\theta_i(T),T).

Construct a *gated inherited-state* model in which all potential latent states \(U_i(T)\) with the same joint law H are already fixed before randomization; treatment T only selects which latent state is expressed. The observable conditional joint distribution of every sequence of predeclared post-treatment P1, S2, matched delayed outcomes can be identical under the two models.

This is an observational equivalence claim, **not an inference that bats have genetically specified all potential routes**. It shows the *origin* of the latent parameter cannot be read off from P1 plus repeated/post-reset correlations alone.

Randomizing the arbitrary route identity S separately from T establishes a different, better-defined causal estimand: whether independently assigned specific route experience alters **later choice of that assigned route** under the same post-reset four-route opportunity.

## Interpretation and experiment firewall

1. A supported future route-seed test would reject a **pure route-fixed predisposition independent of randomized route experience** as a complete explanation for that measured delayed seed effect.
2. It would NOT yet prove hippocampal memory storage, physiology, optimality, a unique 2D personal flight law, or ecological fitness benefit. Differential reward, route salience, sensory priming, early commitment, and higher-order route-memory states require independent controls.
3. S2 with matched forced R1 in both original families, as explored in \`prospective/solution-repertoire-history-reset-v1\`, adds a proper randomized opportunity contrast but still does not separate **treatment-gated stable predisposition** from truly newly formed latent route preference without an independent randomized which-route input.
4. Candidate seed study would be *new protocol/version*, not a post-hoc redefinition of PR #72. It needs geometry/payoff matching, schedule/sham, ethical/welfare pilot approval, no-interference and tracking checks, sample-size design, and individual route assignment before any outcome exposure.
5. Measured **flight cost, energy expenditure or task payoff** must ultimately be linked to randomized history if the biological claim is adaptive specialization. A significant association with the seed by itself is path dependence, not fitness.
6. The present synthetic rejection fractions depend on the deliberately chosen seven models. They cannot be portrayed as actual bat effect sizes, biological power estimates, or evidence that persistent preference is formed in nature.

## Next empirical contrast
Fresh randomized seed S_i \(\rightarrow\) controlled initial route experience with balanced reward \(\rightarrow\) matched open experience \(\rightarrow\) forced common R1 state (or prospectively justified other reset) \(\rightarrow\) fixed early reopening free-route trials. Compare probability of using assigned S_i, under restricted blocked randomization, against observed behavior under the sharp null of no seed effect. If this works, separately measure whether that route yields higher payoff or simply persists despite switching costs.

The decisive distinction is between **recognizing the same bat after disruption** and **demonstrating that arbitrarily assigned personal history made that bat choose a different route**.
