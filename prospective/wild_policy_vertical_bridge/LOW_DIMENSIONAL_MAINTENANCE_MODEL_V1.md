# Low-dimensional specialization maintenance model v1

## Purpose

This note formalizes the mechanism suggested by the post-freeze bat programme without modifying JAE v0.4.0.

The empirical problem is:

> persistent individual specialization remains detectable even when persistent spatial partitioning is absent.

A minimal model must therefore allow:
- individual repeatability;
- environmental reconfiguration;
- high spatial overlap;
- no continuing exclusion between individuals.

## Generative model

Let the measured movement-policy vector of individual i in environment/task e on bout t be:

`x_iet = mu_e + Lambda_s theta_i + epsilon_iet`

where:

- `mu_e` = task/environment-specific response shared at the population level;
- `theta_i` = persistent low-dimensional individual control coordinate;
- `Lambda_s` = species/task-specific mapping from latent control coordinates into observed movement variables;
- `epsilon_iet` = bout-scale variation and measurement noise.

The realized 3-D route is a further environment-dependent mapping:

`trajectory_iet = F_s(E_e, theta_i, eta_iet)`.

Therefore identical `theta_i` values need not generate identical absolute trajectories when `E_e` changes.

## Maintenance without partitioning

Suppose physical position overlap is summarized by a separate occupancy process:

`space_iet = G_s(E_e, theta_i, eta_iet)`.

Persistent spatial partition is not required if different values of `theta_i` can map to overlapping values of `space`.

Thus:

`theta_i != theta_j`

does **not** imply:

`support(space_i) ∩ support(space_j) = empty`.

Individual specialization can reside in the control rule rather than exclusive spatial support.

## Repeatability condition

For one observed policy axis with loading vector lambda:

`y_iet = lambda' x_iet`

and after removing the environment mean:

`y*_iet = a theta_i + eps_iet`.

If:

`Var(a theta_i) > 0`,

then observations from the same individual on different bouts are positively associated even if positions overlap.

A simple repeatability ratio is:

`R = sigma_theta^2 / (sigma_theta^2 + sigma_epsilon^2)`.

Spatial partitioning does not appear in this expression.

Therefore persistent individuality can be maintained whenever a stable between-individual policy component is large enough relative to within-individual bout noise.

## Scalar-plus-noise prediction

For two individuals i and j:

`Delta y_e = a(theta_i-theta_j) + Delta epsilon_e`.

Consequences:

1. pairwise differences estimated from other environments should predict held-out pairwise differences;
2. ordering errors should be concentrated when `|theta_i-theta_j|` is small;
3. large-separation pairs should retain their order more reliably.

These predictions are observed for *Rhinolophus nippon*:
- no-refit pairwise R² about 0.627;
- ordering errors concentrated at smaller policy margins;
- probability of correct held-out ordering increases with policy separation.

## Two-dimensional extension

The one-dimensional approximation is incomplete.

Current ablation supports:

`theta_i = (theta_I,i, theta_M,i)`

where approximately:

- `theta_I` = FlightIntensity;
- `theta_M` = maneuver / route-organization tendency.

Removing PC1 leaves calibrated identity.
Removing PC1+PC2 eliminates calibrated residual identity.

Hence a useful approximation is:

`x_iet = mu_e + lambda_I theta_I,i + lambda_M theta_M,i + epsilon_iet`.

For *R. nippon*, the two loading directions are highly stable across held-out obstacle configurations.

## Species dependence

The mapping `Lambda_s` need not be universal.

This resolves the apparent contrast:
- low-dimensional portable identity is strong in *R. nippon*;
- fixed Rhino axes do not generalize to *Miniopterus fuliginosus*;
- FlightIntensity does replicate externally in *Carollia perspicillata*.

The biologically plausible general form is therefore:

`shared architecture != shared coefficients`.

Different species may occupy differently oriented policy manifolds while still using low-dimensional control.

## Link to formation

The present model describes maintenance, not origin.

Possible formation mechanisms for `theta_i` include:
- rapid early experience-dependent symmetry breaking;
- persistent morphology/physiology;
- learned motor calibration;
- developmental sensorimotor tuning;
- combinations of these.

The juvenile first-flight evidence argues against a universal slow monotonic divergence process but does not identify the causal source of `theta_i`.

## Link to JAE vertical individuality

The decisive remaining field bridge is:

> does a policy coordinate estimated from one set of wild bouts predict held-out centered vertical organization within the same fine-place × broad-kinematic contexts?

A positive answer would connect:

`persistent individual vertical strategy`

to

`persistent low-dimensional personal policy`

without requiring spatial exclusion.

## Claim ceiling

This model is not:
- a deterministic law of bat flight;
- a universal two-parameter equation;
- an identified neural mechanism.

It is a falsifiable statistical architecture for how specialization can persist without partitioning.
