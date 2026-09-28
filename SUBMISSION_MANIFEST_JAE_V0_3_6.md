# JAE submission manifest v0.3.6 rc4

Date: 2026-09-28

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
- run: **36330015862**
- head: `864a6908b09b0dcdbcb1b1468b87aa2a59cdf6cc`
- conclusion: **success**
- artifact: `10935526906`
- digest: `sha256:f2aebffbc7d51b4081cd217dd9ef963cb9629b1e2e9459ad54a85667020d6e9b`
- manuscript CI estimate: **7,932 words**
- abstract: **273 words**
- numbered statements: **5**
- keywords: **7**
- Figures 1–7: generated and visually inspected.

## Anonymous review PDF

Final v0.3.6 review-PDF workflow:
- run: **36329796749**
- head: `906a42f841e639d5a4ab1d4397c7425df250d5ab`
- conclusion: **success**
- artifact: `10935182096`
- digest: `sha256:8a7fb006f7e0d5c0f29ddb732039cb3447c50562b0d5a8ec7d10f384e3592d25`
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

All human metadata are centralized in
`submission/jae_v0_3_6_metadata.json`.

Pre-release:
- copy/fill the metadata template except `archive_doi`;
- choose/add the matching repository LICENSE;
- generate title page + CITATION.cff;
- make the Zenodo release gate READY;
- enable the repository in Zenodo and publish the GitHub release.

Post-DOI:
- insert the minted version DOI into the same metadata JSON;
- regenerate the final journal title page;
- make the JAE final-upload gate READY;
- confirm combined manuscript + title-page count <=8,500;
- perform the Journal of Animal Ecology upload.


## Packaging rc3 — one-source final metadata

Scientific content is unchanged.

Final human/archive metadata are now centralized in:
`submission/jae_v0_3_6_metadata.json`.

The deterministic assembler and gates implement two stages:

1. **pre-release** — authorship/license/release metadata complete, archive DOI still empty;
2. **post-DOI** — Zenodo version DOI inserted, final journal title page regenerated.

Synthetic end-to-end Actions self-test:
- run: **36366987729**
- conclusion: **success**
- pre-release assembly: READY
- Zenodo release gate: READY
- post-DOI assembly: READY
- final JAE upload gate: READY

The workflow does not infer authors, licensing, funding, conflicts, ORCIDs, postal address or DOI.


## Packaging rc4 — active-reference integrity

Scientific content is unchanged.

RC4 makes the current submission pointers internally consistent:

- manifest identity is rc4;
- current manuscript remains v0.3.6;
- final human metadata source remains the one-source JSON;
- the final journal title page is the generated `manuscript/TITLE_PAGE_V0_3_6.md`;
- historical v0.3.5 references remain only as provenance, not as current-package pointers.

A dedicated active-reference guard prevents stale current-package wording from re-entering the
manifest, CURRENT_STATUS, JAE audit or readiness documents.
