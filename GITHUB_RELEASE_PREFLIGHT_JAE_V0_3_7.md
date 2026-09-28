# Final GitHub release preflight — JAE v0.3.7

This layer exists only to prevent publishing the wrong branch/tag to Zenodo. It never creates or
publishes a release.

## Before running

The human metadata phase must already be complete:

- `submission/jae_v0_3_7_metadata.json` exists with `archive_doi` still empty;
- the chosen repository `LICENSE` exists;
- generated `CITATION.cff` exists;
- generated pre-release `manuscript/TITLE_PAGE_V0_3_7.md` exists;
- `python scripts/check_zenodo_release_ready.py` reports READY;
- the repository owner has enabled `zuizui0223/batter` in Zenodo's GitHub integration.

## Run

Use the manual workflow:

`jae-github-release-preflight-v0.3.7`

with the final release-candidate ref.

The workflow verifies:

- candidate HEAD equals current `origin/main`;
- metadata/CFF/LICENSE are complete and version-consistent;
- `archive_doi` is still empty before minting;
- release notes contain no placeholders;
- tag `jae-v0.3.7` does not already exist;
- no GitHub Release already uses that tag.

Only after it reports READY should the owner publish one GitHub Release:

- tag: `jae-v0.3.7`
- target: the approved final release-candidate commit
- notes: `RELEASE_NOTES_JAE_V0_3_7.md`

After Zenodo mints the version DOI, continue with the documented post-DOI metadata stage.

No second GitHub release is required merely to insert that DOI into the separate journal title
page.
