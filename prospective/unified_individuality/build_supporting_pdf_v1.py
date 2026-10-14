#!/usr/bin/env python3
"""Produce one INTERNAL review-only PDF from the integrated SI draft."""
from __future__ import annotations
import html, re, sys
from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, LongTable, TableStyle, KeepTogether, CondPageBreak
from svglib.svglib import svg2rlg

ROOT=Path(__file__).resolve().parent
ANONYMOUS="--anonymous" in sys.argv
SOURCE=ROOT / ("SUPPORTING_INFORMATION_ANONYMOUS_DRAFT_V1.md" if ANONYMOUS else "SUPPORTING_INFORMATION_DRAFT_V1.md")
OUT=ROOT / "build" / ("SUPPLEMENTARY_MATERIAL_ANONYMOUS_DRAFT_V1.pdf" if ANONYMOUS else "SUPPLEMENTARY_MATERIAL_INTERNAL_DRAFT_V1.pdf")
OUT.parent.mkdir(parents=True,exist_ok=True)
FONT=Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
BOLD=Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
if FONT.exists() and BOLD.exists():
    pdfmetrics.registerFont(TTFont("TextSans",str(FONT)))
    pdfmetrics.registerFont(TTFont("TextSansBold",str(BOLD)))
    pdfmetrics.registerFontFamily("TextSans",normal="TextSans",bold="TextSansBold")
    normal,bold="TextSans","TextSansBold"
else:
    normal,bold="Helvetica","Helvetica-Bold"
ink=colors.HexColor("#213447")
light=colors.HexColor("#F1F5F8")
rule=colors.HexColor("#D8E0E5")
pageW,pageH=landscape(A4)
margin=31
usable=pageW-2*margin
styles={
 "h1":ParagraphStyle("h1",fontName=bold,fontSize=13,leading=18,spaceBefore=6,spaceAfter=10,textColor=ink),
 "h2":ParagraphStyle("h2",fontName=bold,fontSize=10.3,leading=13.5,spaceBefore=12,spaceAfter=8,textColor=ink,keepWithNext=True),
 "h3":ParagraphStyle("h3",fontName=bold,fontSize=9,leading=12,spaceBefore=10,spaceAfter=6,textColor=ink,keepWithNext=True),
 "p":ParagraphStyle("p",fontName=normal,fontSize=8.1,leading=11.7,spaceAfter=5,textColor=ink),
 "td":ParagraphStyle("td",fontName=normal,fontSize=6.25,leading=8.0,textColor=ink,wordWrap="CJK"),
 "th":ParagraphStyle("th",fontName=bold,fontSize=6.5,leading=8.4,textColor=ink,wordWrap="CJK")
}
def fmt(x):
    x=html.escape(x.strip())
    x=re.sub(r"\[([^\]]+)\]\([^)]+\)",r"\1",x)
    x=re.sub(r"\*\*([^*]+)\*\*",r"<b>\1</b>",x)
    x=re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)",r"<i>\1</i>",x)
    x=re.sub(r"\x60([^\x60]+)\x60",r"\1",x)
    return x
def iscell(x):
    t=x.strip()
    return t.startswith("|") and t.endswith("|")
def draw_table(lines):
    rows=[[x.strip() for x in line.strip().strip("|").split("|")] for line in lines]
    rows=[r for r in rows if not all(re.fullmatch(r":?-{3,}:?",c or "") for c in r)]
    if not rows:return []
    n=max(map(len,rows))
    rows=[r+[""]*(n-len(r)) for r in rows]
    col_first=usable*(.22 if n<=5 else .16)
    widths=[col_first]+[(usable-col_first)/(n-1)]*(n-1)
    data=[[Paragraph(fmt(cell),styles["th" if i==0 else "td"]) for cell in row] for i,row in enumerate(rows)]
    tab=LongTable(data,colWidths=widths,repeatRows=1,splitByRow=1,hAlign="LEFT")
    commands=[
      ("BACKGROUND",(0,0),(-1,0),light),
      ("VALIGN",(0,0),(-1,-1),"TOP"),
      ("LINEBELOW",(0,0),(-1,0),.6,rule),
      ("LINEBELOW",(0,1),(-1,-1),.25,rule),
      ("LEFTPADDING",(0,0),(-1,-1),4),
      ("RIGHTPADDING",(0,0),(-1,-1),4),
      ("TOPPADDING",(0,0),(-1,-1),4),
      ("BOTTOMPADDING",(0,0),(-1,-1),4),
    ]
    for row in range(2,len(data),2):
        commands.append(("BACKGROUND",(0,row),(-1,row),colors.HexColor("#FAFBFC")))
    tab.setStyle(TableStyle(commands))
    tab.spaceBefore=5
    tab.spaceAfter=9
    # Keep short source tables intact. Long tables may split with a repeated header.
    return [KeepTogether([tab])] if len(data)<=8 else [tab]
