# Peer-defined environment-specific expression map result v1

## Status

**INCONCLUSIVE / PREDICTIVE MAP FAILED.**

Authoritative workflow:
- run: **37407334962**
- job: **112087686450**
- conclusion: **success**
- fail-closed shell: `set -euo pipefail`

Parent:
`PEER_DEFINED_ENVIRONMENT_EXPRESSION_MAP_CONTRACT_V1.md`

This is a post-primary falsification diagnostic.

## Question

The cross-environment test showed that one I/M -> detailed-geometry map learned in other obstacle environments does not exhaust geometry identity in an unseen environment.

This diagnostic asked a stronger alternative:

> **Can the current environment's expression map be learned from other bats in that environment and then applied to a completely excluded focal bat?**

For every focal bat:
- the I/M -> geometry regression excluded that bat entirely;
- at least 3 peer bats were required;
- no ridge/nonlinear rescue was allowed.

## Structural support

The frozen >=3-peer rule admits only Env1–Env4.

Env5–Env7 stop because too few peer bats remain after focal exclusion.

Cross-configuration residual identity therefore has four candidate bats with >=3 supported environments:
- B
- C
- D
- E

A is structurally excluded from the residual-identity programme because only two supported peer-map environments remain for A.

## Peer-map prediction quality

Across **37** focal trajectories predicted from maps fit only to same-environment peers:

[
R^2_{geometry}
=
-1.4192
]

relative to the environment-centered zero prediction.

Thus the peer-defined linear map is **not predictively adequate** for focal detailed geometry.

This is a critical gate on interpretation.

## Residual identity after the peer map

- K = **-0.23321**
- candidate bats = B,C,D,E
- positive bats = **2/4**
- p = **0.6599**
- null mean = **-0.01995**
- null 95% interval = **[-0.6546,+0.8956]**

Verdict under the frozen identity rule:

**UNSUPPORTED_IDENTITY_BEYOND_PEER_ENV_MAP**

## Why this is not evidence for a shared environment map

If the peer-defined map predicted focal geometry well and residual identity disappeared, the natural conclusion would be:

[
	ext{portable personal state}
+
	ext{shared }G_e
ightarrow
	ext{detailed geometry}.
]

But that prerequisite fails badly:

[
R^2=-1.42.
]

The map destroys identity while also worsening geometry prediction.

Therefore the disappearance of residual identity cannot be interpreted as successful removal of a shared environment-specific expression process.

A plausible explanation is that the small peer-only regressions are too unstable and add enough residual noise to erase the identity statistic.

## Current inference

The preceding results remain valid:

1. I/M predicts portable personal coordinates across tasks.
2. Within an environment, I/M is strongly aligned with detailed geometry.
3. A single I/M -> geometry map learned in other environments leaves residual identity in a new environment.

The present test adds:

4. **the available replication is insufficient to identify a predictive shared environment-specific linear map from peers alone.**

Therefore the model

[
g_{i,e}=G_e	heta_i+epsilon_{i,e}
]

remains a useful conceptual decomposition, but (G_e) is **not empirically identified as a peer-estimable shared map** by this archive.

## What remains possible

The failed peer-map prediction is compatible with several alternatives:

- environment-specific maps require more trajectories/individuals to estimate;
- the expression map is nonlinear;
- additional latent personal coordinates are needed;
- individual × environment terms matter;
- geometry realization contains substantial task-specific noise.

The present data cannot distinguish these.

## No rescue

Do not:
- lower the 3-peer threshold;
- add ridge regularization after seeing the result;
- simplify/select geometry outputs post hoc;
- add nonlinear terms;
- reclassify residual-identity failure as support for shared (G_e).

## Strongest bounded statement

> **Detailed route geometry is context dependent, but the current archive does not identify a predictive environment-specific expression map from conspecific data alone.**

## JAE firewall

No change to JAE v0.4.0.
