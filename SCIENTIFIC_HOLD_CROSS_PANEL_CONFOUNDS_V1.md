# Scientific submission hold — cross-panel confound and effect-null calibration

Date: 2026-09-27

## Status

**SCIENTIFIC HOLD RESOLVED FOR v0.3.5.**

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

## Resolution

Both required audit families were frozen before output, executed, and retained without rescue.
The completed synthesis is in `CROSS_PANEL_CONFOUND_AUDIT_RESULT_V1.md`.

The manuscript was then revised to `manuscript/MANUSCRIPT_DRAFT_V0_3_5.md` with the title
explicitly restricted to **coarse horizontal occupancy**. The completed audit shows:

- 4/5 comparative panels pass the frozen 1-km endpoint-neighbourhood rule;
- *Eidolon* retains p=0.0002 but fails the frozen post-exclusion n gate;
- focal *Tadarida* remains FAIL at p=0.1109;
- calibrated pairwise self-identification passes in 5/6 panels;
- focal raw 256.459-m AGL separation has a 133.733-m null mean and 122.727-m calibrated excess,
  p=0.0297.

No additional ecological analysis is required by this v1 audit family. Final release remains
blocked only by packaging/human metadata tasks such as visual inspection, software license,
author metadata and Zenodo DOI.
