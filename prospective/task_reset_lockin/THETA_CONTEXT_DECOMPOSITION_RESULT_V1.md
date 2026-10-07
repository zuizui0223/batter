# Rhino stable-theta versus context-specific solution result v1

## Execution

- workflow run: 37633212757
- head SHA: `0670ffad57d262e1c0e6a5e7d1e2cf79e54580bb`
- conclusion: success
- artifact: 11486538507

## Question

For the same held-out trajectory, how much prediction is carried by:

1. a portable scalar personal coordinate estimated from other environments;
2. a repeated same-individual state estimated from other trials in the same environment?

The decomposition was:

[
y_{i,e,t}=	heta_i+h_{i,e}+epsilon_{i,e,t}.
]

## Common target set

30 trajectories from four bats (B–E) had both:
- >=2 other environments for a cross-environment theta estimate;
- >=1 other trajectory in the same bat × environment cell for a context estimate.

Bat A had no repeated within-environment trajectory support and is therefore not part of the h decomposition.

## Predictive decomposition

Equal environment within bat, then equal bat:

### Portable theta gain

[
G_	heta = +0.17273
]

cluster-bootstrap 95% CI:

[
[+0.03337,+0.41497].
]

Supported.

### Context-specific increment

[
G_h = +0.08726
]

95% CI:

[
[-0.11464,+0.36555].
]

Unsupported at the programme level.

### Total personal gain

[
G_{total}=+0.25999
]

95% CI:

[
[+0.04424,+0.47574].
]

Supported.

The exact additive identity
(G_{total}=G_	heta+G_h)
held to numerical precision.

## Individual architectures

| bat | theta | between-environment SD | G_theta | G_h | G_total | descriptive architecture |
|---|---:|---:|---:|---:|---:|---|
| B | +0.175 | 0.610 | +0.040 | +0.057 | +0.097 | mixed / weak |
| C | +0.303 | 0.832 | +0.084 | **+0.499** | +0.583 | strongly context-dependent |
| D | -0.790 | 0.161 | **+0.540** | -0.172 | +0.368 | strongly theta-dominant |
| E | -0.473 | 0.394 | +0.026 | -0.035 | -0.009 | weak on this strict common target set |

Bat A, although not evaluable for the same-environment increment, has:
- theta = +1.070;
- between-environment SD = 0.306;
- held-out full-theta R² = 0.904 in the separate convergence analysis.

## Interpretation

A single portable theta is not merely a population average artifact. It provides positive held-out prediction on the strict common target set.

However, individual architectures differ substantially.

The clearest contrast is:

- D: stable scalar coordinate dominates;
- C: environment-specific personal realization carries much more of the predictive information.

This motivates a richer finite-person model:

[
y_{i,e,t}
=
	heta_i
+
sigma_i u_{i,e}
+
epsilon_{i,e,t},
]

where:
- (	heta_i) is the portable personal coordinate;
- (sigma_i) is an individual-specific context-sensitivity amplitude;
- (u_{i,e}) is the environment-specific realization.

At present (sigma_i) is only a hypothesis-level second personal parameter, not independently identified.

## Descriptive variance signal

Across all five bats:
- SD of bat-level theta values: approximately 0.725;
- RMS within-bat between-environment SD: approximately 0.518.

A rough variance-ratio summary places about two thirds of scalar variation in the stable between-individual component and one third in within-individual environment dependence.

This is descriptive because the design is unbalanced and the within-bat term combines genuine bat × environment interaction with finite cell-estimation noise.

## Claim ceiling

Supported:
- a portable scalar personal component;
- strong heterogeneity among individuals in context dependence.

Not established:
- that context sensitivity is itself a stable scalar trait;
- that h is learned route memory;
- a finite environmental feature basis for h;
- a universal two-parameter law across bats or species.
