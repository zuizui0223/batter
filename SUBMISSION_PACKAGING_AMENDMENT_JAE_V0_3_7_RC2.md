# JAE v0.3.7 rc2 packaging amendment

Date: 2026-09-28

## Purpose

RC2 is a packaging-only successor to v0.3.7 rc1.

The scientific manuscript, results, figures, audit outcomes and claim boundary are unchanged.

## Added in RC2

A fail-closed final GitHub/Zenodo release preflight now checks the exact state that will be
published to Zenodo.

It verifies:

- final human metadata JSON exists and is complete;
- exactly one repository LICENSE file exists;
- generated CITATION.cff is complete and v0.3.7-consistent;
- the pre-release title page exists and still has no minted archive DOI;
- the candidate commit matches current main;
- the working tree is clean;
- release notes contain no placeholders;
- the target tag `jae-v0.3.7` does not already exist;
- no GitHub Release already uses that tag;
- the Zenodo release-readiness gate reports READY.

The workflow does not create a tag and does not publish a release.

## Release notes

Prepared:

`RELEASE_NOTES_JAE_V0_3_7.md`

These summarize the final scientific result, frozen provenance and public Movebank data DOIs
without requiring the Zenodo version DOI before it is minted.

## Validation

Release-preflight synthetic self-test:

- workflow run: `36373116328`
- conclusion: **success**
- synthetic pre-release metadata assembly: READY
- Zenodo release gate: READY
- candidate integrity: READY
- target tag absent
- target GitHub Release absent

Final active-reference guard after merge/provenance updates:

- workflow run: `36373353000`
- head: `6f1bfcbf5b0c664e9846e161d26b1d639e217ad6`
- conclusion: **success**

## Scientific freeze

No manuscript text, result, figure input, source, endpoint, permutation, grid, bin, exclusion
radius, smoothing rule, negative control, audit result or claim ceiling changed in RC2.

Remaining work is explicit human metadata, license choice, Zenodo enablement/DOI minting and final
JAE upload only.
