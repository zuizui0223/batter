# Behavioral Ecology submission requirements audit v1

Date checked: 2026-10-07.

Official source:
`https://academic.oup.com/beheco/pages/information_for_authors`

## Verified current requirements

### Double-anonymized review

Required:
- manuscript text anonymized;
- supplementary material anonymized;
- data/archive materials used for review anonymized;
- separate cover page + acknowledgements not for review.

Current programme:
- `COMPLETE_ANONYMOUS_TEXT_V1.md` generated from the current full manuscript;
- `COVER_PAGE_AND_ACKNOWLEDGEMENTS_V1.md` separate.

### Complete Anonymous Text order

Required order:
1. lay summary;
2. title and abstract;
3. text;
4. references;
5. figure legends;
6. tables/table legends;
7. figures.

Current programme:
- deterministic builder: `build_complete_anonymous_text_v1.py`;
- format/anonymization guard: `anonymous_submission_guard_v1.py`.

Figures may be uploaded separately at initial submission, so the anonymous text can terminate after figure legends if figure files are separately supplied.

### Length gates

Journal requirements:
- title ideally <=100 characters;
- abstract <=250 words;
- lay summary <=75 words.

Current:
- title = 77 characters;
- abstract = 197 words;
- lay summary = 71 words.

PASS.

### Funding

Required as a separate `Funding` section.

Human-author input still required.

### Conflict of interest

Submission requires an explicit conflict statement, including “none declared” if true.

Human-author verification required.

### Supplementary material

At most one Supplementary Material file is recommended/accepted for the ancillary tables/figures/text used here.

Current content draft:
`SUPPLEMENTARY_MATERIAL_DRAFT_V1.md`.

Still needed if supplement is submitted:
- render to one anonymous PDF;
- add manuscript citation placeholder at top;
- final legibility check.

### Data repository

The journal requires a public data repository link at submission and states that GitHub is not an acceptable permanent data repository.

Current source-data situation:

- Harten: Mendeley DOI — PASS;
- Rachum: Mendeley DOI — PASS;
- Elie: Mendeley DOI — PASS;
- Diebold: Zenodo DOI — PASS;
- Aharon: Mendeley DOI — PASS;
- Foskolos: Zenodo + Dryad DOI — PASS;
- Teshima: Figshare public dataset — PASS;
- Eveland/Carollia: source article deposits trial data/code on GitHub only — permanence gap for this journal;
- Taub/Yovel: source article deposits data on public Dropbox only — permanence/licensing gap for this journal.

Carollia repository license:
- CC0 1.0;
- exact source subset may therefore be mirrored in the final permanent review/publication archive.

Taub:
- source paper is CC BY 4.0;
- dataset itself is linked only through Dropbox and an explicit dataset redistribution license has not been verified in this programme;
- do not silently mirror raw Dropbox files without permission/licensing confirmation.

Possible safe submission routes for Taub:
1. obtain permission / dataset-license confirmation and mirror the exact used files in the permanent repository;
2. ask the Behavioral Ecology editorial office whether the original source-public Dropbox plus reproducible extraction script satisfies the secondary-reanalysis data requirement;
3. if required by the editor, obtain the data directly from the source authors under a redistributable archive.

### Analysis/code archive

Behavioral Ecology does not require code, but it may be included.

For this manuscript, a permanent anonymous review archive is strongly recommended because the evidentiary contribution depends on:
- frozen contracts;
- support rules;
- exact/randomization logic;
- positive and negative result receipts;
- provenance corrections.

GitHub alone is not suitable as the final archive.

Recommended workflow:
- generate a sanitized review bundle automatically;
- upload to an anonymizable DOI-capable repository / review system;
- use anonymous review URL in `COMPLETE_ANONYMOUS_TEXT_V1.md`;
- after acceptance, replace with permanent identified DOI.

### AI disclosure

Current OUP/Behavioral Ecology requirement:
- disclose generative-AI use in the cover letter;
- disclose it in Methods or Acknowledgements;
- include tool/version, use description, and author direction/verification.

Current files:
- full disclosure in `COVER_LETTER_BEHAVIORAL_ECOLOGY_V1.md`;
- full disclosure in `COVER_PAGE_AND_ACKNOWLEDGEMENTS_V1.md`;
- anonymous manuscript contains a non-identifying provenance statement.

Final human verification of exact tool/model/date wording is still required.

### Reference formatting

Behavioral Ecology uses CSE name-year references.

However, initial submissions are format-free.

Therefore:
- every listed reference must be cited in the text — required now;
- perfect journal punctuation/style conversion is **not** a submission blocker at initial submission.

The current manuscript has been updated to include author-year citations for all working-list references.

## Remaining blockers after this audit

### Human-only

1. author names and affiliations;
2. corresponding-author contact details;
3. Funding statement;
4. Conflict of Interest statement;
5. verified CRediT roles;
6. acknowledgements / permissions;
7. final AI-disclosure verification;
8. decision on Taub raw-data permanence / redistribution.

### Technical/package

9. anonymous permanent review/data archive URL;
10. one Supplementary PDF if supplement is retained;
11. final word-processor/PDF rendering with page and continuous line numbers;
12. replace `[ANONYMIZED_REVIEW_ARCHIVE_URL]` before upload.

## Current verdict

**SCIENTIFIC / EVIDENCE QA: PASS**

**ANONYMOUS TEXT CONTENT: PASS, subject to current CI guard**

**JOURNAL UPLOAD: BLOCKED BY ARCHIVE + HUMAN METADATA/POLICY INPUT**
