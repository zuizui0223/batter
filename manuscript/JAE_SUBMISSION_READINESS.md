# JAE submission readiness v0.3.4

Checked: 2026-09-27

## Current target

First shot: **Journal of Animal Ecology — Research Article**.  
Backup: **Movement Ecology**.

## Scientific status

The superseded v0.3.3 architecture manuscript must not be submitted.

Current manuscript:
`manuscript/MANUSCRIPT_DRAFT_V0_3_4.md`

Current central claim:

> Across six bat tracking panels, identity-matched vertical profiles retain more held-out
> predictive information than expected under session-level exchangeability after occupancy among
> the tested horizontal cells is standardized.

This claim is intentionally narrower than “independent of horizontal fidelity.” Fine-scale
within-cell and central-place structure remain possible contributors.

## Completed scientific gates

- [x] outcome-blind public source universe closed;
- [x] focal early/late identity assignment supported;
- [x] stable residual cell × height map negative retained;
- [x] estimator non-zero-null concern tested under frozen calibration;
- [x] common-cell horizontal standardization applied to all six panels;
- [x] old marginal-dominant 2022 classification shown not robust and superseded;
- [x] AGL common-cell calibration frozen before output and passed at 5 km;
- [x] 2.5-km focal AGL sensitivity passed;
- [x] 10-km focal AGL sensitivity failed and retained;
- [x] predeclared 1-km night-endpoint-neighbourhood exclusion failed and retained;
- [x] fixed 0.5/2-km endpoint sensitivities failed and retained;
- [x] descriptive biological effect translations frozen before output;
- [x] source-study ethics provenance verified.

No new public-data mining belongs in this paper.

## Submission package

- [x] v0.3.4 ecological manuscript;
- [x] five-statement numbered abstract;
- [x] updated vertical-specialization literature positioning;
- [x] calibrated Figures 1–6;
- [x] v0.3.4 anonymous review-PDF workflow;
- [x] v0.3.4 cover-letter draft;
- [x] v0.3.4 title-page template;
- [x] claim-amendment history for Supporting Information.

## Automated format status

- manuscript CI estimate: **6,384 words**;
- abstract: **286 words**;
- numbered abstract statements: **5**;
- keywords: **7**;
- calibrated Figures 1–6: generated and visually inspected;
- anonymous double-spaced line-numbered review PDF: **22 pages**, all pages visually inspected;
- no clipping, overlapping text or broken glyphs observed.

## Release-candidate status

- [x] clean v0.3.4 revision merged to main;
- [x] v0.3.4 manuscript/figure workflow passed on main;
- [x] v0.3.4 anonymous review-PDF workflow passed on main;
- [x] superseded v0.3.3 submission/PDF workflows retired;
- [x] `release/jae-v0.3.4-rc1` frozen after the final submission manifest was committed; main and rc1 were verified identical at `1f28e833` before packaging-only follow-up.

## Final upload guard

A separate strict guard now checks only upload-time metadata:
`python scripts/check_jae_upload_ready.py`.

It is intentionally expected to fail until the final title page contains the author list,
affiliations, corresponding-author email and ORCID, CRediT statement, acknowledgements, funding,
conflict declaration, and a permanent archive DOI. The matching GitHub Actions workflow is
manual-only (`jae-upload-readiness-v0.3.4`) so unresolved human metadata does not turn the
scientific RC CI red. This guard does not re-open empirical analyses.

## Archive-release readiness

A separate manual guard, `python scripts/check_zenodo_release_ready.py`, now blocks a GitHub
release intended for Zenodo until an explicit software LICENSE and one final metadata source
(`CITATION.cff` or `.zenodo.json`) are present without placeholders.

The repository currently remains **BLOCKED** at this archival layer because neither the software
license nor final release metadata has been supplied. This does not affect the frozen empirical
result.

The current JAE requirements audit is
`manuscript/JAE_INITIAL_SUBMISSION_AUDIT_2026_09_27.md`.

## Human-input items before journal upload

- permanent versioned archive DOI;
- final authors and affiliations;
- corresponding-author details and ORCID;
- CRediT contributions;
- funding and acknowledgements;
- conflict-of-interest declaration.

## Claim boundary

Supported:
- repeatable vertical individual identity;
- vertical identity beyond occupancy differences among tested coarse horizontal cells;
- direct pairwise vertical distinguishability under common horizontal weighting;
- terrain-relative focal identity at 2.5–5 km.

Not supported:
- complete removal of fine-scale horizontal fidelity;
- independence from central-place departure/arrival structure;
- 10-km focal scale invariance;
- stable individual-specific 3-D route maps;
- personality, learning, adaptation or optimality;
- harmonized foraging-height specialization;
- one universal causal mechanism.
