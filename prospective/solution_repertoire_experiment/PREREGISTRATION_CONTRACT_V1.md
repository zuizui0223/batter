# Solution-repertoire experiment preregistration contract v1

## Status

**PROSPECTIVE FAIL-CLOSED CONTRACT. OUTCOME OPENING NOT AUTHORIZED.**

This contract converts the structural design into a confirmatory experiment.

It must be completed with the physical obstacle dimensions, exact trial counts, route-capability threshold and final eligible sample size **before** any common-OPEN outcome is opened.

Parent:
- DESIGNED_SOLUTION_REPERTOIRE_EXPERIMENT_V1.md
- SAMPLE_SIZE_PLANNING_V1.md
- RANDOMIZATION_AND_INTERFERENCE_GUARD_V1.md
- PRIMARY_ROUTE_SPECIALIZATION_ENDPOINT_V1.md
- PRIMARY_IM_ENDPOINT_APPENDIX_V1.md

JAE v0.4.0 remains frozen.

---

## 1. Confirmatory question

Does access to multiple feasible movement solutions during acquisition increase later individual-specific movement-policy organization when OPEN-acquired and CONSTRAINED-acquired matched environments are subsequently tested under the same four-route OPEN opportunity?

Primary causal estimand:

Delta_A = A_OPEN-acquired - A_CONSTRAINED-acquired.

The biological unit is the individual bat.

The treatment is **solution opportunity during acquisition**, not obstacle identity and not route count during the common probe.

---

## 2. Matched environment requirement

Families A and B must be constructed as geometry-matched / graph-isomorphic task families as far as physically possible.

Before animal outcome collection, record for every corresponding route:
- route-graph identity;
- shortest path length;
- minimum aperture;
- required vertical displacement;
- required horizontal displacement;
- obstacle count;
- obstacle material;
- start/goal distance;
- reward schedule.

Any non-isomorphic difference judged biologically important before outcome opening must be documented in the frozen engineering receipt.

No family may be redesigned after common-OPEN outcomes are viewed.

---

## 3. Capability gate and route-familiarity equalization

Before free-choice acquisition inference, every candidate animal is tested with routes isolated one at a time.

The same frozen number of successful isolated-route traversals is required for every route in both families before treatment assignment. This makes physical route familiarity symmetric before OPEN versus CONSTRAINED acquisition is randomized.

The final numeric capability rule must be inserted here before confirmatory collection:

- required successful traversals per route: **TBD BEFORE FREE-CHOICE OUTCOME OPENING**;
- maximum allowed collision/failure fraction: **TBD BEFORE FREE-CHOICE OUTCOME OPENING**;
- minimum valid 3-D tracking support per isolated traversal: **TBD BEFORE FREE-CHOICE OUTCOME OPENING**.

An animal failing the frozen capability rule is excluded **before treatment randomization**.

If a route is infeasible for a predeclared fraction of candidate animals, the obstacle family is structurally invalid and confirmatory collection does not begin.

No capability threshold relaxation after randomization.

---

## 4. Randomization unit and restricted design

Randomization occurs only after the capability gate.

Eligible animals are assigned opaque study IDs.

Animals are entered into sequential blocks of four.

Within every complete block there is exactly one animal in each cell:

1. A = OPEN acquisition, acquisition sequence starts A;
2. A = OPEN acquisition, acquisition sequence starts B;
3. B = OPEN acquisition, acquisition sequence starts A;
4. B = OPEN acquisition, acquisition sequence starts B.

Thus:
- OPEN-family assignment is balanced within block;
- starting-family order is balanced within block;
- treatment and starting-family order are orthogonal within block.

Use randomization_schedule_v1.py.

The randomization seed is frozen in that script before outcome opening.

---

## 5. Acquisition schedule

Do not train one complete family and then the other.

Acquisition exposure is interleaved across families to limit period confounding.

For each animal:
- begin with its randomized starting family;
- alternate A/B acquisition sessions thereafter;
- preserve equal planned acquisition exposure in A and B;
- preserve equal rest and reward schedule.

The OPEN-acquired family has four simultaneously available routes.

The CONSTRAINED-acquired family has only the predeclared canonical route available.

The canonical route is fixed by engineering design before animal assignment.

No adaptive stopping when an individual appears to have stabilized.

