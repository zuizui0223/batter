# Geometry-policy target-normalization sensitivity result v1

## Status

**SUPPORTED UNDER BOTH TARGET-SCALING RESTRICTIONS.**

Authoritative workflow:
- run: **37401917560**
- job: **112070795027**
- conclusion: **success**
- fail-closed shell: \`set -euo pipefail\`

Parent:
\`GEOMETRY_POLICY_TARGET_NORMALIZATION_CONTRACT_V1.md\`

This is a post-primary robustness diagnostic.

## Question

Does cross-configuration identity in the eight frozen scale-free route-geometry features survive when the held-out obstacle environment contributes less—or no—normalization information?

Parent geometry result:
- K = **+0.38857**
- 5/5 bats positive
- p = **0.0153**

## S1 — target-centered, training-scaled

The held-out environment contributes its feature mean but **not its SD**.

All feature scaling is learned from centered training-environment residuals.

Result:
- K = **+0.42064**
- 5/5 bats positive
- positive fraction = **1.00**
- 9,999 / 9,999 valid permutations
- null mean = **-0.02553**
- null 95% interval = **[-0.27607,+0.29534]**
- one-sided p = **0.0040**

Verdict:
**SUPPORTED**

Therefore target-specific variance normalization is not required for the portable geometry signal.

## S2 — fully training-only global normalization

The held-out environment contributes **neither mean nor SD**.

All centering and scaling parameters come from the other six obstacle configurations.

Result:
- K = **+0.23140**
- 4/5 bats positive
- positive fraction = **0.80**
- 9,999 / 9,999 valid permutations
- null mean = **-0.02142**
- null 95% interval = **[-0.24951,+0.27412]**
- one-sided p = **0.0440**

Individual means:
- A = **-0.2317**
- B = **+0.2970**
- C = **+0.5324**
- D = **+0.2051**
- E = **+0.3542**

Verdict:
**SUPPORTED_ABSOLUTE_TRAINING_SCALE_GEOMETRY_TRANSFER**

## Interpretation

The scale-free geometry signature does not depend on using the unseen environment's variance—or even its mean—to make individuals look comparable.

A personal route-organization signature learned from other obstacle configurations remains detectable when applied unchanged to a new configuration.

This strengthens the interpretation that the geometry-level signal is a portable control phenotype rather than an artifact of target-domain normalization.

The fully training-only result is weaker than the target-centered result, which is biologically sensible:
obstacle geometry causes real population-wide shifts in route shape.

The negative value for bat A under S2 is retained and prevents claiming perfect individual-level transfer.

## Relation to geometry-family ablation

The independent family-ablation diagnostic showed:
- global route organization alone carries identity;
- horizontal maneuver geometry alone carries identity;
- vertical slope alone does not;
- deleting any one broad family leaves calibrated identity.

Together:

> **portable geometry individuality is distributed across several route-control components and survives application to an unseen task without target-derived scaling.**

## Claim ceiling

Supported:
- cross-task portability of scale-free route organization;
- robustness to target normalization.

Not established:
- universal cross-species geometry law;
- direct environmental solution abundance;
- motor degeneracy as the causal origin;
- exact biomechanical or neural carrier.

## JAE firewall

No change to JAE v0.4.0.
