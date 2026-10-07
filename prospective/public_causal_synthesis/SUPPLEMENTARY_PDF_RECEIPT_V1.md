# Behavioral Ecology supplementary PDF receipt v1

## Status

**BUILD PASS / TEXT AUDIT PASS / ALL-PAGE RENDER PASS / VISUAL REVIEW PASS**

Authoritative workflow:
- workflow: `behavioral-ecology-supplementary-pdf-v1`
- run: **37598656753**
- job: **112717340258**
- source commit: **0775a5185208e59d170bee99cb9daacb2f1c8052**
- artifact ID: **11471922622**

Generated PDF:
`SUPPLEMENTARY_MATERIAL_V1.pdf`

PDF properties:
- pages: **7**
- bytes: **108,252**
- SHA256: **414f40314bbba8d15d28bb5ca0505fe29a0b95ec5ce368a5249b2d7f8e40bdb8**

GitHub artifact wrapper:
- bytes uploaded: **858,927**
- SHA256: **cadce1ef1c659e032983b272254aa06f0803b007e9024f326f17d905e97b7cfd**

## Automated checks

PASS:
- Supplementary Table S1 present;
- Supplementary Table S2 present;
- Supplementary Figures S1-S3 present;
- first-flight primary-failure wording present;
- wild 2/4 boundary present;
- exploratory-only wild H/V wording present;
- identifying development-repository tokens absent;
- all 7 pages rendered to PNG;
- extracted text successfully read from all pages.

## Independent local render verification

The workflow artifact was downloaded and the PDF was rendered independently with:

`/home/oai/skills/pdfs/scripts/render_pdf.py`

at 160 dpi.

Visual review of all seven rendered pages found:
- no clipped table edges;
- no overlapping text;
- no black-square glyph failures;
- no cut-off figure panels;
- no missing supplementary figures;
- readable landscape tables;
- figure captions retained;
- page numbering present.

Observed layout:
- pp.1-2: source/provenance and frozen-inference tables;
- p.3: provenance timeline;
- pp.4-5: developmental decomposition text/figure;
- p.6: exact-null-resolution figure;
- p.7: evidence-tier and cross-study-boundary methods/disclosure.

## Verdict

**PASS_SUPPLEMENTARY_PDF_FOR_HUMAN_SUBMISSION_REVIEW**

The scientific content is frozen by `SUPPLEMENTARY_MATERIAL_DRAFT_V1.md`.
Any later content edit requires rebuilding this PDF and refreshing this receipt.
