# Randomized route-seeding discriminator — prospective mathematical and synthetic contract v1

## EVIDENCE STATUS
**NEW EXPERIMENT PROPOSAL / SYNTHETIC DESIGN STRESS. NO ANIMAL OUTCOME.** This branch does not modify the JAE v0.4.0 freeze, existing PR #72 P1/P2, its randomized treatment sequence, or PR #81's already-completed memory/inertia stress test. Do not merge this idea into current P1 or conduct it in the same confirmatory animals without a completely new approved protocol. The base branch is prospective/solution-repertoire-manipulation-v1.

## Biological identification problem
We seek to distinguish **newly acquired, route-specific individual information** from **a pre-existing personal preference made visible by a treatment**, not just from first-order autocorrelation.

Exact observational-equivalence counterexample:
- Formation model: treatment T is assigned and an individual persistent route parameter theta_i(T) is created, with its joint distribution across assigned families H; future behavior/reopening is generated from F(theta_i(T), physical scene).
- Gated predisposition model: prior to randomization the individual already possesses potential route parameters U_i(T) with precisely the same joint law H; T merely selects which latent potential is expressed; future behavior/reopening is generated from the same F(U_i(T), scene).
- Any observed post-treatment probability law, including repeated probes, route reset, P1 and a matched delayed P1-like contrast, is identical for these models. Without a manipulation of the specific history that determines route preference, the **time or causal origin of the parameter is not identified**. Randomization of T can identify an average effect of T, but not classify a resulting latent parameter as newly formed.

## Candidate *distinct* prospective manipulation (not yet a registered animal experiment)
Before the formation assay in a fresh experimental cohort, independently randomize **which of four equally feasible routes is initially experienced or cued**. Seed route S_i in {R1,R2,R3,R4} is assigned in complete four-animal blocks (one assigned to each route per block), with equal handling/reward and equal physical opportunity after that controlled initial exposure. Do not let an individual's self-chosen route or measured predisposition determine S_i.

The mechanistically useful target is delayed influence of an **arbitrary assigned history** after all animals undergo the same forced-route R1 and after free access to the four routes is restored. This setup can separate pure route-fixed predisposition and a shared first-order route state from a route-specific lasting history effect, conditional on the chosen physical/reward controls. The forced reset is NOT assumed to erase long-term memory.

Do not claim seed-induced delayed preference is necessarily memory storage: attentional priming, differential familiarity, differential route-specific practice, or learned affordance all remain viable. Its causal interpretation is narrower: a randomly manipulated *which-route* experience affects subsequent personal route use.

## Frozen synthetic architecture (all hypothetical)
- N=20 virtual animals in five four-animal randomized blocks.
- K=4 routes.
- Within every block assign exactly one animal to each seed route via a random 4! permutation; all 24^5 route-assignment combinations are legal.
- 8 post-reset OPEN choice flights per animal, no re-training or late-window selection; sample size is a hypothetical pilot dimension inherited from PR #72's target 20 and existing 8-flight re-expression proposal. It does not freeze animal welfare/trial counts.
- All animals forced on the same canonical R1 immediately before the reopening phase; for the Markov competitor it resets the immediate observable route state.
- Each animal receives a pre-existing stable route preference b_i (Dirichlet with each concentration .35) except the pure short-memory competitor.
- Route seed S_i is orthogonal to b_i by restricted randomization; a physical route may still have common attractiveness.

## Frozen synthetic mechanisms
Exactly 1000 independent simulated experiments per scenario, seven total, with root NumPy PCG64 seed 202610081401. Independent per-scenario and per-replicate SeedSequence substreams. Report per-scenario mean observed statistic, test-rejection fraction, binomial Monte Carlo SE, and full integer-count distribution summary.

1. TRAIT_ONLY: route choices across opening and reopening independently follow pre-existing b_i. No influence of random seed.
2. TRAIT_WITH_ROUTE_ASYMMETRY: b_i drawn from a Dirichlet concentration vector [1.6,0.6,0.5,0.3] (nonuniform physical attractiveness), but no seed effect. Exact randomized inference must remain valid under asymmetric baseline routes.
3. GATED_PREDISPOSITION: individuals have stronger pre-existing latent propensities than (1): b_i drawn from Dirichlet with all .12; treatment would expose b_i but the **independently randomized seed has zero effect**.
4. MARKOV_WITH_RESET: all individuals share rho=.95 in P(next=same route) mixture; after common forced R1 the subsequent eight reopened routes use that shared transition kernel. No seed-specific personal preference.
5. HISTORY_IMPRINT_WEAK: same b_i as (1); after assigned experience a persistent route mixture q_i=(1-lambda)b_i+lambda delta_(S_i), lambda=.15, generates all 8 reopened choices after forced R1. This is a *hypothetical latent state*, not measured learning.
6. HISTORY_IMPRINT_STRONG: same but lambda=.35.
7. MARKOV_NO_RESET (diagnostic counterfactual): everyone shares rho=.95 but reopening starts directly from their randomized seed route without common forced R1. This isolates why reset is necessary. It is not a test of a durable personal strategy.

**Seven scenarios including the last diagnostic.** Do not relabel the diagnostic as a distinct ecological species or empirical sample.

For mixture Markov transition:
Pr(X_(t+1)=r|X_t=s)=rho I(r=s)+(1-rho)/4.
When reset, initial state is fixed R1 for all bats, otherwise initially randomized seed S_i.

## Primary simulated statistic and exact blocked inference
Define integer counts c_(i,r) among the eight post-reset target choices.
- observed seed-hit total H_obs = sum_i c_(i,S_i);
- effect statistic T = H_obs/(N*8) - 1/4;
- against the *sharp null of no effect of seed assignment on any individual's target outcomes*, reassign seeds among the same four animals within each block, keeping all target outcomes fixed. There are exactly 24^5=7,962,624 legal assignments.
- no randomization Monte Carlo is needed: for each four-animal block enumerate its 24 possible seed mappings, compute the integer hit-count contribution for each, tabulate the 33-category contribution histogram, and convolve five block histograms. Exactly 24^5 assignments are counted.
- exact one-sided p = (# null assignments with H>=H_obs)/(24^5); positive decision requires T>0 and exact p<=.05. No outcome-based adjustment or tuning.
- report fixed N, routes, Q=8, exact assignment count, and all scenario-specific positive decisions.

## Pre-result invariant gates
1. Show each block's 24 unique route mappings and exactly 24^5 legal allocations.
2. For a synthetic toy with 1 block, verify integer-histogram convolution yields the same full null histogram as exhaustive permutation enumeration; extend to 2 blocks and verify against 576 brute-force assignments.
3. Every block's histogram sums to 24; combined histogram sums to 24^5.
4. Under every assignment the population seed use is balanced (five assignments per route).
5. The no-seed trait-only potential outcomes do not access the randomized S.
6. For common Markov reset all animals start at the same R1 state, independent of S. In the no-reset diagnostic they start at S.
7. Under independent balanced randomization the sharp-null test's synthetic rejection rates should not systematically exceed nominal .05 beyond simulation uncertainty; do not change test after seeing output.

## Interpretive boundaries
The imprinting models trivially assume the randomized first route affects later route preference. A higher simulated detection fraction is a test of *this design's ability to observe a hypothesized effect*, not a discovery about bats or proof of a certain psychological mechanism.

There is no biological experiment, observation or claim that the animals do follow these equations. Route affordance equality, tracking, handling, welfare, exact trial counts, washout/sham and sample size require pilot/facility review before any registration. The existing original PR #72 test remains unchanged. A separate prospective allocation design and testing protocol would be required to implement this idea.
