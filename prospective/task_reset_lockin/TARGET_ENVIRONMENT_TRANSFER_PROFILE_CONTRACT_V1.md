# Target-environment transfer profile contract v1

## Status

**POST-PRIMARY DIAGNOSTIC. NOT CONFIRMATORY.**

Frozen after the main cross-configuration movement, geometry and pulse identity analyses and after leave-one-environment robustness.

## Question

When each obstacle configuration is treated as the held-out target context, how broadly does the individual's previously observed policy transfer into that environment?

This is different from leave-one-environment deletion:
- LOO asks whether an environment is necessary as part of the training/reference set.
- This diagnostic asks whether individuality is visible **when predicting into each environment**.

## Modalities

Use exactly the frozen observed-data representations for *Rhinolophus nippon*:

1. movement policy: the eight Primary B features;
2. scale-free geometry policy: the eight geometry-only features;
3. pulse policy: the six pulse features.

No feature changes or new transformations.

## Target-level identity advantage

For every valid target trajectory q in environment e:

- build the focal bat centroid from all of that bat's usable environments except e, with equal environment weighting;
- build each donor-bat centroid similarly from donor environments except e;
- require >=2 other environments for focal and donor centroids;
- require >=2 donor bats;
- compute:
  `I_q = mean distance to donor centroids - distance to own centroid`.

Positive means identity transfers into the target environment.

## Environment aggregation

Within each target environment:

1. average target `I_q` equally within bat;
2. average bats equally for `I_env`.

Report:
- `I_env`;
- individual means;
- number/fraction of positive bats;
- number of valid target trajectories.

## Descriptive transfer label

An environment is descriptively called **broadly transferred** if:
- `I_env > 0`;
- >=70% evaluable bats have positive individual mean.

No new p-value is calculated.

## Interpretation

- all/most environments transferred: stable policy generalizes broadly across configurations;
- a few environments fail: portable individuality is context-dependent, and the failing environments should be characterized rather than deleted;
- movement/pulse transfer broader than geometry: stable sensorimotor policy is not reducible to a fixed route geometry.

## No rescue

Do not:
- alter features by environment;
- drop a difficult target environment;
- modify the >=2 training-environment rule;
- reinterpret descriptive transfer labels as confirmatory significance tests.
