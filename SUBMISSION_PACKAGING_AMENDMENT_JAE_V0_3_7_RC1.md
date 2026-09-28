# JAE v0.3.7 rc1 packaging amendment

Date: 2026-09-28

## Purpose

v0.3.7 rc1 promotes the comparative-first editorial revision to the current Journal of Animal
Ecology submission package.

No scientific analysis, result, audit outcome, threshold, source, permutation, grid, bin,
exclusion, smoothing rule or claim ceiling changed relative to v0.3.6.

## Editorial change

The manuscript now leads with the strongest comparative result:

- all five comparative panels retain calibrated vertical-distribution shape identity after
  session-median centering;
- *Tadarida* is the motivating boundary case rather than the template for the general claim;
- detailed freeze/audit/supersession history is Supporting Information;
- former focal/mechanistic and architecture-diagnostic figures are Supporting Figures S1-S2.

## Validated package

Main manuscript/figure run:
- `36371352865`
- success
- 6,548-word manuscript CI estimate
- 255-word Abstract
- 685-word Introduction
- 5 main figures
- 2 Supporting Figures

Anonymous review run:
- `36371352895`
- success
- anonymity PASS
- 22 pages

Main active-reference guard:
- `36371824746`
- success
- head `eed0e2654c81d6b95fd909665a5585ec79cee734`

## Metadata infrastructure

The one-source metadata/Zenodo/JAE upload workflow has been promoted to v0.3.7.

Synthetic integration test:
- run `36371640078`
- success
- pre-release combined count: 6,730 words
- post-DOI combined count: 6,725 words
- final upload gate: READY

Actual final author metadata are recalculated and fail closed if the JAE combined count exceeds
8,500 words.

## Remaining blockers

Human/archive metadata only:
- final author order and affiliations;
- corresponding-author email/address/ORCID;
- CRediT;
- acknowledgements/funding/conflict declaration;
- software license + LICENSE;
- release date;
- Zenodo integration and version DOI;
- final JAE upload.

No new scientific analysis is permitted before submission.
