# History-reset identifiability audit v1 — P1 is not a storage test

## Evidence tier and firewall

**Synthetic design stress test; no real-animal outcome used.** This document is a prospective-protocol *critique*, not a new bat finding and not an amendment of the frozen P1/P2 analysis in [PR #72](https://github.com/zuizui0223/batter/pull/72). It is a standalone post-design note. The original JAE v0.4.0 paper, PR #72 primary, and previously opened Rhinolophus sources remain untouched.

### Question

The existing randomized OPEN-versus-CONSTRAINED acquisition experiment tests whether free solution opportunity during acquisition increases 8-early-to-8-late individual route predictability under the same currently open four-route task.

It **does not by itself identify the storage of a durable individual-specific route policy**, because adjacent early and late flights can agree through finite-lag Markov route inertia without any stable individual trait or personal history variable surviving a forced reset.

Two distinct causal generative processes can pass the original P1:

- **Acute inertia**: exposure changes only within-probe transition stickiness; route at flight t predicts t+1, but forcing every bat through the common R1 route erases the earlier route state.
- **Latent route preference**: acquisition modifies the animal-specific probability distribution over feasible routes, and this personal distribution can reappear after a period of forced common behavior.

Both produce a positive early-to-late own-history log score relative to same-family donors. Only the second makes the stronger storage/re-expression claim.

## Exact synthetic counterexample

Use the frozen PR #72 P1 formula, not a newly selected estimator:

- N=20 animals, five complete four-animal randomization blocks;
- two counterbalanced topology-matched families A and B;
- four discrete routes R1–R4;
- 16 OPEN-probe flights/family: 8 early, 8 late;
- symmetric Dirichlet 0.5 smoothing and own minus mean same-family donor late-trial log-score;
- treatment effect of OPEN-acquired versus CONSTRAINED-acquired family, exact 4^5=1,024 restricted assignments;
- one-sided p<=0.05; 500 independent simulation replicates (seed 202610081737).

**Acute memory-only counterexample.** All animals have identical first-order four-route Markov transition laws, with no individual parameters. Upon common OPEN probe entry the first route is uniform; later flights persist on the previous route with probability 0.95 after OPEN acquisition versus 0.25 after CONSTRAINED acquisition; alternative routes are equiprobable. In this model acquisition affects *only the immediate transition dynamics*. After forced R1 all animals start reopening from that identical state, independently of pre-suppression individual history.

**Persistent personal propensity**. Each animal and family draws a fixed four-route probability vector used both in the 16-flight OPEN probe and after forced R1. OPEN-acquired vectors are Dirichlet(0.15,0.15,0.15,0.15), CONSTRAINED-acquired vectors Dirichlet(4,4,4,4). Trials are independent conditional on that personal distribution.

**Negative controls**. Under a no-treatment scenario, both families have persistent individual-specific Dirichlet(0.6 each) preferences, and a second null has uniform route choice without Markov persistence.

### Synthetic results (500 replicates/scenario)

| Data-generating process | P1 positive and exact p<=0.05 | Mean P1 Delta_R | OPEN-only own-vs-donor identity after forced R1 | If BOTH families are identically forced and reopened: mean delayed randomized treatment Delta | P1 AND delayed exact p<=0.05 |
|---|---:|---:|---:|---:|---:|
| Persistent pre-existing traits in both arms; no acquisition effect | 0.062 | -0.004 | +0.734 | -0.010 | 0.020 |
| Uniform Markov without acquisition effect | 0.048 | +0.001 | -0.003 | +0.008 | 0.002 |
| **Acquisition changes immediate Markov inertia only** | **0.856** | **+0.659** | **-0.004** | **-0.673** | **0.000** |
| Fixed predisposition + acute inertia (no acquired durable personal parameter) | 0.098 | +0.023 | +0.734 | -0.572 | 0.000 |
| **Acquisition creates persistent personal propensity** | **1.000** | **+0.807** | **+1.436** | **+0.799** | **1.000** |

These numbers are **simulation-specific proof of non-uniqueness**, not estimated bat effect sizes, general statistical power, animal behavior observations, or an argument to change the original P1 outcome definition. Results depend on arbitrarily illustrative transition and Dirichlet values.

In the acute-Markov construction, P1 often passes although **no bat has any stored personal route preference**. This is not a type-I error: the randomized opportunity truly changes short-term route persistence. The problem is interpreting this as evidence of durable individuality.

Sensitivity within the acute-Markov construction (350 repeats each, held constrained p_stay=0.25): OPEN p_stay=0.80 gives P1 rejection 0.014; 0.90 -> 0.354; 0.95 -> 0.871; 0.98 -> 1.000. It is not enough to show a positive P1 alone to identify which underlying process occurred.

The inherited theory branch `prospective/decentralized-route-theory-v1` already contrasts finite-lag decay against personal route propensities. This audit demonstrates the practical identifiability consequence for the actual preregistered P1 estimator.

## Why current Phase 3–4 is not yet sufficient for a strong causal storage claim

PR #72 suppresses and reopens **only the formerly OPEN-acquired family**. A positive OPEN-only reopening self-history signal would show *within-arm reappearance*, but not necessarily that randomized acquisition *created* the stable signal: the negative-control model with pre-existing propensities has a strong positive OPEN-only history score despite no treatment effect. The experiment needs a matched counterfactual for the **delayed** signal, rather than an OPEN-only test.

The obvious response is **not** to promote the post-outcome synthetic scenarios into new confirmatory thresholds. It is to consider a before-collection **v2 mechanism design** with identical suppression and reopening in BOTH A and B, while preserving P1 exactly.

## Proposed causal delayed-history discriminator (NOT YET AUTHORIZED FOR CONFIRMATORY USE)

### Additional mirrored intervention
After the frozen common-OPEN P1/P2 probe, force R1 in **both** A and B families under the same predeclared number of valid flights, identical timing/rest/reward conditions and matched reopening schedule. After a predeclared pause, restore all four original routes in both families; record a fixed number of reopening flights in each, with both family orders counterbalanced.

The physical obstacle scale, welfare load, fixed suppression/reopening counts, sample N, animal-tracking threshold, blinding and source hashes must be frozen **before any new confirmatory outcomes**. This addition entails greater trial burden, and requires animal-welfare/pilot approval. Do not add it silently to PR #72 or bypass pilot feasibility.

### Treatment-blind delayed family score
For each bat i and family f:
- From the **existing early eight common-OPEN probe flights**, compute fixed categorical personal history p_i,f(r) with the inherited Dirichlet 0.5 smoother.
- For each later *post-reset* reopening route r, score `log p_i,f(r) - mean_{j != i in same family} log p_j,f(r)` using **all other eligible bat histories** in the same physical family, independent of acquisition-treatment labels.
- Average over the frozen reopening flights to obtain `D_i,f`, a personal re-expression score.
- Compute the matched randomized treatment contrast `Delta_D = mean_i [D_i,OPEN-assigned-family - D_i,CONSTRAINED-assigned-family]`.
- Under the original four-animal restricted assignment space, leave fixed all outcome data, family scores, starting-order labels and animals; relabel treatment only. Calculate the exact one-sided 4^B assignment p-value.

This is **acquisition-history dependence after equal current opportunity, equal forced intervention and equal reopening**. If the latent preference is persistent it can produce a positive Delta_D. If the original P1 comes only from short-term Markov inertia whose entire predictive state is reset to R1, no positive delayed persistence is expected under this constructed model.

An alternative delayed result does not establish a neural storage location, an exact learned differential equation, or a wild 3-D niche consequence. Other unobserved durable mechanisms remain possible.

### Required inference hierarchy before real outcome opening
To make Delta_D a new confirmatory test, the whole experiment must be versioned and its sequence/error control frozen before collection. A bounded option is P1 primary -> delayed Delta_D conditional on P1 -> inherited I/M P2 as another gated secondary. Existing P1 and P2 are untouched unless a separate formal v2 preregistration is approved. No multiple-testing adjustment is retroactively applied to a frozen result.

If modifying the trial burden is infeasible: leave PR #72 as-is and **restrict conclusions**:
- P1 can causally demonstrate acquisition opportunity changing short-horizon route individuality/predictability.
- Existing OPEN-only reopening can suggest re-expression after suppression, but it is not a randomized causal treatment contrast on storage and cannot exclude fixed predisposition.
- Do not claim that durable history-specific information was causally acquired or stored.

## Decision

**DESIGN_NONIDENTIFIABILITY_DEMONSTRATED.** A first-order short-memory generator can pass P1 at high probability without possessing the latent individual memory that the study ultimately seeks.

**Next scientifically valuable step:** prioritize the paired forced-reset and matched delayed-treatment contrast, subject to feasibility/ethical constraints, rather than another same-archive Rhinolophus parameter search or one more generic identity-retention dataset.
