# Miniopterus species-specific one-dimensional policy axis contract v1

## Status

**POST-PRIMARY EXPLORATORY DIAGNOSTIC.**

This analysis is frozen after:
- the full 8-D *Miniopterus fuliginosus* cross-configuration identity primary failed;
- the fixed Rhino FlightIntensity and Rhino PC1 axes also failed to transfer to Miniopterus.

It does not rescue those failures.

## Question

Does *Miniopterus* nevertheless possess its **own** low-dimensional cross-configuration individual axis whose orientation differs from *Rhinolophus*?

## Data

Use the same 19 already-opened *Miniopterus fuliginosus* trajectories and the same eight movement features.

Use the frozen Mini standardization:
- subtract each environment's feature mean;
- divide all environment-centered residuals by the species-wide pooled residual SD.

No individual label is used in standardization.

## Leave-one-environment-out PCA1

For each target environment e:

1. training = all standardized Mini trajectories from environments other than e;
2. center the training 8-D matrix by its training mean;
3. fit ordinary PCA by SVD using training data only;
4. retain PC1 only;
5. project training and target trajectories onto that training PC1.

PC1 sign is arbitrary and irrelevant because identity uses absolute distances.

## Identity estimator

Use the scalar leave-one-environment-out architecture:
- average training trajectories within bat × environment;
- average training environments equally within bat;
- target advantage = mean absolute distance to other-bat centroids - absolute distance to own-bat centroid;
- equal target -> equal bat -> species K.

A bat must have >=2 training environments for its own centroid.
Require >=3 candidate bats.

## Null

Within every environment independently permute complete bat×environment clusters among bat labels.

PCA1 bases are label-free and fixed under permutation.

9,999 permutations.
Seed: `202610042331`.

## Diagnostic support

Descriptively supported only if:
- K > 0;
- p <= 0.05;
- >=3/4 bats have positive individual means.

## Interpretation

Supported:

> Miniopterus also carries cross-configuration individuality in a one-dimensional movement axis, but that axis is species-specific rather than the Rhino flight-intensity axis.

Unsupported:

> the current Miniopterus archive does not support even a species-specific unsupervised 1-D carrier under the same architecture.

No alternate PC or supervised axis may replace PC1 after opening.
