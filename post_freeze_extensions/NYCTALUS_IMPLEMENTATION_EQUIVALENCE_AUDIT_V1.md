# Nyctalus implementation-equivalence audit v1

## Question

Did the difference between the first n=27 Nyctalus result and the later n=36 result arise from changes other than source-track eligibility?

This audit is descriptive/provenance-only. It does not create a new inferential test.

## Aggregation-ID audit

The first implementation encoded identity as `cohort::bat_id` before panel aggregation.

The later implementation kept cohort-specific model construction but used raw `bat_id` as the aggregation key.

The later outcome-blind preflight reports primary eligible IDs by cohort:

- 2019 early: 6
- 2019 late: 6
- 2020 early: 11
- 2020 late: 13

Total: **36**.

The listed bat IDs are disjoint across the four cohorts. Therefore, for this source, using raw `bat_id` versus `cohort::bat_id` does not merge any eligible individual across cohorts and cannot explain the difference between n=27 and n=36.

## Unified-code anchor reproduction

The post-outcome eligibility-robustness implementation holds the estimator fixed and varies only the minimum number of presence-qualified fixes per source track.

It reproduces both historical endpoints:

### No source-track minimum

- n = **36**
- calibrated excess = **+0.08600497756886367**
- p = **0.0115**

This exactly reproduces the later revised-eligibility result.

### >=50 fixes/source track

- n = **27**
- calibrated excess = **+0.051747374510001**
- p = **0.1224**

This reproduces the first prospective result (archived calibrated excess +0.051747; rounding difference <4e-7, identical p).

## Conclusion

Within the tested unified implementation, the n=27 versus n=36 difference is attributable to the source-track eligibility filter rather than a hidden change in horizontal grid, vertical bins, permutation seed, target-event threshold, identity aggregation across cohorts, or score definition.

This strengthens the interpretation of the seven-threshold diagnostic as a genuine eligibility sensitivity analysis.

It does not change the evidence class:
- >=50 result = prospective primary, FAIL;
- relaxed analyses = post-outcome sensitivity/convergent evidence.
