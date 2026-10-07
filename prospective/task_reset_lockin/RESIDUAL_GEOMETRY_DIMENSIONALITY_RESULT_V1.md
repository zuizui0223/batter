# Residual-geometry dimensionality — authoritative result v1

## Execution

- workflow run: **37630072161**
- artifact: **11487160105**
- conclusion: **success**

## D1 — training-only residual PCA

Minimal sufficient dimension:

[
d_{geometrymid theta}=1.
]

At d=1:
- K = **+0.56879**
- 5/5 bats positive
- p = **0.0106**
- median training residual-geometry variance explained = **57.4%**

All higher cumulative dimensions also remain supported, but the frozen minimal sufficient dimension is one.

## D2 — training-only residual identity subspace

Minimal sufficient dimension:

[
d_{identity, geometrymid theta}=1.
]

At d=1:
- K = **+0.60734**
- 5/5 positive
- p = **0.0090**

Thus one-dimensional sufficiency is recovered independently by:
- unsupervised residual PCA;
- a supervised training-only identity subspace.

## Interpretation

The portable individual structure is not exhausted by the one-dimensional FlightIntensity theta, but the remaining scale-free geometry information is itself compressible to one additional dimension.

The current minimum linear representation is therefore:

[
oxed{
personal policy approx (	heta_i,phi_i)
}
]

where:
- theta = movement-intensity / vigor coordinate;
- phi = scale-free geometry coordinate statistically remaining after theta removal.

This is stronger than saying that individuals merely differ in many movement variables.

It suggests that a high-dimensional trajectory can carry a low-dimensional portable personal state.

## Important distinction

One dimension was sufficient for individual **identification** in the original 8-D policy.

But complete portable individual **representation** requires at least the theta component plus residual geometry.

Therefore:

[
minimal identification dimension = 1
]

while the current linear decomposition supports:

[
minimal descriptive policy coordinates approx 2.
]

This remains a statistical coordinate system, not a claim of two literal neural control variables.
