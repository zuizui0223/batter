# Held-out policy-to-geometry coupling result v1

## Status

**UNSUPPORTED.**

Authoritative workflow:
- run: **37408445931**
- job: **112091199225**
- conclusion: **success**
- fail-closed shell: `set -euo pipefail`

Parent:
`HELDOUT_POLICY_GEOMETRY_COUPLING_CONTRACT_V1.md`

## Question

Does pairwise separation in the portable transparent I/M policy, estimated strictly from non-target environments, predict pairwise separation in detailed scale-free route geometry in the held-out target environment?

The target environment contributes:
- no movement-policy feature;
- no I/M coordinate;
- only the frozen scale-free geometry outcome.

Thus the predictor and target are separated by environment.

## Result

Eligible pair × target-environment observations:
**35**

By target environment:
- Env1: 6 pairs
- Env2: 6
- Env3: 6
- Env4: 10
- Env5: 3
- Env6: 3
- Env7: 1

Pooled association:

- Spearman rho = **+0.19104**
- Pearson r = **+0.16135**

Environment-blocked geometry-label permutation:
- 9,999 / 9,999 valid
- null mean = **+0.08017**
- null 95% interval = **[-0.2210,+0.3715]**
- one-sided **p = 0.2437**

Verdict:

**UNSUPPORTED_HELDOUT_POLICY_GEOMETRY_COUPLING**

## Descriptive environment heterogeneity

Spearman rho by target environment:

- Env1: **+0.771**
- Env2: **+0.543**
- Env3: **+0.429**
- Env4: **-0.127**
- Env5: **+0.500** (3 pairs)
- Env6: **-0.500** (3 pairs)
- Env7: not estimable (1 pair)

These values are descriptive and no environment was selected post hoc.

## Interpretation

Portable policy differentiation does not provide a stable metric prediction of detailed route-geometry differentiation in an unseen task.

Thus the result does **not** support:

[
d_	heta(i,j)
longrightarrow
d_g(i,j,e)
]

through one stable monotonic mapping.

This is stronger than saying that one linear I/M -> geometry coefficient matrix fails.

Even at the lower-dimensional level of pairwise separation magnitude, the policy-to-geometry relation is context dependent.

## Relation to the positive held-out policy result

This does not weaken the established portability of policy space itself.

Within transparent I/M policy space:
- held-out individual coordinates are predictable;
- pair-displacement vectors have R² = **0.5797**;
- 97.1% have positive directional alignment.

Therefore the current contrast is:

[
oxed{
	ext{stable relational geometry in policy space}

otRightarrow
	ext{stable relational geometry in realized route space}
}
]

## Claim boundary

Supported:
- detailed geometry does not preserve pairwise policy separation robustly across environments.

Not established:
- which obstacle feature causes the distortion;
- a specific nonlinear realization function;
- a universal environment-induced metric;
- solution abundance.

## JAE firewall

No change to JAE v0.4.0.
