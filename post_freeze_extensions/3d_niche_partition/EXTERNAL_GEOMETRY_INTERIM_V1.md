# External 3D geometry interim result v1

## Status

New 3D geometry endpoint; previous centered-vertical outcomes were already known.

Prediction contract:
- EXTERNAL_GEOMETRY_PREDICTION_CONTRACT_V1.md

### Implementation equivalence

The original external geometry implementation and the vectorized implementation were both run on *Myotis vivesi* with the same source, session universe, seed and 9,999 whole-session permutations.

They matched exactly for:
- observed D = 0.03567682656878024
- null mean = 0.0002172884839553815
- q025 = -0.0441061606474151
- q50 = 0.00013331043425220124
- q975 = 0.04273825328278376
- p(null >= observed) = 0.055

The vectorized Pteropus result is therefore treated as an exact implementation-equivalent evaluation of the frozen estimator.

## Myotis vivesi

Prediction: weak / surface-constrained geometry.

- evaluable individuals: 4 / 4
- horizontal overlap self / other: 0.1424 / 0.1453
- conditional vertical overlap self / other: 0.8270 / 0.7913
- D = +0.03568
- calibrated excess = +0.03546
- p = 0.0550
- R3D self / other = 0.0569 / 0.0786
- primary decision: not supported

Interpretation:
The prediction is directionally aligned but only narrowly. The system is not exactly zero: vertical solution fidelity is positive, but it does not meet the pre-specified primary criterion. Horizontal self-overlap is not stronger than other-individual overlap. This is consistent with a weak, non-stable realized spatial geometry in a surface-constrained, unpredictable-prey system.

## Nyctalus noctula

Prediction: weak / context-dependent geometry.

- first prospective n=27 universe retained
- target sessions: 47
- 500-m structurally evaluable individuals: 2
- primary gate: 5
- structural decision: non-evaluable
- descriptive horizontal overlap self / other: 0.4656 / 0.2321
- descriptive conditional vertical overlap self / other: 0.7489 / 0.6844
- descriptive D = +0.06445

Interpretation:
The 500-m geometry endpoint cannot adjudicate the prediction. Fine-scale shared support collapses from the 5-km source-level analysis to only two evaluable individual-cohort units. Do not count this as a prediction success or failure.

## Pteropus poliocephalus

Prediction: nested 3D geometry.

- evaluable individuals: 4 / 4
- horizontal overlap self / other: 0.4475 / 0.2268
- H = +0.2207
- conditional vertical overlap self / other: 0.7372 / 0.4556
- V = D = +0.28155
- calibrated excess = +0.27908
- valid permutations: 7,823
- p = 0.0001278
- R3D self / other = 0.13865 / 0.41889
- S = other R3D - self R3D = +0.28024
- primary decision: supported

Interpretation:
This is a strong nested-3D pattern. Individuals repeatedly reuse different horizontal portions of the landscape, but even within pairwise-shared 500-m cells they also reuse strongly individual-specific centered vertical configurations. Adding height removes much more of the between-individual horizontal overlap than of within-individual overlap.

Terrain-relative 3D geometry remains to be evaluated under the separately frozen secondary diagnostic.

## Hipposideros source

Prediction: horizontal-dominant or weak-vertical geometry.

Status: no 3D outcome opened.

The current GitHub Actions run reached Dryad but received HTTP 401 from the authenticated file endpoint. The public landing page confirms GPS_data.csv is part of the published dataset, but the fixed raw file could not be retrieved through the frozen authenticated route. No substitute file, altered source or reconstructed dataset is used.

## Current external synthesis

- Pteropus: prediction strongly aligned.
- Myotis: prediction narrowly aligned (positive D, but criterion not met).
- Nyctalus: structurally non-evaluable at 500 m.
- Hipposideros: source retrieval blocked; outcome unopened.

This is not a cross-system confirmatory test of ecology causing geometry. It is the first fixed-endpoint external comparison of the generated geometry hypothesis.
