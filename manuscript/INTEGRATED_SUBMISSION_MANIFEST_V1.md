# Integrated JAE submission manifest v1

## Canonical submission files

- Main manuscript: `manuscript/MANUSCRIPT_INTEGRATED_V1.md`
- Supporting Information: `manuscript/SUPPORTING_INFORMATION_INTEGRATED_V1.md`
- Claim ledger: `manuscript/INTEGRATED_CLAIM_LEDGER_V1.md`
- Figure/structure plan: `post_freeze_extensions/INTEGRATED_FIGURE_PATCH_PLAN_V1.md`
- Future ecological prediction contract: `post_freeze_extensions/ECOLOGICAL_CONTINGENCY_PREDICTION_CONTRACT_V1.md`
- Pteropus terrain audit result: `post_freeze_extensions/pteropus_terrain_audit/TERRAIN_AUDIT_RESULT_V1.md`

## Main-text status

Numbered English Abstract: **333 words** (JAE limit: 350).

Repository word count after SI split: **7,752 words** for the current Markdown main document, including references and figure legends but before a separate title page is added.

Journal of Animal Ecology Research Article limit checked on 2026-10-01: 8,500 words including title page, abstract, main text, references, tables and figure legends; Supporting Information is excluded.

## Scientific freeze

No additional scientific analysis is authorized for this manuscript.

Permitted work:
- shorten or clarify wording without changing claims;
- move already reported material between main text and SI;
- render/reformat existing figures;
- correct references, labels, typographical errors and submission metadata;
- anonymize files for double-anonymized review;
- build the final archive/release from already frozen evidence.

Not permitted:
- search for another external source;
- open a new response;
- change an estimator, threshold, grid, bin or source gate;
- try alternative ecological codings on the current opened systems;
- add a new mechanism family to improve the story;
- reinterpret the Pteropus attenuation ratio as causal mediation.

## Remaining submission-production tasks

1. render and visually inspect Figures 1–5;
2. ensure Figures 1–3 use existing frozen results only;
3. add/anonymize the separate title page;
4. final citation/reference cross-check;
5. final word-count check after title page;
6. package manuscript + SI + figures and mint/freeze the submission archive.

This manifest supersedes v0.3.8 as the intended JAE submission route while preserving v0.3.8 on `main` as historical frozen provenance.

## Dataset citation check

All ten public tracking datasets used in the integrated analysis now have full dataset citations in the manuscript's **Data sources** section, in addition to the Data and code availability statement. This satisfies the journal requirement to cite archived datasets with persistent identifiers rather than listing DOIs only.

- Methods and Data availability both point to the **Data sources** section; ten archived tracking datasets have full persistent-identifier citations.

- Rendered Figure 1–5 SVG files are committed under `figures/integrated_*.svg`; figure source tables and generation scripts remain versioned alongside them.
- Reviewer-facing main manuscript and cover letter contain zero occurrences of the internal decision terms `frozen`, `PASS`, or `FAIL`; the translation policy is documented in `manuscript/JAE_TERMINOLOGY_MAP_V1.md`.
