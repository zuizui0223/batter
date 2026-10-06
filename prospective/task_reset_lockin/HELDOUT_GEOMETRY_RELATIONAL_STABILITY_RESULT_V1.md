# Held-out geometry relational stability result v1

## Status

**UNSUPPORTED.**

Authoritative workflow:
- run: **37408758573**
- conclusion: **success**
- fail-closed shell: `set -euo pipefail`

Parent:
`HELDOUT_GEOMETRY_RELATIONAL_STABILITY_CONTRACT_V1.md`

## Question

If two bats are far apart in scale-free route geometry across other obstacle configurations, are they also far apart in the held-out configuration?

This test uses geometry only.

For each target environment and bat pair:
- predictor = mean pairwise geometry distance across >=2 shared non-target environments;
- outcome = pairwise geometry distance in the target environment.

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
- Env7: 0

Pooled:

- Spearman rho = **+0.07821**
- Pearson r = **+0.17960**

Environment-wise label permutation:
- 9,999 / 9,999 valid
- null mean = **+0.01597**
- null 95% interval = **[-0.2858,+0.3108]**
- one-sided **p = 0.3490**

Verdict:

**UNSUPPORTED_HELDOUT_GEOMETRY_RELATIONAL_STABILITY**

## Descriptive target heterogeneity

Spearman rho:
- Env1: **+0.657**
- Env2: **+0.657**
- Env3: **+0.143**
- Env4: **-0.050**
- Env5: **-0.500**
- Env6: **+1.000** (3 pairs)

These are descriptive only.

## Interpretation

Scale-free route geometry remains identity-bearing across configurations, but the **between-individual metric structure of that geometry is not stable**.

This distinction matters.

The positive geometry-identity statistic asks:

> is a target trajectory closer to the same individual's history than to other individuals?

The present relational test asks:

> are the distances among all individuals preserved across environments?

The first is supported.
The second is not.

Therefore:

> **self correspondence survives without metric preservation among individuals.**

A bat can remain recognizably "itself" while the relative geometric arrangement of all bats changes with task context.

## Relation to portable policy space

Transparent I/M policy space shows much stronger held-out relational stability:
- pair-displacement-vector R² = **0.5797**
- p = **0.0001**
- 97.1% positive directional alignment.

Detailed route geometry does not.

Thus the evidence supports a coarse-to-fine hierarchy:

[
oxed{
	ext{portable policy relational structure}
>
	ext{route-geometry relational structure}
}
]

## Claim boundary

Do not call this a formal topological invariant.
The bounded empirical statement is:
- biological identity correspondence transfers;
- detailed route-space pair distances do not show reliable cross-environment preservation.

## JAE firewall

No change to JAE v0.4.0.
