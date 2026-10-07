#!/usr/bin/env python3
"""Build Behavioral Ecology Complete Anonymous Text DOCX v1.

Source of scientific content:
- COMPLETE_ANONYMOUS_TEXT_V1.md

Adds only submission formatting:
- Times New Roman 12 pt;
- double spacing;
- 1-inch margins;
- Lay Summary page 1;
- title/abstract page 2;
- main text starts page 3;
- continuous line numbering;
- footer page numbers;
- short running title;
- main figures appended after figure legends.

No scientific text or evidence tier is changed here.
"""

from __future__ import annotations

from pathlib import Path
import json
import re
import shutil
import subprocess
import tempfile

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.shared import Inches, Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parents[2]
SYN=ROOT/"prospective"/"public_causal_synthesis"
FIG=ROOT/"figures"/"public_causal"
OUTDIR=ROOT/"submission"/"public_causal"
SRC=SYN/"COMPLETE_ANONYMOUS_TEXT_V1.md"
OUT=OUTDIR/"COMPLETE_ANONYMOUS_TEXT_BEHAVIORAL_ECOLOGY_V1.docx"
RECEIPT=OUTDIR/"COMPLETE_ANONYMOUS_TEXT_BEHAVIORAL_ECOLOGY_V1_RECEIPT.json"

TITLE="Individual organization remains detectable across acute perturbations in bats"
RUNNING="Individual organization across perturbations"

FIGURES=[
    ("Figure 1",FIG/"FIGURE_1_CAUSAL_LAYERS_V1.svg"),
    ("Figure 2A",FIG/"FIGURE_2A_FIRST_FLIGHT_FORMATION_V1.svg"),
    ("Figure 2B",FIG/"FIGURE_2B_DEVELOPMENTAL_RANDOMIZATION_V1.svg"),
    ("Figure 3",FIG/"FIGURE_3_ACUTE_PERTURBATION_IDENTITY_V1.svg"),
    ("Figure 4",FIG/"FIGURE_4_PORTABILITY_AND_WILD_BOUNDARY_V1.svg"),
]

BANNED=[
    "zuizui0223",
    "github.com/zuizui0223",
    "ZHANG Ruiqi",
    "張瑞琪",
]

def set_run_font(run,name="Times New Roman",size=12):
    run.font.name=name
    run.font.size=Pt(size)
    rpr=run._element.get_or_add_rPr()
    rfonts=rpr.rFonts
    if rfonts is None:
        rfonts=OxmlElement("w:rFonts")
        rpr.insert(0,rfonts)
    for attr in ("ascii","hAnsi","eastAsia","cs"):
        rfonts.set(qn(f"w:{attr}"),name)

def set_style_font(style,name="Times New Roman",size=12,bold=None):
    style.font.name=name
    style.font.size=Pt(size)
    if bold is not None:
        style.font.bold=bold
    rpr=style.element.get_or_add_rPr()
    rfonts=rpr.rFonts
    if rfonts is None:
        rfonts=OxmlElement("w:rFonts")
        rpr.insert(0,rfonts)
    for attr in ("ascii","hAnsi","eastAsia","cs"):
        rfonts.set(qn(f"w:{attr}"),name)

def set_line_numbering(section):
    sectPr=section._sectPr
    for old in list(sectPr.findall(qn("w:lnNumType"))):
        sectPr.remove(old)
    el=OxmlElement("w:lnNumType")
    el.set(qn("w:countBy"),"1")
    el.set(qn("w:start"),"1")
    el.set(qn("w:restart"),"continuous")
    sectPr.append(el)

def add_page_field(paragraph):
    paragraph.alignment=WD_ALIGN_PARAGRAPH.CENTER
    pPr=paragraph._p.get_or_add_pPr()
    if pPr.find(qn("w:suppressLineNumbers")) is None:
        pPr.append(OxmlElement("w:suppressLineNumbers"))
    run=paragraph.add_run()
    fldBegin=OxmlElement("w:fldChar"); fldBegin.set(qn("w:fldCharType"),"begin")
    instr=OxmlElement("w:instrText"); instr.set(qn("xml:space"),"preserve"); instr.text=" PAGE "
    fldSep=OxmlElement("w:fldChar"); fldSep.set(qn("w:fldCharType"),"separate")
    txt=OxmlElement("w:t"); txt.text="1"
    fldEnd=OxmlElement("w:fldChar"); fldEnd.set(qn("w:fldCharType"),"end")
    run._r.extend([fldBegin,instr,fldSep,txt,fldEnd])
    set_run_font(run,size=10)

def add_keep_with_next(paragraph):
    pPr=paragraph._p.get_or_add_pPr()
    if pPr.find(qn("w:keepNext")) is None:
        pPr.append(OxmlElement("w:keepNext"))

