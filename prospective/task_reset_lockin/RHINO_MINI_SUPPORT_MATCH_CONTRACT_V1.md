# Rhino Mini-like support matching contract v1

## Status

**POST-PRIMARY SUPPORT-STRESS DIAGNOSTIC.**

Frozen after:
- Rhino one-dimensional policy transfer passed;
- Rhino remained supported when every held-out centroid was forced to use exactly two training environments;
- Miniopterus failed the family-wise calibrated dimensionality sweep from PCA dimensions 1–8 and supervised identity dimensions 1–3.

No four-bat / one-trajectory-per-training-environment outcome has been calculated before this contract.

## Question

Can the Rhino–Mini contrast be explained by Rhino having:
- five rather than four individuals;
- multiple trajectories within some bat × environment clusters;
- more precise training cluster centroids?

## Fixed data and representation

Use exactly the authoritative 45 feature-valid *Rhinolophus nippon* trajectories and authoritative within-environment 8-D standardization.

Evaluate:
1. training-only PCA1;
2. transparent FlightIntensity = mean of the first four standardized speed/vertical-speed features.

Do not re-standardize after deleting one bat. This keeps the previously frozen representation fixed and changes only inferential support.

## Four-bat subsets

Evaluate all five leave-one-bat-out subsets of the five authoritative bats:

- omit A;
- omit B;
- omit C;
- omit D;
- omit E.

Each subset therefore contains exactly four biological individuals, matching Miniopterus.

No subset may be selected after outcome opening.

## Exactly two training environments

For every held-out target trajectory:
- its focal bat must have at least two non-target environments;
- every donor bat must have at least two non-target environments;
- every personal centroid is formed from exactly two non-target environments.

## One trajectory per training environment

For a chosen pair of training environments (e1,e2) for bat i:

- enumerate every pair of one trajectory from i in e1 and one trajectory from i in e2;
- for each trajectory pair form the scalar centroid = mean of the two scalar coordinates;
- self distance is the mean target distance to all such one-trajectory-per-environment centroids across all eligible environment pairs.

For donor bats, use the same construction.

Thus no training centroid averages multiple trajectories within an environment.

Target trajectories are scored individually and then aggregated:
equal target trajectory -> equal biological bat -> subset K.

## PCA fitting

For each four-bat subset and held-out target environment:
- fit PCA using only training-environment trajectories belonging to those four bats;
- use authoritative z8 coordinates as input;
- project subset training and target trajectories onto training PC1.

PC1 is label-free and fixed under null permutations.

## Null

For each four-bat subset and representation separately:

Within every environment independently permute complete bat × environment trajectory clusters among the labels present in that subset.

Preserve:
- complete trajectories and scalar coordinates;
- environment membership;
- cluster trajectory counts;
- exact within-environment label multiplicity.

Break only cross-environment identity correspondence.

B = 9,999 per subset × representation.

Seeds:
- PCA1: 20261007920 + omitted-bat index A=1...E=5
- FlightIntensity: 20261007930 + omitted-bat index.

## Subset support rule

A four-bat subset is supported only if:
- K > 0;
- one-sided p <= .05;
- >=3/4 bats have positive K;
- 9,999 valid permutations.

## Programme stress verdict

Call the sparse-support contrast **robust across all four-bat subsets** only if all five leave-one-bat-out subsets are supported for the representation.

Otherwise report the exact supported subset count; do not choose a favorable subset.

## Interpretation

If PCA1 and/or FlightIntensity remain supported across all five subsets, then the Rhino–Mini contrast is not explained by:
- one extra Rhino individual;
- training on more than two environments;
- or within-environment averaging of repeated Rhino trajectories.

It still does not equalize:
- species-specific environment geometry;
- measurement noise;
- exact trajectory counts in target environments;
- nonlinear policy structure.
