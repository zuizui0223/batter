# JAE submission manifest v0.3.7 rc2

Date: 2026-09-28

## Scientific status

Current manuscript:
`manuscript/MANUSCRIPT_DRAFT_V0_3_7.md`

Title:

**Repeatable vertical identity in bat airspace persists after coarse horizontal occupancy is standardized**

v0.3.7 changes narrative hierarchy only; all scientific data, analyses, frozen audits and claim
ceilings are inherited unchanged from v0.3.6.

The strongest ecological result is now presented explicitly as comparative:

- all five comparative panels retain calibrated vertical-distribution shape identity after
  session-median centering;
- focal *Tadarida* is treated as the motivating boundary case and does not retain centered-shape
  identity (p=0.5121);
- stationary correction retains identity in the two structurally eligible comparative panels;
- pipeline-specific exchangeability calibration remains the second major contribution.

## Validated manuscript package

Main submission run:
- workflow run: **36371352865**
- head: `5f0c68b316c909250ed68065a1c36b807b8e5f2a`
- conclusion: **success**
- manuscript CI estimate: **6,548 words**
- abstract: **255 words**
- Introduction: **685 words**
- Results: **1,059 words**
- Discussion: **1,077 words**
- keywords: **7**
- main figures: **5**
- supporting figures: **2**

Main-figure artifact:
- id: `10949730214`
- digest: `sha256:789ad64f884dc4125e427c77ca5ba2b806d27a1bf0c4d034e3152a2b25ef939d`

Supporting-figure artifact:
- id: `10949575931`
- digest: `sha256:e9c86535aca5a5f547da252bacbfdc5df74b3a7ce6274cb0830c191194a01781`

Anonymous review run:
- workflow run: **36371352895**
- head: `5f0c68b316c909250ed68065a1c36b807b8e5f2a`
- conclusion: **success**
- anonymity guard: **PASS**
- review PDF: **22 pages**
- artifact id: `10948449463`
- digest: `sha256:1712cc2f367d39eca904f13e3c97309faa1409f72cafc14d1fa9a3de6621bcac`

Visual QA:
- main Figures 1–5 inspected;
- Supporting Figures S1–S2 inspected;
- final 22-page review PDF inspected;
- no clipping, overlap or broken glyphs found.

## Supporting Information

`manuscript/SUPPORTING_INFORMATION_CLAIM_AMENDMENT_HISTORY.md`

contains the detailed freeze/audit/supersession chronology and the Supporting Figure S1–S2
legends. This history is preserved without making it the main manuscript's narrative entry point.

## Claim boundary

Supported:
- six-panel vertical identity relative to panel-specific exchangeability after coarse horizontal
  standardization;
- vertical-distribution shape identity in all five comparative panels after additive altitude
  level is removed;
- empirical stationary-offset corroboration in both structurally eligible comparative panels;
- pairwise calibrated self-identification in five panels;
- endpoint-neighbourhood robustness in four comparative panels;
- pipeline-specific null calibration as a general methodological lesson.

Not established:
- device-independent vertical-distribution shape in focal *Tadarida*;
- complete removal of fine-scale horizontal fidelity or central-place structure;
- elimination of tag-specific altitude-error variance;
- elimination of temporal-context confounding, especially in *P. hastatus* 2016;
- personality, learning, adaptation, optimality or one universal mechanism.

## Final metadata workflow

One human metadata source:
`submission/jae_v0_3_7_metadata.json`

Template:
`submission/jae_v0_3_7_metadata.template.json`

Assembler:
`scripts/apply_jae_v0_3_7_metadata.py`

Stages:
1. pre-release — explicit human metadata + LICENSE; archive DOI empty;
2. post-DOI — insert the minted Zenodo version DOI and regenerate the final journal title page.

No human identity, authorship, license, funding, conflict declaration, ORCID, postal address or DOI
is inferred.


## Packaging validation

v0.3.7 one-source metadata workflow:
- synthetic self-test run: `36371640078` — **success**
- pre-release assembly: READY
- post-DOI assembly: READY
- final JAE upload gate: READY
- synthetic combined count: 6,730 words pre-release / 6,725 words post-DOI

Active-reference guard:
- run: `36371726985` — **success**

No authorship, license, ORCID, funding, conflict declaration, postal address or DOI was inferred.


## Packaging rc2 — final GitHub release preflight

Scientific content is unchanged.

RC2 adds a fail-closed manual preflight immediately before the one GitHub Release intended for
Zenodo archiving. It verifies the final release-candidate commit matches current main, human
metadata/CITATION/LICENSE are complete, the archive DOI is still empty before minting, release
notes contain no placeholders, and the target tag/release do not already exist.

The preflight never creates a tag or publishes a release.
