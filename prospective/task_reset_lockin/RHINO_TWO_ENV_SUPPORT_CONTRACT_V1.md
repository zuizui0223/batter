# Rhino two-training-environment support diagnostic v1

## Status

POST-PRIMARY support-matching diagnostic.

Frozen after:
- Rhino one-dimensional cross-configuration identity was supported;
- Rhino theta convergence was supported;
- Miniopterus failed every linear dimensionality from 1–8 under its much smaller archive.

No two-training-environment identity result has been calculated before this contract.

## Question

Does the Rhino one-dimensional personal signal survive when every held-out prediction is forced to estimate each bat's training centroid from exactly **two** non-target environments, matching the key per-target support limitation of the Miniopterus archive?

## Data

Use the same 45 authoritative *Rhinolophus nippon* trajectories and environment-wise standardization.

Evaluate two already-defined one-dimensional representations:

1. training-only leave-one-environment-out PCA1;
2. transparent FlightIntensity scalar.

No new feature fitting is allowed.

## Exactly-two-environment centroid estimator

For a held-out target environment e and assigned bat b:

- collect all non-target environments containing b;
- require at least 2;
- enumerate every unordered pair of those environments;
- for each pair, average the two bat×environment cluster centroids equally;
- self distance = mean distance from target to all own two-environment centroids.

For each donor bat:
- construct all of its two-environment centroids in the same way;
- donor distance = mean distance from target to those centroids.

Other distance = equal-donor mean donor distance.

Target advantage:

[
K = D_{other}-D_{self}.
]

Aggregate equal target trajectory -> equal biological bat -> programme.

Thus every identity comparison uses exactly two training environments per personal centroid.

## Null

Within each environment independently permute complete bat×environment clusters among labels.

Rebuild:
- label presence;
- all exactly-two-environment centroids;
- target identity;
- self and donor distances.

9,999 permutations per representation.

Seeds:
- PCA1: 20261007911
- FlightIntensity: 20261007912

## Support rule

Descriptively supported if:
- K > 0;
- one-sided p <= .05;
- >=4/5 evaluable bats have positive mean K;
- all 9,999 permutations valid.

## Interpretation

If supported, the Rhino/Mini contrast cannot be explained simply by Rhino having more than two training environments available for each held-out personal estimate.

It still does not equalize:
- total trajectory count;
- exact environment incidence;
- species biology;
- measurement noise.
