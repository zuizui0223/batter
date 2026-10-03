#!/usr/bin/env python3
"""Strict final-upload guard for the JAE v0.4.0 package.

This is intentionally separate from the scientific manuscript/figure gate.
It should fail until human metadata and the permanent archive DOI are filled.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLE_PAGE = ROOT / "manuscript" / "TITLE_PAGE_V0_4_0.md"
METADATA = ROOT / "submission" / "jae_v0_4_0_metadata.json"
MANIFEST = ROOT / "SUBMISSION_MANIFEST_JAE_V0_4_0.json"
MANUSCRIPT = ROOT / "manuscript" / "MANUSCRIPT_DRAFT_V0_4_0.md"

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

    for path in (TITLE_PAGE, MANIFEST, MANUSCRIPT, METADATA):
        if not path.exists():
            failures.append(f"missing required file: {path.relative_to(ROOT)}")

    if failures:
        for item in failures:
            print(f"BLOCKED: {item}")
        return 1

    title_page = TITLE_PAGE.read_text(encoding="utf-8")
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))

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
    archive_match = re.search(
        r"archived\s+at\s+https://doi\.org/(10\.\d{4,9}/\S+)",
        data_access,
        flags=re.IGNORECASE,
    )
    metadata_doi = str(metadata.get("archive_doi", "")).strip()
    if not archive_match:
        failures.append("data-availability section has no permanent code/provenance archive DOI")
    elif not metadata_doi:
        failures.append("metadata JSON archive_doi is empty")
    elif archive_match.group(1).rstrip(".,;") != metadata_doi:
        failures.append("title-page archive DOI does not match metadata JSON archive_doi")

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

    if metadata.get("package_version") != "v0.4.0":
        failures.append("metadata JSON package_version is not v0.4.0")
    if metadata.get("manuscript_title") != expected_title:
        failures.append("metadata JSON manuscript_title does not match manifest title")

    def count_words(text: str) -> int:
        cleaned = re.sub(r"`{1,3}.*?`{1,3}", " ", text, flags=re.S)
        cleaned = re.sub(r"[*_#>[]()]", " ", cleaned)
        return len(re.findall(r"\b[\w.+−-]+\b", cleaned, flags=re.UNICODE))

    combined_words = count_words(manuscript) + count_words(title_page)
    if combined_words > 8500:
        failures.append(f"combined manuscript + title-page count {combined_words} exceeds JAE 8500-word limit")

    if failures:
        print("JAE v0.4.0 final upload gate: BLOCKED")
        for item in failures:
            print(f" - {item}")
        print(f"\n{len(failures)} blocker(s) remain. Scientific RC content is not being re-evaluated.")
        return 1

    print("JAE v0.4.0 final upload gate: READY")
    print(f"Human metadata and DOI are consistent; combined CI word count = {combined_words}.")
    print("This guard does not re-open or alter the frozen empirical programme.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
