# Auditory perturbation public-data structural audit v1

## Status

**OUTCOME-BLIND STRUCTURAL AUDIT. NO ACOUSTIC OUTCOME VALUES OPENED.**

## Source

Diebold et al. (2024),
*Rapid sensorimotor adaptation to auditory midbrain silencing in free-flying bats*.

Public dataset:
- Zenodo DOI: `10.5281/zenodo.13857870`
- Version: v1

The publication reports:
- 4 DREADD-treated behavioral bats;
- 2 sham behavioral bats;
- reversible ligand-induced suppression of excitatory inferior-colliculus neurons;
- Baseline / Saline / Ligand behavioral conditions;
- synchronized audio and flight measurements.

## Public source structure already established from deposited code

DREADD audio analysis code uses exactly:

`batlist={'jane','bea','jason','stella'}`

and source fields including:
- treatment;
- trialtype;
- trial index / trial number;
- call onset;
- call duration;
- call bandwidth;
- start frequency;
- end frequency;
- trial length;
- SSG identifiers.

The same source code compares Saline (`treatment==1`) and Ligand (`treatment==2`) while restricting the primary acoustic analyses to `trialtype < 4`.

Trajectory analysis code loads only:
- jane;
- bea;
- jason.

Therefore:

> **trajectory individuality is structurally underidentified for a conventional exact identity primary (3! = 6; p_min = 0.1667).**

Trajectory data are not authorized as a confirmatory individual-identity endpoint.

## Stage-1 audit

For each of:
- jane_audiopooldata.mat;
- bea_audiopooldata.mat;
- jason_audiopooldata.mat;
- stella_audiopooldata.mat;

report only:
- file availability;
- file hash;
- top-level MAT variable name/class/shape;
- audiopoolstruct field names;
- shape/length of structural fields;
- counts of trial rows by treatment and trialtype only.

Do not report or calculate:
- call duration values;
- bandwidth values;
- IPI values;
- call-rate values;
- individual centroids;
- treatment effects;
- identity statistics.

## Proceed gate

The numeric primary may open only if all four bats have:

- the expected `audiopoolstruct`;
- treatment labels 1 and 2;
- `trialtype` support;
- >=5 eligible Saline trials with `trialtype < 4`;
- >=5 eligible Ligand trials with `trialtype < 4`;
- finite structural availability for all four frozen primary feature families.

If any bat fails:
**STOP_AUDIO_POLICY_PRIMARY_SUPPORT**.

## Claim boundary

This structural audit establishes only whether the public source can support the already-frozen primary.

It does not establish persistence of individual policy.
