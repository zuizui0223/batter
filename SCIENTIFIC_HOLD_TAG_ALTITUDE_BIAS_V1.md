# Scientific submission hold — tag altitude-bias audit v1

Date: 2026-09-27

## Status

**FINAL SCIENTIFIC AUDIT BEFORE SUBMISSION. DO NOT MINT THE FINAL ZENODO RELEASE YET.**

The v0.3.5 manuscript has passed the completed cross-panel confound and effect-null audits. One
remaining reviewer-facing alternative is being tested: a constant device/individual-specific
vertical offset could contribute to apparent vertical identity.

This v1 family is explicitly the final new scientific audit. After it is complete, remaining
concerns about deployment timing, behavioural state, fine-scale horizontal structure and unknown
device properties are handled as limitations rather than by opening new analysis families.

## Audit logic

1. Run an x-y/time-only structural preflight. No numeric vertical values are used.
2. Freeze which panels have enough shared stationary-cluster support for an empirical
   stationary-height offset correction.
3. Independently of stationary-cluster availability, test a shift-invariant vertical-shape
   fingerprint that removes each held-out session's absolute vertical location before comparing
   candidate shapes.
4. Summarize cohort deployment/tracking-window overlap descriptively from timestamps only.
5. Open vertical outcomes only after the structural preflight and final decision contract are
   frozen.

## Closed dimensions

No new source search, taxa, panels, terrain products, horizontal grids, endpoint radii, behavioural
classifiers, or post-output threshold tuning is authorized.

The current pre-audit manuscript is:
`manuscript/MANUSCRIPT_DRAFT_V0_3_5.md`.
