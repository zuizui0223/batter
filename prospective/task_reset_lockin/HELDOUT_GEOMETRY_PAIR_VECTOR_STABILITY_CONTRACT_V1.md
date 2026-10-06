# Held-out geometry pair-vector stability contract v1

## Status

**POST-PRIMARY REPRESENTATION-COMPARISON DIAGNOSTIC.**

Parents:
- `GEOMETRY_ONLY_POLICY_RESULT_V1.md`
- `HELDOUT_GEOMETRY_RELATIONAL_STABILITY_RESULT_V1.md`
- `TWO_PARAMETER_POLICY_LAW_CONTRACT_V1.md`

The transparent I/M policy shows strong held-out pair-vector preservation.
The existing geometry relational test examined only pairwise distance magnitudes.

This diagnostic applies the same vector-level question to scale-free route geometry.

## Question

For a bat pair (i,j) and held-out environment e:

> does the mean geometry difference vector estimated from the pair's other shared environments predict the geometry difference vector in e?

## Representation

Use exactly the parent eight scale-free geometry features, standardized within environment exactly as in the supported geometry-only identity diagnostic.

No feature selection or rotation.

For each bat × environment:
- average valid trajectory geometry vectors equally.

For every pair × target environment:
- require the pair is present in target e;
- require >=2 other shared environments;
- predictor = equal-environment mean of pair difference vectors across those other environments;
- target = pair difference vector in e.

## Metrics

Report:

1. no-refit pair-vector R²:
[
1-rac{sum|Delta^{obs}-Delta^{pred}|^2}
{sum|Delta^{obs}|^2};
]

2. median cosine between predicted and observed pair vectors;

3. positive-cosine fraction;

4. Pearson correlation between predicted and observed pair-vector magnitudes;

5. Spearman correlation between magnitudes.

## Null

Within each environment independently permute complete bat labels among bat × environment centroids.

Recompute all pair histories and target vectors.

9,999 permutations.

Seed:
`202610061801`.

Primary descriptive calibration is the upper-tail null for pair-vector R².

## Interpretation

If vector R² is unsupported while I/M pair-vector R² remains supported:

> **individual relational structure is substantially more stable in policy space than in detailed route-geometry space.**

If geometry vector R² is supported:
detailed route geometry has more cross-context relational stability than the distance-only diagnostic suggested.

## Ceiling

Do not call either space a formal topological invariant.
Do not infer causal internal coordinates.
This is a representation-level stability comparison.
