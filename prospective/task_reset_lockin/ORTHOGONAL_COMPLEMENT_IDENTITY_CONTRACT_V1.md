# Orthogonal-complement identity contract v1

## Status

**POST-PRIMARY DIMENSIONALITY FALSIFICATION DIAGNOSTIC.**

Frozen after:
- full 8-D cross-configuration identity was supported;
- one-dimensional PCA identity was sufficient;
- rank-one held-out reconstruction was supported.

No identity test in the orthogonal complement of PC1 has yet been calculated.

## Question

Does transferable individual identity remain after the dominant one-dimensional policy axis is removed?

If little or no identity remains, the portable individual signal is concentrated in a rank-one subspace.

If substantial identity remains, one dimension is sufficient for discrimination but not exclusive as a carrier.

## Data

Use exactly the authoritative 45 *Rhinolophus nippon* trajectories and the exact eight Primary-B environment-standardized movement features.

## Leave-one-environment-out axis

For target environment e:

1. fit ordinary PCA to trajectory-level standardized vectors from all other environments;
2. retain training PC1 unit vector `lambda_-e`;
3. do not use bat labels to fit the axis.

## Orthogonal residual

For every training and target trajectory vector z in that fold:

`r = z - lambda_-e (lambda_-e^T z)`.

Thus all information along PC1 is removed exactly.

No re-fitting or rotation is done after removal.

## Identity estimator

Within each held-out fold:

- construct bat × environment centroids from residual vectors;
- training centroid for bat i averages environments equally;
- target identity advantage:
  `K = mean distance to other-bat training centroids - distance to own training centroid`;
- require >=2 training environments for focal and donor bats;
- equal target -> equal bat -> equal target-environment aggregation.

Pool across held-out environments using the same equal-bat logic as the authoritative Primary B diagnostic.

## Null

Within every environment independently:
- permute complete bat × environment trajectory clusters among labels;
- preserve residual feature vectors, environment membership and cluster sizes;
- break only cross-environment identity correspondence.

PC1 axes are label-free and remain fixed within each fold.

9,999 permutations.

Seed:
`202610050921`.

One-sided p for positive residual identity.

## Secondary fixed transparent-axis removal

Also remove the normalized transparent FlightIntensity direction:

`v_FI=(1,1,1,1,0,0,0,0)/2`

from every environment-standardized vector:

`r_FI=z-v_FI(v_FI^T z)`.

Use the same cross-configuration identity estimator and null.

9,999 permutations.

Seed:
`202610050922`.

## Interpretation

### PC1 complement unsupported

> most transferable individual information is concentrated in the dominant one-dimensional policy direction.

### PC1 complement supported

> additional individual policy dimensions remain after removing the dominant axis.

### Transparent-axis complement supported while PC1 complement fails

The data-adaptive PC1 contains identity information beyond the simple four-speed FlightIntensity proxy.

### Both complements fail

A strong approximately scalar carrier result.

## Ceiling

Failure of residual identity does not prove exact mathematical one-dimensionality; power is limited by five individuals and 45 trajectories.
