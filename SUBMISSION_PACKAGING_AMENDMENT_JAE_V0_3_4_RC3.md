# JAE v0.3.4 rc3 packaging amendment

Date: 2026-09-27

## Release role

RC3 is a **packaging-only** successor to RC2.

Scientific-content commit remains:

`29c18a9f3c29ee2f561e0f7d28cd340fcc55aa22`

RC1 scientific/provenance baseline remains:

`1f28e833402d3fdd7dd6ce274e5392bf253fee84`

RC2 packaging baseline remains:

`00de1efd01d2384cd12119e0a593adb2fae25762`

## What RC3 fixes

1. The generated JAE review manuscript now replaces the author-identifying
   `zuizui0223/batter` repository string with an anonymized placeholder.
2. A dedicated review-anonymity guard runs before PDF rendering.
3. The non-anonymous title page now uses the journal's “Data availability statement” heading and
   lists all six Movebank source DOIs.
4. The final-upload gate requires a **distinct** permanent code/provenance archive DOI rather than
   accepting one of the already-public source-data DOIs.
5. A Zenodo/GitHub release-readiness gate now blocks release when software licensing or final
   citation metadata are absent.
6. A dated JAE initial-submission compliance audit is included.

## Current release blockers

The package is scientifically ready but archival release is intentionally blocked by:

- no explicit repository software `LICENSE`;
- no final `CITATION.cff` or `.zenodo.json`;
- final author / affiliation / corresponding-author metadata;
- CRediT, funding, acknowledgements and conflict declaration;
- Zenodo GitHub integration must be enabled by the repository owner;
- permanent archive DOI must then be inserted into the title page.

## Scientific freeze

No dataset, public-source universe, admission rule, endpoint, permutation design, horizontal grain,
exclusion radius, vertical bin, smoothing rule, result table, figure-data input, ecological claim,
or retained negative control changed in RC3.
