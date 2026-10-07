# Anonymous DOCX visual QA receipt v1

## Status

**PASS — 42/42 RENDERED PAGES VISUALLY INSPECTED.**

Manuscript:
**Individual organization remains detectable across acute perturbations in bats**

Authoritative workflow:
`behavioral-ecology-complete-anonymous-docx-v1`

Latest guarded successful run:
- run: `37607682467`
- commit: `5cf47d5908414e9fc1c0ede390646ae71457a02d`
- artifact: `11475319930`

Previously visually inspected normalized build:
- run: `37607531802`
- commit: `df6d3efe04eea95c76281c8e069a37fe850c37fa`
- artifact: `11475940064`

## Build QA

The workflow successfully completed:

1. rebuild anonymous Markdown from current manuscript, Lay Summary and figure captions;
2. submission-format normalization;
3. anonymous-format guard;
4. Pandoc -> DOCX conversion;
5. journal-style DOCX formatting;
6. LibreOffice DOCX -> PDF conversion;
7. PDF -> 144-dpi PNG rendering;
8. automated page-dimension / nonblank-page checks.

Rendered manuscript length:
**42 pages**.

## Visual inspection

All pages 1–42 were inspected visually.

Checks:
- no clipped text;
- no overlapping text;
- no blank pages;
- no missing figure pages;
- no missing glyphs visible;
- no broken page geometry;
- continuous line numbering present;
- page numbering present;
- Lay Summary occupies the first page;
- title/abstract block occupies the second page;
- main text begins on page 3;
- references remain within margins;
- long DOI / URL strings wrap within page bounds;
- figure legends are present;
- all five main figure pages render cleanly.

## Conversion defect found and corrected before PASS

An earlier DOCX build exposed systematic Markdown-conversion defects:

- list items were flattened into body prose;
- simple equation blocks appeared as raw square-bracket notation;
- `P le 0.05` appeared instead of `P ≤ 0.05`.

Corrections were made upstream in
`build_complete_anonymous_text_v1.py`:

- explicit list-block boundaries;
- submission-safe plain equation rendering;
- Unicode inequality / degree notation;
- reference paragraphs normalized for hanging-indent styling;
- anonymous Markdown rebuilt from current source manuscript before every DOCX build.

The corrected build was then rerendered and reinspected.

## Latest-build equivalence check

The guarded latest build and the fully visually inspected normalized build differ at the DOCX/PDF byte level because office-document generation is not byte deterministic.

Therefore the rendered pages were compared directly.

Result:

- pages compared: **42**
- pages with any changed rendered pixel: **0**
- conclusion: **pixel-identical rendered output**

Thus the 42-page visual inspection applies exactly to the latest guarded successful build.

## Verdict

**PASS_COMPLETE_ANONYMOUS_DOCX_VISUAL_QA_V1**

The anonymous manuscript DOCX itself is no longer a submission blocker.

Remaining submission blockers are external/metadata packaging items such as:
- anonymized analysis archive;
- real author / affiliation metadata for the separate cover page;
- funding;
- CRediT;
- conflict-of-interest statement;
- final AI-disclosure verification;
- final journal-system packaging.

This receipt certifies layout/render quality only; scientific numerical provenance is separately guarded by:
- `MANUSCRIPT_NUMERICAL_AUDIT_V1.md`;
- `manuscript_evidence_guard_v1.py`.
