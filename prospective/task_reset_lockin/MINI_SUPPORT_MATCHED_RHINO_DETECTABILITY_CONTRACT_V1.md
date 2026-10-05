# Miniopterus-support-matched Rhino detectability contract v1

## Status

**POST-PRIMARY SPECIES-BOUNDARY / DETECTABILITY DIAGNOSTIC.**

Frozen after:
- fixed FlightIntensity was strongly supported in *Rhinolophus nippon*;
- the same fixed FlightIntensity was supported in an independent *Carollia perspicillata* cohort;
- fixed FlightIntensity was unsupported in *Miniopterus fuliginosus* (K = 0.09747, p = 0.2508; 3/4 bats positive);
- a Miniopterus-specific PCA1 was also unsupported.

No support-matched Rhino resampling result has yet been calculated.

## Question

Could the Miniopterus failure be explained simply by its smaller and sparser public design
(4 individuals, 19 trajectories, uneven environment × individual support)?

## Exact support architecture

Open no new biological response.

From the already-opened Miniopterus public trajectory set, record the exact count:

`n_{e,b}`

for every environment e × Miniopterus bat b cell.

The support-matched Rhino analysis must reproduce this complete cell-count table exactly.

## Mapping Mini support to Rhino individuals

Rhino has five source-native individuals.

Enumerate all injective mappings from the four Mini bat labels to four distinct Rhino bats.

A mapping is feasible only if, for every Mini cell with count n>0, the mapped Rhino bat has at least n feature-valid trajectories in the same environment.

No environment may be substituted and no cell may be pooled.

If no mapping is feasible:
`STOP_NO_EXACT_SUPPORT_MATCH`.

## Resampling

For each replicate:

1. choose one feasible injective mapping uniformly;
2. within every required environment × mapped-Rhino-bat cell, sample exactly the Mini count without replacement;
3. relabel the sampled Rhino bat with the corresponding Mini label;
4. retain the exact Mini environment × label support architecture.

Replicates:
**1,000**

Seed:
`202610051301`.

Independent sampling is allowed across replicates.

## Fixed representation

Use the same support-compatible standardization used for the Mini fixed-axis analysis:

1. subtract the feature mean separately within each environment;
2. estimate one pooled residual SD per feature across the complete support-matched sample;
3. divide centered values by that pooled residual SD.

All eight SDs must be finite and positive.

Compute fixed:

`I = mean(z1,z2,z3,z4)`.

No weight is refit.

## Identity statistic

Use exactly the Mini cross-configuration scalar identity estimator:

- bat × environment centroids;
- target trajectory held out by environment;
- training centroid for the same bat from all other environments, equal-environment weighted;
- donor bat centroids built identically;
- target K = mean distance to donors minus distance to own centroid;
- equal target -> equal bat mean.

A replicate is evaluable only if the frozen estimator yields >=3 candidate bats.

## Per-replicate calibration

Within each evaluable support-matched replicate:

- independently permute complete bat labels among bat × environment clusters within each environment;
- preserve the exact Mini cell-count architecture.

Permutations:
**999** per replicate.

Seed for replicate r:
`202610052000 + r`, r=1..1000.

One-sided p.

A support-matched Rhino replicate counts as a detected FlightIntensity identity if:
- K > 0;
- p <= 0.05;
- >=3 of 4 evaluable bat means are positive.

## Primary detectability outputs

Report:
- number of feasible mappings;
- exact Mini support table;
- number of evaluable resamples;
- median and 2.5–97.5% interval of Rhino support-matched K;
- **detectability fraction** = fraction satisfying the frozen detection rule;
- fraction with K <= the observed Mini K = 0.09746691786566167;
- fraction with p >= observed Mini p = 0.2508;
- distribution of positive-bat counts.

## Interpretation

### Detectability high

If most support-matched Rhino resamples still detect identity, sparse Mini support is not a sufficient explanation for the Mini negative result.

This strengthens a species/task boundary interpretation.

### Detectability low

The Mini failure remains power/support-limited; do not infer a biological species boundary.

## Ceiling

This is an empirical detectability calibration using Rhino as a positive reference system.

It is not:
- a formal post-hoc power analysis for Miniopterus;
- proof that the species differ causally;
- evidence about why any species difference exists.
