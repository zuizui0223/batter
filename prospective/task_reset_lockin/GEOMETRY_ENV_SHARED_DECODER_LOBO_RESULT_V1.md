# Leave-one-bat-out environment-specific I/M -> geometry decoder result v1

## Status

**SHARED LINEAR ENVIRONMENT DECODER NOT SUPPORTED.**

Authoritative workflow:
- run: **37424003468**
- job: **112139435637**
- conclusion: **success**
- fail-closed shell: `set -euo pipefail`

Parent:
`GEOMETRY_ENV_SHARED_DECODER_LOBO_CONTRACT_V1.md`

This is a post-primary exploratory falsification diagnostic.

## Design

For every focal bat in Env1–Env4:

- movement scaling estimated from other bats only;
- geometry scaling estimated from other bats only;
- linear I/M -> geometry map fit to other bats only;
- focal bat contributes no value to scaling or coefficients;
- fitted map applied unchanged to focal trajectories.

Residual-identity population:
- B
- C
- D
- E

Bat A is structurally excluded from the cross-environment residual-identity statistic because it has only two supported peer-map environments.

## Predictive adequacy

Across focal held-out trajectories:

- decoder SSE = **1211.15**
- zero/environment-centered baseline SSE = **887.42**
- descriptive held-out-bat R² = **-0.3648**

Thus the other-bat environment-specific linear decoder predicts focal detailed geometry **worse than the zero-centered baseline**.

This fails the necessary predictive gate for interpreting a disappearance of residual identity as successful explanation.

## Residual identity

After applying the peer-trained decoder:

- K = **+0.05876**
- positive bats = **3/4**
- 9,999 / 9,999 valid permutations
- null mean = **-0.02742**
- null 95% interval = **[-0.7495,+0.8437]**
- one-sided p = **0.3987**

Verdict:

**UNSUPPORTED_IDENTITY_BEYOND_SHARED_ENV_DECODER**

## Interpretation

Residual identity disappears, but the decoder itself is not predictive.

Therefore the result does **not** support:

[
g_{i,e}=G_e	heta_i
]

with a peer-estimable shared linear (G_e).

The same qualitative boundary was reached independently by the earlier peer-defined map:
- predictive R² = **-1.419**
- residual identity unsupported.

Two implementations therefore agree on the important point:

> **the current archive is too sparse / the mapping too heterogeneous for a simple shared linear environment decoder to explain detailed route geometry.**

## Current model boundary

Supported:
- policy coordinates are portable;
- detailed geometry remains identity-bearing;
- one cross-environment linear decoder fails;
- peer-only same-environment linear decoders are predictively inadequate.

Not identified:
- a shared (G_e);
- an individual-specific decoder;
- a nonlinear environment map;
- additional latent policy dimensions.

## No rescue

Do not:
- add ridge/nonlinear terms after output;
- lower peer requirements;
- reinterpret residual-identity disappearance as evidence for a successful shared decoder.

## JAE firewall

No change to JAE v0.4.0.
