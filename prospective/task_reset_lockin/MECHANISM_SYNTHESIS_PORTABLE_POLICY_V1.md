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


---

# 9. The portable movement policy is strongly low-dimensional

The frozen post-primary latent-dimensionality programme used the same 45 *Rhinolophus nippon* trajectories and the same eight environment-standardized movement features.

Both an unsupervised and an identity-targeted route reached the same conclusion.

## Unsupervised training-only PCA

For every target obstacle configuration:
- PCA was fit using only the other six environments;
- the held-out environment never contributed to the latent axis.

A **single PC** was already sufficient:

- K = **+0.957848**;
- 5/5 bats positive;
- 9,999/9,999 valid identity permutations;
- p = **0.0006**.

The full eight-dimensional Primary-B statistic was K = +0.943560.

Thus the single unsupervised training-derived axis retained essentially the full cross-configuration individual signal.

PC1 explained only about **46.7%** of training movement variance (fold range 45.7–50.3%), so the result is not simply a trivial consequence of retaining almost all total variance.

The dominant median squared loadings were:

- median speed: 0.211;
- p90 speed: 0.231;
- median absolute vertical speed: 0.215;
- p90 absolute vertical speed: 0.230;
- median turning rate: 0.005;
- p90 turning rate: 0.074;
- path efficiency: 0.001;
- vertical range: 0.029.

Approximately 89% of the squared loading lies on the four speed / vertical-speed variables.

The dominant latent axis is therefore descriptively a **flight-intensity / vertical-performance axis**.

## Training-only individual-identity subspace

A separate procedure used individual labels only in the six training environments to estimate the between-individual subspace, then tested transfer to the unseen environment.

Again, **one dimension was sufficient**:

- K = **+0.884830**;
- 5/5 bats positive;
- p = **0.0021**.

Its first identity axis is even more strongly concentrated on:
- median and p90 speed;
- median and p90 vertical speed.

## Consequence

The portable individual movement signature is not empirically irreducible across the eight measured features.

A much better present model is:

`theta_i (dominant scalar flight-intensity tendency) + secondary maneuver dimensions`

interacting with:

`environment/task geometry`

to generate each realized trajectory.

This weakens the analogy to an inscrutable or arbitrarily high-dimensional individual rule.

It instead suggests a low-dimensional latent control architecture.

The next frozen interpretability diagnostic asks whether PCA is even unnecessary: can the equal-weight mean of the four speed / vertical-speed z-scores carry the same cross-configuration identity signal?

See:
`FLIGHT_INTENSITY_SCALAR_CONTRACT_V1.md`.

## Important ceiling

The one-dimensional axis is a behavioural latent coordinate.

It is **not yet identified** as:
- body size;
- muscle capacity;
- metabolism;
- motivation;
- personality;
- learned vigor;
- a neural control variable.

Exact same-individual morphology linkage remains unavailable.


---

# 10. A transparent scalar captures a substantial fraction of the portable policy

A deliberately non-fitted scalar was defined from the four features dominating the one-dimensional latent axis:

`FlightIntensity = mean(z median speed, z p90 speed, z median |vertical speed|, z p90 |vertical speed|)`.

No identity-fitted weights were used.

Cross-configuration held-out result:

- K = **+0.496556**;
- 5/5 bats positive;
- p = **0.0003**.

This transparent scalar carries about:
- 52% of the PCA1 K magnitude;
- 53% of the full eight-dimensional K magnitude.

Therefore the dominant individual policy is interpretable but not completely exhausted by one equal-weight vigor scalar.

The best decomposition is currently:

`dominant flight-intensity axis + secondary maneuver/geometry dimensions`.

This is consistent with the earlier result that steering/efficiency-only identity and scale-free geometry identity remain detectable.

---

# 11. Individuals occupy reproducibly ordered positions on the scalar axis

A separate frozen leave-one-environment rank test asked whether relative position on FlightIntensity is preserved across obstacle configurations.

Result:

- equal-pair order accuracy R = **0.8217**;
- null mean ≈ 0.499;
- 9/10 bat pairs above chance;
- p = **0.0048**.

The equal-environment descriptive scalar centers rank:

`A > C > B > E > D`.

Approximate centers:

- A: +1.070;
- C: +0.303;
- B: +0.175;
- E: -0.473;
- D: -0.790.

The only pair with strongly unstable ordering is B–C, whose global scalar separation is small (≈0.128).

This suggests that the most useful mathematical object is not a perfectly fixed point `theta_i`, but an individual-specific distribution around a stable scalar center:

`theta_{i,e,t} = theta_i + context deviation + within-individual noise`.

For well-separated individuals, ordering is highly stable.
For nearby individuals, secondary policy dimensions or context can reverse the scalar order.

Thus the data support a low-dimensional policy state without requiring a deterministic one-number trajectory generator.

---

# 12. The low-dimensional policy is not currently a universal bat rule

The same obstacle dataset contains *Miniopterus fuliginosus*.

Under the already-opened full eight-dimensional cross-configuration Primary-B test:

- K = **-0.0136**;
- 2/4 bats positive;
- p = **0.1687**;
- verdict: FAIL.

Thus the strong portable individual-policy result is not automatically shared by the second bat species in the same experimental framework.

A post-primary cross-species diagnostic is now frozen to ask whether the simpler Rhino-derived one-dimensional axes transfer despite the failed full representation.

Until that result is available, the correct scope is:

> strong low-dimensional portable individual policy in *Rhinolophus nippon*, with cross-species generality unresolved and already bounded by a negative full-policy result in *Miniopterus fuliginosus*.
