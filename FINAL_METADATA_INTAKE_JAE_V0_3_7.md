# JAE v0.3.7 final metadata intake

All remaining human information is centralized in one JSON file.

## Phase A — before the GitHub/Zenodo release

1. Copy `submission/jae_v0_3_7_metadata.template.json` to
   `submission/jae_v0_3_7_metadata.json`.
2. Fill every human field **except `archive_doi`**, which stays empty until Zenodo mints it.
3. Choose the repository software license and add the matching `LICENSE` file.
4. Run:
   `python scripts/apply_jae_v0_3_7_metadata.py --stage pre-release`.
5. Commit the final metadata JSON, LICENSE, generated `CITATION.cff`,
   `manuscript/TITLE_PAGE_V0_3_7.md`, and metadata summary.
6. Run `python scripts/check_zenodo_release_ready.py`.
7. Only when that gate reports READY, publish the GitHub release from the final release candidate.
   Zenodo then archives that release and mints the version DOI.

The pre-release title page deliberately says that the versioned Zenodo DOI is pending. It is not
the file uploaded to the journal.

## Phase B — after Zenodo mints the version DOI

1. Put the minted version DOI into `archive_doi` in
   `submission/jae_v0_3_7_metadata.json`.
2. Run:
   `python scripts/apply_jae_v0_3_7_metadata.py --stage post-doi`.
3. This regenerates the final journal title page with the DOI and recomputes the combined
   manuscript + title-page word count.
4. Run:
   - `python scripts/check_zenodo_release_ready.py`
   - `python scripts/check_jae_upload_ready.py`
5. Commit the post-DOI title-page/metadata update to main as submission metadata. A second GitHub
   Release is **not** required merely to put the already-minted archive DOI on the journal title
   page.
6. Upload the separate title page and anonymous review manuscript to Journal of Animal Ecology.

## Important

The generator never infers authors, CRediT roles, funding, conflicts, ORCIDs, postal address,
software license or DOI.

The combined JAE word count is recalculated after the generated title page. Assembly fails if the
manuscript plus title page exceeds the 8,500-word Research Article limit.

No scientific result, figure input, endpoint, or analysis rule is changed by this workflow.
