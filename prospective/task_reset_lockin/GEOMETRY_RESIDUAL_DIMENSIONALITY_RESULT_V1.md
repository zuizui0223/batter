# Cross-fitted residual-geometry dimensionality result v1

## Status

**NO LEADING TWO-PC RESIDUAL CARRIER. RESIDUAL IDENTITY REMAINS OUTSIDE THE FIRST TWO RESIDUAL PCs.**

Authoritative workflow:
- run: **37424852642**
- job: **112142085451**
- conclusion: **success**
- fail-closed shell: `set -euo pipefail`

Parent:
`GEOMETRY_RESIDUAL_DIMENSIONALITY_CONTRACT_V1.md`

This is a post-primary exploratory falsification diagnostic.

## Question

The parent cross-fitted I/M -> geometry test leaves held-out residual geometry identity.

Does that residual identity collapse onto one or two additional training-only principal axes?

For each held-out environment:
- the I/M -> geometry residual was rebuilt using only the other six environments;
- PCA was fit to training residual geometry only;
- held-out trajectories contributed no PCA direction or centering parameter.

## Variance structure

Across the seven leave-one-environment folds:

### PC1 variance fraction
- min = **0.5612**
- median = **0.5701**
- max = **0.5996**

### PC1 + PC2 variance fraction
- min = **0.7229**
- median = **0.7416**
- max = **0.7670**

Thus the first two residual PCs capture about three quarters of residual variance.

## D1 — PC1 identity

- K = **+0.07071**
- positive bats = **3/5**
- p = **0.2284**

Verdict:
**UNSUPPORTED**

The dominant residual-variance axis is not a supported portable identity carrier.

## D2 — PC1 + PC2 identity

- K = **+0.15825**
- positive bats = **5/5**
- p = **0.0608**

Verdict:
**UNSUPPORTED**

Despite all five bats being directionally positive, the predeclared calibration does not support a portable leading-two-PC residual carrier.

Do not relax the p threshold.

## D3 — residual after PC1 + PC2

After removing the first two training residual PCs:

- K = **+0.15833**
- positive bats = **5/5**
- p = **0.0075**
- null 95% interval = **[-0.1182,+0.1211]**

Verdict:
**SUPPORTED**

## Main interpretation

The cross-fitted geometry identity left beyond I/M is **not** well described as one additional portable residual axis, nor as a leading two-dimensional residual subspace.

Instead, identity remains in the lower-variance residual complement after the first two PCs are removed.

Therefore the data argue against the simple rescue:

[
	heta_i=(I_i,M_i,	ext{third portable geometry axis}).
]

A better bounded interpretation is:

> **I/M captures the strongest portable coarse policy, while the remaining geometry identity is distributed across lower-variance, context-sensitive structure rather than one dominant extra portable coordinate.**

This is consistent with:
- environment-dependent geometry realization;
- omitted nonlinear/context interactions;
- several weak system-specific coordinative details.

It does not prove high-dimensional neural control.

## Important variance/identity distinction

The leading residual PCs explain most **variance** but not most **identity**.

Thus:

[
oxed{
	ext{largest behavioral variance directions}

eq
	ext{most identity-bearing directions}
}
]

in the residual geometry space.

This is an important reason not to infer personal-policy dimensionality from PCA variance alone.

## Relation to V16

The result strengthens the distinction between:

- a robust, interpretable coarse personal coordinate I/M;
- detailed geometry whose residual personal information is weaker and context sensitive.

Do not add a third empirical policy axis based on the present archive.

## Claim ceiling

Not established:
- exact residual dimensionality;
- nonlinear absence from PC1/PC2;
- anatomical dimensionality;
- universal high-dimensional personal state.

The result only rejects the predeclared leading-PC simplification under held-out transfer.

## JAE firewall

No change to JAE v0.4.0.
