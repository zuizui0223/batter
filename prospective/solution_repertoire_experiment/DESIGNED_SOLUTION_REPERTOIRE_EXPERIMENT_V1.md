# Designed solution-repertoire manipulation v1

## Status

**PROSPECTIVE STRUCTURAL EXPERIMENT DESIGN. NO NEW OUTCOME DATA OPENED.**

Purpose:
test whether access to multiple feasible movement solutions causally promotes the formation of individual-specific movement policy, and whether the resulting personal organization persists when expression is temporarily constrained.

This is the first authorized mechanism route after the same-data *Rhinolophus* geometry ceiling.

It does not modify JAE v0.4.0 and does not reopen the failed wild field bridge.

---

# 1. Biological hypothesis

The current programme supports:
- personal-history refinement;
- portable individual movement information;
- context-dependent fine-maneuver realization;
- persistence of individual bias across reversible sensory perturbation.

What remains untested is the proposed formation mechanism:

\[
\text{multiple feasible solutions}
\times
\text{personal history}
\rightarrow
\text{individualized policy}.
\]

Primary biological hypothesis:

> **Ecological opportunity at the level of movement solutions allows personal history to crystallize into stable individual policy.**

The decisive experiment must distinguish this from:
- fixed intrinsic differences that would appear regardless of opportunity;
- trivial population-level adaptation;
- route infeasibility;
- simple room-side preference;
- exact-path memory with no portable personal organization.

---

# 2. Key causal improvement — matched environment families

Use two obstacle families, **A** and **B**.

Each family must be engineered to contain the same four predefined feasible route classes when fully open.

The two families should be matched as closely as possible in:
- shortest-path length;
- gap width;
- total obstacle density;
- approximate turning demand;
- vertical displacement demand;
- obstacle material;
- reward;
- illumination/acoustic recording architecture.

They should differ enough in exact spatial layout that memorizing coordinates in A does not directly solve B.

For every biological individual, randomly assign:

- one family to **OPEN acquisition**: all four feasible routes available;
- the other family to **CONSTRAINED acquisition**: only one canonical route available.

Counterbalance A/B assignment across animals.

Thus each individual serves as its own control for solution opportunity.

The critical treatment is not "easy versus hard".

It is:

\[
\boxed{
\text{multiple feasible solutions during acquisition}
\quad \text{versus} \quad
\text{one feasible solution during acquisition}
}
\]

with the same animal and matched task families.

---

# 3. Capability audit before free-choice inference

A major confound is that an animal may avoid a route because it cannot physically negotiate it.

Before acquisition outcomes are opened:

1. isolate each of the four route classes in both families;
2. verify that every candidate animal can traverse each route under standardized presentation;
3. record success/failure and basic flight performance;
4. apply a predeclared structural feasibility criterion.

No free-choice preference data are used to define feasibility.

If an animal cannot meet the route-capability rule, it is not eligible for the confirmatory solution-opportunity analysis.

If many animals fail the same route, the obstacle family fails structurally and must be redesigned before confirmatory collection.

This separates **can use** from **chooses to use**.

---

# 4. Experimental sequence

## Phase 0 — capability audit and route-familiarity equalization

All route classes are isolated individually.

Every eligible animal receives the same frozen number of successful traversals of every route in both families before treatment assignment.

This serves two purposes:
- structural capability verification;
- equal pre-randomization physical familiarity with all route alternatives.

No free-choice inference is made from this phase.

## Phase 1 — randomized acquisition treatment

Each animal trains in both matched families.

### OPEN family

All four routes simultaneously available.

### CONSTRAINED family

Only the canonical route available.

Requirements:
- equal planned number of trials;
- equal reward schedule;
- matched inter-trial rest;
- A/B treatment assignment randomized and counterbalanced;
- order of OPEN and CONSTRAINED training blocks randomized where carryover permits.

No animal is stopped early because a preference appears stable.

## Phase 2 — common OPEN probe

Now open all four routes in **both** families.

This is the primary causal test.

Both families are measured under the same four-route opportunity.

The probe is split prospectively into:
- an early probe half used only to estimate each individual's current personal policy;
- a late held-out probe half used for the confirmatory identity score.

The only intended difference between matched families is acquisition history:
- one family had simultaneous multi-solution experience;
- one family had constrained single-solution experience.

Because the primary compares early-to-late organization **within the common OPEN probe**, it does not require the constrained acquisition state itself to resemble the common-OPEN state.

## Phase 3 — suppression

For the formerly OPEN-trained family, collapse expression to the canonical single route for a predeclared block.

Purpose:
temporarily remove the opportunity to express the personal multi-solution policy.

This phase is not assumed to erase memory.

## Phase 4 — exact reopening

Restore the exact four-route OPEN geometry in that same family.

Purpose:
test whether the previously acquired personal organization reappears.

## Phase 5 — transformed transfer

Mirror/rotate/relabel the OPEN geometry using a transformation fixed before the first animal enters the experiment.

Purpose:
distinguish:
- exact spatial memory;
- route-class memory;
- more abstract movement-policy portability.

