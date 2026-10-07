# Rhino one-dimensional exhaustiveness diagnostic v1

## Status

**POST-PRIMARY MATHEMATICAL-STRUCTURE DIAGNOSTIC. NOT CONFIRMATORY.**

Frozen after:
- full 8-D cross-configuration individual-policy identity was supported;
- one-dimensional training-only PCA and supervised identity subspaces were sufficient for held-out identity;
- transparent FlightIntensity was supported;
- theta convergence was supported;
- no residual-identity result after removing one personal axis has been calculated.

## Question

A one-dimensional axis can be **sufficient to identify** individuals without being **exhaustive of all portable individual differences**.

This diagnostic asks:

> after removing one frozen/training-only personal axis, does an orthogonal portable individual signature remain?

If residual identity remains, the correct model is low-dimensional but not literally one-parameter exhaustive.

## Data

Use exactly:
- 45 authoritative *Rhinolophus nippon* trajectories;
- Env1–Env7;
- the same 8 environment-standardized movement features.

For every environment × feature:
- subtract environment mean;
- divide by environment sample SD.

No new feature selection.

## R1 — remove transparent FlightIntensity direction

Define the fixed unit vector

[
u_F=(1,1,1,1,0,0,0,0)/2.
]

For every standardized 8-D trajectory z:

[
z_perp=z-(z^T u_F)u_F.
]

This removes the complete equal-weight four-feature FlightIntensity direction while retaining the orthogonal 7-D subspace.

Run the exact frozen Primary-B leave-one-environment identity estimator on (z_perp).

Null:
within every environment independently permute complete bat × environment clusters among labels.

9,999 permutations.
Seed: 20261008301.

## R2 — remove training-only PCA1

For every held-out environment e:

1. fit PCA on all trajectories in the other six environments only;
2. let (u_{PCA,-e}) be training PC1;
3. project both training and target trajectories into the 7-D orthogonal complement:
   [
   z_perp=z-(z^Tu)u;
   ]
4. calculate the held-out identity advantage in that fold.

The target environment never influences the removed axis.

PCA is label-free; under permutations the fold bases stay fixed.

9,999 environment-wise cluster-label permutations.
Seed: 20261008302.

## R3 — remove training-only supervised identity axis

This is the strongest exhaustiveness diagnostic.

For each held-out environment and current label assignment:

1. in the six training environments, calculate each bat's centroid separately within each environment;
2. average environment centroids equally within bat;
3. center bat centroids by their grand mean;
4. SVD the centered bat-centroid matrix;
5. take the first right-singular vector (u_{ID,-e});
6. remove that axis from every training and target trajectory;
7. compute held-out identity in the orthogonal residual space.

For every permutation the supervised identity axis must be recomputed from the permuted **training** labels.

9,999 permutations.
Seed: 20261008303.

## Common estimator

For each held-out target trajectory:
- own reference = equal-environment mean of the focal bat's training centroids;
- other reference = equal mean distance to eligible other-bat training centroids;
- target K = distance-to-other minus distance-to-self.

Aggregate:
equal target trajectory within bat, then equal bat.

Candidate bats and target support are inherited from Primary B.

## Support rule

Residual portable identity is supported for a route only if:
- K_residual > 0;
- one-sided permutation p <= 0.05;
- >=70% of evaluable bats have positive residual K;
- >=9,500 valid permutations.

## Interpretation

### R3 unsupported

The strongest available training-only personal identity axis exhausts the calibrated linear cross-environment identity signal.

This would support an approximately one-parameter portable personal component in the measured 8-D policy.

### R3 supported

One dimension is sufficient for identification but not exhaustive. At least one additional orthogonal portable individual component exists.

### R1 supported but R3 unsupported

The transparent FlightIntensity scalar is an approximation to the dominant personal axis; a better one-dimensional linear axis can absorb the remaining portable signal.

### R2/R3 supported

Portable identity is low-dimensional but cannot be represented exhaustively by a single linear scalar.

## Ceiling

Unsupported residual identity does not prove every biological individual difference is one-dimensional.

It applies only to:
- these 8 movement-policy summaries;
- these obstacle configurations;
- linear orthogonal residual structure.

Nonlinear, sensory, physiological, or unmeasured traits can remain.
