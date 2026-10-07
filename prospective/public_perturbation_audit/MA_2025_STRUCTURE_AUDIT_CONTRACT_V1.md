# Ma et al. 2025 public-source structural audit contract v1

## Status

**OUTCOME-BLIND PUBLIC-DATA STRUCTURAL AUDIT.**

No call-rate, flight-speed, 3-D coordinate, prey-condition, or noise-effect value may be opened in this stage.

## Source

Study:
Ma, Xia, Zheng & Luo (2025),
*Prey evasiveness and masking noise jointly promote the ultrahigh call rate in echolocating bats*.

Public dataset:
- Mendeley Data id: `964fv73w94`
- version: 1
- DOI: `10.17632/964fv73w94.1`

Correction:
an earlier programme note mentioned dataset id `dz5348hs66`; that identifier is not the verified public dataset for this study and must not be used.

## Published design boundary

The paper reports eight adult *Hipposideros pratti*:
- four individuals in foraging experiments;
- four different individuals in landing experiments.

Therefore the dataset cannot support a clean within-individual foraging-versus-landing transfer test unless the public source unexpectedly establishes overlap not described in the paper.

The source remains useful for within-task manipulation:
- prey evasiveness within foraging;
- masking noise within foraging;
- masking noise within landing.

## Stage 1 — metadata/file inventory only

Read only:
- dataset identity;
- version;
- DOI;
- title;
- description;
- file UUIDs;
- filenames;
- sizes;
- content types;
- hashes;
- folder structure if exposed.

Do not download data values.

## Proceed gate

Classify the source into:

- `RAW_TRIAL_3D_PLAUSIBLE`
  - separate trial-level 3-D/trajectory files or clearly referenced raw coordinate files;

- `ANALYSIS_SCRIPT_WITH_EMBEDDED_DATA_PLAUSIBLE`
  - MATLAB or other scripts plausibly contain/import individual/trial data and can be inspected structurally without opening numeric outcomes;

- `SUMMARY_ONLY`
  - only aggregate figure summaries are publicly recoverable;

- `STOP_NO_INDIVIDUAL_TRIAL_STRUCTURE`
  - individual × trial structure cannot be reconstructed.

## Priority if structure passes

Because each task has only four animals, this source is not the preferred new generality panel.

Its best use is a manipulation-localization question:

> does current acoustic/noise or prey context shift group behavior while preserving a measurable individual-specific component within the same task?

Any confirmatory test must preserve task and source design.

## Claim ceiling

Do not use this source to claim:
- cross-task individual portability across foraging and landing;
- broad population prevalence;
- equivalence to the Rhino I/M axes unless fixed-axis support is independently justified;
- origin of individuality.