def insert_paragraph_after(paragraph,text="",style=None):
    new_p=OxmlElement("w:p")
    paragraph._p.addnext(new_p)
    new_para=paragraph._parent.add_paragraph()
    new_para._p.getparent().remove(new_para._p)
    new_p.addnext(new_para._p)
    # swap so new_para occupies the desired new_p position
    new_para._p.getparent().remove(new_para._p)
    new_p.getparent().replace(new_p,new_para._p)
    if style:
        new_para.style=style
    if text:
        r=new_para.add_run(text)
        set_run_font(r)
    return new_para

def add_after(paragraph,text,italic=False,bold=False,align=None):
    new_p=OxmlElement("w:p")
    paragraph._p.addnext(new_p)
    from docx.text.paragraph import Paragraph
    p=Paragraph(new_p,paragraph._parent)
    r=p.add_run(text)
    set_run_font(r)
    r.italic=italic
    r.bold=bold
    if align is not None:
        p.alignment=align
    return p

def convert_svg(svg:Path,png:Path):
    import cairosvg
    cairosvg.svg2png(
        bytestring=svg.read_bytes(),
        write_to=str(png),
        output_width=2100,
    )

def main():
    OUTDIR.mkdir(parents=True,exist_ok=True)
    src_text=SRC.read_text(encoding="utf-8")
    low=src_text.lower()
    for token in BANNED:
        if token.lower() in low:
            raise SystemExit(f"STOP identifying token in anonymous source: {token}")
    if "[ANONYMIZED_REVIEW_ARCHIVE_URL]" not in src_text:
        raise SystemExit("STOP anonymous review URL placeholder absent")

    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        base=td/"base.docx"
        subprocess.run(
            [
                "pandoc",str(SRC),
                "--from=markdown",
                "--to=docx",
                "--output",str(base),
            ],
            check=True,
        )
        doc=Document(base)

        # Remove Pandoc spacer/horizontal-rule paragraphs before submission formatting.
        # They are visually useful in Markdown but consume vertical space in a
        # double-spaced journal manuscript and can push Keywords onto page 3.
        for p in list(doc.paragraphs):
            if not p.text.strip():
                parent=p._element.getparent()
                if parent is not None:
                    parent.remove(p._element)

        # Page geometry and line numbering.
        for section in doc.sections:
            section.top_margin=Inches(1)
            section.bottom_margin=Inches(1)
            section.left_margin=Inches(1)
            section.right_margin=Inches(1)
            set_line_numbering(section)
            footer=section.footer
            p=footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
            p.clear()
            add_page_field(p)

        # Core styles.
        for name in ["Normal","Body Text","List Paragraph"]:
            if name in doc.styles:
                st=doc.styles[name]
                set_style_font(st,size=12)
                st.paragraph_format.line_spacing=2.0
                st.paragraph_format.space_after=Pt(0)
                st.paragraph_format.space_before=Pt(0)
        for name in ["Title","Heading 1","Heading 2","Heading 3"]:
            if name in doc.styles:
                st=doc.styles[name]
                set_style_font(st,size=12,bold=True)
                st.paragraph_format.line_spacing=2.0
                st.paragraph_format.space_before=Pt(6)
                st.paragraph_format.space_after=Pt(0)

        # Apply body formatting broadly.
        for p in doc.paragraphs:
            p.paragraph_format.line_spacing=2.0
            p.paragraph_format.space_after=Pt(0)
            for run in p.runs:
                set_run_font(run)
            if p.style and p.style.name.startswith("Heading"):
                add_keep_with_next(p)

        # Locate key paragraphs.
        lay=None
        title=None
        intro=None
        refs=None
        legends=None
        for p in doc.paragraphs:
            t=p.text.strip()
            if t=="Lay Summary" and lay is None:
                lay=p
            elif t==TITLE and title is None:
                title=p
            elif t=="Introduction" and intro is None:
                intro=p
            elif t=="References" and refs is None:
                refs=p
            elif t=="Figure legends" and legends is None:
                legends=p
        missing=[k for k,v in {
            "Lay Summary":lay,"title":title,"Introduction":intro,
            "References":refs,"Figure legends":legends
        }.items() if v is None]
        if missing:
            raise SystemExit(f"STOP DOCX section anchors missing: {missing}")

        # Submission page architecture.
        title.paragraph_format.page_break_before=True
        intro.paragraph_format.page_break_before=True

        # Keep the title/abstract/keywords block on page 2 while retaining
        # double spacing. Behavioral Ecology specifies page-3 main-text start
        # but does not prescribe a fixed font size for the title/abstract page.
        pars=list(doc.paragraphs)
        ti=next((i for i,p in enumerate(pars) if p.text.strip()==TITLE),None)
        ii=next((i for i,p in enumerate(pars) if p.text.strip()=="Introduction"),None)
        if ti is None or ii is None or ti >= ii:
            raise SystemExit(f"STOP DOCX title/introduction order invalid: title={ti}, intro={ii}")
        for p in pars[ti:ii]:
            p.paragraph_format.line_spacing=2.0
            for run in p.runs:
                set_run_font(run,size=11)

        # Title page formatting.
        title.alignment=WD_ALIGN_PARAGRAPH.CENTER
        for run in title.runs:
            run.bold=True
            set_run_font(run,size=14)
        running=add_after(title,f"Running title: {RUNNING}",italic=False,align=WD_ALIGN_PARAGRAPH.CENTER)
        running.paragraph_format.line_spacing=2.0
        for run in running.runs:
            set_run_font(run,size=11)

        # Lay summary heading.
        lay.alignment=WD_ALIGN_PARAGRAPH.LEFT
        for run in lay.runs:
            run.bold=True

        # References should be hanging-indented and double spaced.
        ref_mode=False
        figlegend_mode=False
        for p in doc.paragraphs:
            t=p.text.strip()
            if t=="References":
                ref_mode=True
                figlegend_mode=False
                continue
            if t=="Figure legends":
                ref_mode=False
                figlegend_mode=True
                continue
            if ref_mode and t:
                p.paragraph_format.left_indent=Inches(0.25)
                p.paragraph_format.first_line_indent=Inches(-0.25)
            if figlegend_mode and t:
                p.paragraph_format.keep_together=True

        # Append figures after legends at manuscript end.
        pngdir=td/"figures"; pngdir.mkdir()
        for idx,(label,svg) in enumerate(FIGURES):
            if not svg.exists():
                raise SystemExit(f"STOP missing figure {svg}")
            png=pngdir/f"{idx+1}.png"
            convert_svg(svg,png)
            p=doc.add_paragraph()
            if idx==0:
                p.paragraph_format.page_break_before=True
            p.alignment=WD_ALIGN_PARAGRAPH.CENTER
            r=p.add_run(label)
            r.bold=True
            set_run_font(r,size=12)
            pic=doc.add_paragraph()
            pic.alignment=WD_ALIGN_PARAGRAPH.CENTER
            rr=pic.add_run()
            rr.add_picture(str(png),width=Inches(6.35))
            # Ensure each main figure block stays visually separated.
            if idx < len(FIGURES)-1:
                spacer=doc.add_paragraph()
                spacer.paragraph_format.page_break_before=True

        # Re-apply section fields after pandoc modifications.
        for section in doc.sections:
            set_line_numbering(section)

        # Core properties anonymized.
        cp=doc.core_properties
        cp.author=""
        cp.last_modified_by=""
        cp.title=TITLE
        cp.subject="Behavioral Ecology Complete Anonymous Text"
        cp.keywords="behavioral individuality; bats; perturbation"
        cp.comments=""

        doc.save(OUT)

    # Structural re-open validation.
    check=Document(OUT)
    texts="\n".join(p.text for p in check.paragraphs)
    for token in [
        "Lay Summary",
        TITLE,
        "Introduction",
        "FAIL_PRIMARY_FORMATION_RULE",
        "112.5554",
        "144.079",
        "0.3244",
        "2/4",
        "Figure legends",
    ]:
        if token not in texts:
            raise SystemExit(f"STOP generated DOCX missing required token: {token!r}")
    for token in BANNED:
        if token.lower() in texts.lower():
            raise SystemExit(f"STOP identifying token leaked into DOCX: {token!r}")

    # Confirm line numbering and PAGE fields in package XML.
    import zipfile
    with zipfile.ZipFile(OUT) as z:
        document=z.read("word/document.xml").decode("utf-8")
        footers="".join(
            z.read(n).decode("utf-8")
            for n in z.namelist()
            if n.startswith("word/footer") and n.endswith(".xml")
        )
        core=z.read("docProps/core.xml").decode("utf-8")
    if "w:lnNumType" not in document:
        raise SystemExit("STOP continuous line numbering missing from DOCX XML")
    if " PAGE " not in footers:
        raise SystemExit("STOP PAGE field missing from DOCX footer")
    for token in BANNED:
        if token.lower() in core.lower():
            raise SystemExit(f"STOP identifying token leaked into core metadata: {token!r}")

    receipt={
        "version":1,
        "docx":str(OUT.relative_to(ROOT)),
        "bytes":OUT.stat().st_size,
        "page_architecture":{
            "lay_summary":"page 1",
            "title_abstract":"page 2",
            "main_text":"starts page 3",
        },
        "font":"Times New Roman 12 pt",
        "line_spacing":"double",
        "line_numbering":"continuous",
        "page_numbers":"footer PAGE field",
        "margins_inches":1.0,
        "figures_appended":len(FIGURES),
        "anonymity_scan":"PASS",
        "evidence_token_scan":"PASS",
    }
    RECEIPT.write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,indent=2))

if __name__=="__main__":
    main()
