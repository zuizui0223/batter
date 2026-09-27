# Tag altitude-bias audit v1 — frozen primary contract

Frozen before any centered-height output: 2026-09-27.

## Primary test: shift-invariant vertical shape

For every already-retained session, subtract that session's median primary height from every fix
**before vertical binning**. Use fixed centered bins:

`[-inf, -400, -200, -100, -50, 0, 50, 100, 200, 400, inf]` m.

Then rerun the exact 5-km common-cell self-vs-other pipeline and whole-session label permutation.

This removes any additive constant tag/device offset exactly. It is deliberately stronger than a
tag-only correction because it also removes night-specific constant altitude shifts.

The held-out target is centered by its own session median using the same identity-blind
transformation applied to every session before prediction.

Each panel must retain its exact original evaluable-individual count. It passes only when:

- centered common-cell observed-minus-null mean >0; and
- one-sided P(null >= observed) <=0.05.

Permutation counts and seeds are exactly those already used for the v0.3.5 panel calibrations.

## Secondary stationary-height correction

Only panels that pass the separately frozen x-y/time-only structural feasibility preflight are
eligible.

Within each shared stationary 100-m cell:

1. take the median primary height for each supported individual;
2. define the cell reference as the median of those individual medians;
3. individual cell offset = individual median - cell reference;
4. individual offset = median of its offsets across shared cells;
5. subtract that offset from all heights for the supported individual;
6. rerun the original v0.3.5 bins and 5-km common-cell calibration.

This is corroborative only. A stationary result cannot rescue a failed centered-shape primary test.

## Time confounding

The structural preflight reports cohort tracking-window overlap. It is included in Supporting
Information and the Limitations. No new time-block permutation family is opened.

## Paper decision

- 6/6 shape PASS: additive device offsets cannot explain the cross-panel result.
- 4–5/6 PASS: offsets are not a general explanation, but non-passing panels may be dominated by
  absolute vertical-location effects (biological or device).
- 1–3/6 PASS: restrict ecological generality to passing systems.
- 0/6 PASS: do not claim individuality beyond additive altitude offsets.

This v1 audit is the declared stopping point before submission.
