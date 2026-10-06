# DREADDs public-source structural audit contract v1

## Status

**OUTCOME-BLIND WITH RESPECT TO THE NEW INDIVIDUAL-MATCHING STATISTIC.**

Published population-level saline/ligand effects are already known.

No new cross-treatment individual-matching statistic, exact identity permutation, or individual rank may be calculated before the primary contract is frozen.

## Source

Study:
Diebold, Lawlor et al. (2024),
*Rapid sensorimotor adaptation to auditory midbrain silencing in free-flying bats*.

Frozen public source:
- Zenodo record: 13857870
- DOI: 10.5281/zenodo.13857870
- version: v1

## Public audio files

Use exactly:

- bea_audiopooldata.mat
  - md5: 1cceb6fed16ad9c400a7862e5fa9b264
- jane_audiopooldata.mat
  - md5: d54aa79392bcfb27db54d14466092a24
- jason_audiopooldata.mat
  - md5: 5ee4427abf357936ed979effb5742e94
- stella_audiopooldata.mat
  - md5: 5726cc9124897e0fc620c41fb4cd0150

The public source code explicitly defines the four-bat audio list as:
jane, bea, jason, stella.

## Source-native treatment semantics

The public analysis code uses:
- treatment == 1: saline
- treatment == 2: ligand

For the acoustic analyses it further restricts to:
- trialtype < 4

No treatment recoding is allowed.

## Frozen primary feature set

Structural support must be available for all five source-native trial summaries:

1. mean call duration per trial;
2. mean call bandwidth per trial;
3. mean inter-pulse interval per trial;
4. call rate per trial;
5. proportion of calls in SSGs per trial.

These definitions are frozen in the numerical contract.

## Structural proceed gate

Proceed only if all four bats have:

- both saline and ligand trials;
- >=5 structurally usable trials in each treatment;
- all fields required for all five frozen features;
- treatment/trial vectors aligned with the trial-level cell arrays.

A trial is structurally usable only if:
- trialtype < 4;
- all feature ingredients required by the five-dimensional endpoint are structurally present;
- call onset has >=2 finite call times for IPI;
- trial duration / lengthadjust is finite and positive;
- at least one call is present for call-rate and SSG proportion.

No threshold relaxation.

## Trajectory disposition

Public trajectory data are available for:
- jane;
- bea;
- jason.

The public trajectory script therefore has n=3 biological individuals.

A saline→ligand identity-label permutation on three bats has only:

3! = 6

possible mappings, so minimum exact one-sided p = 1/6 = 0.1667.

Therefore trajectory identity transfer is **not authorized as a confirmatory p<=0.05 primary**.

Trajectory data may be used only for:
- descriptive mechanistic triangulation;
- source-paper context;
- a separately bounded effect-size analysis that does not masquerade as confirmatory identity evidence.

## Structural output only

The audit may report:
- file checksums;
- four bat names;
- field names;
- treatment/trial support counts;
- usable-trial counts per bat × treatment;
- structural STOP/PASS.

Do not report:
- feature means;
- saline/ligand individual values;
- distances;
- identity statistic;
- p-value.
