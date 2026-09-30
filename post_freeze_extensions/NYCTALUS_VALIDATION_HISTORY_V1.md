# Nyctalus external-validation history v1

## Purpose

This ledger records the complete inferential history of the *Nyctalus noctula* external-validation source without overwriting either analysis.

Source used in all Nyctalus analyses:
- repository: Zenodo
- DOI: `10.5281/zenodo.7535030`
- file: `Observed_GPS_locations.csv`
- SHA256: `2f373d47706c5b56313de70b623bb5446f5925c69af30f1b145993419e382aa9`

The frozen JAE v0.3.8 submission on `main` is unaffected.

## 1. First prospective primary validation

Historical branch:
`prospective/noctule-independent-validation-v1`

The structural contract required at least 50 presence-qualified fixes per retained source track and at least 50 scored common-support target fixes.

Outcome-blind preflight:
- workflow `36650800992`
- 27 evaluable individual×cohort units
- 47 evaluable target tracks

Vertical workflow:
- workflow `36652480017`
- result-record commit `81b0c618f8b847eb86318fa5f21bd9f74c2c586a`
- result-record time: 2026-09-30 00:59:54 UTC

Frozen result:
- n = **27**
- observed identity = **-0.018705**
- permutation-null mean = **-0.070453**
- calibrated excess = **+0.051747**
- one-sided p = **0.1224**
- frozen verdict = **FAIL**

This is the authoritative prospective external-validation result.

Its frozen stop rule stated that the >=50-fix session threshold must not be changed after vertical output and that mechanism extensions must not be opened as rescue analyses following a primary failure.

## 2. Later revised-eligibility analysis on the same source

Historical branch:
`prospective/nyctalus-independent-validation-v1`

The later structural protocol did not impose the previous >=50-fixes-per-source-track filter. It retained the >=50 scored common-support target-event requirement.

Later structural-preflight workflow was prepared after the first source outcome had already been opened. The later Height-opening commit is:
- `6371c42acf01ae9aa87c639047881fcae9e53001`
- 2026-09-30 04:25:50 UTC

Result:
- n = **36**
- observed identity = **+0.005268**
- permutation-null mean = **-0.080737**
- calibrated excess = **+0.086005**
- one-sided p = **0.0115**

This analysis is statistically informative but cannot be classified as a fresh outcome-blind prospective replication because the same source, file and vertical response had already been opened in the first validation.

The source-HMM-state analysis on this later branch yielded:
- n = **27**
- calibrated excess = **+0.050737**
- p = **0.0707**

It is retained as post-outcome exploratory mechanism evidence, not as a prospective mechanism replication.

## 3. Eligibility-robustness diagnostic

Branch:
`post-freeze/nyctalus-eligibility-robustness-v1`

Authoritative workflow:
- run `36694266681`
- head `35c2594cb2614a039f648796979b502fcfcb31d3`
- artifact `11087271548`
- digest `sha256:df290350fecba26af25ac456ac6bb8cbf49fc88ce44dc8f5874e3b7dd77a4b00`

Only minimum fixes per source track was varied: 0, 20, 30, 40, 50, 75, 100. The estimator, horizontal grid, centered-height bins, target-event minimum, common weighting, permutation unit, B and seed were fixed.

Calibrated excess was positive at **7/7** thresholds:
- minimum = **+0.03390**
- median = **+0.06086**
- maximum = **+0.08600**

The original 50-fix endpoint and later 0-fix endpoint were exactly reproduced by the same implementation.

## Inferential classification

### Confirmatory

> The first frozen Nyctalus primary test had a positive calibrated excess but did not meet its preregistered tail criterion (p=0.1224).

### Convergent post-outcome evidence

> The calibrated Nyctalus effect remains positive across all seven pre-frozen session-length sensitivity thresholds, so the direction is not an artefact of one relaxed eligibility cutoff.

### Not established

- a successful prospective Nyctalus replication;
- a prospectively replicated within-HMM-state mechanism;
- a universal cross-bat mechanism.

## Reporting rule

Always report the first prospective result before the revised-eligibility result.

Do not write:
- "Nyctalus prospectively replicated the primary result";
- "four taxa now have prospective independent support";
- "the later preflight was outcome-blind with respect to Height".

Allowed summary:

> The preregistered Nyctalus external test was directionally concordant but non-significant (calibrated excess +0.052, p=0.122). A post-outcome eligibility analysis gave a larger positive effect (+0.086, p=0.0115), and a fixed threshold-sensitivity curve remained positive at all seven tested session-length cutoffs. These results provide convergent external directional evidence, but not a successful prospective replication.
