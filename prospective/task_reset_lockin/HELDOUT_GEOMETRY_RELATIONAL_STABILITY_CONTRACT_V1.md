# Held-out geometry relational stability contract v1

## Status

**POST-PRIMARY MECHANISM DIAGNOSTIC.**

Parents:
- `GEOMETRY_ONLY_POLICY_RESULT_V1.md`
- `GEOMETRY_CROSSFIT_IM_EXPRESSION_RESULT_V1.md`

The current evidence shows:
- scale-free route geometry is individually portable;
- one universal I/M -> geometry map does not exhaust identity in an unseen environment.

This diagnostic asks:

> **Is the pairwise geometry of individual differences itself stable across obstacle environments?**

In other words, if bat i and j are geometrically far apart in other configurations, are they also far apart in a held-out configuration?

## Geometry representation

Use exactly the frozen eight scale-free geometry features.

Within each environment:
- standardize features with that environment's label-free mean and SD;
- average trajectories within bat × environment equally.

No I/M feature enters this diagnostic.

## Held-out predictor

For target environment e and bat pair (i,j):

1. identify non-target environments where both bats have geometry centroids;
2. require at least **2** shared non-target environments;
3. compute Euclidean geometry distance in each shared environment;
4. predictor:

[
ar d^{g,-e}_{ij}
=
mean_{h
eq e} d^g_{ij,h}.
]

The target environment contributes nothing to this predictor.

## Target outcome

[
d^g_{ij,e}
=
|g_{i,e}-g_{j,e}|_2.
]

## Primary diagnostic statistic

Pool all eligible pair × target-environment observations.

Calculate:

[
ho_{GG}
=
Spearman(ar d^{g,-e}, d^g_e).
]

Also report:
- Pearson r;
- number of pair × environment observations;
- counts by environment.

## Null

Within every target environment independently:
- keep the held-out predictor values fixed;
- permute complete biological labels among target geometry centroids;
- preserve the target geometry cloud;
- recompute target pair distances and pooled rho.

9,999 permutations.

Seed:
`202610061901`.

Require >=9,500 valid null statistics.

## Exploratory support rule

Relational geometry stability is supported only if:
- rho > 0;
- one-sided permutation p <= 0.05.

## Interpretation

### Supported

> Pairwise separation among individual route-geometry phenotypes is partly preserved across obstacle configurations, even though the exact coordinate map changes.

This is consistent with an environment-dependent deformation of a stable personal organization.

### Unsupported

> Individual route geometry remains identifiable, but the pairwise geometry among individuals is substantially rearranged by environment.

Then identity portability is topological/local rather than metric: "self remains self-like" without a stable between-individual geometry.

## No rescue

Do not:
- use target geometry in the predictor;
- lower the two-shared-environment requirement;
- select environment subsets;
- switch distance metric after output;
- add nonlinear transformations.

## Claim ceiling

Even support does not identify:
- a linear environment map;
- solution abundance;
- a neural latent space;
- causal learning.