---

# 5. Primary representation

Keep route choice and movement policy separate.

## 5.1 Coarse personal movement policy — primary

Retain the existing interpretable coordinate:

\[
\theta_{i,t}=(I_{i,t},M_{i,t}),
\]

where:
- I = FlightIntensity;
- M = ManeuveringExtent.

Feature definitions must be frozen before new outcomes are scored.

No weights may be learned from the new identity outcome.

This avoids making the primary result a trivial consequence of four route labels being available in one condition.

## 5.2 Route choice — secondary

For every common-OPEN trial record:
- selected route class;
- success/failure;
- family;
- phase;
- trial number.

Route classes are defined from obstacle topology before trajectory outcomes are opened.

## 5.3 Fine trajectory geometry — downstream expression

Use one predeclared scale-free trajectory representation.

It is a secondary realization layer, not the primary causal carrier.

---

# 6. Primary causal endpoint — common-OPEN individual organization

The primary endpoint is measured **entirely inside the common OPEN probe**, where both matched families have the same four-route opportunity.

This avoids confounding the treatment effect with a simple acquisition-to-probe geometry change.

For each individual × family:

1. divide the frozen common-OPEN probe into a fixed early half and late half;
2. estimate the individual's policy centroid from the early half;
3. score every late-half target against:
   - its own early-half centroid;
   - early-half centroids from other eligible individuals in the same family;
4. compute held-out self-history advantage:

\[
A_{i,f}
=
\operatorname{mean}_{j\neq i}
d(\theta_{i,late,f},\theta_{j,early,f})
-
d(\theta_{i,late,f},\theta_{i,early,f}).
\]

Aggregate:
- equal target trials within individual × family;
- equal individuals.

For each animal, the two matched families differ only in acquisition history:
- OPEN-acquired;
- CONSTRAINED-acquired.

Primary treatment contrast:

\[
\Delta_A
=
A_{OPEN-acquired}
-
A_{CONSTRAINED-acquired}.
\]

### Interpretation

Positive Delta_A means that, under the **same current four-route opportunity**, the family in which the animal previously had multiple-solution choice now contains stronger reproducible individual-specific policy organization.

The CONSTRAINED-acquired family has also been exposed to every route during the pre-randomization capability audit. Thus a positive contrast cannot be reduced simply to complete unfamiliarity with the alternative physical routes.

Because both families receive an early common-OPEN probe half before the held-out late-half target is scored, immediate novelty/adaptation is further separated from the primary target.

This makes the primary a conservative test of **history-dependent individual specialization under equal current opportunity**.

---

# 7. Primary randomization null

The cleanest null follows the randomized within-individual assignment.

Within each animal:
- preserve all trajectories and outcomes;
- swap which matched family is labelled OPEN-acquired versus CONSTRAINED-acquired according to the original randomization scheme.

Use the exact paired randomization/permutation distribution permitted by the final design.

This tests the acquisition-opportunity treatment directly.

It does not permute individual identities for the primary treatment effect.

### Primary support rule

Support requires:
1. observed Delta_A > 0;
2. paired randomization p <= 0.05.

Robustness must also be reported:
- fraction of individuals with positive within-individual treatment contrast;
- leave-one-individual-out Delta_A;
- maximum single-individual influence.

If deleting one individual reverses the sign of Delta_A, label the result **fragile / outlier-sensitive** even if the full-sample randomization p <= 0.05.

Do not add a separate arbitrary positive-fraction gate to the primary randomized treatment test.

---

# 8. Formation endpoint — early versus late OPEN acquisition history

This is secondary to the randomized common-OPEN primary.

Within the OPEN-acquired family only:

- early history = fixed first m admissible OPEN acquisition trials;
- late history = fixed last m admissible OPEN acquisition trials;
- target = the frozen early common-OPEN probe half.

This asks whether the personal organization visible at reopening is better predicted by later than earlier multi-solution history.

Define:

\[
Q=A_{late}-A_{early}.
\]

The null must preserve population-level learning/order while breaking the true individual-history link.

### Q supported

Personal organization becomes more identity-informative through experience with multiple feasible solutions.

### Q unsupported

The individual policy may predate acquisition or may form too quickly for this design to resolve.

Do not redefine m after inspection.

---

# 9. Storage/re-expression endpoint

For the OPEN-acquired family:

- personal history = late Phase-1 OPEN acquisition;
- target = earliest admissible Phase-4 exact-reopening trials.

Compare own prior history against other individuals' prior histories using the same fixed policy distance.

Positive calibrated self-history advantage supports:

> personal organization persisted while its normal multi-solution expression was temporarily prevented.

This is a separate endpoint from the Phase-2 opportunity effect.

---

# 10. Transformed transfer endpoint

Use Phase-5 transformed OPEN geometry.

Interpretation:

### Exact reopening positive, transformed transfer negative

Personal organization is retained but strongly tied to the learned scene/path coordinates.

### Both positive

At least part of the individual organization is more abstract than exact route coordinates.

### Both negative

The Phase-2 acquisition effect did not create a durable transferable state.