---

## 6. Common OPEN probe

After acquisition is complete:
- both A and B are presented with all four routes open;
- no additional free-choice training occurs before the primary probe;
- probe-family order is balanced using a fixed ABBA or BAAB sequence determined from randomized starting-family order;
- equal planned probe trials are collected in A and B.

The first fixed probe window is the confirmatory target.

Exact number of probe trials per family:
**TBD BEFORE OUTCOME OPENING**.

Later probe trials are secondary and cannot replace a failed first-window primary.

---

## 7. Primary policy representation

Primary individual movement policy is fixed as theta = (I, M), with:
- FlightIntensity I;
- ManeuveringExtent M.

The exact feature definitions, acquisition-only family-wise standardization, fixed weights and Euclidean policy distance are frozen in PRIMARY_IM_ENDPOINT_APPENDIX_V1.md.

No:
- data-driven reweighting;
- PCA rotation;
- feature deletion;
- nonlinear embedding;
- outcome-selected normalization.

If either primary coordinate is structurally unavailable, the primary returns STOP rather than switching axes.

---

## 8. Common-OPEN held-out individual organization

The primary self-history score is calculated entirely inside the common OPEN probe.

The exact probe has an even number of valid planned trials per family and is split before outcome opening into:
- early probe window;
- late held-out probe window.

For each individual i and family f:

1. calculate the focal early-probe I/M centroid;
2. calculate early-probe centroids for all other eligible individuals in family f;
3. for every late-probe target trial, calculate distance to:
   - own early centroid;
   - each donor early centroid;
4. target advantage is mean donor distance minus own-history distance.

Aggregate:
- equal late targets within individual × family;
- equal individuals.

This yields A for each family under the actual treatment assignment.

Then:

- A_OPEN = mean A for the family that received OPEN acquisition;
- A_CONSTRAINED = mean A for the matched family that received CONSTRAINED acquisition;
- Delta_A = A_OPEN - A_CONSTRAINED.

This primary does **not** use acquisition centroids as its prediction target. Acquisition history defines the randomized treatment; current individual organization is measured under equal current opportunity.

Exact probe trials per family:
**TBD BEFORE OUTCOME OPENING**.

Early/late split:
**exactly half / half of the frozen primary probe trials**.

## 9. Exact randomization inference for P1 and P2

Both P1 and P2 use the same restricted treatment assignment null. Each endpoint must be fully recomputed under every allowed assignment.

Do **not** use a simple sign-flip test on already-computed individual contrasts, because donor pools depend on treatment assignment.

For every allowed treatment reassignment under the frozen block design:

1. keep all observed trajectories, family identities, starting-order labels and outcomes fixed;
2. reassign which family is labelled OPEN versus CONSTRAINED only within the allowed randomization space;
3. relabel which observed family-specific common-OPEN identity score belongs to OPEN-acquired versus CONSTRAINED-acquired treatment;
4. because the common-OPEN identity score itself is computed without treatment labels, preserve those family-specific scores unchanged;
5. recompute A_OPEN, A_CONSTRAINED and Delta_A.

If later endpoint implementation introduces treatment-defined donor pools, then the full donor construction must instead be recomputed under every assignment. The frozen endpoint appendix must state which architecture applies.

Condition on the observed starting-family order.

Within each complete four-animal block there are four treatment assignments compatible with the frozen balance.

Therefore:
- 4 complete blocks (16 animals) -> 4^4 = 256 assignments;
- 5 complete blocks (20 animals) -> 4^5 = 1,024 assignments;
- 6 complete blocks (24 animals) -> 4^6 = 4,096 assignments.

Use the exact assignment set whenever computationally feasible.

One-sided p = number of permuted Delta_A values >= observed Delta_A divided by the number of allowed assignments.

Reference implementation:
randomization_inference_reference_v1.py.

---

## 10. Confirmatory decision rule

### P1 route-specialization support

Requires:
- Delta_R > 0;
- exact randomization p_R <= 0.05.

### P2 I/M support

Evaluated confirmatorily only after P1 support.

Requires:
- Delta_A > 0;
- exact randomization p_A <= 0.05.

The strongest causal statement requires both P1 and P2.

P1 alone establishes opportunity-driven route-choice individual specialization without establishing that the effect occupies the previously identified transparent I/M policy space.

