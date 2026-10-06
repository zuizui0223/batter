# Cross-fitted I/M residual geometry family result v1

## Status

**RESIDUAL IDENTITY IS LOCALIZED TO MANEUVER GEOMETRY, NOT GLOBAL ROUTE ORGANIZATION.**

Authoritative workflow:
- run: **37425152832**
- job: **112143023593**
- conclusion: **success**
- fail-closed shell: `set -euo pipefail`

Parent:
`GEOMETRY_CROSSFIT_IM_RESIDUAL_FAMILY_CONTRACT_V1.md`

This is a post-primary exploratory localization diagnostic.

## Question

The cross-fitted I/M -> geometry model leaves held-out residual geometry identity.

Which previously frozen broad geometry family carries that model insufficiency?

Families:
- G = global route organization;
- H = horizontal maneuver geometry;
- V = vertical maneuver geometry.

No individual feature was selected after outcome.

## G — global route organization

- K = **+0.02583**
- positive bats = **3/5**
- p = **0.2904**

Verdict:
**UNSUPPORTED**

The cross-fitted I/M insufficiency is not localized to:
- path efficiency;
- normalized net displacement;
- normalized vertical range

as a broad family.

## H — horizontal maneuver geometry

- K = **+0.19588**
- positive bats = **5/5**
- p = **0.0096**

Verdict:
**SUPPORTED**

## V — vertical maneuver geometry

- K = **+0.18380**
- positive bats = **5/5**
- p = **0.0031**

Verdict:
**SUPPORTED**

Frozen diagnostic verdict:

**RESIDUAL_IDENTITY_DISTRIBUTED_MULTIPLE_FAMILIES**

## Interpretation

Within an environment, the transparent I/M representation statistically absorbs the identity-bearing geometry signal.

But when the I/M -> geometry map is learned from other environments and transferred to an unseen environment, the remaining individual signal is concentrated in:

- horizontal turning geometry;
- vertical local-slope geometry;

rather than broad global route organization.

Thus the failure of a universal I/M decoder is best localized to **fine maneuver realization**.

This supports a coarse-to-fine architecture:

[
oxed{
	ext{portable coarse personal policy}
+
	ext{context-sensitive fine maneuver realization}
}
]

rather than:

[
	ext{portable policy}
+
	ext{one additional global route axis}.
]

## Relation to residual PCA

A separate training-only residual PCA shows:
- PC1 explains median **57.0%** of residual variance but does not carry supported identity;
- PC1+PC2 explain median **74.2%**, still unsupported for identity;
- identity remains after removing those two PCs:
  - K = **+0.15833**
  - 5/5 positive
  - p = **0.0075**.

Together:

> **the remaining maneuver identity is distributed across lower-variance residual structure rather than one dominant extra portable axis.**

## Claim boundary

Do not infer:
- independent neural H and V modules;
- a causal third/fourth policy coordinate;
- exact residual dimensionality;
- universal fine-maneuver individuality across species.

The fixed Rhino geometry representation is not externally supported in Carollia.

## JAE firewall

No change to JAE v0.4.0.