def decorate(c,doc):
    c.saveState()
    c.setStrokeColor(rule)
    c.line(margin,pageH-26,pageW-margin,pageH-26)
    c.setFillColor(colors.HexColor("#667786"))
    c.setFont(normal,6.5)
    c.drawString(margin,pageH-20,"UNIFIED BAT INDIVIDUALITY | "+("ANONYMOUS SI DRAFT" if ANONYMOUS else "INTERNAL SUPPORTING INFORMATION DRAFT"))
    c.drawRightString(pageW-margin,17,f"Page {doc.page}")
    c.restoreState()
def build():
    source=SOURCE.read_text(encoding="utf-8")
    markers=(["Supplementary Table S6","Supplementary Table S8","Supplementary Methods S13","Supplementary Figure S1","post-outcome"] if ANONYMOUS
             else ["Supplementary Table U6","Supplementary Table U8","Supplementary Methods U13","Supplementary Figure S1","post-outcome"])
    for x in markers:
        assert x.lower() in source.lower(),f"Missing mandatory SI section: {x}"
    blocks=[]
    lines=source.splitlines()
    i=0
    paragraph=[]
    def flush():
        if paragraph:
            t=" ".join(p.strip() for p in paragraph)
            if t:blocks.append(Paragraph(fmt(t),styles["p"]))
            paragraph.clear()
    while i<len(lines):
        line=lines[i].strip()
        if not line:
            flush();i+=1;continue
        if line.startswith("!["):
            flush()
            found=re.fullmatch(r"!\[([^\]]+)\]\((figures/[a-zA-Z0-9_./-]+\.svg)\)",line)
            assert found is not None,f"Unexpected SI figure link: {line}"
            relative=found.group(2)
            assert relative=="figures/FIGURE_S1_WITHIN_COHORT_VERTICAL_SHAPE_OVERLAP_V1.svg"
            svgfile=ROOT/relative
            assert svgfile.is_file(),f"Missing supplement image: {svgfile}"
            drawing=svg2rlg(str(svgfile))
            assert drawing is not None and drawing.width>100 and drawing.height>100
            assert drawing.width<=usable, "Supplementary vector exceeds PDF content width"
            drawing.hAlign="CENTER"
            blocks.append(CondPageBreak(drawing.height+18))
            blocks.append(drawing)
            blocks.append(Spacer(1,10))
            i+=1
            continue
        if iscell(line):
            flush();group=[]
            while i<len(lines) and iscell(lines[i]):
                group.append(lines[i]);i+=1
            blocks.extend(draw_table(group));continue
        if line.startswith("#"):
            flush();level=len(line)-len(line.lstrip("#"))
            # Move table headings together with their next table header/first rows.
            if line[level:].strip().startswith(("Supplementary Table U9.", "Supplementary Table S9.")):
                # Keep the cohort-imbalance heading and its first numerical table together.
                blocks.append(CondPageBreak(385))
            elif line[level:].strip().startswith("Supplementary Table "):
                blocks.append(CondPageBreak(160))
            if line[level:].strip().startswith("Supplementary Figure S1."):
                # Reserve space for title and complete 177-mm-wide source SVG.
                # Without this, the title can be orphaned on the preceding page.
                blocks.append(CondPageBreak(485))
            blocks.append(Paragraph(fmt(line[level:].strip()),styles["h1" if level==1 else "h2" if level==2 else "h3"]))
            i+=1;continue
        if line=="---":
            flush();i+=1;continue
        if line.startswith("- "):
            flush()
            blocks.append(Paragraph("&#8226; "+fmt(line[2:]),styles["p"]))
            i+=1;continue
        paragraph.append(line);i+=1
    flush()
    doc=SimpleDocTemplate(str(OUT),pagesize=landscape(A4),leftMargin=margin,
      rightMargin=margin,topMargin=38,bottomMargin=35,
      title="Supplementary Material - Anonymous Draft" if ANONYMOUS else "Supplementary Material - Internal Review Draft",
      author="Anonymous manuscript")
    doc.build(blocks,onFirstPage=decorate,onLaterPages=decorate)
    assert OUT.is_file() and OUT.stat().st_size>5000
    print(f"CREATED {OUT} bytes={OUT.stat().st_size} original_source_words={len(source.split())}")
if __name__=="__main__":
    build()
