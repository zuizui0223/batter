# Integrated JAE submission readiness v1

## Decision

**Scientific analysis CLOSED. Submission route = integrated manuscript.**

The frozen v0.3.8 manuscript on `main` remains provenance only and is no longer the intended submission version.

## Canonical files

- Main manuscript: `manuscript/MANUSCRIPT_INTEGRATED_V1.md`
- Supporting Information: `manuscript/SUPPORTING_INFORMATION_INTEGRATED_V1.md`
- Title page: `manuscript/TITLE_PAGE_INTEGRATED_V1.md`
- Cover letter: `manuscript/COVER_LETTER_JAE_INTEGRATED_V1.md`
- Claim ledger: `manuscript/INTEGRATED_CLAIM_LEDGER_V1.md`
- Submission manifest: `manuscript/INTEGRATED_SUBMISSION_MANIFEST_V1.md`
- Future prediction contract: `post_freeze_extensions/ECOLOGICAL_CONTINGENCY_PREDICTION_CONTRACT_V1.md`
- Pteropus terrain audit: `post_freeze_extensions/pteropus_terrain_audit/TERRAIN_AUDIT_RESULT_V1.md`

## Journal-format checks

Checked against the Journal of Animal Ecology author guidelines on 2026-10-01.

- Research Article word limit: 8,500 words including title page, abstract, references, tables and figure legends; Supporting Information excluded.
- Current reviewer-facing main manuscript repository count: **7,803 words**; current title-page template: **151 words**; combined repository estimate: **7,954 words**, leaving approximately 546 words before the 8,500-word ceiling.
- Numbered English Abstract: **313 words**; limit 350.
- Keywords: **7**, alphabetically ordered; limit 8.
- Main manuscript has the required Introduction, Materials and Methods, Results, Discussion and References structure.
- Data/archive statement is present.
- Reviewer-facing manuscript scan finds no explicit project-owner name/repository identifier.
- Anonymous cover letter: **399 words**; journal limit 500.
- Supporting Information is separated from the journal word count (**2,437 words** in the current repository file).

A final journal-platform word count must be rechecked after author names, affiliations and other title-page metadata are inserted.

## Main/SI split

Moved to Supporting Information rather than deleted:

- historical conditional/marginal estimator details;
- direct pairwise self-identification;
- focal early/late and residual-map ceiling;
- focal AGL and biological-scale translation details;
- endpoint-neighbourhood exclusion details;
- full stationary-offset support gate and correction;
- descriptive individual centered profiles;
- detailed temporal-overlap summaries;
- full pipeline-calibration history.

Main text retains:

- common-cell estimator and permutation calibration;
- centered-shape primary result;
- one compact robustness summary;
- mechanism-localization synthesis;
- all four external frozen outcomes;
- Pteropus terrain audit;
- post-hoc ecological synthesis and frozen future prediction.

## Main figures

Figure generation is source-backed and does not introduce new analysis.

1. Figure 1 — inference ladder:
   `scripts/make_integrated_inference_ladder_figure_v1.py`
2. Figure 2 — original centered-shape result:
   `figures/integrated_centered_shape_v1.csv`
   `scripts/make_integrated_centered_shape_figure_v1.py`
3. Figure 3 — mechanism localization from frozen stress-test outputs:
   `figures/integrated_mechanism_localization_v1.csv`
   `scripts/make_integrated_mechanism_localization_figure_v1.py`
4. Figure 4 — external boundary + Pteropus terrain-adjusted diagnostic:
   `figures/integrated_external_boundary_v1.csv`
   `scripts/make_integrated_external_boundary_figure_v1.py`
5. Figure 5 — non-quantitative generated ecological hypothesis:
   `scripts/make_integrated_ecological_hypothesis_figure_v1.py`

Workflow:
`.github/workflows/integrated-main-figures-v1.yml`

## Claim ceilings locked

The submission must preserve all of the following:

- Pteropus historical external primary = n=4 prospective PASS under its separate programme.
- Pteropus terrain-adjusted diagnostic = excess +0.03231, p=0.0023; diagnostic, not a second replication.
- Pteropus terrain-only identity = excess +0.37887, p=0.0034.
- Nyctalus, Hipposideros and Myotis frozen primary FAILs remain visible.
- External PASS/FAIL outcomes are not pooled into a prevalence estimate.
- Three Phyllostomus panels are one species for ecological-synthesis counting.
- Resource anchoring × vertical opportunity is generated post hoc, not confirmed.
- The future >=8-source test may require new coordinated field data; it is not claimed to be immediately feasible from public archives.
- No attenuation ratio is interpreted as causal mediation.

## Data provenance completed

External source identifiers now include:

- Nyctalus noctula: Zenodo 10.5281/zenodo.7535030
- Hipposideros armiger / H. pratti: Dryad 10.5061/dryad.j0zpc86r1; source paper DOI 10.1111/1365-2435.70088
- Myotis vivesi: Movebank 10.5441/001/1.kk3bg2f4
- Pteropus poliocephalus: Movebank 10.5441/001/1.5bd6pq55

## Remaining work is packaging only

Allowed:
- visually inspect rendered Figures 1–5 and adjust typography/layout without changing data;
- fill final author, affiliation, contribution, funding and conflict fields on the separate title page;
- final reference-format and spelling pass;
- create a review-safe/permanent code archive;
- produce the journal upload files.

Not allowed:
- any new source search;
- any new vertical outcome opening;
- any estimator/threshold/bin/grid change;
- any current-system ecological recoding or retrospective predictor test;
- any new mechanism analysis intended to strengthen the story.

## Current submission assessment

**Scientifically ready; packaging in finalization.**

The integrated paper is now shorter, more falsifiable and more ecologically informative than v0.3.8 while preserving all negative and boundary evidence.

## Dataset citation check

All ten public tracking datasets used in the integrated analysis now have full dataset citations in the manuscript's **Data sources** section, in addition to the Data and code availability statement. This satisfies the journal requirement to cite archived datasets with persistent identifiers rather than listing DOIs only.
