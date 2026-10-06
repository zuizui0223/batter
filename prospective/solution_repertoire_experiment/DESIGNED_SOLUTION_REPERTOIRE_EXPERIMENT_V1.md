# Designed solution-repertoire manipulation v1

## Status

**PROSPECTIVE STRUCTURAL EXPERIMENT DESIGN. NO NEW OUTCOME DATA OPENED.**

Purpose:
test the causal formation hypothesis that multiple feasible movement solutions, combined with personal history, can generate and preserve individual-specific movement policy.

This is the first authorized mechanism route after the same-data Rhinolophus geometry ceiling.

It does not modify JAE v0.4.0 and does not reopen the failed wild field bridge.

---

# 1. Biological hypothesis

The mechanism programme currently supports:
- personal-history refinement;
- portable individual movement information;
- context-dependent fine-maneuver realization;
- persistence of individual bias across a reversible sensory perturbation.

What remains untested is:

\[
\text{multiple feasible solutions}
\times
\text{personal history}
\rightarrow
\text{individualized policy}.
\]

Primary biological hypothesis:

> **When several approximately equivalent flight solutions are simultaneously feasible, repeated experience will cause individuals to settle into reproducible personal policies; when the solution set is collapsed, expression will converge, and when the previous repertoire is restored, prior individual organization will reappear.**

This separates:
- existence of multiple solutions;
- formation of individual preference/history;
- temporary suppression of expression;
- persistence/re-expression of the underlying personal organization.

---

# 2. Core design

Use the same identified bats across modular obstacle environments in which the number and structure of feasible routes are experimentally known.

Required causal sequence:

1. constrained baseline;
2. open multi-solution acquisition;
3. constrained suppression;
4. exact multi-solution reopening;
5. geometry-transformed transfer.

No post-hoc choice of obstacle layouts based on observed individuality.

---

# 3. Environment architecture

## C1 — constrained

One broad feasible corridor.

Purpose:
- shared-solution control;
- estimate condition-level movement shift;
- verify flight competence;
- create a state in which route-choice individuality is structurally suppressed.

## C2 — two-solution

Two approximately equivalent corridors.

Match before animal outcomes are opened:
- minimum gap width;
- shortest-path length;
- total turning demand;
- vertical displacement demand;
- obstacle material;
- reward.

## C4 — four-solution

Four approximately equivalent corridors.

The additional solutions must be true route alternatives, not small perturbations of one opening.

At least two dimensions of route structure should vary so the four alternatives do not reduce to one left-right choice.

## Reopened C4

Restore the exact physical C4 layout after a constrained block.

Purpose:
test whether prior personal organization reappears after its expression was temporarily restricted.

## Transformed C4

Mirror, rotate, or otherwise relabel the physical positions of the same route classes while preserving difficulty as closely as possible.

Purpose:
distinguish:
- absolute room-location memory;
- exact-path memory;
- more abstract movement-policy portability.

The transformation must be fixed before the first animal enters the study.

---

# 4. Required phase sequence

## Phase A — constrained baseline

C1.

Goal:
establish shared competence and baseline movement coordinates.

## Phase B — multi-solution acquisition

C4.

Goal:
observe whether individual route/policy organization emerges with repeated experience.

The formation comparison is early versus late Phase B.

## Phase C — constrained suppression

Return to C1.

Goal:
remove the opportunity to express multi-route choice while retaining biological identity.

This phase is not assumed to erase memory.

## Phase D — exact reopening

Restore the exact Phase-B C4 geometry.

Primary storage/re-expression test:
does late Phase-B individual organization predict the earliest admissible Phase-D behavior?

## Phase E — transformed transfer

Use transformed C4.

Goal:
test which part of personal organization transfers when exact route coordinates change.

---

# 5. Capability control

A major confound is that an individual may avoid one route because it cannot physically negotiate it.

