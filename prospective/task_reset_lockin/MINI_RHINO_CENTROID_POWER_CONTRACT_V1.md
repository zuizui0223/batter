# Miniopterus sparse-support power diagnostic using Rhino positive control v1

## Status

**POST-PRIMARY POWER / SUPPORT DIAGNOSTIC. NOT CONFIRMATORY.**

Frozen after:
- Miniopterus full 8-D cross-environment identity failed;
- Miniopterus PCA dimensions 1–8 failed;
- Miniopterus supervised identity-subspace dimensions 1–3 failed;
- the outcome-blind centroid-support preflight found 4,212 exact occupancy mappings of the 12 Mini bat×environment cells onto Rhino.

No centroid-level matched-support movement outcome has been calculated before this contract.

## Question

Would the exact sparse cross-environment support available for *Miniopterus fuliginosus* be sufficient to recover a known strong one-dimensional personal-policy signal if that signal were Rhino-like?

This distinguishes:

- **low support / low detection power**
from
- **genuinely much weaker portable linear individuality in Miniopterus**.

## Common preprocessing for both species

Use the same eight movement features.

Within each species and feature:

1. subtract the feature mean separately within every environment;
2. pool all environment-centered residuals across the species;
3. divide by the species-wide pooled residual SD.

No individual label is used in standardization.

Then collapse every occupied bat × environment cell to one equal-trajectory centroid in this standardized 8-D space.

This produces:
- Mini: exactly 12 occupied centroids;
- Rhino: the structural pool used by the preflight.

## Mini observed endpoint

Use all 12 Mini centroids under their source-native bat and environment labels.

For every held-out environment:

1. fit ordinary PCA on all cell centroids from the other environments only;
2. retain PC1;
3. project training and target centroids;
4. for each target bat require >=2 training environments;
5. compare absolute distance to the focal bat's equal-environment training centroid versus equal mean distance to other eligible bat centroids.

Aggregate:
equal target centroid -> equal bat -> species.

Report:
- (K_{Mini});
- bat means;
- positive bats;
- 9,999 environment-wise label permutations;
- one-sided p.

Seed:
`20261007951`.

Support requires:
- K > 0;
- p <= 0.05;
- >=3/4 bats positive;
- >=9,500 valid permutations.

## Exact-support Rhino positive control

Use the 4,212 feasible mappings frozen by the centroid-support preflight.

Each mapping consists of:
- a Mini-bat -> Rhino-bat mapping;
- one global Mini-environment -> Rhino-environment permutation.

For each mapping:
- take exactly the 12 mapped Rhino bat×environment centroids;
- relabel them back into the Mini 4-bat × 7-environment support pattern;
- calculate the same training-only PCA1 K.

### Full observed mapping distribution

Calculate observed K and positive-bat count for all 4,212 mappings.

### Calibrated mapping sample

To limit permutation cost, select exactly **256** mappings deterministically:

- sort feasible mappings lexicographically by serialized bat map then environment map;
- take indices `floor(j*(N-1)/255)` for j=0..255;
- deduplicate only if integer collisions occur; if collisions occur, take the next unused mapping in lexical order.

For each selected mapping:
- 1,999 within-environment bat-label permutations;
- seed = `20261008000 + selected_mapping_rank`.

A mapping is detected if:
- K > 0;
- p <= 0.05;
- >=3/4 bats positive;
- >=1,900 valid permutations.

## Power interpretation

Primary positive-control quantity:

[
P_{detect}^{Rhino|Mini-support}
=
fraction of the 256 calibrated Rhino mappings detected.
]

Frozen interpretation:

- >=0.80: **Mini support is adequate for a Rhino-like 1-D signal**;
- <0.50: **Mini support is substantially power-limited**;
- 0.50–0.80: **ambiguous support adequacy**.

This is not a formal power calculation for an unknown Mini effect size. It asks only whether the observed Mini support could detect a signal resembling the known Rhino system.

## Additional descriptive comparison

Report:
- Mini observed K;
- median / 2.5% / 97.5% observed K across all 4,212 Rhino matched mappings;
- fraction of all Rhino mappings with K > Mini K;
- calibrated detection fraction.

## Claim boundary

If Rhino detection fraction is high while Mini remains unsupported:

> the Mini failure is difficult to explain by sparse support alone and instead indicates a substantially weaker/different portable linear individual signal in this archive.

Do not conclude:
- mathematical nonexistence of individual rules in Miniopterus;
- infinite dimensionality;
- no individual specialization;
- species-wide universality from these two taxa.
