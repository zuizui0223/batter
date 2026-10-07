# Theta-to-lane linkage diagnostic contract v1

## Status

**POST-PRIMARY MECHANISM DIAGNOSTIC. NOT CONFIRMATORY.**

Frozen after all of the following were already known:

- *Rhinolophus nippon* cross-configuration movement policy is strongly individual-specific;
- one portable latent dimension is sufficient;
- the transparent FlightIntensity scalar behaves like a convergent personal parameter theta;
- within repeated obstacle configurations, absolute route centroid/lane identity is supported;
- start point, end point and displacement-vector identity are unsupported;
- centroid-centered route identity is unsupported under the frozen route-axis rule.

No theta-to-lane predictive linkage has been calculated before this contract.

## Question

Can the configuration-specific personal lane be derived from the portable scalar theta, or is an additional individual × environment term required?

Compare:

[
c_{i,e}=a_e+b_e	heta_i+epsilon
]

against the simpler environment-only centroid baseline.

Here (c_{i,e}) is the 3-D mean route centroid for bat i in environment e.

## Data

Species:
*Rhinolophus nippon*.

Route data:
- exact authoritative route-valid trajectories from the Teshima archive;
- only Env1–Env3, the repeated-route environments used by Primary A;
- bat × environment cell must contain >=2 route-valid trajectories.

Theta data:
- exact transparent FlightIntensity scalar;
- for target environment e, estimate theta for bat i only from that bat's other environments:

[
hat	heta_{i,-e}=mean_{e'
eq e}(y_{i,e'}).
]

Require >=2 non-target environments for theta estimation.

Thus no target-environment FlightIntensity value enters the theta predictor.

## Eligible bat × environment cells

Determine structurally from the frozen data.

Require each evaluated environment to contain >=3 eligible bats.

No environment may be added or dropped after route centroids or theta values are opened.

## Primary L1 — leave-one-bat-out affine lane prediction

Within each eligible environment e:

For each target bat i:

1. use all other eligible bats j != i as training bats;
2. fit a multivariate affine mapping independently by coordinate:

[
c_{j,e,k}=a_{e,k}+b_{e,k}hat	heta_{j,-e},quad kin{x,y,z};
]

3. predict target centroid (hat c_{i,e}^{theta});
4. baseline prediction is the equal-training-bat mean centroid (hat c_{i,e}^{base});
5. compute squared Euclidean errors:

[
E^{theta}_{i,e}=||c_{i,e}-hat c^{theta}_{i,e}||^2
]

[
E^{base}_{i,e}=||c_{i,e}-hat c^{base}_{i,e}||^2.
]

Target gain:

[
G_{i,e}=E^{base}_{i,e}-E^{theta}_{i,e}.
]

Positive means theta improves held-out lane prediction.

Aggregate:
- equal target bat within environment;
- equal environment.

Primary statistic:
[
G=mean_e mean_i G_{i,e}.
]

## Secondary L2 — pairwise monotonic geometry

Within each eligible environment:

- for every unordered bat pair compute
  (|hat	heta_i-hat	heta_j|);
- compute Euclidean distance between their 3-D route centroids;
- calculate Spearman rho across pairs within that environment.

Report equal-environment mean rho.

This is descriptive and cannot rescue a failed L1.

## Exact null

Within each environment independently:
- permute the complete theta values among eligible bat labels;
- retain all route centroids unchanged;
- recompute L1 and L2.

Enumerate the full Cartesian product of within-environment permutations if <=100,000 total mappings.
If larger, use 99,999 random mappings with seed 20261007901.

Primary one-sided p:
fraction of null G >= observed G, including the observed assignment using the usual +1 correction for sampled nulls.

L1 support requires:
- observed G > 0;
- one-sided p <= 0.05;
- >=70% of target bat × environment gains positive.

## Interpretation

### L1 supported

A portable scalar theta carries predictive information about configuration-specific lane placement. The task-specific term h may then be partly generated as an environment-specific transformation of theta.

### L1 unsupported

The one-dimensional portable policy does not determine where within a given obstacle configuration the individual flies. A separate task-specific individual state h is required by the current evidence.

## Ceiling

Even a supported result would not prove:
- a causal effect of speed/vigor on lane choice;
- a neural scalar;
- that h is fully determined by theta;
- generality outside the tested configurations.

An unsupported result does not imply h is infinite-dimensional. It only establishes that one portable scalar is insufficient to recover lane placement under this affine/monotonic test.