Before free-choice inference is opened:
- each route class must be demonstrated to be physically traversable by each individual under a standardized route-isolation or equivalent guided block;
- route-specific collision/failure rates must be recorded;
- an individual is not eligible for free-choice inference if structural inability makes one or more nominal alternatives infeasible.

Do not redefine the solution repertoire using free-choice outcomes.

If many bats cannot traverse all nominal routes, the environment fails structurally and must be redesigned before confirmatory data collection.

---

# 6. Data representation

Keep route identity and movement policy separate.

## 6.1 Route-choice state

For every free-choice flight record:
- route class;
- success/failure;
- trial index;
- phase;
- obstacle configuration.

Route classes are defined from obstacle topology before trajectory outcomes are opened.

## 6.2 Coarse portable policy

Retain the interpretable movement summary:

\[
\theta_{i,t}=(I_{i,t},M_{i,t}),
\]

where:
- I = FlightIntensity;
- M = ManeuveringExtent.

Feature definitions must be frozen from the existing programme or independently fixed before new data are scored.

Do not refit weights to maximize identity in the new experiment.

## 6.3 Fine realized geometry

Use a predeclared scale-free trajectory representation.

This remains an expression layer, not the primary causal carrier.

---

# 7. Primary confirmatory endpoint — re-expression after reopening

The primary outcome is not simply whether bats differ in C4.

For each individual:
- estimate late-acquisition personal state from only late Phase-B trials;
- predict the earliest admissible Phase-D reopening trials;
- compare the individual's own Phase-B history against histories from other individuals.

For policy vector theta:

\[
A_i
=
\operatorname{mean}_{j\neq i}
d(\theta_{i,D},\theta_{j,B})
-
d(\theta_{i,D},\theta_{i,B}).
\]

The distance metric is frozen before outcome opening.

Aggregate:
- equal trials within individual;
- equal individuals overall.

Positive means reopening behavior is closer to that individual's prior multi-solution policy than to other bats' prior policies.

### Null

Permute complete biological identities attached to Phase-B personal histories while preserving:
- Phase-D outcomes;
- condition;
- trial counts;
- cohort/batch;
- route availability.

The exact permutation architecture must be frozen before the outcome is opened.

### Primary support rule

Support requires all of:
1. programme-level self-history advantage > 0;
2. permutation p <= 0.05;
3. >=70% of eligible individuals have positive individual mean advantage.

No threshold relaxation.

---

# 8. Formation endpoint — history-specific refinement

Ask whether late multi-solution history predicts reopening better than an equally sized early history.

For each individual:
- early history = fixed first m admissible C4 trials;
- late history = fixed last m admissible C4 acquisition trials;
- target = early Phase-D reopening behavior.

Define:

\[
Q=A_{late}-A_{early}.
\]

The null must preserve general trial-order learning while breaking the true individual-history link.

### Q supported

Personal organization becomes more identity-informative through experience in a multi-solution environment.

### Q unsupported

Stable individuality may predate experimental history, or acquisition may be too short.

Do not redefine early/late windows after inspection.

---

# 9. Direct solution-repertoire effect

Compare identity information across C1, C2 and C4 using a representation whose null is recalibrated separately within condition.

Directional prediction:

\[
A_{C4}>A_{C2}>A_{C1}.
\]

Do not compare raw p-values across conditions.

Freeze one synchronized condition-comparison statistic before data opening.

For example:

\[
D=
(A_{C4}-E_0[A_{C4}])
-
(A_{C2}-E_0[A_{C2}]).
\]

C1 is primarily a suppression/control state. A trivial route-choice contrast against C1 must not be presented as the main evidence for solution-abundance-driven specialization.

---

# 10. Route-choice individuality — secondary

For C2 and C4:
- estimate each individual's route-choice distribution from training trials;
- score held-out trials with a proper probabilistic score;
- compare own-history prediction against pooled/other-individual prediction.

