# Geometry identity beyond FlightIntensity theta contract v1

## Status

**POST-PRIMARY MATHEMATICAL-STRUCTURE DIAGNOSTIC. NOT CONFIRMATORY.**

Frozen after:
- full 8-D cross-configuration policy identity was supported in *Rhinolophus nippon*;
- one-dimensional PCA / identity-subspace sufficiency was established;
- transparent FlightIntensity theta was supported and shown to converge with repeated environments;
- scale-free geometry-only identity was separately supported;
- theta did not predict held-out absolute route-centroid placement.

No geometry-after-theta residual identity result has been calculated before this contract.

## Question

Does portable individual geometry contain information beyond the one-dimensional FlightIntensity parameter?

This distinguishes:

[
	ext{one scalar is sufficient to identify individuals}
]

from the stronger claim

[
	ext{all portable individual behavioural structure is one-dimensional}.
]

## Data

Use exactly the authoritative 45 *Rhinolophus nippon* trajectories.

### Theta covariate

Use the exact transparent FlightIntensity scalar from the existing programme:

[
I_q =
[z(v_{med})+z(v_{90})+z(|v_z|_{med})+z(|v_z|_{90})]/4.
]

### Geometry response

Use the exact eight scale-free geometry features from
`GEOMETRY_ONLY_POLICY_DIAGNOSTIC_CONTRACT_V1.md`:

1. 3-D path efficiency;
2. horizontal displacement ratio;
3. absolute vertical displacement ratio;
4. vertical range ratio;
5. median absolute horizontal turn angle;
6. p90 absolute horizontal turn angle;
7. median absolute vertical slope;
8. p90 absolute vertical slope.

Use the already-frozen within-environment standardization from the geometry-only analysis.

## Cross-fitted theta removal

For each held-out target environment e:

- training rows = all trajectories from environments other than e;
- for each geometry feature k, fit ordinary least squares on training rows only:

[
g_{qk}=a_k+b_k I_q+epsilon_{qk}.
]

No bat identity enters the regression.

Apply the training-fitted coefficients to:
- all training trajectories;
- all target-environment trajectories.

Residual vector:

[
r_q = g_q-hat g_q(I_q).
]

No target-environment geometry outcome may be used to fit the regression.

## Cross-environment residual identity

Within every target-environment fold:

- build each bat's training residual centroid by averaging trajectories within environment first, then environments equally;
- require >=2 non-target environments for the focal bat;
- require >=2 donor bats;
- target advantage:

[
K_q =
mean_j ||r_q-ar r_{j,-e}||
-
||r_q-ar r_{i,-e}||.
]

Aggregate:
- equal target within bat;
- equal bat across programme.

This is the same held-out identity architecture as Primary B.

## Null

Within each environment independently:

- permute complete bat × environment trajectory clusters among labels;
- preserve geometry residual vectors, FlightIntensity values, environment membership and cluster sizes;
- break only cross-environment biological identity correspondence.

The cross-fitted geometry~FlightIntensity regressions are label-free and remain fixed under permutation.

Permutations:
9,999.

Seed:
20261007921.

Require >=9,500 valid permutations.

One-sided p:
[
(1+#K_{null}ge K_{obs})/(1+n_{valid}).
]

## Support rule

Residual geometry identity is supported only if:

- K_residual > 0;
- p <= 0.05;
- >=70% evaluable bats have positive individual mean K;
- >=9,500 valid permutations.

## Secondary reporting

Report:
- raw geometry identity reference K = 0.3885703906;
- residual K;
- residual/raw K ratio;
- individual residual K;
- fold-specific regression slopes for each geometry feature.

## Interpretation

### Supported

Portable individual behaviour is not exhausted by one FlightIntensity scalar.

A minimal descriptive representation becomes at least:

[
personal policy = 	heta_i + phi_i + ...
]

where:
- theta captures movement intensity;
- phi denotes scale-free geometry information statistically independent of linear FlightIntensity effects.

This does not prove two true biological latent dimensions; theta and phi may be nonlinear manifestations of a shared deeper state.

### Unsupported

The previously observed geometry-only identity can be statistically accounted for by covariance with FlightIntensity under this linear cross-fitted test.

That would strengthen the one-parameter approximation.

## Claim ceiling

This diagnostic does not establish:
- orthogonal biological control variables;
- neural dimensions;
- causal independence;
- that two dimensions are necessary in every representation;
- universality across species.

No geometry features, theta definition, regression family, folds, weighting, or support rule may change after outcome opening.
