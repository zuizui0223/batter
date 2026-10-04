# Cross-species transfer of the Rhinolophus flight-intensity axis v1

## Status

**POST-PRIMARY CROSS-SPECIES GENERALITY DIAGNOSTIC.**

Important chronology:
- the *Miniopterus fuliginosus* full 8-D Primary-B outcome was already opened and failed before this diagnostic;
- therefore this analysis is not an untouched external confirmation and cannot rescue that failed primary.

The purpose is narrower: does the simple individual-policy axis discovered in *Rhinolophus nippon* transfer descriptively to the second species under the same obstacle experiment?

## Source species

*Rhinolophus nippon*.

Frozen source result:
- a one-dimensional movement-policy axis was sufficient;
- a transparent scalar based on four speed / vertical-speed features was supported.

## Target species

*Miniopterus fuliginosus*.

Use only the 19 already-opened Miniopterus trajectories from the same Figshare archive.

## Target-species preprocessing

Use the same eight trajectory features and the same within-environment standardization used in the configuration-conditioned programme.

No target-species individual labels are used to define either tested axis.

## G1 — transparent FlightIntensity transfer

Apply exactly the Rhino-derived non-fitted scalar:

`FlightIntensity = mean(z_median_speed, z_p90_speed, z_median_abs_vertical_speed, z_p90_abs_vertical_speed)`.

No refitting.

Use the exact leave-one-environment-out scalar identity estimator:
- within training environment, average target-species trajectories within bat;
- equal-environment average within bat;
- target advantage = mean absolute distance to other-bat centroids minus distance to own centroid;
- equal target -> equal bat.

## G2 — Rhino-derived PCA1 transfer

Fit a single PCA axis using **Rhinolophus only**:
- use all 45 Rhino trajectories;
- within every Rhino environment standardize the eight authoritative movement features;
- fit ordinary PCA by SVD to the resulting 45×8 matrix;
- orient PC1 so the sum of loadings on the first four speed / vertical-speed variables is positive.

Freeze this 8-vector before applying it to Miniopterus.

For each Miniopterus trajectory:
- use its own-species, own-environment standardized 8-D feature vector;
- project onto the fixed Rhino PC1 vector.

Then use the same leave-one-environment-out scalar identity estimator.

No Miniopterus label or outcome is used to fit the projection.

## Null

For G1 and G2 separately:
- independently within every Miniopterus environment, permute complete bat×environment clusters among bat labels;
- preserve values, environment membership and cluster sizes;
- break only cross-environment identity correspondence.

9,999 permutations.

Seeds:
- G1: `202610042311`
- G2: `202610042312`

## Descriptive support

Report:
- K;
- individual means;
- positive fraction;
- null 95% interval;
- one-sided p.

Call the cross-species axis descriptively supported if:
- K > 0;
- p <= 0.05;
- >=3/4 Miniopterus bats have positive individual means.

## Interpretation

### G1/G2 supported despite full 8-D failure

The full Euclidean policy representation may have diluted a lower-dimensional shared individual axis.

This remains post hoc for Miniopterus and does not reverse the failed Primary B.

### G1/G2 unsupported

The dominant portable axis found in Rhinolophus does not generalize to Miniopterus in the same experimental framework.

This would support ecological/taxonomic contingency rather than a universal bat flight-personality scalar.

## No rescue

Do not:
- refit weights using Miniopterus identity;
- select Miniopterus environments;
- alter the four transparent features;
- select a different Rhino PC;
- reinterpret a positive post-hoc diagnostic as independent external validation.
