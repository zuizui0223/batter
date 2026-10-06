# Held-out geometry pair-vector stability result v1

## Status

**SUPPORTED AT THE VECTOR LEVEL; MAGNITUDE RELATIONAL STABILITY REMAINS WEAK.**

Authoritative workflow:
- run: **37424268313**
- job: **112140245763**
- conclusion: **success**
- fail-closed shell: `set -euo pipefail`

Parent:
`HELDOUT_GEOMETRY_PAIR_VECTOR_STABILITY_CONTRACT_V1.md`

This is a post-primary representation-comparison diagnostic.

## Question

For each bat pair and held-out obstacle environment:

> does the pair's mean scale-free geometry difference vector from other shared environments predict its geometry difference vector in the held-out environment?

This is the vector analogue of the transparent-policy pair-displacement test.

## Result

Eligible pair × target-environment observations:
**33**

By target:
- Env1: 6
- Env2: 6
- Env3: 6
- Env4: 9
- Env5: 3
- Env6: 3

Observed:

- pair-vector no-refit R² = **+0.10407**
- median cosine = **0.59748**
- positive-cosine fraction = **25/33 = 75.8%**
- magnitude Pearson r = **+0.17338**
- magnitude Spearman rho = **+0.01805**

Environment-wise identity permutation:
- 9,999 / 9,999 valid
- null R² mean = **-0.38320**
- null 95% interval = **[-0.63282,-0.03529]**
- one-sided p = **0.0027**

Verdict:

**SUPPORTED_GEOMETRY_PAIR_VECTOR_STABILITY**

## Relation to the earlier magnitude-only result

The earlier held-out geometry relational test asked whether pairwise geometry **distance magnitudes** are stable.

That result was unsupported:
- Spearman rho = **+0.0782**
- p = **0.349**.

The present vector result resolves the apparent tension.

> **The direction of an individual's relative geometry difference can retain information across tasks even when the magnitude/ranking of pairwise geometry distances is unstable.**

This is consistent with environment-dependent stretching/compression of an identity-bearing geometric organization.

## Comparison with transparent policy space

Transparent I/M pair vectors are substantially more stable:

### Policy
- pair-vector R² = **+0.57972**
- median cosine = **0.86305**
- positive cosine = **97.1%**
- p = **0.0001**

### Scale-free route geometry
- pair-vector R² = **+0.10407**
- median cosine = **0.59748**
- positive cosine = **75.8%**
- p = **0.0027**

Do not treat the raw R² difference as a separately calibrated between-representation hypothesis test.

The bounded descriptive hierarchy is:

[
oxed{
	ext{policy relational structure is much more stable than detailed route-geometry relational structure}
}
]

while route geometry still retains non-random directional correspondence.

## Mechanistic interpretation

The result supports neither:
- a completely invariant realized geometry;
- nor completely arbitrary context-specific routes.

Instead:

[
oxed{
	ext{partial geometry correspondence}
+
	ext{strong environment-dependent metric deformation}
}
]

is the best current description.

The environment can alter:
- gain;
- relative distance magnitude;
- pairwise separation ranking;

while leaving enough orientation/identity structure for same individuals to remain recognizably related across tasks.

## Claim boundary

Supported:
- held-out geometry pair vectors are better predicted than identity-exchangeability;
- their magnitude structure is much less stable than policy-space relational structure.

Not established:
- a fitted environment metric;
- a shared linear decoder;
- a causal latent coordinate;
- universal geometry portability across species.

The fixed Rhino geometry representation remains externally unsupported in *Carollia*.

## JAE firewall

No change to JAE v0.4.0.
