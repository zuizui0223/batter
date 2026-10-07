# Theta-to-route-centroid linkage contract v1

## Status

**POST-PRIMARY MECHANISM LINKAGE DIAGNOSTIC. NOT CONFIRMATORY.**

Frozen after:
- cross-configuration movement-policy identity was supported in *Rhinolophus nippon*;
- one-dimensional policy sufficiency and FlightIntensity theta convergence were established;
- within-configuration absolute route-centroid identity was already supported;
- no theta-to-route-centroid outcome has been calculated before this contract.

## Question

Does the portable one-dimensional personal policy parameter predict where an individual places its route in a new obstacle configuration?

This tests a mechanistic bridge:

[
portable personal policy;	heta_i
ightarrow
configuration	ext{-}specific spatial realization.
]

If unsupported, theta and route/lane placement should be treated as distinct components.

## Data

Use exactly the authoritative 45 *Rhinolophus nippon* trajectories from the Teshima archive.

### Theta predictor

Use the already-defined transparent scalar:

[
FlightIntensity =
[z(v_{med})+z(v_{90})+z(|v_z|_{med})+z(|v_z|_{90})]/4,
]

with the authoritative within-environment feature standardization.

For target route environment e and bat i:

[
	heta_{i,-e}
=
	ext{equal-environment mean FlightIntensity over all observed environments except e}.
]

Require at least 2 non-target environments for theta.

The target environment never contributes to theta.

### Route response

Use exactly the route-valid trajectories and Primary-A route representation.

Restrict route linkage to the three Primary-A repeat-support environments:

Env1, Env2, Env3.

For every bat × route-environment cell:
- compute each trajectory's absolute 3-D route centroid from its 101-point route;
- average repeated trajectories equally within bat × environment.

Call the resulting vector (c_{i,e}).

Require at least 3 eligible bats in each route environment.

## Environment centering

Within each route environment e, among eligible bats:

[
x_{i,e}=	heta_{i,-e}-ar	heta_{-e}
]

and

[
y_{i,e}=c_{i,e}-ar c_e.
]

No coordinate rotation, reflection, scale normalization, or Procrustes alignment is allowed.

This tests absolute arena-oriented lane placement after removing the configuration mean.

## Leave-one-route-environment-out mapping

For each target route environment (e_0):

Training data:
the other two route environments.

Fit one common 3-D slope vector using training environments only:

[
hat b_{-e_0}
=
rac{sum x_{i,e} y_{i,e}}
{sum x_{i,e}^2}.
]

Predict the held-out route-centroid residual:

[
hat y_{i,e_0}=x_{i,e_0}hat b_{-e_0}.
]

Baseline prediction:
[
hat y=0,
]
the target environment mean route centroid.

## Primary endpoint

For each target bat:

[
G_{i,e}
=
||y_{i,e}||^2
-
||y_{i,e}-hat y_{i,e}||^2.
]

Positive means theta improves squared-error prediction of absolute route-centroid placement beyond the environment mean.

Aggregate:
- equal bat within target environment;
- equal target environment across Env1–Env3.

Programme statistic:
[
G = mean_e(mean_i G_{i,e}).
]

Also report held-out (R^2):

[
R^2=1-rac{mean ||y-hat y||^2}{mean ||y||^2},
]

with the same equal-environment weighting.

## Null

Independently within every scalar environment Env1–Env7:

- permute complete bat × environment FlightIntensity clusters among the bat labels present in that environment;
- preserve scalar values, environment membership, bat-presence pattern, and route data;
- recompute theta from permuted non-target environments;
- re-center theta within every route environment;
- refit the leave-one-route-environment-out slope;
- recompute G.

This breaks only the cross-environment biological identity correspondence linking portable theta to route placement.

Permutations:
9,999.

Seed:
20261007901.

Require 9,500 valid permutations.

One-sided:
[
p=(1+#G_{null}ge G_{obs})/(1+n_{valid}).
]

## Support rule

Call theta-to-route linkage supported only if:
- G > 0;
- p <= 0.05;
- at least 2 of 3 target route environments have positive environment-mean G.

## Secondary reporting

Report:
- target-environment G and R²;
- fitted slope vector for each held-out fold;
- cosine similarities among the three fitted slope vectors;
- individual target gains.

Slope-vector direction is descriptive and must not be named biologically post hoc.

## Interpretation

### Supported

A scalar estimated from other obstacle configurations predicts part of an individual's absolute lane/centroid placement in a new obstacle configuration.

This would connect the portable policy parameter to spatial realization.

### Unsupported

Portable movement intensity and configuration-specific lane placement are statistically distinct layers:

[
behaviour =
portable 	heta_i
+
task	ext{-}specific h_{i,e}
+
residual.
]

## Claim ceiling

This diagnostic does not establish:
- causality from theta to lane placement;
- morphology as the source of theta;
- learned route memory;
- transfer to wild 3-D space use;
- a universal theta-to-space mapping across species.

No target environment, coordinate axis, weighting, scalar definition, or support threshold may change after outcome opening.
