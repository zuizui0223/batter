# JAE submission manifest v0.3.6 rc1

Date: 2026-09-27

## Scientific status

Current scientific manuscript:
`manuscript/MANUSCRIPT_DRAFT_V0_3_6.md`

Title:

**Repeatable vertical identity in bat airspace persists after coarse horizontal occupancy is standardized**

The v0.3.5 package is the pre-tag-bias-audit baseline and must not be submitted as the final
scientific version.

## Completed frozen audits

### Cross-panel confound and effect-null audit

- original common-cell identity exceeds panel-specific exchangeability expectations in all six panels;
- 1-km endpoint-neighbourhood exclusion passes in 4/5 comparative panels;
- *Eidolon* retains calibrated excess +0.390, p=0.0002, but fails the frozen post-exclusion n gate;
- focal *Tadarida* endpoint exclusion remains FAIL, p=0.1109;
- calibrated pairwise self-identification passes in 5/6 panels;
- *P. hastatus* 2016 pairwise translation fails, p=0.1168.

### Final tag altitude-bias audit

Primary shift-invariant session-centered audit:
- run: **36324896204**
- result category: **5/6 PASS**

Centered-shape calibrated excess / p:
- *Eidolon*: +0.443, p=0.0002
- *Hypsignathus*: +0.177, p=0.0002
- *P. hastatus* 2022: +0.111, p=0.0002
- *P. hastatus* 2023: +0.118, p=0.0002
- *P. hastatus* 2016: +0.574, p=0.0076
- focal *Tadarida*: -0.022, p=0.5121 — **FAIL**

Stationary-height corroboration:
- run: **36327934667**
- *Hypsignathus*: median absolute estimated offset 4.64 m; calibrated excess +0.0671, p=0.0002;
- *P. hastatus* 2016: median absolute estimated offset 2.00 m; calibrated excess +0.3808, p=0.0002;
- **2/2 structurally eligible panels retain identity after correction**.

Scientific consequence:
- additive constant tag/device altitude offsets are not a general explanation for the cross-panel result;
- focal *Tadarida* does not retain identity after absolute altitude level is removed;
- its raw 256-m AGL translation is therefore descriptive and may contain biological mean-height difference, device offset, or both;
- no further new scientific analysis family is authorized before submission.

## Manuscript and figures

Final v0.3.6 manuscript/figure workflow:
- run: **36329395938**
- head: `b0fdea5dd191eeb7759fec84a899b0bdd78994cd`
- conclusion: **success**
- artifact: `10935221530`
- digest: `sha256:2e58d1883f22beacff27bc8e2f828828216dd473cb51da674b43d7a2aa4b91e0`
- manuscript CI estimate: **7,932 words**
- abstract: **273 words**
- numbered statements: **5**
- keywords: **7**
- Figures 1–7: generated and visually inspected.

## Anonymous review PDF

Final v0.3.6 review-PDF workflow:
- run: **36329434589**
- head: `8e02d1329fcf2fd0dee5ff96090272a70d353263`
- conclusion: **success**
- artifact: `10935232608`
- digest: `sha256:98c54670f7e74904aea05577560d6e7edea47a468453774985c99f7aa05572a1`
- anonymity guard: **PASS**
- rendered pages: **26**
- page size: US Letter
- visual QA: prior full 26-page build inspected; final build differs only on page 26, which was re-inspected after moving Figure 7 legend into the Figure legends section and polishing anonymous repository wording.

## Claim boundary

Supported:
- repeatable vertical individual identity relative to panel-specific session-label exchangeability;
- identity beyond differences in coarse 5-km horizontal occupancy;
- calibrated pairwise self-identification in five panels;
- endpoint-neighbourhood robustness in four comparative panels;
- shift-invariant vertical-distribution shape identity in five panels;
- stationary-offset-corrected identity in both structurally eligible panels.

Not established:
- tag-independent vertical-distribution shape identity in focal *Tadarida*;
- universal independence from central-place or endpoint-associated structure;
- complete removal of fine-scale within-cell horizontal fidelity;
- removal of temporal-context confounding, especially in *P. hastatus* 2016;
- stable individual-specific 3-D route maps;
- verified roost/colony/lek mechanisms;
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
- insert DOI into the v0.3.6 title page;
- final Journal of Animal Ecology upload.
