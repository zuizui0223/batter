#!/usr/bin/env python3
"""Render double-spaced, page- and line-numbered anonymous manuscript review PDF.

Consumes the version-controlled Complete Anonymous Text draft. It does not alter
scientific claims, create source data or certify a journal-ready archive.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE=Path(__file__).resolve().parent
SOURCE=HERE/"COMPLETE_ANONYMOUS_TEXT_DRAFT_V1.md"
OUT=HERE/"build"/"COMPLETE_ANONYMOUS_TEXT_REVIEW_PROOF_V1.pdf"
OUT.parent.mkdir(parents=True,exist_ok=True)
NORMAL=Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
BOLD=Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
if NORMAL.exists() and BOLD.exists():
    pdfmetrics.registerFont(TTFont("ReviewerSans",str(NORMAL)))
    pdfmetrics.registerFont(TTFont("ReviewerSansBold",str(BOLD)))
    textfont,boldfont="ReviewerSans","ReviewerSansBold"
else:
    textfont,boldfont="Helvetica","Helvetica-Bold"

PAGE_W,PAGE_H=A4
MARGIN_LEFT,MARGIN_RIGHT=64,45
LINE_X=34
TEXT_W=PAGE_W-MARGIN_LEFT-MARGIN_RIGHT
TOP=PAGE_H-60
BOTTOM=57
DOUBLE_LEADING=21.0
COLOR=colors.HexColor("#25323C")
MUTED=colors.HexColor("#6D7D8A")

def clean(text: str) -> str:
    text=re.sub(r"\[([^\]]+)\]\([^)]+\)",r"\1",text)
    text=re.sub(r"\*\*([^*]+)\*\*",r"\1",text)
    text=re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)",r"\1",text)
    text=re.sub(r"\x60([^\x60]+)\x60",r"\1",text)
    text=text.replace("\\(","(").replace("\\)",")")
    return text.replace("  "," ").strip()

def wrap_words(text: str,font: str,size: float)->list[str]:
    words=text.split()
    lines=[]
    buf=""
    def measure(x):
        return pdfmetrics.stringWidth(x,font,size)
    for token in words:
        if measure(token)>TEXT_W:
            if buf:
                lines.append(buf)
                buf=""
            part=""
            for ch in token:
                if part and measure(part+ch)>TEXT_W:
                    lines.append(part)
                    part=ch
                else:
                    part+=ch
            if part:buf=part
            continue
        candidate=(buf+" "+token).strip()
        if buf and measure(candidate)>TEXT_W:
            lines.append(buf)
            buf=token
        else:
            buf=candidate
    if buf:lines.append(buf)
    return lines or [""]

def render():
    source=SOURCE.read_text(encoding="utf8")
    assert source.startswith("## Lay Summary")
    assert source.index("## References")<source.index("## Figure legends")
    assert "ANONYMIZED_REVIEW_ARCHIVE_URL" in source
    for forbidden in ["zuizui0223","release/jae","prospective/public-causal-synthesis"]:
        assert forbidden not in source,forbidden
    c=canvas.Canvas(str(OUT),pagesize=A4,pageCompression=1,
        pageTitle="Persistent individuality - anonymous review proof",
        pageAuthor="Anonymous manuscript")
    number=0
    page=0
    y=TOP
    def start():
        nonlocal y,page
        page+=1
        y=TOP
        c.setFillColor(MUTED)
        c.setFont(textfont,7.5)
        c.drawString(MARGIN_LEFT,PAGE_H-35,"BEHAVIORAL ECOLOGY | COMPLETE ANONYMOUS TEXT — WORKING PROOF")
        c.line(MARGIN_LEFT,PAGE_H-41,PAGE_W-MARGIN_RIGHT,PAGE_H-41)
        c.drawRightString(PAGE_W-MARGIN_RIGHT,30,f"Page {page}")
        c.drawString(MARGIN_LEFT,30,"For coauthor review only; anonymous data archive link is pending.")
    def next_line(phrase,font,size):
        nonlocal y,number
        if y< BOTTOM+DOUBLE_LEADING:
            c.showPage()
            start()
        number+=1
        c.setFillColor(MUTED)
        c.setFont(textfont,7.5)
        c.drawRightString(LINE_X+18,y+1,str(number))
        c.setFillColor(COLOR)
        c.setFont(font,size)
        c.drawString(MARGIN_LEFT,y,phrase)
        y-=DOUBLE_LEADING
    start()
    paragraph=[]
    def flush_paragraph():
        nonlocal y
        if not paragraph:
            return
        joined=" ".join(paragraph)
        for row in wrap_words(clean(joined),textfont,10.5):
            next_line(row,textfont,10.5)
        paragraph.clear()
        y-=8
    for line in source.splitlines():
        l=line.strip()
        if not l:
            flush_paragraph()
            continue
        if l.startswith("#"):
            flush_paragraph()
            level=len(l)-len(l.lstrip("#"))
            title=clean(l[level:].strip())
            if y< BOTTOM+DOUBLE_LEADING*4:
                c.showPage()
                start()
            size=13 if level==1 else 11.2
            for row in wrap_words(title,boldfont,size):
                next_line(row,boldfont,size)
            y-=8
        elif l.startswith("- "):
            flush_paragraph()
            for row in wrap_words("• "+clean(l[2:]),textfont,10.5):
                next_line(row,textfont,10.5)
            y-=5
        elif l.startswith("|"):
            flush_paragraph()
            for row in wrap_words(clean(l),textfont,9):
                next_line(row,textfont,9)
        else:
            paragraph.append(l)
    flush_paragraph()
    c.save()
    assert OUT.stat().st_size>10000
    print("CREATED",OUT,"pages",page,"numbered_lines",number,"bytes",OUT.stat().st_size)

if __name__=="__main__":
    render()
