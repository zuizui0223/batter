# Cross-fitted I/M to geometry residual identity contract v1

## Status

**POST-PRIMARY FALSIFICATION DIAGNOSTIC.**

Parents:
- \`GEOMETRY_POLICY_TARGET_NORMALIZATION_RESULT_V1.md\`
- \`GEOMETRY_BEYOND_TRANSPARENT_TWO_AXIS_RESULT_V1.md\`

The within-environment diagnostic shows that jointly removing transparent FlightIntensity (I) and ManeuveringExtent (M) eliminates calibrated geometry identity.

That result still estimates the I/M -> geometry relationship inside the target environment.

This diagnostic removes that remaining target-domain fit.

## Question

> **Does portable scale-free geometry identity remain after geometry is predicted from I/M using only the other six obstacle configurations?**

## Fold construction

For held-out environment e:

1. training = other six environments;
2. target = e;
3. compute training-only mean/SD for the original eight movement features;
4. apply those movement scaling values unchanged to training and target;
5. calculate transparent I and M from those training-defined z scores;
6. compute training-only mean/SD for the eight scale-free geometry features;
7. apply those geometry scaling values unchanged to training and target.

The held-out environment contributes:
- no movement-feature mean;
- no movement-feature SD;
- no geometry mean;
- no geometry SD;
- no regression coefficient.

## Cross-fitted expression map

Fit on training trajectories only:

\[
g
=
a+B
\begin{bmatrix}
I\\
M
\end{bmatrix}
+\epsilon,
\]

where g is the 8-D training-scaled geometry vector.

Use ordinary least squares with an intercept.

Apply the fitted map unchanged to both training and held-out trajectories.

Residual geometry:

\[
g^{res}
=
g-\widehat g(I,M).
\]

## Identity statistic

For each held-out target trajectory:
- construct bat centroids from residual geometry in training environments;
- average trajectories within environment first;
- average environments equally within bat;
- own-distance versus equal donor-bat distance;
- equal target trajectories within bat;
- equal bats for programme K.

Require:
- all seven environments structurally usable;
- >=3 evaluable bats;
- all fold scaling SDs finite and >0.

## Null

Within every environment independently permute complete bat labels among bat × environment clusters.

The:
- training scaling;
- I/M values;
- I/M -> geometry regressions;
- residual geometry vectors

are label-free and fixed within a permutation.

9,999 permutations.

Seed:
\`202610061601\`.

Require >=9,500 valid null statistics.

## Support rule

Residual geometry beyond cross-fitted I/M is supported only if:
- K > 0;
- p <= 0.05;
- >=4/5 bats positive.

## Interpretation

### Unsupported

Strongest bounded conclusion:

> **A training-estimated transparent I/M policy is sufficient to remove the portable identity component of scale-free route geometry in an unseen obstacle configuration.**

This would strongly support a compact personal policy upstream of detailed geometry.

### Supported

Then the within-environment I/M sufficiency result does not transfer as an expression map across tasks; unseen environments contain additional geometry-level identity.

## No rescue

Do not:
- add nonlinear terms;
- refit in the target environment;
- use target means/SDs;
- select geometry features;
- rotate I/M;
- drop environments or bats.

## Claim ceiling

Even an unsupported residual does not establish:
- literal neural two-dimensionality;
- causal sufficiency of I/M;
- universality across species.

It establishes only that a simple training-estimated linear I/M expression map captures the portable geometry identity at the resolution of this archive.
