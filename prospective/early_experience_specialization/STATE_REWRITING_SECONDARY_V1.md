# Early-experience state-rewriting secondary v1

## Status

**POST-PRIMARY DESCRIPTIVE MECHANISM DECOMPOSITION.**

This secondary was authorized in `PRIMARY_CONTRACT_V1.md` before primary outcome opening, but its exact estimator is specified only after the primary result.

Therefore:
- no p-value;
- no confirmatory promotion;
- cannot rescue `UNSUPPORTED_INDIVIDUALIZATION`.

## Question

The primary showed that enrichment did not confirm increased among-individual dispersion beyond the shared treatment shift.

A different mechanistic question remains:

> Does post-enrichment behavior look like a common treatment translation added to each bat's prior personal state, or like convergence toward a treatment-group state that largely replaces baseline individuality?

## Cohort and scaling

Use exactly the frozen primary cohort and baseline scaling:

- Season 2;
- n = 29;
- enriched = 14;
- impoverished = 15;
- Trials 1–3 complete;
- traits = Boldness, Exploration, Activity;
- baseline scale estimated from pooled Trials 1–2 only.

For bat i:

[
b_i=(z_{i1}+z_{i2})/2,
qquad
t_i=z_{i3},
qquad
Delta_i=t_i-b_i.
]

## Leave-one-out predictions

For each bat i in treatment group g, estimate all group quantities excluding i.

### Model B — personal baseline only

[
hat t_i^{B}=b_i.
]

### Model G — treatment-group state only

[
hat t_i^{G}
=
operatorname{mean}_{j
e i,,g(j)=g} t_j.
]

This ignores the bat's own baseline identity.

### Model B+S — personal baseline plus shared treatment shift

[
arDelta_{g,-i}
=
operatorname{mean}_{j
e i,,g(j)=g}(t_j-b_j),
]

[
hat t_i^{B+S}
=
b_i+arDelta_{g,-i}.
]

This preserves the bat's baseline offset and adds the common treatment-associated change estimated from peers.

## Error

For each model:

[
E_{i,m}=||t_i-hat t_i^m||_2^2.
]

Report:
- mean error across bats;
- median error;
- mean error within each treatment group;
- fraction of bats for which B+S beats B;
- fraction for which B+S beats G;
- fraction for which B beats G.

No hypothesis tests.

## Interpretation

### B+S lowest

Supports descriptive **translation-with-memory**:

> later behavior is best approximated by retaining each bat's personal baseline state and adding a shared treatment-associated shift.

### G lowest

Supports descriptive **group-state overwrite/convergence**:

> treatment-group state predicts later behavior better than retaining personal baseline offsets.

### B lowest

Supports descriptive **baseline persistence with weak common rewriting**.

Mixed outcomes are reported as mixed.

## Boundary

This secondary does not identify:
- causal individualization;
- a neural memory substrate;
- movement-policy identity;
- wild persistence.

It describes how the randomized environment appears to transform the laboratory personality state.
