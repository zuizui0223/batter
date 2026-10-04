# Maternal-template to self-history crossover contract v1

## Status

**PROSPECTIVE PRIMARY FORMATION HYPOTHESIS.**

This contract is frozen before this programme opens any route-similarity outcome from the Goldshtein et al. juvenile dataset.

The exact geometric distance estimator will be frozen in a v2 estimator appendix **after schema/sampling inspection and before any route similarity is calculated**. The biological contrast, eligibility rules, chronology, aggregation and stop rules below may not change after schema inspection.

## Core biological hypothesis

The source study already establishes a maternally supplied spatial template early in ontogeny.

The new question is what maintains route organization after independent experience accumulates.

### Formation-maintenance prediction

Early navigation is seeded by maternal exposure, but later route organization becomes increasingly carried by the pup's **own independent movement history**.

The critical new contrast is:

> for held-out later independent trips, does the pup's own strictly prior independent route history predict its route better than its pre-independence maternal-exposure history?

If yes, the system contains a direct formation bridge:

**maternal/socially supplied information -> personal experience -> personal solution reuse.**

This is stronger than merely showing persistent individuality in adults.

---

## Inherited result versus new result

### Inherited from the source paper

The programme treats the following as established source knowledge:
- pups were transported by mothers before independence;
- early independent destinations/routes resembled maternally experienced destinations/routes.

These are not counted as new support.

### New primary endpoint

The new endpoint begins only once a pup has accumulated sufficient independent route history.

For each eligible held-out independent target trip t:

- **maternal predictor M** uses only qualifying pre-independence maternal/pup-carried route exposure;
- **self predictor S** uses only the focal pup's qualifying independent trips completed strictly before t;
- target trip t is never used in either predictor.

Define a target-level source contrast:

`C_it = loss(M -> target_it) - loss(S -> target_it)`

where lower loss means a closer route match.

Thus:
- `C_it > 0`: the pup's own independent history predicts the target route better than the maternal template;
- `C_it = 0`: no predictive-source advantage;
- `C_it < 0`: maternal exposure remains the better route template.

The exact route-loss function is frozen only after the outcome-blind schema/sampling preflight.

---

## Primary population

Use only source-defined mother-pup pairs for which the outcome-blind schema gate passes.

A pup must:
- have a reproducible mother identity;
- have a source-defined transition to independent movement;
- satisfy the support rules in `SCHEMA_PREFLIGHT_CONTRACT_V1.md`;
- remain the unit of biological replication.

No pooling of fixes as biological replicates.

## Route/task matching

The primary contrast should compare **the same movement problem**, not merely arbitrary trips.

Priority order fixed now:

1. exact same source-defined destination / landing site;
2. if exact destination labels are unavailable but target geometry is source-defined, an estimator may standardize routes by the same target endpoint;
3. if neither can be reconstructed outcome-blind, STOP the route-crossover primary.

Do not replace the endpoint with all-trip route similarity after seeing support.

## Chronological self library

For target trip t, the self library contains only independent trips ending before t.

No future-trip leakage.

A target trip enters the primary only when at least **2 strictly prior independent trips** are available for the same admissible task/destination definition.

## Maternal library

The maternal library contains only source-valid pre-independence exposure of that pup to the relevant destination / route problem.

Post-independence maternal trips are not added to improve maternal prediction.

The maternal predictor is therefore a fixed pre-independence information template rather than a moving contemporaneous comparator.

## Equal weighting

For any predictor:
- first aggregate route loss within each history trip;
- then average history trips equally;
- then average eligible targets equally within pup;
- then average pups equally for the programme statistic.

No individual with more GPS fixes or more trips receives larger biological weight.

## Primary individual statistic

For pup i:

`C_i = mean_t(C_it)`

over its eligible held-out later independent target trips.

Primary experiment statistic:

`C = equal-pup mean(C_i)`.

Support for self-maintained personal route organization requires:
- `C > 0`;
- at least **4 of 5** evaluable pups positive when n=5, or at least 70% positive when n>5;
- a predeclared individual-level paired/randomization or bootstrap calibration whose exact implementation is frozen in the estimator appendix before outcome opening.

The direction and individual-consistency requirements are fixed here and may not be relaxed.

## Secondary ontogenetic prediction

If the primary opens, a predeclared secondary asks whether self advantage strengthens with accumulated independent experience.

For each pup, model/describe `C_it` against the number of strictly prior independent trips.

Expected direction:

`d C_it / d experience > 0`.

This is secondary because sampling through ontogeny may be irregular and the source paper already establishes an early maternal contribution.

No breakpoint may be selected after outcome inspection.

## Exploration signature

A secondary descriptive series may quantify route novelty/dispersion through independent-trip order.

Path-dependent refinement predicts:
- high or rising exploration around the independence transition / novel trips;
- subsequent concentration of route use within repeatedly solved tasks;
- increasing held-out self predictability.

This cannot substitute for a failed primary crossover.

## Mechanism interpretation

### If C > 0 is supported

The allowed claim is:

> after maternal exposure seeded early navigation, later independent routes were better predicted by the juvenile's own accumulated movement history than by its pre-independence maternal template.

This directly supports **personal experience as a carrier of maintenance**.

It is compatible with:
- spatial memory;
- learned route familiarity;
- switching/search costs;
- sensorimotor refinement;
- repeated task knowledge.

It does not identify which cognitive mechanism generates the advantage.

### If C is unsupported

Do not infer absence of learning.

Possible bounded interpretations include:
- maternal route templates remain useful;
- personal routes do not stabilize over the observed period;
- destination changes dominate route geometry;
- route history is too sparse.

No alternate distance metric or destination subset may rescue the result after opening.

## Mechanistic contrast with performance matching

Stable morphology could also produce persistent routes.

The ontogenetic crossover is discriminating because a route pattern that becomes increasingly predicted by **accumulated personal history after a maternal template is already present** is not naturally explained by morphology alone.

Morphology remains a potential modifier, not a sufficient explanation for a history-source crossover.

## Stop rules

After route outcome opening:
- no alternate route-distance family;
- no alternate destination definition;
- no alternative early/late split;
- no removal of negative pups;
- no threshold relaxation;
- no pooling Source B to rescue Source A;
- no converting published maternal similarity into an inferential component of this new primary;
- no JAE manuscript modification.

## JAE firewall

This is a separate mechanism/formation paper.

JAE v0.4.0 remains frozen regardless of the result.
