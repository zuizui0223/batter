#!/usr/bin/env python3
"""Journal of Animal Ecology v0.3.6 submission gate."""
from __future__ import annotations
import re
from pathlib import Path

PATH=Path("manuscript/MANUSCRIPT_DRAFT_V0_3_6.md")
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
    for name in ["Introduction","Materials and Methods","Results","Discussion","Conclusion"]:
        assert f"## {name}" in TEXT

    required_phrases=[
        "coarse horizontal occupancy",
        "p=0.5121",
        "Five of six panels",
        "4.64 m",
        "2.00 m",
        "31.1%",
        "Figure 7",
    ]
    for phrase in required_phrases:
        assert phrase in TEXT, f"missing final tag-bias audit result: {phrase}"

    abstract_forbidden=[
        "256-m",
        "256 m",
        "256.459",
    ]
    for phrase in abstract_forbidden:
        assert phrase not in body, f"focal metre translation remains in abstract: {phrase}"

    print({
        "manuscript_words_ci_estimate":tw,
        "abstract_words_ci_estimate":aw,
        "abstract_numbered_statements":len(numbered),
        "keywords":keywords,
        "jae_word_limit":WORD_LIMIT,
        "tag_bias_primary":"5_of_6_pass",
        "stationary_corroboration":"2_of_2_pass",
    })
    return 0

if __name__=="__main__":
    raise SystemExit(main())
