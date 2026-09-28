# JAE v0.3.6 final metadata intake

All remaining human information is intentionally centralized in one file.

## One source of truth

1. Copy:
   `submission/jae_v0_3_6_metadata.template.json`
   to:
   `submission/jae_v0_3_6_metadata.json`.
2. Replace every placeholder.
3. Choose the repository software license and add the matching `LICENSE` file.
4. Run:
   `python scripts/apply_jae_v0_3_6_metadata.py`.
5. Commit the generated:
   - `manuscript/TITLE_PAGE_V0_3_6.md`
   - `CITATION.cff`
   - `submission/jae_v0_3_6_metadata_summary.json`
   together with the final metadata JSON and LICENSE.
6. Run:
   - `python scripts/check_zenodo_release_ready.py`
   - `python scripts/check_jae_upload_ready.py`
7. Create the GitHub release only after both gates report READY.
8. After Zenodo mints the version DOI, if the DOI changed from the prefilled value, update
   `archive_doi`, regenerate the files, and rerun both gates.

## Important

The generator does **not** infer authors, CRediT roles, funding, conflicts, ORCIDs, postal address,
software license or DOI.

The combined JAE word count is recalculated after the final title page is generated. The script
fails if the manuscript plus title page exceeds 8,500 words.

No scientific manuscript result is changed by this workflow.
