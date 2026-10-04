# Post-primary route-axis decomposition contract v1

## Status

**POST-PRIMARY DIAGNOSTIC.**

Frozen after:
- Primary A PASS in absolute 3-D arena coordinates;
- start-centered and chord-residual A FAIL;
- start point, end point and displacement-vector identity unsupported.

This contract cannot rescue or replace Primary A.

## Question

What part of the absolute obstacle-anchored trajectory carries the within-configuration individual signal?

Use exactly:
- authoritative *Rhinolophus nippon* route-valid trajectories;
- Env1–Env3;
- Primary A target/donor weighting;
- Primary A within-environment trajectory-label permutation.

## X1 — absolute horizontal route identity

Use the frozen 101-point routes but retain only X and Y.

Distance:
mean pointwise 2-D Euclidean distance.

9,999 permutations.
Seed:
`202610042241`.

Interpretation:
support indicates individual-specific horizontal obstacle-lane placement.

## X2 — absolute vertical-profile identity

Use only Z along the 101 normalized arc-length positions.

Distance:
mean absolute Z difference.

9,999 permutations.
Seed:
`202610042242`.

Interpretation:
support indicates individual-specific vertical placement/profile under the same obstacle configuration.

## X3 — trajectory-centroid identity

For each route calculate:

`c_q = mean_s r_q(s)`

in absolute 3-D arena coordinates.

Use 3-D Euclidean centroid distance and the same identity estimator/null.

9,999 permutations.
Seed:
`202610042243`.

Interpretation:
support means a persistent overall spatial offset/lane explains a substantial part of absolute-route identity.

## X4 — centroid-centered route identity

For each route:

`r_c(s) = r(s) - c_q`.

Use the original pointwise 3-D route distance and identity estimator/null.

9,999 permutations.
Seed:
`202610042244`.

Interpretation:
- X3 supported + X4 absent: identity is mainly absolute lane/placement.
- X4 supported: within-route organization survives removal of mean spatial placement.
- X1 supported, X2 absent: primarily horizontal obstacle-lane identity.
- X2 supported: vertical policy contributes.

## Ceiling

These diagnostics identify where the statistical signal lies. They do not determine whether obstacle-anchored placement is learned, biomechanical, or imposed by session geometry.

