# Aharon finite-mask support audit contract v1

## Status

**STRUCTURAL SUPPORT ONLY. TURNING-POINT MAGNITUDES MUST NOT BE REPORTED.**

Parent:
- `AHARON_CROSS_CONDITION_IDENTITY_CONTRACT_V1.md`
- `AHARON_PRIMARY_STRUCTURAL_SELECTION_V1.json`

Purpose:
verify trial support and missing-value encoding before any turn-location median is calculated.

## Authorized numerical access

For the structurally selected Figure only, read each `totalTurns` matrix solely to calculate:

- shape;
- number of finite cells;
- number of NaN/nonfinite cells;
- number of exact-zero cells;
- for each trial column:
  - whether at least one finite odd-row entry exists;
  - whether at least one finite even-row entry exists;
  - whether at least one finite nonzero odd-row entry exists;
  - whether at least one finite nonzero even-row entry exists.

Do not report:
- any nonzero turning-point magnitude;
- medians;
- means;
- ranges;
- condition differences;
- individual differences.

## Trial-support gate

The frozen primary requires >=5 valid trial columns for every selected bat × condition.

Two support counts are reported:

1. `finite_bilateral_trials`
2. `finite_nonzero_bilateral_trials`

If any matrix has <5 finite bilateral trials:
**STOP_INSUFFICIENT_TRIAL_SUPPORT.**

## Zero-sentinel gate

If every selected matrix has zero exact-zero cells:
- no zero-sentinel issue exists;
- the numeric primary may use all finite entries.

If exact zeros occur anywhere:
- do not automatically decide that zero is missing or biological;
- return **ZERO_ENCODING_NEEDS_FREEZE**;
- inspect source code/documentation structurally for zero semantics;
- freeze a zero-handling amendment before numeric turning medians are calculated.

No decision may use the sign or magnitude of nonzero turning values.

## Proceed rule

Numeric Aharon primary may open only if:
- structural Figure selection passed;
- every selected bat × condition has >=5 valid trials under the final frozen missingness rule;
- zero encoding is resolved prospectively.

## Claim boundary

This audit is data-support infrastructure, not a biological result.
