# Krauel 2018 field acoustic height x measured ground-moth index

## Status and authorization

Fixed on 2026-11-21 before any new prediction fit. This is **source-open, exploratory reanalysis of an already published table**, not preregistration or an independent replication of the original study. The table, methods and published conclusions were inspected during source qualification. Continued execution and Draft PR updates are authorized by the user's project instructions and `continue` request. No author contact, merge, frozen manuscript change, raw tracking publication or reopening of the closed PLOS exploration is part of this work.

## Original source and admission

- Krauel, Ratcliffe, Westbrook & McCracken (2018), *Brazilian free-tailed bats (Tadarida brasiliensis) adjust foraging behaviour in response to migratory moths*, DOI [10.1139/cjz-2017-0284](https://doi.org/10.1139/cjz-2017-0284).
- Original-author hosted accepted manuscript: <https://krauel.com/publications/Krauel%20et%20al%202018%20CJZ%20early.pdf>, Table 1 on printed page 29 / PDF page index 28. The public web PDF reader exposes the table; independent second transcription agrees on all 13 rows. This is an author-hosted accepted manuscript, **not a byte-authenticated final publisher dataset**. Direct container download returned HTML, so no original-PDF SHA256 is claimed. The canonical transcription receives its own clearly labeled SHA256.
- 13 dates in 2012, one acoustic site, three recorder strata: ground (1.5 m AGL), approximately 100 m AGL, approximately 200 m AGL. The source contains 36 observed date x recorder cells, 1,104 recorded passes, 97 buzz-positive passes. Three cells are explicitly missing because of instrument malfunction.
- Eligibility fixed by complete three-recorder coverage: 10 nights, 30 cells, 1,073 passes, 95 buzz-positive passes. Incomplete dates 2012-09-08, 2012-10-18 and 2012-10-19 are excluded in full; missing values are not zero.
- Predictor: `log1p(trap_moths)`, the independently trapped daily count of four crop-pest moth species pooled across the study's four ground trap sites. It is a measured ground-trap index, **not a measurement of prey density at 100/200 m or total edible biomass**. Five species were bait targets; Table 1 specifies four in the reported catch total.
- Fecal diet richness is excluded: it derives from bats, is sometimes interpolated from a neighboring night, and is not an independent resource-availability measure.
- Outcome: counts of detected call files by recorder stratum and presence/absence of at least one complete feeding buzz. A call file can contain multiple individuals. Buzz absence means no detected complete buzz, not verified transit or absence of feeding.
- Exact recorder-hours by date and stratum and effective detection volumes are unavailable. Identical trigger settings do not establish identical detectability; airborne units had modified housings. No per-hour exposure, occupancy, individual bat altitude, true foraging probability, prey consumption, abundance or causal resource effect will be estimated.

## Fixed estimand and alternatives

The estimand is predictive performance for the **joint recorder stratum and buzz mark of a recorded pass**, with every eligible night weighted equally. It describes this source's recording process under its sampled conditions. Counts within a night are not independent biological replicates, and the ten dates themselves may be serially correlated.

Three approaches were considered by the implementer: individual 3D movement is unavailable; a pooled height/prey association ignores generalization and event clustering; a night-heldout, factorized prediction can answer a narrower observed-data question. The third is chosen under the user's delegated implementation authority.

Write `p(h,b | d,r, detected) = p(h | d,r, detected) p(b | h,d,r, detected)`, where `h` is one of three recorder strata and `b` is the complete-buzz mark. For each night `i`, `N_i=sum_h n_ih` and all log scores use `1/N_i` times the sum over recorded passes. Average night scores equally. No likelihood-based standard errors treating passes as iid and no confirmatory p-value are reported.

### Models and fixed regularization

All standardization is fitted on training nights only using the unweighted population mean and standard deviation; a constant feature uses scale 1. Calendar date is days since the first source date, followed by training-only standardization. Resource is log1p ground moth catch followed by training-only standardization. No model or penalty selection after outputs are opened.

1. Height baseline: symmetric 3-class softmax, with a separate intercept and calendar-day slope for each stratum. Height resource model adds a separate moth-index slope to each stratum.
2. Buzz baseline: logistic regression with three stratum-specific intercepts and one shared calendar-day slope. Buzz resource model adds one shared moth-index slope.
3. Training objective for each factor is its average **night-normalized** negative log likelihood plus `0.5 * sum_j lambda_j * beta_j^2`. Fix lambda to 0.01 for intercepts and 0.15 for day/resource slopes. Regularize all intercepts to guarantee finite support, even if a training category is empty. Symmetric height coefficients avoid privileging an arbitrary reference stratum. Newton optimization with analytic gradients/Hessians and a decreasing-objective line search; convergence must be checked. Report no tuned alternative penalties.
4. Four joint candidates are baseline, resource in height only, resource in buzz only, and resource in both. The score gain for both must equal height gain plus conditional-buzz gain on exactly the same heldout records, up to floating-point tolerance.

### Fixed splits and reports

- Primary: leave one whole eligible night out (10 folds, 9 training nights).
- Temporal stress check: sort the ten eligible dates and hold out adjacent pairs (5 folds, 8 training nights). This removes two chronological neighbors, but does not establish independent weather events, sites or future-only forecasting. All test-night scores remain equally weighted.
- Report per-component mean log-score gain in nats per recorded pass, night-equal aggregation, positive-fold counts, and ordinal fold gains. Avoid converting acoustic gains to population effect sizes or adding inferential p-values.
- No weather adjustment is possible from this table. Same-night trap catch is contemporaneous and is not established as available before acoustic recording. No real-time forecast claim.
- Exclusion and model families are unchanged across both splits. No additional predictor, null search, subgroup or source tuning will follow the result. The analysis ends after these fixed comparisons and implementation verification.

## Implementation plan

> For agentic workers: execute with `superpowers:executing-plans`; validate with `superpowers:test-driven-development` and `superpowers:verification-before-completion`.

**Goal:** produce one reproducible, source-qualified actual field-table predictive result without promoting acoustic counts to individual 3D telemetry.

**Architecture:** a pure-standard-library engine accepts a private JSON table, checks source structure, fits the two factors within each split and emits aggregate receipts. Source observations remain outside GitHub. An independent SciPy implementation checks the numerical results.

**Tech stack:** Python 3.10-3.12 standard library for committed code/tests; SciPy only in the independent temporary verifier.

**Spec:** this document. All constraints above are binding. Only Draft PR #102 is updated.

**Review focus:** missing-versus-zero cells; buzz counts cannot exceed passes; training-only preprocessing and whole-date exclusion; equal-night weighting despite unequal count totals; strict probability support and exact score decomposition. Also review source/version provenance, detector-effort limitations, and absence of source coordinates/IDs in outputs.

### Task 1: engine and meaningful tests

Files: `krauel2018_acoustic_height_resource_v1.py`, `test_krauel2018_acoustic_height_resource_v1.py`.

- [ ] Write tests for malformed counts, missing cells, duplicate dates, constant-resource zero increment, known resource-height and resource-buzz signals, night-count rescaling invariance, outcome-blind heldout predictions and score decomposition. Observe the missing implementation fail.
- [ ] Implement `validate_rows`, `fit_factor`, `predict_factor`, `score_night`, `cross_validate` and `source_receipt`; accept JSON input only from an explicit CLI path, output aggregate JSON only. No input observations hardcoded in production code.
- [ ] Run the focused tests. Expected: all pass without internet or original rows.

### Task 2: original-table computation and independent check

- [ ] Materialize the independently crosschecked 13-row transcription privately, retaining null failures, and record its canonical JSON digest. Expected: 13/36/1104/97 overall, 10/30/1073/95 complete.
- [ ] Run both fixed splits and all four nested candidates exactly once after engine tests pass.
- [ ] Independently optimize the same objectives with SciPy using the frozen equations; require each aggregate component and fold score difference below 1e-7 nats. If not, diagnose numerical causes before changing anything; do not alter the scientific design.

### Task 3: report and existing project integration

Files: `KRAUEL2018_FIELD_ACOUSTIC_HEIGHT_RESOURCE_RESULT_20261121.md`, `krauel2018_field_acoustic_height_resource_receipt_20261121.json`; targeted updates to `evidence_ledger_v1.json` and the current status document.

- [ ] Preserve every earlier source claim and all strict individual-resource-height/SDM null fields. Add only the qualified acoustic result and the finite source-access audit.
- [ ] Obtain independent method/code review; resolve material findings with tests.
- [ ] Update the existing Draft branch; verify exact-head Python 3.10/3.11/3.12 CI and reread the result artifacts and PR state. Expected: all gates pass, PR remains Draft and unmerged.

## Source search closed for this execution

- Cistrone et al., DOI 10.1016/j.foreco.2026.124382, publisher lists data in S1/S2 for 20 plots and ground/canopy insects plus bats. Original supplement files and join keys were not opened because available publisher routes returned 403. Candidate only, no ecological fit.
- Srilopan et al., DOI 10.1007/s10531-026-03307-x, measures 2/25/50/75/100 m trap and acoustic strata; publisher says data are available from the author on reasonable request. No request made and no original numerical table opened here.
- Public artificial-flower choice data with known sugar reward provide an executable later behavior-only route; fixed-height feeding stations cannot supply a height-response outcome and are not spliced into this field source.

## Execution record

Initial state: branch head 96c49e4f24c353f8a74eac5ae14ed30cf8472501; PR #102 open, Draft, unmerged. Source table inspected and independently transcribed; new prediction scores not yet calculated. This document is committed before fitting. All further deviations and verification results belong in the final result note.
