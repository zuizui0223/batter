#!/usr/bin/env python3
"""Strict final-upload guard for the JAE v0.3.6 package.

This is intentionally separate from the scientific manuscript/figure gate.
It should fail until human metadata and the permanent archive DOI are filled.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLE_PAGE = ROOT / "manuscript" / "TITLE_PAGE_TEMPLATE_V0_3_6.md"
MANIFEST = ROOT / "SUBMISSION_MANIFEST_JAE_V0_3_6.json"
MANUSCRIPT = ROOT / "manuscript" / "MANUSCRIPT_DRAFT_V0_3_6.md"

PLACEHOLDER_PATTERNS = (
    r"\[INSERT\b",
    r"Replace this paragraph",
    r"\bTBD\b",
    r"\bTODO\b",
)

DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
EMAIL_RE = re.compile(r"[^\s@]+@[^\s@]+\.[^\s@]+")
ORCID_RE = re.compile(r"\b\d{4}-\d{4}-\d{4}-\d{3}[\dX]\b", re.IGNORECASE)

SUPERSEDED_TITLE = "Individual vertical identity has multiple predictive architectures across bat systems"


def section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    if marker not in text:
        return ""
    tail = text.split(marker, 1)[1]
    return tail.split("\n## ", 1)[0].strip()


def main() -> int:
    failures: list[str] = []

    for path in (TITLE_PAGE, MANIFEST, MANUSCRIPT):
        if not path.exists():
            failures.append(f"missing required file: {path.relative_to(ROOT)}")

    if failures:
        for item in failures:
            print(f"BLOCKED: {item}")
        return 1

    title_page = TITLE_PAGE.read_text(encoding="utf-8")
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, title_page, flags=re.IGNORECASE):
            failures.append(f"title page still contains placeholder matching {pattern!r}")

    expected_title = manifest["manuscript"]["title"]
    if expected_title not in title_page:
        failures.append("title page does not contain the manifest title")
    if expected_title not in manuscript:
        failures.append("manuscript does not contain the manifest title")
    if SUPERSEDED_TITLE in title_page:
        failures.append("title page contains the superseded architecture title")

    corresponding = section(title_page, "Corresponding author")
    if not EMAIL_RE.search(corresponding):
        failures.append("corresponding-author section has no email address")
    if not ORCID_RE.search(corresponding):
        failures.append("corresponding-author section has no ORCID-formatted identifier")

    data_access = section(title_page, "Data availability statement")
    archive_doi = re.search(
        r"archive DOI:\s*(10\.\d{4,9}/[-._;()/:A-Z0-9]+)",
        data_access,
        flags=re.IGNORECASE,
    )
    if not archive_doi:
        failures.append("data-availability section has no permanent code/provenance archive DOI")

    required_sections = (
        "Authors",
        "Affiliations",
        "Author contributions",
        "Acknowledgements",
        "Funding",
        "Conflict of interest",
        "Data availability statement",
    )
    for heading in required_sections:
        body = section(title_page, heading)
        if not body:
            failures.append(f"required title-page section is empty or missing: {heading}")

    if failures:
        print("JAE v0.3.6 final upload gate: BLOCKED")
        for item in failures:
            print(f" - {item}")
        print(f"\n{len(failures)} blocker(s) remain. Scientific RC content is not being re-evaluated.")
        return 1

    print("JAE v0.3.6 final upload gate: READY")
    print("Human metadata placeholders are cleared and a permanent DOI is present.")
    print("This guard does not re-open or alter the frozen empirical programme.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
