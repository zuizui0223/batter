# Behavioral Ecology submission readiness v1

Date checked: 2026-10-07.

## Current manuscript state

Working title:
**Individual organization remains detectable across acute perturbations in bats**

Current full draft:
`MANUSCRIPT_DRAFT_V1.md`

Approximate word counts:
- total Markdown manuscript: **5,270 words**;
- Introduction: **575**;
- Methods: **1,369**;
- Results: **983**;
- Discussion: **1,172**;
- Introduction + Methods + Results + Discussion: **4,099**.

Current QA:
- TODO markers: **0**;
- control-character corruption: **0**;
- main figure callouts present: **Fig. 1, Fig. 2A, Fig. 2B, Fig. 3, Fig. 4**;
- references working list populated;
- Data/Code Availability present;
- Analysis Provenance present;
- Ethics present;
- publication-overlap audit present;
- Movement Ecology Tadarida-only overlapping manuscript retired.

## Behavioral Ecology requirements already addressed

### Journal fit

**PASS**

The manuscript is empirical comparative behavioral ecology centered on:
- individual variation;
- behavioral plasticity;
- developmental environment;
- sensory/navigation perturbation;
- ecological consequence.

### Lay Summary

**DRAFT COMPLETE**

File:
`LAY_SUMMARY_V1.md`

Must remain <=75 words in final submission.

### Cover Page and Acknowledgements

**TEMPLATE COMPLETE; AUTHOR METADATA REQUIRED**

File:
`COVER_PAGE_AND_ACKNOWLEDGEMENTS_V1.md`

Remaining:
- author names;
- affiliations;
- corresponding-author address/phone/email;
- actual funding;
- actual conflict-of-interest statement;
- verified CRediT roles;
- human acknowledgements with permission.

### Cover letter

**DRAFT COMPLETE**

File:
`COVER_LETTER_BEHAVIORAL_ECOLOGY_V1.md`

Contains:
- scientific significance;
- iterative-synthesis transparency;
- dataset/manuscript-overlap disclosure;
- AI disclosure.

### Figures

**PASS — generated; alt text drafted**

Files:
- `FIGURE_1_CAUSAL_LAYERS_V1.svg`;
- `FIGURE_2A_FIRST_FLIGHT_FORMATION_V1.svg`;
- `FIGURE_2B_DEVELOPMENTAL_RANDOMIZATION_V1.svg`;
- `FIGURE_3_ACUTE_PERTURBATION_IDENTITY_V1.svg`;
- `FIGURE_4_PORTABILITY_AND_WILD_BOUNDARY_V1.svg`.

Figure captions:
`FIGURE_CAPTIONS_V1.md`.

Alt text:
`FIGURE_ALT_TEXT_V1.md`

Before final submission:
- check journal-preferred raster/vector formats and resolution;
- decide whether Fig. 2A/2B are combined into one multipanel figure in production.

### Data archiving

**SOURCE DATA PASS; ANALYSIS-ARCHIVE ANONYMIZATION BLOCKER**

All source data are already public.

However, the current analysis repository is identified as `zuizui0223/batter`.

Behavioral Ecology uses double-anonymized review and asks authors to anonymize manuscript, supplementary materials and data archive.

Required before submission:
1. create an anonymized review archive for analysis code/contracts/result receipts;
2. use an anonymous review URL/DOI in the manuscript;
3. replace it with the final identified public archive after acceptance or when journal policy permits.

Do not expose `zuizui0223` in the review manuscript.

### Supplementary material

**CONTENT DRAFT COMPLETE; PDF PACKAGING REMAINS**

Behavioral Ecology permits one Supplementary Material PDF if needed.

Content source:
`SUPPLEMENTARY_MATERIAL_DRAFT_V1.md`

Planned single supplement:
- Table S1 source/data/provenance ledger;
- Table S2 frozen endpoints/nulls/support rules;
- Figure S1 analysis-provenance timeline;
- Figure S2 developmental descriptive decompositions;
- Figure S3 exact-null resolution / small-n explanation.

