#!/usr/bin/env python3
"""Build and verify the single Behavioral Ecology Supplementary Material PDF v1."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import fitz
import markdown
from weasyprint import HTML, CSS

LAYOUT_REVISION = 2  # force rebuild after supplementary-figure layout correction

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"prospective"/"public_causal_synthesis"/"SUPPLEMENTARY_MATERIAL_DRAFT_V1.md"
FIGDIR=ROOT/"figures"/"public_causal_supplement"
OUTDIR=ROOT/"submission"/"public_causal"
PDF=OUTDIR/"SUPPLEMENTARY_MATERIAL_V1.pdf"
RECEIPT=OUTDIR/"SUPPLEMENTARY_MATERIAL_V1_RECEIPT.json"
PREVIEW=OUTDIR/"supplement_preview"

FIGS={
    "S1":FIGDIR/"FIGURE_S1_PROVENANCE_TIMELINE_V1.svg",
    "S2":FIGDIR/"FIGURE_S2_DEVELOPMENTAL_DECOMPOSITIONS_V1.svg",
    "S3":FIGDIR/"FIGURE_S3_EXACT_NULL_RESOLUTION_V1.svg",
}

FORBIDDEN=[
    "zuizui0223",
    "github.com/zuizui0223",
    "[ANONYMIZED_REVIEW_ARCHIVE_URL]",
]

def insert_figures(md:str)->str:
    repl={
        "See Supplementary Material Figure S1.":
            "See Supplementary Material Figure S1.\n\n"
            f"<div class='figure figure-s1'><img src='{FIGS['S1'].as_uri()}'/><p><b>Supplementary Material Figure S1.</b> Analysis-provenance timeline.</p></div>",
        "See Supplementary Material Figure S2.":
            "See Supplementary Material Figure S2.\n\n"
            f"<div class='figure figure-s2'><img src='{FIGS['S2'].as_uri()}'/><p><b>Supplementary Material Figure S2.</b> Developmental descriptive decompositions.</p></div>",
        "See Supplementary Material Figure S3.":
            "See Supplementary Material Figure S3.\n\n"
            f"<div class='figure figure-s3'><img src='{FIGS['S3'].as_uri()}'/><p><b>Supplementary Material Figure S3.</b> Exact-null resolution and biological sample size.</p></div>",
    }
    for a,b in repl.items():
        if a not in md:
            raise SystemExit(f"STOP supplement figure insertion anchor missing: {a}")
        md=md.replace(a,b)
    return md

def main():
    OUTDIR.mkdir(parents=True,exist_ok=True)
    PREVIEW.mkdir(parents=True,exist_ok=True)
    for p in FIGS.values():
        if not p.exists():
            raise SystemExit(f"STOP supplementary figure missing: {p}")

    md=insert_figures(SRC.read_text(encoding="utf-8"))

    # Pandoc/Markdown-style list safety: a prose line ending in ':' must be
    # separated from a following dash-list by a blank line, otherwise some
    # renderers flatten the list into body prose.
    lines=md.splitlines()
    for i in range(len(lines)-1):
        if lines[i].strip().endswith(":") and re.match(r"^\s*-\s+\S", lines[i+1]):
            raise SystemExit(
                f"STOP supplement colon-list boundary at source line {i+1}: {lines[i]!r}"
            )

    html_body=markdown.markdown(
        md,
        extensions=["tables","fenced_code","sane_lists"],
        output_format="html5",
    )

    css="""
    @page {
      size: A4 landscape;
      margin: 12mm 14mm 14mm 14mm;
      @bottom-right { content: "Supplementary Material - " counter(page); font-size: 8pt; color: #555; }
    }
    body {
      font-family: Arial, Helvetica, sans-serif;
      font-size: 9.2pt;
      line-height: 1.32;
      color: #111;
    }
    h1 { font-size: 18pt; margin: 0 0 8pt 0; page-break-after: avoid; }
    h2 { font-size: 13pt; margin-top: 14pt; page-break-after: avoid; }
    h3 { font-size: 11pt; margin-top: 11pt; page-break-after: avoid; }
    p { margin: 4pt 0 7pt 0; }
    ul, ol { margin-top: 3pt; margin-bottom: 7pt; }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 6pt 0 10pt 0;
      table-layout: fixed;
      font-size: 6.9pt;
      page-break-inside: auto;
    }
    th, td {
      border: 0.5pt solid #999;
      padding: 3pt 3.5pt;
      vertical-align: top;
      overflow-wrap: anywhere;
    }
    th { font-weight: 700; }
    tr { page-break-inside: avoid; }
    .figure {
      page-break-inside: avoid;
      break-inside: avoid;
      text-align: center;
      margin: 7pt 0 10pt 0;
    }
    .figure img {
      max-width: 96%;
    }
    .figure-s1 {
      page-break-before: auto;
    }
    .figure-s1 img {
      max-height: 128mm;
    }
    .figure-s2 {
      page-break-before: always;
    }
    .figure-s2 img {
      max-height: 158mm;
    }
    .figure-s3 {
      page-break-before: auto;
    }
    .figure-s3 img {
      max-height: 118mm;
    }
    .figure p {
      font-size: 8.5pt;
      text-align: left;
      margin-left: 2%;
      margin-right: 2%;
    }
    code { font-family: "Courier New", monospace; font-size: 8pt; }
    blockquote { margin-left: 10pt; border-left: 2pt solid #aaa; padding-left: 8pt; }
    """

    html=f"""<!doctype html>
    <html><head><meta charset='utf-8'><title>Supplementary Material</title></head>
    <body>{html_body}</body></html>"""

    HTML(string=html,base_url=str(ROOT)).write_pdf(
        str(PDF),
        stylesheets=[CSS(string=css)],
    )

    doc=fitz.open(PDF)
    if doc.page_count<4:
        raise SystemExit(f"STOP unexpected supplement page count: {doc.page_count}")
    text="\n".join(page.get_text("text") for page in doc)
    for token in FORBIDDEN:
        if token.lower() in text.lower():
            raise SystemExit(f"STOP identifying/internal token in supplement PDF: {token!r}")
    for token in [
        "Supplementary Table S1",
        "Supplementary Table S2",
        "Supplementary Material Figure S1",
        "Supplementary Material Figure S2",
        "Supplementary Material Figure S3",
        "Evidence-tier rules",
        "Cross-study synthesis boundary",
    ]:
        if token not in text:
            raise SystemExit(f"STOP expected supplement content missing from PDF text: {token!r}")

    for old in PREVIEW.glob("*.png"):
        old.unlink()
    pages=sorted(set([0,doc.page_count//2,doc.page_count-1]))
    preview_files=[]
    for idx in pages:
        page=doc.load_page(idx)
        pix=page.get_pixmap(matrix=fitz.Matrix(1.4,1.4),alpha=False)
        name=f"PAGE_{idx+1:03d}.png"
        p=PREVIEW/name
        pix.save(p)
        preview_files.append(name)
    doc.close()

    sha=hashlib.sha256(PDF.read_bytes()).hexdigest()
    receipt={
        "version":1,
        "pdf":str(PDF.relative_to(ROOT)),
        "sha256":sha,
        "bytes":PDF.stat().st_size,
        "pages":len(fitz.open(PDF)),
        "preview_files":preview_files,
        "forbidden_token_scan":"PASS",
        "required_content_scan":"PASS",
    }
    RECEIPT.write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,indent=2))

if __name__=="__main__":
    main()
