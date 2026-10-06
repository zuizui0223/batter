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

# 5. Fixed-sequence confirmatory endpoints

Keep route choice and movement policy separate.

## P1 — direct ecological endpoint: route-choice individual specialization

During the common OPEN probe, both matched families contain the same four-route opportunity.

Use the frozen early-half -> late-half held-out route-identity score in:

PRIMARY_ROUTE_SPECIALIZATION_ENDPOINT_V1.md.

Treatment statistic:

\[
\Delta_R
=
R_{OPEN-acquired}
-
R_{CONSTRAINED-acquired}.
\]

This is the direct test of whether **solution opportunity during acquisition causes stronger individual specialization**.

## P2 — mechanistic endpoint: transparent I/M organization

Only after P1 support, test whether the acquisition treatment also changes reproducible organization in the fixed transparent movement-policy coordinate:

\[
\theta=(I,M),
\]

where:
- I = FlightIntensity;
- M = ManeuveringExtent.

Use the exact raw features, acquisition-only family scaling, fixed weights, Euclidean metric and common-probe early/late identity architecture in:

PRIMARY_IM_ENDPOINT_APPENDIX_V1.md.

Treatment statistic:

\[
\Delta_A
=
A_{OPEN-acquired}
-
A_{CONSTRAINED-acquired}.
\]

No weights may be learned from the new identity outcome.

## Fixed-sequence interpretation

### P1 supported, P2 supported

Solution opportunity causes individual route specialization and the effect extends into the previously identified abstract movement-policy space.

### P1 supported, P2 unsupported

Solution opportunity causes route-choice specialization, but the experiment does not establish that the effect is carried by I/M.

### P1 unsupported, P2 positive

Do not rescue the main ecological hypothesis. Report P2 descriptively.

## Fine trajectory geometry

Use one predeclared scale-free trajectory representation only as a downstream realization layer.

It cannot replace a failed P1 or P2.

---

# 6. Common-OPEN causal logic

The confirmatory outcomes are measured **entirely inside the common OPEN probe**, where both matched families have the same four-route opportunity.

For both P1 and P2:

1. freeze an even number of probe trials per family;
2. divide the probe into early and late halves before outcomes are opened;
3. build individual history from the early half;
4. score held-out late-half behavior against own versus other-individual early histories;
5. obtain one family-specific individual-identity score per animal × family;
6. map each family to OPEN-acquired versus CONSTRAINED-acquired only after the family-specific scores are defined.

This avoids comparing behavior expressed under one-route acquisition directly against behavior expressed under a four-route probe.

The CONSTRAINED-acquired family has also been exposed to every physical route separately during the pre-randomization capability audit, so a positive treatment contrast is not simply complete unfamiliarity with alternative corridors.

Because constrained-history animals experience an early common-OPEN half before late held-out scoring, rapid new learning in the probe can only erode the acquisition-history contrast. The design is therefore conservative for persistent history effects.

---

# 7. Exact restricted randomization null

The primary causal null follows the randomized assignment of which matched family received OPEN acquisition.

Keep fixed:
- biological identity;
- family A/B;
- all common-OPEN outcomes;
- starting-family order;
- family-specific P1/P2 identity scores.

Within every allowed reassignment under the four-animal block design:
- relabel which family is OPEN-acquired versus CONSTRAINED-acquired;
- recompute Delta_R and, if P2 is in the confirmatory chain, Delta_A.

Do not permute biological identities.

Do not use an unrestricted independent sign flip that ignores block/order balance.

Reference:
- PREREGISTRATION_CONTRACT_V1.md;
- RANDOMIZATION_AND_INTERFERENCE_GUARD_V1.md;
- randomization_inference_reference_v1.py.

### P1 support

Requires:
- Delta_R > 0;
- exact p_R <= 0.05.

### P2 support

Tested confirmatorily only if P1 passes.

Requires:
- Delta_A > 0;
- exact p_A <= 0.05.

For both, report:
- positive paired-individual fraction;
- leave-one-individual-out treatment contrast;
- family-assignment strata;
- starting-order strata.

A one-individual sign reversal is labelled fragile/outlier-sensitive.

---

# 8. Formation endpoint — early versus late OPEN acquisition history

This is downstream of the randomized common-OPEN primary.

Within the OPEN-acquired family only:

- early acquisition history = fixed first m admissible OPEN trials;
- late acquisition history = fixed last m admissible OPEN trials;
- target = frozen early common-OPEN behavior.

Ask whether late personal history predicts later individual organization better than equally sized early history.

Do not redefine m after inspection.

---

# 9. Storage/re-expression endpoint

For the OPEN-acquired family:

- personal history = frozen late OPEN acquisition;
- target = earliest admissible exact-reopening trials after the constrained suppression phase.

A positive calibrated own-history advantage supports persistence/re-expression while ordinary multi-solution expression was temporarily unavailable.

This endpoint cannot rescue failed P1.

---

# 10. Transformed transfer endpoint

Use the predeclared transformed OPEN geometry.

### Exact reopening positive, transformed transfer negative

Personal organization is retained but strongly tied to learned scene/path coordinates.

### Both positive

At least part of the individual organization transfers beyond exact route coordinates.

### Both negative

Durable storage/transfer is not established.

No nonlinear rescue model is authorized.

---

# 11. Route choice versus policy is a biological decomposition, not endpoint shopping

P1 asks whether opportunity causes **individual specialization itself**.

P2 asks whether that specialization occupies the previously identified **portable movement-policy coordinate**.

Geometry asks how the policy is realized.

The hierarchy is therefore:

\[
\boxed{
\text{solution opportunity}
\rightarrow
\text{individual route specialization}
\rightarrow
\text{abstract personal policy?}
\rightarrow
\text{fine realization}
}
\]

A downstream layer cannot retroactively rescue a failed upstream layer.

---

# 12. Geometry realization — secondary

Ask whether acquisition treatment changes:
- within-individual trajectory stereotypy;
- fine maneuver realization;
- policy-to-geometry mapping.

These analyses are downstream and must be frozen before their outcomes are opened.

Do not use them to redefine P1 or P2.

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
2. P1 shows no stronger held-out individual route specialization after OPEN acquisition;
3. the treatment contrast is driven by one individual;
4. late OPEN history is no more informative than early OPEN history;
5. acquired organization disappears completely after temporary constraint;
6. results depend on post-hoc route relabeling or feature rotation.

Each failure narrows the mechanism.

---

# 18. Strongest positive inference

The strongest chain requires:
- route feasibility is verified;
- P1: randomized OPEN acquisition increases held-out route-choice individual specialization in the common OPEN probe;
- P2: the same randomized treatment increases held-out organization in the fixed I/M representation;
- late history is more predictive than early history;
- personal organization reappears after suppression;
- some organization survives transformed transfer.

If only P1 is supported, the defensible causal claim is narrower:

> **Access to multiple feasible movement solutions during acquisition causally promotes later individual specialization in route choice under equal current opportunity.**

If P1 and P2 are both supported, followed by reopening support, the programme can support:

> **Access to multiple feasible movement solutions causally promotes the formation of durable individual movement policies through personal history; temporary restriction can suppress their expression without necessarily erasing the underlying organization.**

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
