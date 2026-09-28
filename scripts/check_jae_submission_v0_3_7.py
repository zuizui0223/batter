#!/usr/bin/env python3
"""Journal of Animal Ecology v0.3.7 editorial/submission gate."""
from __future__ import annotations
import re
from pathlib import Path

PATH=Path("manuscript/MANUSCRIPT_DRAFT_V0_3_7.md")
TEXT=PATH.read_text(encoding="utf-8")
WORD_LIMIT=8500
ABSTRACT_LIMIT=350
KEYWORD_LIMIT=8

def words(text):
    text=re.sub(r"`{1,3}.*?`{1,3}"," ",text,flags=re.S)
    text=re.sub(r"[*_#>[]()]"," ",text)
    return re.findall(r"\b[\w.+−-]+\b",text,flags=re.UNICODE)

def section(name,next_name=None):
    marker=f"## {name}"
    assert marker in TEXT, f"missing section: {name}"
    tail=TEXT.split(marker,1)[1]
    if next_name is None:
        return tail
    nm=f"## {next_name}"
    assert nm in tail, f"missing next section: {next_name}"
    return tail.split(nm,1)[0]

def main():
    abstract=section("Abstract","Introduction")
    body=abstract.split("**Keywords:**",1)[0]
    aw=len(words(body))
    numbered=re.findall(r"(?m)^([1-5])\.\s",body)
    assert numbered==["1","2","3","4","5"], numbered
    assert aw<=ABSTRACT_LIMIT, aw

    km=re.search(r"\*\*Keywords:\*\*\s*(.+)",abstract)
    assert km
    keywords=[x.strip() for x in km.group(1).split(";") if x.strip()]
    assert len(keywords)<=KEYWORD_LIMIT
    assert keywords==sorted(keywords,key=str.lower)

    tw=len(words(TEXT))
    assert tw<=WORD_LIMIT, tw
    for name in ["Introduction","Materials and Methods","Results","Discussion","Conclusion","References","Figure legends"]:
        assert f"## {name}" in TEXT

    intro=section("Introduction","Materials and Methods")
    results=section("Results","Discussion")
    discussion=section("Discussion","Conclusion")

    assert len(words(intro))<=900, len(words(intro))
    assert len(re.findall(r"\bfocal\b",intro,flags=re.I))==0, "Introduction re-centred on focal wording"

    required=[
        "five comparative panels",
        "p=0.5121",
        "4.64 m",
        "2.00 m",
        "31.1%",
        "altitude-error variance",
        "Supporting Figure S1",
        "Supporting Figure S2",
        "Pipeline calibration changed the inferential baseline",
        "*Tadarida* is a motivating boundary case rather than the comparative template",
    ]
    for phrase in required:
        assert phrase in TEXT, f"missing v0.3.7 framing/result: {phrase}"

    for phrase in ("256-m","256 m","256.459"):
        assert phrase not in body, f"focal metre translation remains in abstract: {phrase}"

    main_legends=re.findall(r"(?m)^\*\*Figure (\d+)\.",TEXT)
    support_legends=re.findall(r"(?m)^\*\*Supporting Figure (S\d+)\.",TEXT)
    assert main_legends==["1","2","3","4","5"], main_legends
    assert support_legends==["S1","S2"], support_legends
    assert "Figure 6" not in TEXT
    assert "Figure 7" not in TEXT

    assert results.index("Five comparative panels retain vertical-distribution shape") < results.index("*Tadarida* is a motivating boundary case")
    assert discussion.index("Comparative vertical-distribution shape persists") < discussion.index("*Tadarida* defines the boundary")

    print({
        "manuscript_words_ci_estimate":tw,
        "abstract_words_ci_estimate":aw,
        "introduction_words_ci_estimate":len(words(intro)),
        "results_words_ci_estimate":len(words(results)),
        "discussion_words_ci_estimate":len(words(discussion)),
        "abstract_numbered_statements":len(numbered),
        "keywords":keywords,
        "main_figures":len(main_legends),
        "supporting_figures":len(support_legends),
        "jae_word_limit":WORD_LIMIT,
        "comparative_first":True,
    })
    return 0

if __name__=="__main__":
    raise SystemExit(main())
