# Cross-fitted I/M to geometry residual identity result v1

## Status

**SUPPORTED — A TRAINING-ESTIMATED I/M -> GEOMETRY MAP DOES NOT EXHAUST IDENTITY IN AN UNSEEN ENVIRONMENT.**

Authoritative workflow:
- run: **37406552272**
- conclusion: **success**
- fail-closed shell: \`set -euo pipefail\`

Parent:
\`GEOMETRY_CROSSFIT_IM_EXPRESSION_CONTRACT_V1.md\`

This is a post-primary falsification diagnostic.

## Question

Within each obstacle environment, label-free removal of FlightIntensity + ManeuveringExtent eliminates calibrated scale-free geometry identity.

The stronger question was:

> does the same I/M -> geometry relationship transfer to a completely unseen obstacle environment?

For every fold:
- movement-feature mean/SD came from the other six environments only;
- geometry-feature mean/SD came from the other six environments only;
- the linear I/M -> geometry map was fit on the other six environments only;
- the target environment supplied no scaling parameter and no regression coefficient.

## Result

Residual geometry identity after applying the training-estimated I/M -> geometry map to the held-out environment:

- K = **+0.20160**
- positive bats = **5/5**
- 9,999 / 9,999 valid permutations
- null mean = **-0.02569**
- null 95% interval = **[-0.18626,+0.17548]**
- one-sided p = **0.0156**

Verdict:

**SUPPORTED_GEOMETRY_BEYOND_CROSSFIT_IM**

Individual means:
- A = **+0.16147**
- B = **+0.06280**
- C = **+0.24402**
- D = **+0.25872**
- E = **+0.28098**

No individual is negative.

## Interpretation

This result resolves the apparent tension between:
- within-environment I/M sufficiency;
- portable scale-free geometry identity.

Within a given environment, geometry identity lies largely in the transparent I/M span.

But the **mapping from I/M to detailed route geometry changes across obstacle environments**.

Therefore the best model is not:

\[
g_{i,e}=B\theta_i
\]

with one fixed geometry map B.

It is:

\[
\boxed{
g_{i,e}
=
G_e\theta_i
+
\epsilon_{i,e}
}
\]

with an environment-specific expression map \(G_e\).

The personal coordinate can remain portable while the route geometry generated from it is task specific.

## Relation to the two-axis result

The result does **not** falsify portable I/M identity.

I/M itself:
- predicts held-out personal coordinates;
- preserves pairwise individual geometry across configurations.

What fails is stronger:

> one training-estimated linear I/M -> detailed route-geometry map is sufficient for every unseen obstacle configuration.

Thus the transparent two-axis state is best interpreted as a portable empirical personal coordinate whose **behavioral realization is context dependent**.

## Relation to family residualization

Global route organization G and horizontal maneuver H:
- each carries identity alone;
- neither retains supported incremental identity after cross-fitted linear removal of the other.

This suggests a shared low-dimensional geometry organization.

But the orientation/projection of that organization relative to I/M changes among environments.

## Cross-species boundary

The fixed Rhino geometry representation is unsupported in Carollia, while the coarser Rhino-derived policy representation transfers better.

Together:

\[
\boxed{
\text{portable coarse personal state}
+
\text{environment/system-specific geometry map}
}
\]

is better supported than a universal geometry law.

## Claim ceiling

Supported:
- detailed geometry expression is environment dependent;
- a single training-estimated linear I/M -> geometry relation does not exhaust held-out identity.

Not established:
- I/M is a causal internal neural state;
- \(G_e\) is literally linear;
- environment-specific geometry is learned rather than biomechanically constrained;
- solution abundance is measured.

## JAE firewall

No change to JAE v0.4.0.
