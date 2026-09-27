# Scientific submission hold — cross-panel confound and effect-null calibration

Date: 2026-09-27

## Status

**DO NOT SUBMIT. DO NOT CREATE THE FINAL ZENODO RELEASE YET.**

The frozen v0.3.4 rc3 package remains the archival pre-audit baseline. A reviewer-facing audit
identified two inferential gaps that can be resolved without reopening source discovery:

1. the predeclared x-y-only night-endpoint exclusion was tested only in focal *Tadarida* and
   failed there, while the five comparative panels remain untested for the same central-place /
   endpoint structure;
2. two biological effect translations (absolute AGL mean-height separation and pairwise
   self-identification fraction) are currently shown against intuitive zero/0.5 references rather
   than their own finite-sample session-label exchangeability nulls.

## Required before submission resumes

- freeze a cross-panel endpoint-exclusion contract before any new comparative exclusion output;
- freeze an effect-translation null-calibration contract before any new null output;
- execute both under fixed session-label permutation rules;
- retain failures;
- revise title/abstract/manuscript/figures only after all outputs in both families are complete.

## Closed dimensions

This hold does **not** authorize:
- new public dataset search;
- new taxa or panels;
- outcome-adaptive exclusion radii;
- altered vertical bins or smoothing;
- changed session/cohort definitions;
- new terrain products for non-focal panels;
- rescue analyses after a failed endpoint.

Scientific-content commit before this audit:
`29c18a9f3c29ee2f561e0f7d28cd340fcc55aa22`.

Packaging baseline:
`release/jae-v0.3.4-rc3`.
