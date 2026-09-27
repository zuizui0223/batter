# JAE v0.3.4 rc2 packaging amendment

Date: 2026-09-27

## Purpose

This amendment advances the submission package from rc1 to rc2 **without changing scientific
content**.

Scientific-content commit remains:

`29c18a9f3c29ee2f561e0f7d28cd340fcc55aa22`

The rc1 provenance baseline remains:

`1f28e833402d3fdd7dd6ce274e5392bf253fee84`

## Packaging-only changes after rc1

- closed superseded Movement Ecology PR #3 so it cannot be mistaken for the active submission route;
- corrected the stale readiness checkbox recording that rc1 had already been frozen;
- added `scripts/check_jae_upload_ready.py`;
- added manual-only workflow `jae-upload-readiness-v0.3.4`;
- the strict gate checks final authors/affiliations, corresponding-author email and ORCID,
  contribution statement, acknowledgements, funding, conflict declaration, and permanent DOI.

The current placeholder title page correctly returns **BLOCKED**. This is an upload-time metadata
guard, not a scientific analysis gate.

## Empirical freeze

No dataset, source-admission rule, endpoint, permutation design, horizontal grain, exclusion
radius, vertical bin, smoothing rule, result table, figure-data input, manuscript claim or
retained negative control was changed.

The v0.3.4 scientific interpretation therefore remains exactly the rc1 interpretation.

## Release meaning

- rc1 = scientific/provenance freeze;
- rc2 = rc1 scientific content plus safer final-upload packaging.

The final-upload guard should only become READY after the human-input metadata and permanent
archive DOI are supplied.
