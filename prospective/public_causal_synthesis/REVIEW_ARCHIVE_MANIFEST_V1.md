# Anonymized review archive manifest v1

## Purpose

Build a double-anonymized, reviewer-facing package without Git metadata or identified repository URLs.

This package is a **curated review archive**, not a full clone of the working repository.

## Included manuscript-facing files

- `MANUSCRIPT_ANONYMIZED_BEHAVIORAL_ECOLOGY_V1.md`
- `SUPPLEMENTARY_MATERIAL_DRAFT_V1.md`
- `FIGURE_CAPTIONS_V1.md`
- `FIGURE_ALT_TEXT_V1.md`
- `LAY_SUMMARY_V1.md`

## Included evidence/provenance files

- `MASTER_RESULTS_TABLE_V1.md`
- `EVIDENCE_MATRIX_V1.md`
- `MANUSCRIPT_NUMERICAL_AUDIT_V1.md`
- `REVIEWER_RISK_AUDIT_V1.md`
- `PUBLICATION_OVERLAP_AUDIT_V1.md`
- `PUBLIC_DATA_CAUSAL_CEILING_V1.md`
- `PUBLIC_FORMATION_SOURCE_SCREEN_CLOSEOUT_V1.md`

## Included executable manuscript-level code

- `plot_synthesis_figures_v1.py`
- `figure_evidence_guard_v1.py`
- `manuscript_evidence_guard_v1.py`

## Included figures

- `FIGURE_1_CAUSAL_LAYERS_V1.svg`
- `FIGURE_2A_FIRST_FLIGHT_FORMATION_V1.svg`
- `FIGURE_2B_DEVELOPMENTAL_RANDOMIZATION_V1.svg`
- `FIGURE_3_ACUTE_PERTURBATION_IDENTITY_V1.svg`
- `FIGURE_4_PORTABILITY_AND_WILD_BOUNDARY_V1.svg`

## Source-data index

The archive builder creates `SOURCE_DATA_AND_RESULT_INDEX.md` containing:
- public source citation;
- public DOI/archive identifier;
- biological n;
- frozen endpoint;
- authoritative result used in the manuscript;
- evidence tier.

It deliberately does not include working Git branch names or identified repository URLs.

## Excluded

- Git history / `.git`;
- non-anonymous cover page;
- cover letter;
- acknowledgements with author metadata;
- author/affiliation templates;
- identified repository links;
- source-specific exploratory files not used in the manuscript;
- superseded analysis drafts.

## Anonymization stop rule

The build fails if any packaged text file contains:
- the working repository username;
- the working repository name in an identified GitHub URL;
- a direct identified GitHub repository URL;
- a non-anonymous manuscript path that is not intended for review.

The archive is intended to be downloaded and uploaded to the journal or an anonymous review host by the authors.


## Evidence-hierarchy synchronization

The review archive must be rebuilt after any change to:
- the Harten first-flight evidence hierarchy;
- manuscript numerical provenance;
- the wild 2/4 bridge boundary;
- the Rhino/Carollia portability ledger.

Current frozen hierarchy:
1. Harten monotonic formation primary = **FAIL**;
2. Harten late-history = **predeclared secondary supported**;
3. recent-vs-earliest Q = **post-primary diagnostic only**;
4. Rachum randomized history-carrier treatment effect = **FAIL**;
5. wild scalar carrier bridge = **2/4 FAIL**;
6. wild H/V = **exploratory only**;
7. no standalone Rhino held-out-environment p=0.0002 is retained in the submission package.

The packaged `MANUSCRIPT_NUMERICAL_AUDIT_V1.md` is the authoritative transcription map.
