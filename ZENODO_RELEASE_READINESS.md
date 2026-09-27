# Zenodo release readiness

Checked: 2026-09-27

## Current status

**BLOCKED intentionally.**

The repository currently has no `LICENSE`, no final `CITATION.cff`, and no `.zenodo.json`.
Those are release-metadata decisions, not empirical-analysis gaps.

## Safe release sequence

1. Choose the intended software license and add the corresponding `LICENSE` file.
2. Fill `CITATION.cff.template` with the final author order and identifiers, then save it as
   `CITATION.cff` (or use one authoritative `.zenodo.json` instead).
3. Run `python scripts/check_zenodo_release_ready.py`; it must report READY.
4. In Zenodo, connect the GitHub account and enable `zuizui0223/batter` for archiving.
5. Create the GitHub release from the final packaging release candidate.
6. After Zenodo ingests the release, copy the version DOI into
   `manuscript/TITLE_PAGE_TEMPLATE_V0_3_5.md`.
7. Run `python scripts/check_jae_upload_ready.py`; it should then be blocked only by any remaining
   author/funding/conflict metadata.
8. Upload the separate title page and anonymous review manuscript to Journal of Animal Ecology.

## Deliberate non-decisions

This repository does not infer a software license or final author list. Those choices require
explicit human input and are therefore hard blockers rather than silently guessed defaults.

## Scientific freeze

The current scientific package is v0.3.5. Its cross-panel confound and effect-null audit is complete,
and the v0.3.4 rc3 branch is retained as the immutable pre-audit baseline.

Nothing in this release-readiness layer reopens data selection, endpoints, estimator calibration,
spatial scales, exclusion radii, vertical bins, smoothing rules or retained negative results.