Because route-category count differs between C2 and C4, use within-condition null calibration before cross-condition comparison.

Raw entropy alone is not evidence for individuality.

---

# 11. Reopening versus transformed transfer

## Exact reopening positive

Supports latent storage/re-expression of a previously learned personal organization when the old solution repertoire returns.

## Transformed C4 positive

Supports portability beyond exact spatial coordinates.

## Reopening positive, transformed transfer negative

Supports scene/path-specific memory more strongly than an abstract transferable policy.

## Both positive

Supports a more abstract personal movement organization that survives both temporary suppression and coordinate transformation.

---

# 12. Prospective covariates

Measure where feasible:
- body mass;
- forearm length;
- wingspan / wing area;
- sex;
- age class if known;
- baseline flight performance.

These are secondary explanatory covariates.

Do not use them to define or exclude individuals after observing the identity outcome.

A biomechanics decomposition must be independently frozen.

---

# 13. Sample-size rule

The new experiment must not repeat the n=5 mechanism ceiling.

Target:
- **>=12 evaluable biological individuals** completing Phases A-D.

Preferred:
- 16 or more if husbandry and ethics allow.

Structural minimum for opening the confirmatory primary:
- **10 evaluable biological individuals**.

If fewer than 10 complete the required phases:
- return structural STOP for the primary;
- report acquisition/descriptive data only;
- do not relax the minimum post hoc.

The final planned N must be fixed before confirmatory outcome opening and justified by simulation or prospective precision analysis using the planned repeated-measures structure.

---

# 14. Trial support

Exact trial counts must be frozen before confirmatory collection.

Principles:
- enough trials per phase to estimate individual history without one-flight domination;
- same planned trial count across individuals;
- predefined rest and fatigue limits;
- no stopping an individual's trials because its preference appears stable.

Missing trials are handled by a predeclared support rule.

---

# 15. Randomization and blinding

Predeclare:
- animal order;
- configuration order where order is not biologically fixed;
- transformed-layout mapping;
- route-label coding;
- analysis seeds.

Where possible:
- trajectory preprocessing should be blind to biological identity;
- route classification should use obstacle topology, not visually inferred preferred paths.

---

# 16. Failure modes

The experiment does not support the formation hypothesis if:

1. the capability audit shows that nominally equivalent routes are not genuinely feasible for most animals;
2. C4 produces population-level route preference but little held-out individual identity;
3. individuality appears during C4 but does not reappear after constrained suppression;
4. early history predicts reopening as well as late history;
5. any apparent effect depends on one route, one animal, or post-hoc geometry relabeling.

Each is biologically informative.

---

# 17. Strongest positive interpretation

If:
- all route classes are demonstrably feasible;
- C4 produces calibrated held-out individuality;
- late history predicts reopening better than early history;
- personal organization reappears after C1 suppression;
- at least part of policy transfers under transformed C4;

then the programme may support:

> **Individual movement specialization can be generated and stored through personal history when the environment offers multiple feasible solutions; temporary removal of those alternatives suppresses expression without necessarily erasing the personal organization.**

That would directly connect functional abundance to formation and maintenance of individual specialization.

---

# 18. Claim ceiling

Even a positive experiment would not establish:
- universal applicability to all bats;
- fitness advantage of specialization;
- a specific neural storage mechanism;
- equivalence between laboratory policy and the unresolved wild vertical-individuality carrier;
- that more environmental complexity always causes more specialization.

The causal claim is specifically about experimentally manipulated feasible-solution repertoire under the tested task.

---

# 19. Why this is decisive

The current archive can show that individual information exists, transfers, and is contextually realized.

It cannot show why distinct personal policies formed.

This design changes the missing causal variable itself:

\[
\boxed{
\text{known feasible-solution repertoire}
\rightarrow
\text{history-dependent personal organization}
}
\]

and then tests whether that organization survives temporary loss of expressive opportunity.

That is information the existing archives do not contain.
