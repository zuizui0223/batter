# Orthogonal route seed versus motor practice — prospective synthetic design v1

## Evidence status, versioning, provenance
**SYNTHETIC COUNTEREXAMPLE / EXPERIMENT PLANNING ONLY. No bat data.** This is a distinct branch rooted in PR #83, and it makes no change to PR #72 original preregistered P1/P2, JAE v0.4, PR #81, #82, or #83 results. Source outcomes from prior controlled bat archives must not be mined to choose this design.
All parameters, code-counts, randomization mechanisms and decision rules below are frozen *before* running simulated outcomes.

## Scientific questions
1. Can randomized forced **practice** on route P, assigned independently of an earlier randomly **seeded** route S, change route choice and measurable performance while preserving the two origins as distinct causal assignments?
2. Does positive practice→performance and positive practice→choice prove that improved motor performance *mediates* the new route preference? **No:** two incompatible biological causal stories can generate identical outcomes under both independent randomizations and generic route cost shocks.
3. Under which prospective assumptions could a *skill-mediation* claim be pursued with a further intervention?

## Balanced crossed assignment
- Hypothetical N=20 bats in 5 complete four-bat blocks; 4 feasible routes (0,1,2,3).
- Within each block randomly assign each seed route once by a uniform 4! permutation.
- Independently assign practice routes **P != S** by a uniform derangement relative to the block's seed permutation: exactly 9 allowed derangements per block; each practice route occurs once per block.
- Conditional on realized S and block structure, the **exact practice-assignment null** has 9^5=59,049 legal assignments. No unrestricted practice-label shuffling, no seed-label permutations in the practice p-value.
- Under this derangement, expected practice hit rate is *not 25%*: the exact null conditions on seed and all route-choice targets. A practice route is equally likely to be any of the other 3 routes. Therefore the conditional expected fraction of P choices is (1/3) times the fraction of all observed choices that are NOT on S. Use exact block permutation distributions, not a naive one-quarter baseline.
- Pre-register the actual route exposure and handling controls, feasible airspace, welfare thresholds and independent trial counts before an animal study; 20 animals, 8 target trials and 2 cost assays per route below are illustrative synthetic settings, NOT approved animal workload.

## Exact statistic
For eight late four-route choice opportunities per bat, let c[i,r] count observed route r.
Observed practice-hit H=sum_i c[i,P_i].
For every block, enumerate the 9 allowed P permutations given S, obtain the distribution of integer hit counts 0..32; convolve across 5 blocks to give an **exact** null probability mass function over 59,049 assignments. One-sided p=Pr(H_null >= H_obs), counting ties; positive decision H observed exceeds conditional null expectation and p<=0.05.
Compare against direct enumeration of 9²=81 assignments in a 2-block synthetic self-test.

A cost-gain endpoint is frozen descriptively: before and after practice, record all-route performance c0[i,r] and c1[i,r]; practice-associated improvement G_cost = mean_i(mean_{r != P_i}(c1-c0)[i,r] - (c1-c0)[i,P_i]). The measured cost is **hypothetical**, not a proxy validated for real energy use. For model verification check exact expected G_cost=gamma and 0.

