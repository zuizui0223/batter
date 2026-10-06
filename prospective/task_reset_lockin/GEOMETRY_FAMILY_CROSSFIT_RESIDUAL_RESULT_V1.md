# Geometry-family cross-fitted residual identity result v1

## Status

**NEITHER RESIDUAL FAMILY SUPPORTED.**

Authoritative workflow:
- run: **37405840519**
- job: **112083102468**
- conclusion: **success**
- fail-closed shell: \`set -euo pipefail\`

Parent:
\`GEOMETRY_FAMILY_CROSSFIT_RESIDUAL_CONTRACT_V1.md\`

This is a post-primary exploratory mechanism diagnostic.

## Question

Global route organization (G) and horizontal maneuver geometry (H) each carry portable individual identity when analysed alone.

Do they retain identity after the part linearly predictable from the other family is removed using **training environments only**?

For every held-out environment:
- normalization uses training environments only;
- the G -> H or H -> G regression is fitted on training trajectories only;
- the fitted mapping is applied unchanged to the held-out environment;
- bat identity is never used in the regression.

## H residual after G

Representation:

\[
H^{res}
=
H-\widehat H(G).
\]

Result:
- K = **+0.06290**
- positive bats = **3/5**
- p = **0.1064**
- null mean = **-0.01258**
- null 95% interval = **[-0.10625,+0.11140]**

Verdict:

**UNSUPPORTED**

## G residual after H

Representation:

\[
G^{res}
=
G-\widehat G(H).
\]

Result:
- K = **+0.00604**
- positive bats = **4/5**
- p = **0.4035**
- null mean = **-0.00624**
- null 95% interval = **[-0.12440,+0.14185]**

Verdict:

**UNSUPPORTED**

## Interpretation

The family-ablation result remains true:
- G alone carries identity;
- H alone carries identity;
- dropping either family from the full geometry vector still leaves identity.

But the cross-fitted residual test shows that neither family contributes a clearly supported **incremental linear identity component** after accounting for the other.

Thus the most coherent current interpretation is:

> **global route organization and horizontal maneuver geometry are two observable manifestations of a shared lower-dimensional personal coordination state, rather than two independently identity-bearing modules.**

This is consistent with the separate I/M falsification diagnostic:
- FlightIntensity alone does not remove geometry identity;
- FlightIntensity + ManeuveringExtent together do.

The geometry results therefore support a compact latent personal policy more strongly than a high-dimensional modular fingerprint.

## Claim boundary

Do not conclude:
- G and H are mathematically identical;
- nonlinear residual information is absent;
- the control system literally has two neural dimensions;
- motor degeneracy is disproven.

The present result only shows that simple cross-fitted linear residual identity is unsupported in both directions.

## JAE firewall

No change to JAE v0.4.0.
