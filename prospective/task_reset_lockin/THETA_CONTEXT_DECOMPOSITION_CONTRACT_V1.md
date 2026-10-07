# Rhino stable-theta versus context-specific solution decomposition v1

## Status

**POST-PRIMARY MECHANISM DIAGNOSTIC. NOT CONFIRMATORY.**

Frozen after:
- full 8-D cross-configuration identity was supported;
- a one-dimensional FlightIntensity scalar was supported;
- theta convergence with increasing environments was supported;
- the environment-specific decomposition below has not yet been calculated.

## Question

How much of an individual's scalar flight policy is carried by:

1. a **portable personal coordinate** (	heta_i) that transfers across obstacle configurations;
2. a **configuration-specific personal realization** (h_{i,e}) that is repeatable only within the current environment?

Use the decomposition

[
y_{i,e,t}=	heta_i+h_{i,e}+epsilon_{i,e,t},
]

where (y) is the already-defined within-environment standardized FlightIntensity.

## Data

Use exactly the authoritative 45 feature-valid *Rhinolophus nippon* trajectories from the Teshima configuration programme and the same transparent scalar:

[
FlightIntensity =
[z(v_{med})+z(v_{90})+z(|v_z|_{med})+z(|v_z|_{90})]/4.
]

Within each environment, the four contributing features are standardized exactly as in the existing scalar programme before averaging.

## Target gate

For a trajectory target (y_{i,e,t}), require both:

- at least **2 other environments** for the same bat, to estimate portable (	heta_i);
- at least **1 other trajectory in the same bat × environment cell**, to estimate context-specific personal state.

Only targets satisfying both enter the primary decomposition.

No target may contribute to its own predictor.

## Models

### M0 — environment-standardized population baseline

[
hat y_0=0.
]

### M1 — portable personal theta

For target environment e:

1. average training trajectories within each other environment for bat i;
2. average those environment centroids equally:

[
hat	heta_{i,-e}
=
mean_{e'
eq e}(ar y_{i,e'}).
]

This contains no target-environment observation.

### M2 — context-specific personal solution

Use only other trajectories of the same bat in the same target environment:

[
hat c_{i,e,-t}
=
mean_{t'
eq t}(y_{i,e,t'}).
]

This contains no target trajectory but may exploit repeated exposure to the same obstacle configuration.

## Additive predictive decomposition

For every eligible target define squared errors:

[
E_0=(y-hat y_0)^2
]
[
E_	heta=(y-hat	heta)^2
]
[
E_c=(y-hat c)^2.
]

Then:

### portable-theta gain
[
G_	heta=E_0-E_	heta
]

### context-specific increment
[
G_h=E_	heta-E_c
]

### total personal gain
[
G_{total}=E_0-E_c
]

with the exact identity:

[
G_{total}=G_	heta+G_h.
]

Positive gain means lower held-out squared error.

## Aggregation

Primary:
1. equal target trajectories within bat × environment;
2. equal environments within bat;
3. equal bats.

Also report:
- raw target-weighted means;
- individual bat means.

## Uncertainty

Cluster bootstrap biological bats with replacement.

B = 9,999.

Seed = 20261007901.

Report percentile 95% CIs for:
- (G_	heta);
- (G_h);
- (G_{total}).

A component is supported when its equal-bat mean is >0 and the bootstrap 95% lower bound is >0.

## Individual stability descriptors

For each bat report:
- number of eligible target environments;
- mean (G_	heta);
- mean (G_h);
- mean (G_{total});
- SD of its bat×environment centroids;
- full-data theta.

These descriptors test whether some bats are theta-dominant while others are context-dominant.

## Interpretation

### (G_	heta>0), (G_happrox0)

A stable scalar personal coordinate is sufficient; repeated configuration-specific experience adds little.

### (G_	heta>0), (G_h>0)

A stable personal prior exists, but each environment also induces a repeatable individual-specific offset.

### (G_	hetale0), (G_h>0)

The individual is recognizable mainly through configuration-specific solutions rather than a portable scalar coordinate.

### Both unsupported

The scalar endpoint is too noisy under the strict common target set.

## Claim ceiling

This is a predictive decomposition, not a unique mechanistic identification.

The context-specific term (h_{i,e}) can include:
- learned lane/route placement;
- obstacle-specific control;
- repeated start-state effects;
- other stable within-configuration conditions.

It must not automatically be called route memory.