## Synthetic counterexample parameters
- R=1,000 independent synthetic experiments per condition, 20 animals, eight choice trials per bat.
- Root numpy SeedSequence seed 202610081616; independent replicate streams within each scenario. The two rival SKILL_CAUSES_CHOICE/FAMILIARITY_CAUSES_CHOICE worlds share the **same** scenario and replicate streams by design; other scenario streams are independent. NumPy 2.3.5.
- Each animal has pre-existing (unseeded) route preference u[i,r] ~ Normal(0,0.45); independently assigned route seed S confers direct preference bias h_S=1.2, equal across models.
- Practice effect if enabled: eta=1.8 choice-utility units on assigned practice route P; practice-associated physical saving gamma=0.3 synthetic cost units. Set inverse cost sensitivity a=eta/gamma=6. Thus choice utility contribution eta I(r=P) is numerically identical to a*gamma I(r=P).
- Base physical costs c0[i,r]=1+individual_offset_i+route_offset[i,r], with normal SD 0.07 and 0.025 respectively.
- External safe hypothetical route-cost perturbation D[i,r] drawn independently from Uniform(-0.10,0.10) and held fixed between paired worlds. The **physical** cost becomes c1-D? To avoid sign confusion, D is **added** to route cost in the late choice context. Both causal models use the same direct cost coefficient -a*D in utility.
- End-of-practice physical cost is c1[i,r]=c0[i,r]-gamma I(r=P) when skill enabled; else c1=c0.
- Given route seed and practice, choice probability:
  q[i,r] ∝ exp(u[i,r] + h_S I(r=S) + eta I(r=P) - a D[i,r]).
- Draw eight routes using a shared uniform random array between the two rival models.

## Five frozen scenarios
1. BASELINE_NO_PRACTICE: P assigned but has no physical gain and no choice effect.
2. SKILL_CAUSES_CHOICE: P training lowers true cost by gamma=.3, and choice uses its physical saving (eta=a gamma).
3. FAMILIARITY_CAUSES_CHOICE: P training lowers true cost by the same gamma incidentally, but P preference eta is from practice-induced familiarity, *not caused by skill*; same observed cost and same choice q, for every possible external route-cost D.
4. PRACTICE_SKILL_ONLY: cost saving gamma=.3, no practice-associated choice increment.
5. PRACTICE_FAMILIARITY_ONLY: choice increment eta=1.8, no physical saving.

For scenarios 2 and 3, use exactly the same assigned S/P, u, D, costs, choice random numbers, resulting choices, exact H p, and measured cost endpoints **within each simulated paired replicate**. Their likelihood over every observed variable and intervention D is identical by construction, despite different causal parent of the practice preference.

## Frozen reported metrics
For all five scenarios: 1000 synthetic-run rejection fraction (H greater than conditional null expectation and exact p<=.05), mean absolute H, mean excess H over exact conditional null expectation, mean practice-specific true cost saving G_cost, MC binomial SE, mean observed practice hit rate and mean seed hit rate.
For SKILL_CAUSES_CHOICE and FAMILIARITY_CAUSES_CHOICE, assert exact equality of every replicate's observed assignments, route sequence, external D and all-route pre/post physical costs and exact practice p.
Preflight checks before numerical outcomes:
- 24 seed permutations/block and exactly 9 derangements for P given S, 59,049 legal P assignments conditional on S, all assigned balanced.
- Two-block 81-assignment exhaustive check equals exact block-convolution histogram; five-block histogram sums to 59,049.
- Conditional practice-hit null mean matches (total nonseed route hits)/3 for arbitrary synthetic route counts.
- Zero unmodeled direct P route effect for baseline and SKILL_ONLY; `choice` generative mechanism definition fixed.

## Interpretive ceiling
Randomizing practice can identify a **causal total effect of extra route-specific practice on later route use** and **another total effect on measured motor performance**. It does NOT, by itself, identify a causal *mediated share*, because practice may separately change familiarity, expectation or reward salience.
Even changing external route cost D does not separate the skill-mediated and skill-correlated-familiarity models when both have cost-responsive behavior: `eta=a gamma` gives identical predictions for every D.
A genuine mediator intervention would have to independently manipulate the accumulated **skill state** while holding the sensory cue, route familiarity, immediate reward and expected exertion components fixed, or else state an empirically defensible exclusion/identification assumption. This is not guaranteed feasible/ethical in bats. If impossible, retain the conservative claim 'practice causally changes choice and performance' rather than 'performance mediates choice'.
Fitness claims require naturalistic tasks and calibrated energetic/intake/risk measures, not an experiment with synthetic cost units.
