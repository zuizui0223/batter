# JAE submission manifest v0.3.5 rc1

Date: 2026-09-27

## Scientific status

The v0.3.4 rc3 package is the immutable pre-audit baseline and must not be submitted as the final
scientific version.

Current scientific manuscript:
`manuscript/MANUSCRIPT_DRAFT_V0_3_5.md`

Working title:

**Repeatable vertical identity in bat airspace persists after coarse horizontal occupancy is standardized**

## Completed frozen audit

Primary cross-panel confound/effect-null workflow:
- run: **36317089590**
- conclusion: **success**

Key results:
- common-cell identity exceeds panel-specific exchangeability expectation in all six original panels;
- 1-km endpoint-neighbourhood exclusion passes in 4/5 comparative panels;
- *Eidolon* fails only the frozen n gate (11 < 15) despite calibrated excess +0.390, p=0.0002;
- focal *Tadarida* endpoint exclusion remains FAIL, p=0.1109;
- pairwise self-identification exceeds its panel-specific null in 5/6 panels;
- *P. hastatus* 2016 pairwise translation does not pass, p=0.1168;
- focal raw AGL separation 256.459 m has null mean 133.733 m, calibrated excess 122.727 m,
  p=0.0297.

## Manuscript and figures

JAE v0.3.5 manuscript/figure workflow:
- run: **36322870626**
- conclusion: **success**
- manuscript CI word estimate: **7,047**
- abstract: **271 words**
- numbered abstract statements: **5**
- keywords: **7**
- Figures 1–6: generated successfully and visually inspected; Figure 6 label-overlap fix verified

## Anonymous review PDF

JAE v0.3.5 review-PDF workflow:
- run: **36322873490**
- conclusion: **success**
- anonymity guard: **PASS**
- rendered pages: **24**
- page size: US Letter
- visual inspection: **passed on all 24 pages**; no clipping, overlap or broken glyphs after the final Figure 6 legend update

## Claim boundary

Supported:
- repeatable individual vertical identity relative to panel-specific session-label exchangeability;
- identity beyond differences in coarse 5-km horizontal occupancy;
- calibrated pairwise self-identification in five panels;
- focal AGL metre-scale separation above its own non-zero exchangeability baseline;
- endpoint-neighbourhood robustness in four comparative panels.

Not established:
- universal independence from central-place or endpoint-associated structure;
- complete removal of fine-scale within-cell horizontal fidelity;
- stable individual-specific 3-D route maps;
- a verified roost, colony or lek mechanism;
- personality, learning, adaptation or optimality;
- one universal causal mechanism.

## Remaining non-scientific blockers

- choose/add repository software LICENSE;
- fill final author list and affiliations;
- corresponding-author postal address, email and ORCID;
- CRediT contributions;
- funding and acknowledgements;
- conflict-of-interest declaration;
- finalize CITATION.cff or .zenodo.json;
- enable GitHub repository in Zenodo and mint the version DOI;
- insert DOI into title page;
- final visual inspection/upload.
