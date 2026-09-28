# Zenodo release readiness — JAE v0.3.7

Checked: 2026-09-28

## Current status

**BLOCKED intentionally on human metadata.**

The scientific package is frozen. Release readiness now has one human metadata source:
`submission/jae_v0_3_7_metadata.json`, created from the checked-in template.

## Phase A — pre-release

1. Copy `submission/jae_v0_3_7_metadata.template.json` to
   `submission/jae_v0_3_7_metadata.json`.
2. Fill authorship, affiliations, corresponding-author details, CRediT roles, acknowledgements,
   funding, conflict declaration, release date and software-license SPDX identifier.
3. Leave `archive_doi` empty: Zenodo has not minted it yet.
4. Add the matching repository `LICENSE` file.
5. Run:
   `python scripts/apply_jae_v0_3_7_metadata.py --stage pre-release`.
6. Run:
   `python scripts/check_zenodo_release_ready.py`.
7. Commit the explicit metadata JSON, LICENSE, generated `CITATION.cff`,
   pre-release `manuscript/TITLE_PAGE_V0_3_7.md`, and metadata summary.
8. Enable `zuizui0223/batter` in the repository owner's Zenodo GitHub integration.
9. Publish the GitHub release from the final release candidate only when the Zenodo gate reports
   READY.

The pre-release title page deliberately states that the versioned Zenodo DOI is pending. It is not
yet the journal-upload title page.

## Phase B — after Zenodo creates the version DOI

1. Copy the minted version DOI into `archive_doi` in
   `submission/jae_v0_3_7_metadata.json`.
2. Run:
   `python scripts/apply_jae_v0_3_7_metadata.py --stage post-doi`.
3. Run:
   - `python scripts/check_zenodo_release_ready.py`
   - `python scripts/check_jae_upload_ready.py`
4. Commit the post-DOI journal title page and metadata summary to main.
5. Upload the separate final title page and anonymous review manuscript to Journal of Animal
   Ecology.

No second GitHub release is required just to add the already-minted archive DOI to the journal
title page.

## Automated safeguards

- the assembler refuses placeholders, invalid author/affiliation links, unsupported CRediT roles,
  missing corresponding-author email/ORCID, missing LICENSE, or malformed dates;
- pre-release permits `archive_doi` to be empty;
- post-DOI requires a DOI beginning with `10.`;
- `CITATION.cff` version, release date and license must match the one-source metadata JSON;
- the final upload gate requires the archive DOI in the title page to match the JSON exactly;
- manuscript + generated title-page word count must remain <=8,500 words.

The complete workflow was exercised end-to-end with synthetic metadata in GitHub Actions without
committing the synthetic identity or license.

## Scientific freeze

The current scientific package is v0.3.7. Cross-panel confound, effect-null and final
tag-altitude-bias audits are complete. Nothing in this release-readiness layer reopens source
selection, endpoints, estimator calibration, scales, exclusions, bins, smoothing, results or
claims.
