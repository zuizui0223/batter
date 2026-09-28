#!/usr/bin/env python3
"""Prepare anonymous JAE v0.3.8 review Markdown."""
from pathlib import Path

SRC=Path("manuscript/MANUSCRIPT_DRAFT_V0_3_8.md")
OUT=Path("manuscript/generated/JAE_REVIEW_V0_3_8.md")
TITLE="Repeatable individual shapes of vertical space use persist beyond coarse horizontal occupancy in bats"

def main():
    text=SRC.read_text(encoding="utf-8")
    lines=text.splitlines()
    cleaned=[]
    skip=False
    for line in lines:
        if line.strip()=="# Manuscript draft v0.3.8":
            continue
        if line.strip()=="## Working title":
            skip=True
            continue
        if skip:
            if not line.strip():
                continue
            if line.startswith("**") and line.endswith("**"):
                skip=False
                continue
            skip=False
        cleaned.append(line)
    front=["---",f'title: "{TITLE}"','author: ""','date: ""',"---",""]
    review="\n".join(front+cleaned).strip()+"\n"
    review=review.replace("the public GitHub repository `zuizui0223/batter`","an anonymous code repository prepared for peer review")
    review=review.replace("`zuizui0223/batter`","[code repository anonymized for peer review]")
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(review,encoding="utf-8")
    print(OUT)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
