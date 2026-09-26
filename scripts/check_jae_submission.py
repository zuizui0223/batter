#!/usr/bin/env python3
"""Lightweight Journal of Animal Ecology initial-submission gate."""
from __future__ import annotations

import re
from pathlib import Path

PATH = Path("manuscript/MANUSCRIPT_DRAFT_V0_3_2.md")
TEXT = PATH.read_text(encoding="utf-8")

WORD_LIMIT = 8500
ABSTRACT_LIMIT = 350
KEYWORD_LIMIT = 8


def words(text: str) -> list[str]:
    # Markdown-light count suitable as a CI guard, not a publisher-final count.
    text = re.sub(r"`{1,3}.*?`{1,3}", " ", text, flags=re.S)
    text = re.sub(r"[*_#>[]()]", " ", text)
    return re.findall(r"\b[\w.+−-]+\b", text, flags=re.UNICODE)


def section(name: str, next_name: str | None = None) -> str:
    marker = f"## {name}"
    if marker not in TEXT:
        raise AssertionError(f"missing section: {name}")
    tail = TEXT.split(marker, 1)[1]
    if next_name is None:
        return tail
    next_marker = f"## {next_name}"
    if next_marker not in tail:
        raise AssertionError(f"missing next section: {next_name}")
    return tail.split(next_marker, 1)[0]


def main() -> int:
    abstract = section("Abstract", "Introduction")
    abstract_body = abstract.split("**Keywords:**", 1)[0]
    abstract_words = len(words(abstract_body))

    numbered = re.findall(r"(?m)^([1-5])\.\s", abstract_body)
    assert numbered == ["1", "2", "3", "4", "5"], numbered
    assert abstract_words <= ABSTRACT_LIMIT, abstract_words

    m = re.search(r"\*\*Keywords:\*\*\s*(.+)", abstract)
    assert m, "missing keywords"
    keywords = [x.strip() for x in m.group(1).split(";") if x.strip()]
    assert len(keywords) <= KEYWORD_LIMIT, keywords
    assert keywords == sorted(keywords, key=str.lower), "keywords must be alphabetical"

    total_words = len(words(TEXT))
    assert total_words <= WORD_LIMIT, total_words

    required = ["Introduction", "Methods", "Results", "Discussion", "Conclusion"]
    for name in required:
        assert f"## {name}" in TEXT, f"missing section: {name}"

    print({
        "manuscript_words_ci_estimate": total_words,
        "abstract_words_ci_estimate": abstract_words,
        "abstract_numbered_statements": len(numbered),
        "keywords": keywords,
        "jae_word_limit": WORD_LIMIT,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
