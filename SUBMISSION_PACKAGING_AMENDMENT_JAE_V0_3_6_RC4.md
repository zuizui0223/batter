# JAE v0.3.6 rc4 packaging amendment

Date: 2026-09-28

## Purpose

RC4 is a **packaging-only** successor to v0.3.6 rc3.

The scientific manuscript, results, figures, audit outputs and claim boundary are unchanged.

## Active-reference cleanup

RC4 makes the active submission state internally consistent and fail-closed:

- current submission manifest: **v0.3.6 rc4**;
- current manuscript: `manuscript/MANUSCRIPT_DRAFT_V0_3_6.md`;
- current one-source human metadata:
  `submission/jae_v0_3_6_metadata.json`;
- final journal title page:
  `manuscript/TITLE_PAGE_V0_3_6.md`, generated only after explicit human metadata;
- historical v0.3.5 references remain only as provenance, never as current-package pointers.

## Guard

A dedicated active-reference guard checks CURRENT_STATUS, the current manifest, JAE initial audit,
readiness checklist and metadata guide.

Latest branch validation before merge:

- workflow run: `36367831733`
- conclusion: **success**

## Metadata infrastructure inherited from rc3

The two-stage one-source metadata workflow remains unchanged:

1. pre-release — explicit human metadata + LICENSE, archive DOI empty;
2. post-DOI — insert the Zenodo version DOI, regenerate final journal title page.

End-to-end synthetic metadata validation remains:

- workflow run: `36366987729`
- conclusion: **success**

No identity, authorship, license, funding, conflict declaration, ORCID, postal address or DOI is
inferred.

## Scientific freeze

No scientific manuscript text, result, figure input, endpoint, permutation, horizontal grain,
exclusion radius, vertical bin, smoothing rule, negative control, audit outcome or claim changed in
RC4.

Remaining work is human/archive metadata only.
