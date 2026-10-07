# Theta fixed-versus-plastic decomposition v1

## Status

Post-primary descriptive synthesis from the authoritative *Rhinolophus nippon* FlightIntensity centroids and theta-convergence result.

This is not a new confirmatory test.

## Model

For bat i in obstacle environment e:

[
y_{i,e}=	heta_i+eta_{i,e}.
]

- (	heta_i): equal-environment personal mean;
- (eta_{i,e}): environment-specific expression / residual around that mean.

The scalar (y) is the already-defined environment-standardized FlightIntensity.

## Individual parameters

| bat | theta | contextual SD sigma_i | leave-one-env theta range |
|---|---:|---:|---:|
| A | +1.0699 | 0.3061 | [0.9565, 1.1606] |
| B | +0.1746 | 0.6104 | [0.0129, 0.4685] |
| C | +0.3028 | 0.8319 | [0.0644, 0.5200] |
| D | -0.7904 | 0.1613 | [-0.8453, -0.7534] |
| E | -0.4735 | 0.3943 | [-0.5571, -0.3061] |

Thus the five bats differ not only in personal position (	heta_i) but also in how strongly environment changes the observed expression around that position.

## Held-out predictability by individual

From the authoritative theta-convergence workflow, using all available non-target environments to estimate theta:

| bat | held-out R² vs zero |
|---|---:|
| A | +0.904 |
| B | -0.603 |
| C | -0.340 |
| D | +0.952 |
| E | +0.442 |

A and D are strongly predictable from a stable personal scalar. E is moderately predictable. B and C show enough environment-dependent expression that the simple scalar mean is worse than the zero baseline for their individual held-out observations.

This does not negate the programme-level scalar result, because cross-individual separation and held-out pairwise calibration are supported overall.

## Descriptive variance comparison

Across the five personal means:

[
SD(	heta_i)=0.7245.
]

Equal-bat mean within-individual contextual variance:

[
mean_i(sigma_i^2)=0.2680.
]

Between-individual variance of theta:

[
Var(	heta_i)=0.5249.
]

A descriptive signal fraction is therefore

[
rac{Var(	heta)}
{Var(	heta)+mean(sigma_i^2)}
=0.662.
]

This is not presented as a formal ICC because the bat × environment table is sparse and unequal. It simply shows that the stable personal component and contextual expression are of comparable order, with the stable component larger overall.

## Important heterogeneity

The portable one-dimensional parameter is not equally rigid in every individual.

Contextual SD relative to the across-bat theta SD:

- A: 0.42
- B: 0.84
- C: 1.15
- D: 0.22
- E: 0.54

C is especially context-sensitive; D especially rigid.

Leave-one-environment jackknife confirms the extremes:
- C sigma remains high: 0.737–0.944;
- D sigma remains low: 0.100–0.180.

For B and E the sigma estimate is more sensitive to which environment is omitted, so their apparent plasticity amplitude is less securely estimated.

## Rank structure

Large theta separations are usually stable across shared environments, whereas the near-tie B–C reverses frequently.

Examples:
- A–D: same sign in 4/4 shared environments;
- A–E: 3/3;
- C–D: 5/5;
- B–D: 3/3;
- B–C: only 1/3.

Thus theta is best interpreted as a stable ordering coordinate with environment-dependent noise/interaction, not an exact deterministic rank in every configuration.

## Revised finite-parameter representation

The data now motivate a minimum individual representation of at least:

[
(	heta_i,sigma_i)
]

rather than theta alone, where:
- theta locates the bat on the portable movement-intensity axis;
- sigma describes the amplitude of context-dependent expression.

A fuller model remains:

[
x_{i,e,t}=mu_e+alpha_{e,t}	heta_i+h_{i,e,t}+epsilon_{i,e,t}.
]

The current archive supports theta strongly, suggests heterogeneity in expression amplitude, and leaves the structure of (h_{i,e,t}) unresolved.

## Mathematical implication

A finite personal parameter can exist even when exact trajectories remain highly variable.

The remaining mathematical question is no longer “does a finite theta exist?” for this Rhino system.

It is:

> how many additional finite parameters are needed to describe individual-specific plasticity around theta?
