# Flight-intensity rank stability contract v1

## Status

**POST-PRIMARY INTERPRETABILITY DIAGNOSTIC.**

Frozen before the transparent flight-intensity scalar result is opened.

Parent:
`FLIGHT_INTENSITY_SCALAR_CONTRACT_V1.md`

## Question

If the dominant individual policy is approximately one-dimensional, do bats retain their relative position on that axis across obstacle configurations?

This distinguishes:
- a stable individual scalar tendency `theta_i`;
from
- a scalar that identifies bats only through configuration-specific rearrangements.

## Scalar

Use exactly:

`FlightIntensity = mean(z_median_speed, z_p90_speed, z_median_abs_vertical_speed, z_p90_abs_vertical_speed)`.

No fitted weights.

## Environment-level bat score

Within every environment:

- average FlightIntensity across trajectories of the same bat;
- this gives one bat × environment centroid.

## Leave-one-environment pair-order prediction

For target environment e and a bat pair (i,j):

Eligibility:
- both bats occur in target environment e;
- each bat has FlightIntensity centroids in >=2 other environments.

Training score:
- equal-environment mean of bat i over environments other than e;
- equal-environment mean of bat j over environments other than e.

Prediction:
- predicted sign = sign(theta_i_train - theta_j_train).

Observed target sign:
- sign = sign(theta_i_e - theta_j_e).

Ties:
- exact zero training or target difference is scored as 0.5.

Correct non-tie order:
1.

Incorrect non-tie order:
0.

## Aggregation

For each unordered bat pair:
- average accuracy across all eligible target environments.

Programme statistic:

`R = equal-pair mean(pair_accuracy)`.

Thus pairs with more shared environments do not dominate.

Also report:
- number of evaluable pairs;
- target-environment count per pair;
- each pair's accuracy.

## Null

Within each environment independently:
- permute complete bat × environment scalar clusters among bat labels;
- preserve cluster sizes and all scalar values;
- recompute the entire leave-one-environment pair-order procedure.

9,999 permutations.

Seed:
`202610042302`.

One-sided p:
`(1 + #null >= R_obs)/(10000)`.

## Diagnostic support

Call relative scalar ordering stable if:
- R_obs > 0.5;
- p <= 0.05;
- >=70% of evaluable bat pairs have pair accuracy >0.5.

## Interpretation

Supported:

> individuals occupy reproducibly ordered positions on a common one-dimensional flight-intensity axis across obstacle configurations.

This is stronger than merely showing that a one-dimensional coordinate contains identity information.

Unsupported:

> the one-dimensional coordinate can still identify individuals on average, but a single stable global ordering of bats is not justified.

## Ceiling

Even stable ordering does not identify the biological origin of the scalar:
- morphology;
- physiology;
- development;
- long-lived learning

remain unresolved.