Report, but do not add as a second primary threshold:
- positive-individual fraction;
- leave-one-individual-out Delta_A;
- largest individual contribution.

If any single-individual deletion reverses the sign:
label **SUPPORTED_BUT_FRAGILE** rather than a clean robust support claim.

---

## 11. Randomization-stratum interpretation guard

Always report Delta_A separately for:
- A-open versus B-open assignments;
- A-start versus B-start sequences.

These are descriptive/robustness strata, not additional hypothesis tests.

If the treatment contrast reverses sign across either randomized factor:
- do not claim a general solution-opportunity mechanism;
- label the result **context/order dependent**;
- preserve the overall randomized estimate and p-value.

No stratum may be selected post hoc as the “correct” subset.

---

## 12. Interference boundary

Because the same animal experiences both matched families, generic learning can transfer across families.

The paired design therefore estimates the **family-specific incremental effect of OPEN solution opportunity against shared organism-level experience**.

Cross-family transfer is expected mainly to attenuate the paired contrast.

However, if strong asymmetric carryover is suggested by the frozen order strata, the causal claim must be narrowed to the observed acquisition schedule.

No post-hoc washout subset or first-period-only rescue is authorized.

An independent parallel-group replication remains the cleanest future test if interference proves substantial.

---

## 13. Structural sample gate

Planning target:
- 20 evaluable randomized animals;
- 5 complete four-animal randomization blocks.

Hard confirmatory minimum:
- 16 evaluable animals;
- 4 complete randomization blocks.

If fewer than 16 paired animals reach the common OPEN probe with the frozen support:
**STRUCTURAL STOP**.

Incomplete blocks and post-randomization attrition must be reported.

The missing-data rule must be finalized before confirmatory collection.

No lowering of the minimum.

---

## 14. Secondary endpoints

Only after the primary is frozen:

### S1 — history refinement
Late OPEN-acquisition history versus equally sized early OPEN-acquisition history.

### S2 — suppression and exact reopening
Does the previously OPEN-acquired personal policy reappear after a constrained expression block?

### S3 — transformed transfer
Does the policy survive the predeclared geometry transformation?

### S4 — route-choice individuality
Held-out probabilistic route-choice identity under the common OPEN probe.

### S5 — fine geometry realization
Predeclared scale-free trajectory geometry.

A positive secondary cannot rescue a failed primary.

---

## 15. Claim map

### P1 positive, P2 positive
Solution opportunity causes route-choice individual specialization and the effect extends into the fixed transparent movement-policy representation.

### P1 positive, P2 negative
Solution opportunity causes individual specialization in route choice, but the experiment does not establish that this specialization is carried by I/M.

### P1 negative, P2 positive
Do not rescue the main hypothesis. Report the I/M pattern descriptively; direct opportunity-driven route specialization was not established.

### P1 and P2 positive, reopening positive
Strongest chain: opportunity-driven specialization extends into personal policy and is re-expressed after temporary suppression.

### P1/P2 positive, reopening negative
Formation is supported, durable latent storage is not.

---

## 16. Hard prohibitions

After outcome opening do not:
- change I/M weights;
- rotate to H/V or PCA axes;
- redefine route classes;
- alter late-history window;
- exclude an inconvenient family;
- select acquisition order;
- select “responsive” animals;
- lower N or trial support;
- fit nonlinear decoders to rescue the primary;
- promote a secondary after primary failure.

---

## 17. Freeze checklist before first confirmatory outcome

Must all be complete:

- [ ] physical A/B engineering receipt;
- [ ] route-isomorphism mapping;
- [ ] numeric capability rule;
- [ ] exact acquisition trial counts;
- [ ] exact probe trial counts;
- [ ] common-OPEN early/late probe split frozen;
- [ ] late-history window size for secondary formation endpoint;
- [x] exact I/M endpoint appendix fixed as PRIMARY_IM_ENDPOINT_APPENDIX_V1.md;
- [ ] randomization schedule generated and archived;
- [ ] randomization seed archived;
- [ ] missing-data rule fixed;
- [ ] analysis code hashes archived;
- [ ] no common-OPEN outcome inspected.

Until every box is complete:
**OUTCOME OPENING NOT AUTHORIZED.**