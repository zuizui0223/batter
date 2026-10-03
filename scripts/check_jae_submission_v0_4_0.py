#!/usr/bin/env python3
"""Journal of Animal Ecology v0.4.0 maintenance-synthesis submission gate."""
from __future__ import annotations
import re
from pathlib import Path

PATH=Path("manuscript/MANUSCRIPT_DRAFT_V0_4_0.md")
SI_PATH=Path("manuscript/SUPPORTING_INFORMATION_CLAIM_AMENDMENT_HISTORY.md")
TEXT=PATH.read_text(encoding="utf-8")
SI_TEXT=SI_PATH.read_text(encoding="utf-8")
WORD_LIMIT=8500
ABSTRACT_LIMIT=350
KEYWORD_LIMIT=8
EXPECTED_TITLE="Persistent individual vertical strategies need not partition three-dimensional space in two tropical bat species"

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
    assert f"**{EXPECTED_TITLE}**" in TEXT
    assert "# Manuscript draft v0.4.0 candidate" in TEXT

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

    required=[
        "origin of individual specialization",
        "maintenance of specialization",
        "Post-outcome maintenance stress tests",
        "Terrain-relative individuality persists without general vertical segregation",
        "Self-history remains predictive across days and matched movement contexts",
        "Persistent personal solutions need not imply exclusive niches",
        "personal solution reuse",
        "A prospective test of strategy maintenance",
        "p=0.5121",
        "p=0.0544",
        "Figure 6",
        "not separately",
        "Independent external tests limit generality",
        "task-level ecological opportunity",
        "Supporting Figure S3",
        "p=0.1224",
        "p=0.8616",
        "p=0.4419",
    ]
    for phrase in required:
        assert phrase in TEXT, f"missing v0.4.0 phrase: {phrase}"

    forbidden=[
        "A prospective test of vertical individuality",
        "behavioural-mixture individuality",
        "Two mechanisms could generate individual organization of vertical space use",
    ]
    for phrase in forbidden:
        assert phrase not in TEXT, f"stale v0.3.8 framing remains: {phrase}"

    assert results.index("Terrain-relative individuality persists without general vertical segregation") < results.index("Self-history remains predictive across days and matched movement contexts")
    assert results.index("Self-history remains predictive across days and matched movement contexts") < results.index("*Tadarida* is a motivating boundary case")
    assert discussion.index("Persistent personal solutions need not imply exclusive niches") < discussion.index("*Tadarida* defines the boundary")

    main_legends=re.findall(r"(?m)^\*\*Figure (\d+)\.",TEXT)
    support_legends_main=re.findall(r"(?m)^\*\*Supporting Figure (S\d+)\.",TEXT)
    support_legends_si=re.findall(r"(?m)^\*\*Supporting Figure (S\d+)\.",SI_TEXT)
    assert main_legends==["1","2","3","4","5","6"], main_legends
    assert support_legends_main==[], support_legends_main
    assert support_legends_si==["S1","S2","S3"], support_legends_si

    assert "Figure 1. From vertical individuality to maintenance without exclusive spatial partitioning." in TEXT
    assert "no further same-data mechanism fishing" not in TEXT.lower(), "internal stop-rule language leaked into manuscript"

    print({
        "manuscript_words_ci_estimate":tw,
        "abstract_words_ci_estimate":aw,
        "introduction_words_ci_estimate":len(words(intro)),
        "results_words_ci_estimate":len(words(results)),
        "discussion_words_ci_estimate":len(words(discussion)),
        "keywords":keywords,
        "main_figures":len(main_legends),
        "supporting_figures":len(support_legends_si),
        "jae_word_limit":WORD_LIMIT,
        "maintenance_synthesis":True,
    })
    return 0

if __name__=="__main__":
    raise SystemExit(main())
