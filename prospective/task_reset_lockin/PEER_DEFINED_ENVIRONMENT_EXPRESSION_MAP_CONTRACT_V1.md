# Peer-defined environment-specific I/M -> geometry map contract v1

## Status

**POST-PRIMARY FALSIFICATION DIAGNOSTIC.**

Parents:
- `GEOMETRY_CROSSFIT_IM_EXPRESSION_RESULT_V1.md`
- `GEOMETRY_BEYOND_TRANSPARENT_TWO_AXIS_RESULT_V1.md`
- `GEOMETRY_FAMILY_CROSSFIT_RESIDUAL_RESULT_V1.md`

The current evidence implies:

- transparent FlightIntensity + ManeuveringExtent (I/M) align strongly with identity-bearing route geometry within an environment;
- a single I/M -> geometry map learned from other environments fails to exhaust identity in an unseen environment.

The next question is:

> **Is the missing map environment-specific but shared among individuals?**

## Model

For environment e:

[
g_{i,e}
=
G_e
egin{bmatrix}
1\I_{i,e}\M_{i,e}
end{bmatrix}
+
r_{i,e}.
]

For every focal bat i in environment e, estimate (G_e) using **only other bats in the same environment**.

The focal bat contributes no trajectory to the regression fit.

## Frozen environment support

A focal bat × environment map is evaluable only if:

- at least **3 peer bat identities** remain after excluding the focal bat;
- the peer regression design has rank 3;
- all original eight movement features and all eight geometry features have finite positive within-environment SD.

This rule is frozen before the residual-identity output is calculated.

Because the public configuration has only 2–3 bats in Env5–Env7, those environments are expected to stop rather than be rescued with ridge regression or a lower peer-bat threshold.

## Scaling

Within each environment, before any bat exclusion:

- z-score the original eight movement features using the environment-wide label-free mean and SD;
- construct transparent I and M exactly as frozen;
- z-score the eight scale-free geometry features using the same environment-wide label-free mean and SD.

These transformations use no identity labels.

The peer-only regression then uses biological labels solely to exclude the focal bat.

No target-bat trajectory enters its own (G_e) regression.

## Residual representation

For each focal trajectory:

[
r_{i,e}
=
g_{i,e}
-
widehat G_{e,-i}
egin{bmatrix}
1\I_{i,e}\M_{i,e}
end{bmatrix}.
]

Every bat cluster therefore receives residuals from a map fit without that cluster.

## Cross-configuration residual identity

Use only environments where the focal peer-map gate passes.

A biological bat is candidate-evaluable only if it has peer-map residuals in at least **3 environments**.

For a target environment:
- require residual history from >=2 other supported environments for the same bat;
- require >=2 donor-bat residual centroids;
- average trajectories within environment first;
- average training environments equally;
- equal target trajectories -> equal bat.

Primary diagnostic statistic:

[
K_{peer-map}
=
D_{other}-D_{self}.
]

## Null

Precompute each original bat-cluster residual using its own peer-excluded map.

Then, within each environment independently:
- permute complete bat labels among bat clusters;
- preserve residual vectors and peer-map fits;
- recompute the entire identity statistic.

This is valid because every numerical cluster was residualized using a map that excluded that cluster itself before any pseudo-label assignment.

Permutations:
**9,999**

Seed:
`202610061701`.

Require >=9,500 valid statistics.

## Support rule

Residual identity beyond a shared environment-specific peer map is supported only if:

- K > 0;
- p <= 0.05;
- >=75% of evaluable bats positive.

The higher fraction reflects the expected four-bat evaluable set after the structural >=3-peer gate.

## Interpretation

### Residual identity unsupported

Strong bounded conclusion:

> **Other individuals in the current environment are sufficient to estimate the I/M -> detailed-geometry expression map that removes portable geometry identity from the focal bat.**

This supports:

[
oxed{
	ext{portable personal state}
+
	ext{shared environment-specific expression map}
ightarrow
	ext{detailed route geometry}
}
]

### Residual identity supported

Then even a peer-defined environment-specific map is insufficient.

The minimum model requires:
- additional latent personal coordinates;
- individual × environment expression;
- nonlinear mapping;
- or some combination.

## Prediction-quality secondary

Report the focal-trajectory no-refit multivariate geometry R² of the peer map relative to the environment-centered zero prediction.

This is descriptive and cannot rescue the identity diagnostic.

## No rescue

Do not:
- lower the >=3 peer-bat gate;
- add ridge regularization;
- add nonlinear terms;
- select geometry features;
- refit with focal-bat trajectories;
- include Env5–Env7 by threshold relaxation.

## Claim ceiling

Even if residual identity disappears, do not claim:
- literal neural I/M state;
- (G_e) is mechanistically linear;
- environment geometry has been independently measured;
- the map is learned rather than biomechanically constrained.
