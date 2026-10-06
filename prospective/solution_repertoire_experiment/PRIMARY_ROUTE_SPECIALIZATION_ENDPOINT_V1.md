# Primary route-specialization endpoint v1

## Status

**PROSPECTIVE CONFIRMATORY ENDPOINT. NO COMMON-OPEN OUTCOME OPENED.**

Biological question:

> Does prior access to multiple feasible solutions cause stronger individual specialization in route choice when both acquisition histories are later tested under the same four-route opportunity?

This is P1, the direct ecological-opportunity endpoint.

## Target probe architecture

Use only the frozen first common-OPEN probe in each matched family.

The probe must contain an even predeclared number of valid trials per individual × family and is split before outcome opening into:
- early probe half;
- late held-out probe half.

Exact trial count:
**TBD BEFORE OUTCOME OPENING**.

Later probe, reopening and transfer trials cannot replace this target.

## Route states

Each trial is assigned to one of four route classes defined from obstacle topology before animal outcomes are opened.

No clustering of observed trajectories may redefine route classes.

## Early-probe categorical history

For each individual i in family f, count route choices in the early probe half.

Apply fixed symmetric Dirichlet smoothing with alpha = 0.5 per route.

For route r:

p_i,f(r) = (n_i,f,r + 0.5) / (N_i,f,early + 2).

## Held-out late-probe score

For each late target trial q of individual i in family f with observed route r_q:

- own log score = log p_i,f(r_q);
- donor log scores use early-probe route distributions from **all other eligible individuals in the same family**, regardless of acquisition treatment label;
- target advantage:

L_q = log p_i,f(r_q) - mean_j log p_j,f(r_q).

Using all same-family donors makes each individual × family route-identity score independent of treatment labels; the randomized treatment assignment is applied only afterward.

Require at least three donor individuals in each family.

## Family-specific individual route identity

Average L_q equally across late target trials within individual × family.

Call this R_i,f.

For each animal, treatment assignment maps one family to OPEN-acquired and the other to CONSTRAINED-acquired.

Primary treatment statistic:

Delta_R = mean_i [ R_i,OPEN-family - R_i,CONSTRAINED-family ].

Positive Delta_R means prior multi-solution opportunity produces stronger held-out individual route organization under the same current four-route opportunity.

## Exact randomization null

Keep all family-specific R_i,f scores fixed.

Under every allowed restricted treatment reassignment:
- preserve animal, family, route outcomes and acquisition-start order;
- change only which family is labelled OPEN-acquired versus CONSTRAINED-acquired;
- recompute Delta_R.

Condition on starting-family order and the frozen four-animal block design.

Do not permute biological identities.

## Confirmatory support

Support requires:
- Delta_R > 0;
- exact randomization p_R <= 0.05.

Report robustness:
- positive paired individual contrast fraction;
- leave-one-individual-out Delta_R;
- A-open/B-open strata;
- A-start/B-start strata.

If one-individual deletion reverses the sign, label SUPPORTED_BUT_FRAGILE.

## Interpretation

### Supported

> Prior access to multiple feasible movement solutions causally increases individual specialization in route choice when all animals are later given the same solution opportunity.

Because both families are four-route OPEN during the target probe, the contrast cannot be reduced to contemporaneous route count.

### Unsupported

The experiment does not establish opportunity-driven route-choice specialization.

P2 I/M may be reported descriptively but cannot rescue P1.

## Claim ceiling

P1 alone does not establish:
- a portable I/M carrier;
- durable storage;
- transfer beyond route coordinates;
- a neural mechanism;
- fitness benefit;
- equivalence to wild vertical individuality.