Do not place executable code inside the PDF; code belongs in the review archive.

### Double-anonymized manuscript

**DRAFT COMPLETE; ANONYMOUS ARCHIVE URL REMAINS**

Anonymous file:
`MANUSCRIPT_ANONYMIZED_BEHAVIORAL_ECOLOGY_V1.md`

Checks:
- identified GitHub username absent;
- identified analysis-repository path absent;
- no author/affiliation metadata;
- source-study citations retained normally;
- review archive represented as `[ANONYMIZED_REVIEW_ARCHIVE_URL]`.

Remaining blocker:
replace the placeholder with a genuinely anonymized review archive before upload.

### Funding

**BLOCKER — AUTHOR INPUT REQUIRED**

Journal requires a separate Funding section.

### CRediT

**BLOCKER — AUTHOR INPUT REQUIRED**

Must reflect actual human contributions.

### AI disclosure

**DRAFT COMPLETE; FINAL HUMAN VERIFICATION REQUIRED**

OUP's current journal-author AI policy requires disclosure in both:
- cover letter;
- Acknowledgements;

and, where AI was integral to methodology, relevant Methods disclosure may also be appropriate.

Current draft disclosure identifies:
- tool: OpenAI ChatGPT;
- model: GPT-5.6 Sol during final synthesis;
- date window: September–October 2026;
- uses: literature triage, code review/drafting, analysis/provenance organization, figure-code drafting, substantial manuscript editing;
- human accountability/verification.

Before submission, the authors must verify:
- exact model/version wording;
- access dates;
- whether any other AI tools/models were used and must also be disclosed.

## Publication-overlap status

**PASS WITH DISCLOSURE**

Authoritative audit:
`PUBLICATION_OVERLAP_AUDIT_V1.md`.

Active manuscripts:
1. JAE vertical-individuality manuscript;
2. public causal synthesis.

Retired as separate submission:
- Movement Ecology Tadarida-only manuscript.

Source-specific PRs #73–#76 are analysis provenance, not separate article submissions.

Required:
- disclose overlapping public datasets and distinct endpoints in cover letter;
- cite/disclose the other active manuscript if public/accepted/submitted concurrently as journal policy requires.

## Scientific claim QA

### Confirmatory positive core

PASS:
- acute perturbation identity retention across four independent controlled systems;
- Rhino coarse-policy portability;
- Carollia external coarse-policy support.

### Formation boundary

PASS after provenance correction:
- monotonic first-flight formation primary = FAIL;
- predeclared late-history secondary = supported;
- recent-vs-early Q = post-primary diagnostic only;
- randomized enrichment history-carrier effect = FAIL;
- randomized enrichment total individualization = unsupported;
- randomized auditory-feedback total individualization = no difference.

### Wild boundary

PASS:
- frozen scalar field carrier gate = 2/4 FAIL;
- H/V post-outcome only.

## Remaining submission blockers

### Must resolve before upload

1. **Anonymous analysis archive**
2. **Author/affiliation/corresponding-author metadata**
3. **Funding statement**
4. **CRediT roles**
5. **Conflict-of-interest statement**
6. **Final AI disclosure verification**
7. **Single Supplementary PDF packaging, if used**
8. **Final reference-style conversion to Behavioral Ecology format**

### Strongly recommended

11. one external/internal human read focused on biological coherence rather than code;
12. one final cross-check that every manuscript number matches `MASTER_RESULTS_TABLE_V1.md`;
13. one cover-letter check against the submission status of the JAE manuscript.

## Current readiness verdict

**SCIENTIFIC DRAFT: READY FOR HUMAN COAUTHOR/PI REVIEW**

**JOURNAL UPLOAD: NOT YET READY**

The remaining blockers are packaging/anonymization/author metadata, not unresolved numerical analyses.
