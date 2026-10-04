# Mechanism synthesis: portable personal flight policy v1

## Status

**POST-PRIMARY SYNTHESIS.**

This document integrates completed frozen and post-primary diagnostics without upgrading exploratory analyses to confirmatory status.

It does not modify JAE v0.4.0.

---

## Current biological question

JAE established that persistent individual vertical organization does not require persistent spatial partitioning.

The mechanistic question became:

> **What carries individual specialization if other individuals do not need to keep excluding one another from space?**

The accumulated evidence now distinguishes several candidate architectures.

---

# 1. Persistent individuality is not simply persistent spatial exclusion

JAE v0.4.0:

- individual history predicts later vertical organization;
- persistence survives multi-day separation;
- coarse place and broad movement-state matching do not remove it;
- same-night conspecific use does not generally replace self-history;
- positive contemporaneous separation beyond the null is unsupported;
- the post-hoc upper bounds make large additional co-use separation difficult to reconcile with the data.

Thus the maintenance carrier is attached to the individual more strongly than to an exclusive spatial compartment.

---

# 2. The carrier is already present early; a common slow formation ramp is unsupported

Harten first-flight prospective programme:

- the predeclared common monotonic growth of self-history advantage was not supported;
- later self-history predictability was positive for most juveniles;
- self-history advantage was already positive at the earliest estimable stage.

Thus the best current description is not:

`weak individuality -> slow common strengthening -> adult specialization`.

A more compatible architecture is:

`rapid differentiation / early lock-in -> persistent reuse`.

This does not identify whether the early differentiation is learned, developmental or performance-constrained.

---

# 3. Broad early environmental enrichment does not measurably set the carrier strength

Rachum randomized early-experience programme:

- nightly behavioural strategy is individually repeatable/history-dependent;
- the randomized enriched-versus-impoverished treatment contrast on the new history-carrier endpoint was not supported.

Therefore broad captive environmental enrichment is not supported as the dominant cause of later history-carrier strength under that experiment.

This does not reject more specific learning histories.

---

# 4. A portable movement policy survives changes in obstacle configuration

*Teshima et al.* / *Rhinolophus nippon* configuration-conditioned primary:

## Movement-policy transfer

Primary B:

- `K = +0.94356`;
- 5/5 bats positive;
- permutation `p = 0.0001`.

The signature transfers across seven different obstacle configurations after removing each environment's mean and scale.

Leave-one-environment diagnostics:
- movement-policy statistic remains positive with 5/5 positive bats after dropping every environment in turn;
- therefore the result is not carried by one exceptional arena.

This is currently the strongest direct evidence for a **portable personal policy/performance state**.

---

# 5. Literal route shape is not the primary carrier

The absolute-coordinate same-configuration route primary was positive.

However post-primary diagnostics changed its interpretation:

- start-centered route identity: unsupported;
- chord-residual route identity: unsupported;
- start point alone: unsupported;
- end point alone: unsupported;
- displacement vector alone: unsupported.

Axis decomposition showed that absolute arena placement/lane contributes, but a translation-invariant personal route-shape template is not robustly supported.

Therefore the evidence is inconsistent with the simplest story:

> each bat memorizes one literal geometric route and repeats that curve.

The carrier is more abstract than a fixed path.

---

# 6. The portable movement signature is not just one speed scalar

Post-primary decomposition:

- performance-magnitude-only transfer is strong;
- steering/efficiency-only transfer is weaker but supported;
- leave-one-feature-out removal of any one original movement feature leaves the full signal positive.

Geometry-only diagnostic removes:
- elapsed time;
- speed magnitude;
- absolute path length;
- absolute vertical scale.

It still gives:

- `K_geometry = +0.38857`;
- 5/5 bats positive;
- descriptive permutation `p = 0.0153`.

Thus a scale-free maneuver-geometry component exists in addition to performance magnitude.

However its target-environment profile is more context dependent than the full movement-policy signature.

Therefore the most defensible current wording is:

> a stable individual movement policy contains both performance-scale and maneuver-geometry components, with the latter more configuration-sensitive.

---

# 7. Echolocation timing is individually repeatable, but its independence from movement is not established

Pulse-only cross-configuration identity was strong:

- `P = +0.66335`;
- 5/5 positive;
- `p = 0.0014`.

Pulse decomposition showed identity in:
- overall pulse rate;
- IPI structure without pulse rate;
- IPI variability;
- central/quantile IPI timing.

Simple same-data residualizations also retained pulse identity after movement/route predictors.

However the stricter **cross-fitted nuisance-control** diagnostic did not support an independent residual pulse identity:

- `P_crossfit = +0.11791`;
- 3/5 positive;
- `p = 0.2032`.

Therefore the current evidence does **not** justify claiming an autonomous sensing-style component beyond movement policy.

The correct bounded interpretation is:

> echolocation timing covaries with individual identity across environments, but current data do not establish that this information is independent of the individual's movement/route policy.

---

# 8. Simple body mass is not a supported explanation, but morphology remains unresolved

Separate adult-panel morphology diagnostics:

- predicted body-mass donor-gradient supported in 0/4 evaluable panels.

Thus simple body mass does not generally explain transfer of individual vertical organization.

For the five *R. nippon* obstacle-flight bats, exact same-individual morphology attribution is currently blocked:

- obstacle archive IDs: A–E;
- evsBat archive exposes five numeric *R. nippon* identifiers: 2670, 2681, 2860, 2868, 2899;
- no reproducible source crosswalk has been recovered.

Therefore morphology cannot be assigned by matching sample size.

Wing shape, wing loading, muscle state, sensory morphology and other stable traits remain viable mechanisms.

---

# Current best architecture

The accumulated evidence is best summarized as:

`stable portable personal movement-policy prior × current task geometry/history -> realized route`.

The realized route is environment specific.

The policy prior is more stable than the route itself.

Persistent individual specialization therefore does not require individuals to maintain different spatial territories or lanes at all times.

Instead, individuals can enter overlapping space while solving movement tasks through different persistent control tendencies.

---

# What "history dependence" now means

The results no longer support using "history dependence" as shorthand for:

> memorizing a single route.

A better interpretation is:

> past experience and stable individual constraints place each animal in a persistent region of policy space, from which task-specific trajectories are generated.

The available data cannot yet separate how much of that policy state is:
- developmental;
- learned;
- morphological;
- physiological;
- genetically constrained.

---

# Strongest next mathematical question

The next discriminator is the **dimensionality of the portable policy state**.

If the eight observed movement features can be compressed to one or two training-derived latent axes while retaining held-out-environment identity, then the system is consistent with a low-dimensional personal control state.

If identity requires many dimensions, or only nonlinear representations succeed, the policy is distributed.

This is frozen separately in:

`LATENT_POLICY_DIMENSIONALITY_CONTRACT_V1.md`.

---

# Current claim ceiling

Supported:

> Persistent bat individuality can be carried by a portable individual movement-policy signature rather than by persistent spatial exclusion or a fixed memorized route.

Not yet supported:

- the policy is learned;
- the policy is innate;
- the policy is caused by morphology;
- the policy is a unique low-dimensional attractor;
- echolocation has an independent identity component after cross-fitted movement control;
- a particular mathematical control law is uniquely identified.