No nonlinear rescue model is authorized after these outcomes.

---

# 11. Route-choice individuality — secondary

Because both matched families are four-route environments during the common probe, route-choice outcomes are directly comparable there.

For each family:
- estimate held-out individual route-choice distributions;
- score own-history versus other-individual/pool predictions with a proper probabilistic score.

Do not use raw entropy as evidence for individuality.

A stronger OPEN-acquired route-choice identity signal than CONSTRAINED-acquired signal is supportive secondary evidence for opportunity-driven specialization.

It is not allowed to replace a failed primary I/M treatment contrast.

---

# 12. Geometry realization — secondary

Ask whether acquisition treatment changes:
- within-individual trajectory stereotypy;
- fine maneuver realization;
- policy-to-geometry mapping.

These analyses are downstream and must be frozen before their outcomes are opened.

Do not use them to redefine the primary policy coordinate.

---

# 13. Prospective covariates

Measure where feasible:
- body mass;
- forearm length;
- wingspan;
- wing area;
- sex;
- age class;
- baseline flight performance.

These are secondary explanatory variables.

They may later test whether biomechanics constrains which personal solution is acquired.

They must not be used for outcome-dependent exclusion.

---

# 14. Sample-size rule

The experiment must not repeat the n=5 same-data ceiling.

Prospective planning uses the paired within-individual OPEN-versus-CONSTRAINED treatment contrast.

A one-sided paired-effect planning approximation gives, for standardized treatment effect d = 0.7:
- n=14: about 80% power;
- n=16: about 85% power;
- n=18: about 89% power;
- n=20: about 92% power.

Although n=14 crosses the approximate 80% planning threshold for d=0.7, the restricted design requires complete four-animal blocks. The confirmatory minimum is therefore n=16, not n=14.

For d = 0.6, n=20 is only about 83%.

Therefore:

Planning target:
- **20 evaluable biological individuals** completing Phases 0-4;
- this yields five complete four-animal restricted-randomization blocks.

Preferred if feasible:
- 24 evaluable individuals / six complete blocks.

Structural minimum for opening the confirmatory primary:
- **16 evaluable biological individuals**;
- four complete randomization blocks.

If fewer than 16 complete:
- primary = STRUCTURAL STOP;
- no threshold relaxation;
- descriptive acquisition data may still be reported.

The power calculation is a planning approximation; the confirmatory analysis remains the paired randomization test.

See SAMPLE_SIZE_PLANNING_V1.md and sample_size_planning_v1.py.

The final planned N and exact trial counts must be frozen before confirmatory outcome opening.

---

# 15. Trial support

Freeze before confirmatory collection:
- acquisition trials per family;
- common-probe trials;
- suppression trials;
- reopening trials;
- transformed-transfer trials;
- minimum valid 3-D trajectory support.

No adaptive stopping based on apparent individual stabilization.

Missing trials follow a predeclared support rule.

---

# 16. Randomization and blinding

Predeclare:
- OPEN versus CONSTRAINED family assignment for each animal;
- A/B block order;
- canonical constrained route;
- transformed-layout mapping;
- route-label coding;
- analysis seeds.

Where feasible:
- trajectory preprocessing is blind to individual identity and treatment;
- route classification uses topology rather than visually judged preferred paths.

---

# 17. Critical failure modes

The formation hypothesis is not supported if:

1. the capability audit shows nominal routes are not genuinely feasible;
2. the common OPEN probe shows no stronger personal-policy prediction after OPEN acquisition;
3. the treatment contrast is driven by one individual;
4. late OPEN history is no more informative than early OPEN history;
5. acquired organization disappears completely after temporary constraint;
6. results depend on post-hoc route relabeling or feature rotation.

Each failure narrows the mechanism.

---

# 18. Strongest positive inference

If:
- route feasibility is verified;
- randomized OPEN acquisition increases held-out personal-policy identity in the common OPEN probe;
- late history is more predictive than early history;
- personal organization reappears after suppression;
- some organization survives transformed transfer;

then the programme can support:

> **Access to multiple feasible movement solutions causally promotes the formation of stable individual movement policies through personal history; temporary restriction can suppress their expression without necessarily erasing the underlying organization.**

This is substantially stronger than showing that individuals merely differ.

---

# 19. Claim ceiling

Even a positive experiment would not establish:
- universal applicability across bats;
- a fitness advantage;
- a specific neural storage mechanism;
- equivalence with the unresolved wild vertical-individuality carrier;
- that environmental complexity in general causes specialization.

The causal claim is specifically about **solution opportunity during acquisition** under the tested movement task.

---

# 20. Why this closes the current causal gap

The existing archives show:
- individuality;
- portability;
- history refinement;
- context-sensitive realization;
- persistence under sensory perturbation.

They do not manipulate the opportunity from which a personal solution can form.

The matched-family randomized design does:

\[
\boxed{
\text{solution opportunity during history}
\rightarrow
\text{later individual-specific policy}
}
\]

while holding biological identity fixed and testing both storage and transfer afterward.

That is the missing causal link.
