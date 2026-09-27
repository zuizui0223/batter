# Final scientific hold — tag-altitude-bias audit v1

Date: 2026-09-27

## Status

**ONE FINAL EMPIRICAL AUDIT BEFORE SUBMISSION.**

JAE v0.3.5 rc1/rc2 remains the audited pre-tag-bias baseline. A remaining reviewer-facing
alternative is that repeated individual vertical identity partly reflects a persistent
device/tag-specific additive altitude offset because the same individual is generally tracked by
the same deployment.

This hold authorizes exactly one new scientific family:
`batter-tag-altitude-bias-audit-v1`.

It does not authorize new source search, new taxa, new environmental covariates, retuned grids,
new vertical bin tuning after output, or new rescue analyses.

## Planned audit

1. **Primary, all six panels:** remove a training-estimated additive individual vertical shift
   before re-binning and rerun the same common-cell identity pipeline under the existing
   whole-session permutation designs.
2. **Secondary where structurally identifiable:** estimate relative altitude offsets from
   x-y/time-defined shared stationary clusters, without using altitude to define stationary
   eligibility, then rerun the original vertical pipeline after correction.
3. **Descriptive temporal-overlap audit:** summarize tracking-date overlap within each frozen
   cohort using session timestamps/deployment metadata only. No outcome-dependent temporal block
   width will be selected after results.

## Stop rule

After this v1 family is completed and incorporated, **no further post-hoc empirical robustness
families will be added before submission**. Any remaining concerns will be stated in Limitations,
unless a reproducibility bug invalidates an already reported result.
