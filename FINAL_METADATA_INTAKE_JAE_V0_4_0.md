# Final metadata intake — JAE v0.4.0

## Purpose

This file is the only remaining human-input checklist for `release/jae-v0.4.0-rc1`.

Scientific content is frozen. Do not use metadata completion as an occasion to modify analyses, claims, figures or manuscript interpretation.

## Frozen manuscript identity

Title:

**Persistent individual vertical strategies need not partition three-dimensional space in bats**

Release candidate:
`release/jae-v0.4.0-rc1`

Expected release tag after all gates pass:
`jae-v0.4.0`

Human metadata template:
`submission/jae_v0_4_0_metadata.template.json`

Final human metadata source to create:
`submission/jae_v0_4_0_metadata.json`

Do not edit the template in place. Copy it to the final metadata path and replace every placeholder explicitly.

## Required human fields

The final metadata JSON must contain, in final author order:

- given names and family name for every author;
- ORCID for the corresponding author, and any other available ORCIDs;
- affiliation IDs for every author;
- CRediT roles for every author;
- exactly one corresponding author;
- full affiliation text for every affiliation ID;
- corresponding-author postal address;
- corresponding-author email address;
- acknowledgements, or the literal value `None`;
- funding sources / grant numbers, or the literal value `None`;
- conflict-of-interest declaration;
- software licence SPDX identifier matching exactly one committed LICENSE file;
- release date;
- archive DOI left empty before the GitHub release and filled only after Zenodo mints the version DOI.

No field above should be inferred from repository history, account identity, email history or prior drafts.

## Pre-release sequence

1. Copy `submission/jae_v0_4_0_metadata.template.json` to `submission/jae_v0_4_0_metadata.json`.
2. Fill every human field.
3. Add exactly one repository LICENSE file matching `software_license_spdx`.
4. Keep `archive_doi` empty.
5. Run:
   `python scripts/apply_jae_v0_4_0_metadata.py --stage pre-release`
6. Confirm generated `manuscript/TITLE_PAGE_V0_4_0.md` and `CITATION.cff`.
7. Confirm combined manuscript + generated title page remains <= 8,500 words.
8. Run:
   `python scripts/check_zenodo_release_ready_v0_4_0.py`
9. Run the manual GitHub Action:
   `jae-github-release-preflight-v0.4.0`
   with candidate `release/jae-v0.4.0-rc1`.
10. Only after every pre-release gate is READY and the repository is enabled in Zenodo, publish one GitHub release with tag `jae-v0.4.0` from the RC.

## Post-DOI sequence

1. Copy the exact version DOI minted by Zenodo into `archive_doi`.
2. Run:
   `python scripts/apply_jae_v0_4_0_metadata.py --stage post-doi`
3. Run:
   `python scripts/check_zenodo_release_ready_v0_4_0.py`
4. Run:
   `python scripts/check_jae_upload_ready_v0_4_0.py`
5. Confirm the title-page Data Availability section contains the same Zenodo DOI.
6. Confirm the final combined count remains <= 8,500 words.
7. Upload the journal package.

## Already validated

Synthetic pipeline run **37093159799** passed:
- pre-release assembly READY;
- combined pre-release count 8,216 / 8,500;
- post-DOI assembly READY;
- combined post-DOI count 8,211 / 8,500;
- final upload gate READY.

Those synthetic values validate the workflow only. They do not substitute for real human metadata.

## Scientific stop rule

No further same-data mechanism fishing is authorized for v0.4.0. Metadata completion and archive publication must not alter the frozen scientific claims.
