# Transparent two-axis policy contract v1

## Status

**POST-PRIMARY INTERPRETABILITY AND FALSIFICATION DIAGNOSTIC.**

Frozen after:
- PC1 was identified as a stable flight-intensity axis;
- PC2 was identified as a stable second axis;
- removal of PC1 alone left calibrated residual identity;
- removal of PC1+PC2 eliminated calibrated residual identity.

No transparent second-scalar identity result has yet been calculated.

## Question

Can the two PCA dimensions carrying cross-configuration individual identity be replaced by two simple, interpretable scalar rules?

## Data

Use exactly the authoritative 45 *Rhinolophus nippon* trajectories and the same eight environment-standardized movement features as Primary B.

Feature order:
1. median 3-D speed;
2. p90 3-D speed;
3. median absolute vertical speed;
4. p90 absolute vertical speed;
5. median absolute horizontal turning rate;
6. p90 absolute horizontal turning rate;
7. path efficiency;
8. vertical range.

## Axis 1 — FlightIntensity

Use the already-frozen transparent scalar:

`I = mean(z1,z2,z3,z4)`.

## Axis 2 — ManeuveringExtent

The signed PC2 stability diagnostic showed robust loadings:
- median speed: negative;
- median/p90 turn rate: positive;
- path efficiency: positive;
- vertical range: positive;
- p90 speed: weakly negative;
- vertical-speed features: near zero.

Freeze the transparent second scalar as:

`M = mean(-z1, z5, z6, z7, z8)`.

The rule uses only features with median absolute PC2 loading >=0.20.

No fitted weights are allowed.

## T1 — PC2 alignment

Define the normalized transparent M direction in 8-D:
`v_M ∝ (-1,0,0,0,1,1,1,1)`.

For each leave-one-environment-out fold:
- compute cosine between oriented PC2 and v_M.

Report min/median/max.

No inferential p-value.

## T2 — ManeuveringExtent-only cross-environment identity

Use exactly the scalar leave-one-environment-out identity architecture used for FlightIntensity:
- training bat centroid = equal-environment mean of M;
- target distance = absolute scalar difference;
- K = mean distance to other-bat centroids minus distance to own centroid;
- equal target -> equal bat aggregation.

Null:
- independently permute complete bat labels within every environment.

9,999 permutations.
Seed:
`202610050921`.

Support rule:
- K>0;
- p<=0.05;
- >=70% positive bat means.

## T3 — transparent 2-D identity

For every trajectory define:
`u = (I,M)`.

Within every held-out target environment:
- form training bat centroids by averaging each scalar within bat × training environment, then averaging training environments equally;
- use ordinary Euclidean distance in the 2-D (I,M) plane.

No additional scaling or fitted rotation.

Use the same environment-wise label permutation null.

9,999 permutations.
Seed:
`202610050922`.

Report:
- K_2D;
- bat means;
- positive fraction;
- p;
- ratio K_2D / K_full8, where K_full8=0.9435600964999665.

## T4 — identity after removing the transparent 2-D span

Define fixed 8-D vectors:
- v_I = (1,1,1,1,0,0,0,0);
- v_M = (-1,0,0,0,1,1,1,1).

Obtain an orthonormal basis Q for their 2-D span by QR decomposition.

For every standardized 8-D feature vector:
`r = z - Q Q' z`.

Run the exact full-vector leave-one-environment-out identity statistic on r.

Null:
- independently permute bat labels within environment;
- fixed transparent basis Q is not refit.

9,999 permutations.
Seed:
`202610050923`.

If residual identity is unsupported, the transparent two-axis span captures the calibrated cross-configuration individual signal to the resolution of this dataset.

## Interpretation

### T2 supported, T3 supported, T4 unsupported

Strongest interpretable result:

> individual policy is approximately two-dimensional: flight intensity plus maneuvering/route organization.

### T2 unsupported but T3 supported, T4 unsupported

The second scalar helps only jointly with intensity; the transparent 2-D span still approximates the identity subspace.

### T4 remains supported

Two transparent axes are incomplete; the PCA two-axis result cannot yet be reduced to these simple formulas.

## Ceiling

This remains a behavioural state-space description.
It does not identify the physiological, morphological, developmental or learned origin of either parameter.
