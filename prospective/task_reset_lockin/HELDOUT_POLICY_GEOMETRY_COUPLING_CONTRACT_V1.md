# Held-out policy-to-geometry coupling contract v1

## Status

**POST-PRIMARY MECHANISM DIAGNOSTIC.**

Parents:
- \`TWO_PARAMETER_POLICY_LAW_RESULT_V1\`;
- \`GEOMETRY_ONLY_POLICY_RESULT_V1.md\`;
- \`GEOMETRY_CROSSFIT_IM_EXPRESSION_RESULT_V1.md\`.

The exact environment-specific I/M -> geometry map is not transportable across tasks, and a peer-only target-environment map is not predictively adequate.

This diagnostic asks a lower-dimensional question:

> **Does the distance between two individuals in portable policy space, estimated without the target environment, predict how different their realized scale-free route geometry will be in that target environment?**

## Predictor: strictly held-out personal-policy distance

Within each obstacle environment:
- standardize the original eight movement features exactly as in the transparent-policy programme;
- calculate FlightIntensity I and ManeuveringExtent M;
- average trajectories within bat × environment.

For target environment e and bat i:

\[
\theta_{i,-e}
=
mean_{h\neq e}
(I_{i,h},M_{i,h})
\]

with equal environment weighting.

Require >=2 non-target environments.

For every eligible target bat pair (i,j):

\[
d^\theta_{ij,e}
=
\|\theta_{i,-e}-\theta_{j,-e}\|_2.
\]

No target-environment movement feature enters this predictor.

## Outcome: target-environment geometry distance

Within target environment e:
- calculate the frozen eight scale-free geometry features;
- standardize them with the target environment's label-free mean/SD exactly as in the parent geometry diagnostic;
- average trajectories within bat.

For target pair (i,j):

\[
d^g_{ij,e}
=
\|g_{i,e}-g_{j,e}\|_2.
\]

## Primary statistic

Pool all eligible pair × target-environment observations.

Calculate:

\[
\rho_{PG}
=
Spearman(d^\theta,d^g).
\]

This tests monotonic coupling between portable policy separation and realized detailed-geometry separation.

Also report:
- Pearson r descriptively;
- number of pair × environment observations;
- target-environment pair counts.

## Null

Within every target environment independently:
- keep all held-out \(\theta_{i,-e}\) values fixed;
- permute complete bat labels among target geometry centroids;
- preserve the geometry cloud and number of bats;
- recompute all pair distances and the pooled Spearman statistic.

9,999 permutations.

Seed:
\`202610061801\`.

Require >=9,500 valid null statistics.

## Exploratory support rule

Coupling is supported only if:
- rho > 0;
- one-sided permutation p <= 0.05.

## Interpretation

### Supported

> Individuals farther apart in policy space before seeing a target task tend to realize more different route geometry in that task, even though the exact policy-to-geometry mapping is environment specific.

This would support a portable state whose **degree of differentiation** propagates into detailed realization.

### Unsupported

> Portable policy identity and detailed route geometry are both individualized, but their pairwise separation magnitudes are not stably coupled across unseen tasks.

Then environment/task realization can substantially warp the geometry of individual differences.

## Important non-circularity boundary

The predictor uses I/M estimated from non-target environments only.

Therefore the target geometry outcome cannot trivially correlate with the predictor through same-trajectory feature overlap.

## No rescue

Do not:
- use target-environment I/M;
- select environments after output;
- drop bat A or difficult configurations;
- add nonlinear transforms;
- replace Spearman with a selected alternative after output.

## Claim ceiling

Even a positive coupling does not identify a linear \(G_e\), environmental solution abundance, or causal neural state.
