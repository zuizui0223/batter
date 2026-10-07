# Rhino combined personal-policy dimensionality contract v1

## Status
POST-PRIMARY MATHEMATICAL-STRUCTURE DIAGNOSTIC. NOT CONFIRMATORY.

Known before freezing:
- the original eight movement-policy features transfer individual identity across obstacle configurations;
- a one-dimensional movement-intensity axis is sufficient within that feature family;
- scale-free route geometry also transfers identity;
- geometry identity remains after linear removal of FlightIntensity.

Unknown before this contract:
- the minimum dimension of the combined movement + scale-free-geometry individual policy.

## Question
How many stable individual coordinates are required to carry held-out cross-configuration identity when both policy families are represented together?

## Data
Use exactly the authoritative 45 Rhinolophus nippon trajectories.

Feature vector = 16 frozen features:
A. original Primary-B eight movement features:
median/p90 3-D speed; median/p90 absolute vertical speed; median/p90 horizontal turn rate; path efficiency; absolute vertical range.
B. frozen geometry-only eight features:
3-D path efficiency; horizontal displacement ratio; absolute vertical displacement ratio; vertical range ratio; median/p90 horizontal turn angle; median/p90 absolute vertical slope.

No pulse or absolute route coordinates.

## Standardization
Within every obstacle environment and feature:
subtract environment mean and divide by environment sample SD.
Require all 16 feature SDs finite and positive in all usable environments.
No outcome-based feature dropping.

## Leave-one-environment-out supervised identity subspace
For each target environment:
1. use all other environments as training;
2. compute one 16-D centroid per bat per training environment;
3. average training environments equally within bat;
4. center the five training bat centroids by their grand mean;
5. SVD the centered bat-centroid matrix;
6. project training and held-out trajectories onto the first d right-singular vectors.

Evaluate d=1,2,3,4 (maximum nontrivial between-bat rank with five bats).

Identity statistic uses the exact Primary-B architecture:
- equal trajectory within bat x training environment;
- equal training environments within bat;
- target distance to own training centroid vs equal donor-bat centroids;
- equal target trajectories within bat;
- equal bats programme-wide.

## Null and family-wise calibration
Within every environment independently permute complete bat x environment trajectory clusters among bat labels.
For every permutation and held-out fold, recompute the training-only identity subspace.

B=9,999; seed=20261007951.

For each permutation retain max(K_d) over d=1..4.
Adjusted p_d=(1 + number of max-null >= observed K_d)/(B+1).

## Support
Dimension d is supported only if:
- K_d>0;
- max-T adjusted p_d<=0.05;
- all 5 bats evaluable and >=4/5 have positive individual mean K.

The minimal supported d is the smallest d satisfying the rule.

## Interpretation
- d=1 sufficient: the combined portable individual policy can be represented by one latent coordinate even though multiple observable feature families carry it.
- d=2 minimal: at least two stable individual coordinates are required; a natural descriptive interpretation would be intensity plus coordinative geometry, but loadings must support that label.
- d=3/4 minimal: portable individual policy is still finite low-dimensional but not nearly scalar.
- no d supported: combined representation fails to define a stable held-out individual coordinate under this diagnostic.

## Ceiling
This estimates linear predictive dimensionality over the sampled tasks. It does not identify neural variables, lifetime dimensionality, genetic origin, or exact trajectory equations.
