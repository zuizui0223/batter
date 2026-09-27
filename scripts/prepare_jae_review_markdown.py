#!/usr/bin/env python3
"""Prepare the anonymous JAE review-manuscript Markdown."""
from __future__ import annotations

from pathlib import Path

SRC = Path("manuscript/MANUSCRIPT_DRAFT_V0_3_4.md")
OUT = Path("manuscript/generated/JAE_REVIEW_V0_3_4.md")
TITLE = "Repeatable vertical identity in bat airspace persists after horizontal occupancy is standardized"


def main() -> int:
    text = SRC.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Remove repository/draft-only headings while retaining the scientific manuscript.
    cleaned = []
    skip_title_value = False
    for line in lines:
        if line.strip() == "# Manuscript draft v0.3.4":
            continue
        if line.strip() == "## Working title":
            skip_title_value = True
            continue
        if skip_title_value:
            if not line.strip():
                continue
            if line.startswith("**") and line.endswith("**"):
                skip_title_value = False
                continue
            skip_title_value = False
        cleaned.append(line)

    front = [
        "---",
        f'title: "{TITLE}"',
        'author: ""',
        'date: ""',
        "---",
        "",
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(front + cleaned).strip() + "\n", encoding="utf-8")
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
