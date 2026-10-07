# Auditory-feedback adult vocal individualization schema audit v1

## Status

**OUTCOME-BLIND SCHEMA AUDIT. ACOUSTIC NUMERIC VALUES REMAIN CLOSED.**

## Design fact now verified from the primary paper

The ten pups were **randomly assigned** to kanamycin versus saline treatment.

Group structure:
- 5 hearing controls;
- 5 deafened;
- 3 females + 2 males in each treatment.

Therefore a later treatment randomization test may preserve sex exactly.

Sex-stratified assignment space:

[
inom{6}{3}inom{4}{2}=120.
]

This architecture is frozen before acoustic outcomes are opened.

## Files authorized for structural inspection

Primary:
- `PAF_AllBatsData.mat` (~6.4 MB)

Code/schema support:
- `DeafBats11_PCARegularizedPermutationDFA.m`
- `DeafBats8_ParsingVocalSpace.m`
- `DeafBats3_AcousticMeasurements.m`

Authorized extraction:
- top-level MAT variable names/classes/shapes;
- table/struct field names;
- row counts;
- BatID levels/counts;
- treatment labels/counts;
- sex labels/counts;
- acoustic-group / call-class labels and counts;
- feature column names;
- number of repeated calls per bat × class.

Forbidden:
- acoustic feature means;
- centroids;
- distances;
- treatment differences;
- identity prediction;
- dispersion;
- p-values.

## Structural proceed gate

A numerical individualization primary may open only if:

1. exactly 10 source bats are recoverable;
2. hearing/deaf = 5/5;
3. sex balance is 3F/2M within each treatment;
4. all bats have repeated adult calls;
5. one fixed common acoustic feature representation is available across all 10;
6. call-class structure can either be recovered or explicitly shown absent.

If any fails:
**STOP_ADULT_VOCAL_INDIVIDUALIZATION_PRIMARY**.

## Primary-design decision to make after schema only

The schema determines whether the later fixed identity statistic will be:

A. call-class-conditioned individual identity, if a common class label exists across bats; or  
B. whole-repertoire individual identity, if the source representation does not expose a stable shared class variable.

This is a structural decision, not outcome selection.

No acoustic numeric result may be opened before that choice is frozen.
