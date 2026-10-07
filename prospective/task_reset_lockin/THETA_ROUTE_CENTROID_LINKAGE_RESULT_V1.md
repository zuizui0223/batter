# Theta-to-route-centroid linkage — authoritative result v1

## Execution

- workflow run: **37628504520**
- head SHA: `3e9a99df12cdfcbe92bce11c73e62dbbfe673804`
- conclusion: **success**
- artifact: **11485461849**

## Result

Portable FlightIntensity theta was estimated from non-target obstacle environments and used to predict the bat's absolute 3-D route-centroid placement in held-out Env1–Env3.

Programme result:

[
G=-0.10776,
]

[
R^2=-0.5243,
]

one-sided permutation:

[
p=0.948.
]

Target-environment mean gains:
- Env1: +0.0320, R²=+0.101;
- Env2: +0.0452, R²=+0.119;
- Env3: -0.4005, R²=-1.793.

Two of three environments are weakly positive, but the frozen programme-level support rule fails decisively.

Verdict:

`UNSUPPORTED_THETA_TO_ROUTE_CENTROID_LINKAGE`

## Interpretation

The portable one-dimensional FlightIntensity parameter does not provide a stable cross-configuration mapping to absolute lane/route-centroid placement.

This supports a layered representation:

[
behaviour
=
portable personal policy;	heta_i
+
configuration	ext{-}specific spatial realization;h_{i,e}
+
residual.
]

Within-configuration route centroid identity remains real, but its direction in arena space is not predicted by the scalar theta learned from other obstacle configurations.

Thus a one-dimensional theta is sufficient for portable individual identification, but is not a complete coordinate system for all individual-specific spatial behaviour.
