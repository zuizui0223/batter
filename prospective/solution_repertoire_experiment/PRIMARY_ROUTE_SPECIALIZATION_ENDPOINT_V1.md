# Primary route-specialization endpoint v1

## Status

**PROSPECTIVE CONFIRMATORY ENDPOINT. NO COMMON-OPEN OUTCOME OPENED.**

Biological question:

> Does prior access to multiple feasible solutions cause stronger individual specialization when both acquisition histories are later tested under the same four-route opportunity?

This is the direct ecological-opportunity endpoint.

## Common-OPEN target window

Use only the first predeclared common-OPEN probe window in each matched family.

Planned number of valid probe trials per individual × family:
**TBD BEFORE OUTCOME OPENING**.

The route-specialization primary does not use later probe, reopening or transfer trials.

## Route states

Each probe trial is assigned to one of the four route classes defined from obstacle topology before animal outcomes are opened.

Route labels are family-local; no numerical ordering is assumed.

No clustering of observed trajectories is allowed to redefine route classes.

## Leave-one-trial-out own predictor

For a target probe trial q of individual i in family f:

1. remove q;
2. count the four route classes in i's remaining primary-window probe trials in family f;
3. form a Dirichlet-smoothed categorical distribution with fixed alpha = 0.5 per route.

For route r:

p_i(r) = (n_i,r + 0.5) / (N_i,-q + 2).

## Donor predictors

For every other individual j belonging to the same family f and the same acquisition treatment under the hypothesized assignment:
- use all of j's primary-window probe trials;
- form the same alpha=0.5 smoothed route distribution.

Require at least three donor individuals for a scored target.

If this donor rule fails under the observed restricted assignment, the primary returns STRUCTURAL STOP.

## Target log-score advantage

For the observed route r_q:

L_q = log p_i(r_q) - mean_j log p_j(r_q).

Positive means the target route is better predicted by that individual's own other probe choices than by other individuals exposed to the same acquisition treatment.

Aggregate:
1. equal target trials within individual × family;
2. equal individuals within acquisition treatment;
3. obtain R_OPEN and R_CONSTRAINED.

Primary treatment statistic:

Delta_R = R_OPEN - R_CONSTRAINED.

## Exact randomization null

Use the same restricted assignment space as PREREGISTRATION_CONTRACT_V1.md.

For every allowed reassignment:
- keep route outcomes, family identities and starting-family order fixed;
- relabel which family received OPEN versus CONSTRAINED acquisition;
- rebuild treatment-specific donor sets;
- recompute R_OPEN, R_CONSTRAINED and Delta_R.

Do not sign-flip precomputed individual effects.

One-sided confirmatory p is the exact upper-tail fraction of Delta_R under the allowed randomization assignments.

## Primary support

Support requires:
- Delta_R > 0;
- exact randomization p <= 0.05.

Report robustness:
- positive within-individual family contrast fraction;
- leave-one-individual-out Delta_R;
- A-open/B-open strata;
- A-start/B-start strata.

If one-individual deletion reverses the sign, label SUPPORTED_BUT_FRAGILE.

## Interpretation

### Supported

> Prior access to multiple feasible movement solutions causally increases individual specialization in route choice when all animals are later given the same solution opportunity.

Because both matched families are four-route OPEN during the target probe, this is not a trivial difference in contemporaneous route count.

### Unsupported

The experiment does not establish that solution opportunity during acquisition increases route-choice individual specialization.

Do not promote I/M, geometry or reopening endpoints to replace a failed direct ecological primary.

## Claim ceiling

This endpoint alone does not show:
- durable storage;
- transfer beyond route coordinates;
- a low-dimensional personal I/M policy;
- a neural mechanism;
- fitness benefit;
- equivalence to wild vertical individuality.