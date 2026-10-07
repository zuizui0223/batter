# Cross-configuration route-centroid portability contract v1

## Status

**POST-PRIMARY MECHANISM DIAGNOSTIC. NOT CONFIRMATORY.**

Frozen after:
- cross-configuration 8-D movement-policy identity passed;
- one-dimensional movement-intensity theta was supported;
- within-configuration route-centroid identity passed;
- start/end/displacement identity was unsupported within repeated configurations.

No cross-configuration route-centroid identity result has been calculated before this contract.

## Question

Is the personal lane/placement component itself portable across obstacle configurations, or is it task-specific?

## Representation

For each authoritative *Rhinolophus nippon* route-valid trajectory q:

[
c_q = mean_s R_q(s)
]

is the 3-D route centroid in arena coordinates.

Within each environment and coordinate independently:
- subtract the environment trajectory mean;
- divide by environment trajectory sample SD.

If any coordinate has zero/nonfinite SD, stop.

This removes environment-specific absolute placement and scale while preserving relative individual placement within each configuration.

## Cross-configuration identity

Use the exact Primary-B architecture on the standardized 3-D centroid vector:

- average trajectories within bat × environment;
- for each held-out target environment, average other environments equally within bat;
- require focal bat history in >=2 other environments;
- require >=2 donor bats;
- target K = mean Euclidean distance to donor centroids minus distance to own centroid;
- equal target → equal bat → species.

Candidate bat must occur in >=3 environments.

## Null

Within every environment independently, permute complete bat × environment clusters among bat labels.

Preserve:
- route centroids;
- environment membership;
- trajectory counts per bat × environment.

Break only cross-environment identity correspondence.

9,999 permutations.
Seed: 20261007941.
Require >=9,500 valid permutations.

## Support

Portable centroid identity is supported only if:
- K > 0;
- p <= .05;
- >=70% evaluable bats have positive K.

## Interpretation

Supported:
> relative lane/placement is itself a portable personal coordinate across obstacle configurations.

Unsupported:
> lane/placement individuality is configuration-specific even though the higher-level movement policy transfers.

## Ceiling

A supported result would not establish a single universal physical lane across different obstacle geometries; environment centering/scaling means only the individual's relative placement tendency transfers.
