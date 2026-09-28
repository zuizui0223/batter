#!/usr/bin/env python3
"""Fail-closed local preflight for the final GitHub release intended for Zenodo.

This script does not create a tag or release.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VERSION = "v0.3.8"
EXPECTED_TAG = "jae-v0.3.8"
METADATA = ROOT / "submission" / "jae_v0_3_8_metadata.json"
CFF = ROOT / "CITATION.cff"
NOTES = ROOT / "RELEASE_NOTES_JAE_V0_3_8.md"
MANIFEST = ROOT / "SUBMISSION_MANIFEST_JAE_V0_3_8.json"
TITLE_PAGE = ROOT / "manuscript" / "TITLE_PAGE_V0_3_8.md"
LICENSE_CANDIDATES = ("LICENSE", "LICENSE.md", "LICENSE.txt")
PLACEHOLDER = re.compile(r"\[INSERT\b|\bTBD\b|\bTODO\b", re.IGNORECASE)


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main() -> int:
    failures: list[str] = []

    for path in (METADATA, CFF, NOTES, MANIFEST, TITLE_PAGE):
        if not path.is_file():
            failures.append(f"missing required pre-release file: {path.relative_to(ROOT)}")

    licenses = [ROOT / name for name in LICENSE_CANDIDATES if (ROOT / name).is_file()]
    if len(licenses) != 1:
        failures.append(
            f"expected exactly one LICENSE file among {LICENSE_CANDIDATES}; found {len(licenses)}"
        )

    if failures:
        print("GitHub/Zenodo release preflight: BLOCKED")
        for item in failures:
            print(f" - {item}")
        return 1

    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cff = CFF.read_text(encoding="utf-8")
    notes = NOTES.read_text(encoding="utf-8")
    title = TITLE_PAGE.read_text(encoding="utf-8")

    if metadata.get("package_version") != EXPECTED_VERSION:
        failures.append(f"metadata package_version must be {EXPECTED_VERSION}")
    if str(metadata.get("archive_doi", "")).strip():
        failures.append("archive_doi must still be empty before the Zenodo-minting GitHub release")
    if manifest.get("submission_id") != "batter-jae-v0.3.8-rc2":
        failures.append("machine manifest is not the v0.3.8 rc2 submission package")
    if manifest.get("manuscript", {}).get("path") != "manuscript/MANUSCRIPT_DRAFT_V0_3_8.md":
        failures.append("machine manifest does not point to the v0.3.8 manuscript")

    for label, text in (("metadata JSON", json.dumps(metadata)), ("CITATION.cff", cff), ("release notes", notes)):
        if PLACEHOLDER.search(text):
            failures.append(f"{label} still contains placeholder text")

    if not re.search(r"(?m)^version:\s*['\"]?v0\.3\.7['\"]?\s*$", cff):
        failures.append("CITATION.cff version is not v0.3.8")
    if "versioned Zenodo DOI" not in title:
        failures.append("pre-release title page does not state that the Zenodo DOI is pending")

    try:
        head = git("rev-parse", "HEAD")
        main = git("rev-parse", "origin/main")
        if head != main:
            failures.append(f"release candidate HEAD {head} does not match origin/main {main}")
    except Exception as exc:
        failures.append(f"could not compare HEAD with origin/main: {exc}")

    try:
        dirty = git("status", "--porcelain")
        if dirty:
            failures.append("working tree is not clean")
    except Exception as exc:
        failures.append(f"could not inspect working tree: {exc}")

    if failures:
        print("GitHub/Zenodo release preflight: BLOCKED")
        for item in failures:
            print(f" - {item}")
        return 1

    print("GitHub/Zenodo release preflight: READY")
    print(f"Release version: {EXPECTED_VERSION}")
    print(f"Recommended Git tag: {EXPECTED_TAG}")
    print("Candidate HEAD matches origin/main.")
    print("This script does not create or publish the release.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
