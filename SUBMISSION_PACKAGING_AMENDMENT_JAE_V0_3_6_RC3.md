# JAE v0.3.6 rc3 packaging amendment

Date: 2026-09-28

## Purpose

RC3 is a **packaging-only** successor to v0.3.6 rc2.

No scientific manuscript text, result, figure input, endpoint, permutation, scale, exclusion,
vertical bin, smoothing rule, negative control or claim boundary changed.

## What RC3 adds

All remaining human/archive information is centralized in one source:

`submission/jae_v0_3_6_metadata.json`

created from:

`submission/jae_v0_3_6_metadata.template.json`.

A deterministic assembler generates:

- `manuscript/TITLE_PAGE_V0_3_6.md`;
- `CITATION.cff`;
- `submission/jae_v0_3_6_metadata_summary.json`.

## Two-stage release logic

### Pre-release

The archive DOI is intentionally empty. Explicit authorship, affiliations, corresponding-author
details, CRediT, acknowledgements, funding, conflict declaration, release date and software
license are required. The repository LICENSE must exist.

The Zenodo gate verifies that metadata JSON, LICENSE and CITATION.cff agree before a GitHub Release
is published.

### Post-DOI

After Zenodo archives the GitHub Release and mints the version DOI, that DOI is inserted into the
same metadata JSON. The assembler regenerates the final journal title page.

The JAE upload gate then verifies:

- exact archive DOI consistency;
- final title/manuscript consistency;
- corresponding-author email and ORCID;
- required title-page sections;
- absence of placeholders;
- combined manuscript + title-page count <=8,500 words.

A second GitHub Release is not required merely to put the already-minted DOI on the JAE title
page.

## Validation

End-to-end synthetic Actions self-test:

- workflow run: `36366987729`
- conclusion: **success**
- pre-release metadata assembly: READY
- Zenodo release gate: READY
- simulated Zenodo DOI mint
- post-DOI metadata assembly: READY
- final Zenodo consistency gate: READY
- final JAE upload gate: READY

Synthetic one-author combined count:
- pre-release: 8,114 words;
- post-DOI: 8,109 words.

The actual final metadata are always recalculated and blocked automatically if the combined count
exceeds 8,500 words.

## Remaining blockers

Only explicit human choices/data remain:

- final author order and affiliations;
- corresponding-author postal address, email and ORCID;
- per-author CRediT roles;
- acknowledgements;
- funding/grants;
- conflict declaration;
- software-license choice and LICENSE file;
- release date;
- Zenodo GitHub integration and minted version DOI;
- final JAE upload.

No new scientific analysis is permitted before submission.
