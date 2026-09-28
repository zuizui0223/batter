#!/usr/bin/env python3
"""Preflight guard before creating a GitHub release intended for Zenodo archiving."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LICENSE_CANDIDATES = ("LICENSE", "LICENSE.md", "LICENSE.txt")
PLACEHOLDER = re.compile(r"\[INSERT\b|\bTBD\b|\bTODO\b", re.IGNORECASE)
EXPECTED_VERSION = "v0.3.6"
METADATA = ROOT / "submission" / "jae_v0_3_6_metadata.json"


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def main() -> int:
    failures: list[str] = []

    licenses = [ROOT / name for name in LICENSE_CANDIDATES if (ROOT / name).is_file()]
    if not licenses:
        fail("no repository LICENSE file; choose the intended software license before release", failures)

    cff = ROOT / "CITATION.cff"
    zenodo = ROOT / ".zenodo.json"

    metadata = None
    if not METADATA.is_file():
        fail("missing submission/jae_v0_3_6_metadata.json", failures)
    else:
        try:
            metadata = json.loads(METADATA.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"metadata JSON is invalid: {exc}", failures)
        else:
            if PLACEHOLDER.search(json.dumps(metadata, ensure_ascii=False)):
                fail("metadata JSON still contains placeholder text", failures)
            if metadata.get("package_version") != EXPECTED_VERSION:
                fail(f"metadata package_version must be {EXPECTED_VERSION}", failures)
            if not str(metadata.get("software_license_spdx", "")).strip():
                fail("metadata software_license_spdx is empty", failures)
            if not str(metadata.get("release_date", "")).strip():
                fail("metadata release_date is empty", failures)

    if not cff.exists() and not zenodo.exists():
        fail("no release metadata: create CITATION.cff or .zenodo.json", failures)
    if cff.exists() and zenodo.exists():
        fail("both CITATION.cff and .zenodo.json exist; choose one authoritative Zenodo metadata source", failures)

    if cff.exists():
        text = cff.read_text(encoding="utf-8")
        if PLACEHOLDER.search(text):
            fail("CITATION.cff still contains placeholders", failures)
        for key in ("cff-version:", "title:", "type:", "authors:", "version:", "date-released:"):
            if key not in text:
                fail(f"CITATION.cff missing required release field: {key}", failures)
        version_match = re.search(r"(?m)^version:\s*['\"]?([^'\"\s]+)['\"]?\s*$", text)
        if not version_match or version_match.group(1) != EXPECTED_VERSION:
            fail(f"CITATION.cff version must be {EXPECTED_VERSION}", failures)
        license_match = re.search(r"(?m)^license:\s*['\"]?([^'\"\n]+)['\"]?\s*$", text)
        date_match = re.search(r"(?m)^date-released:\s*['\"]?([^'\"\n]+)['\"]?\s*$", text)
        if metadata is not None:
            if not license_match or license_match.group(1).strip() != str(metadata.get("software_license_spdx", "")).strip():
                fail("CITATION.cff license does not match metadata software_license_spdx", failures)
            if not date_match or date_match.group(1).strip() != str(metadata.get("release_date", "")).strip():
                fail("CITATION.cff date-released does not match metadata release_date", failures)

    if zenodo.exists():
        try:
            payload = json.loads(zenodo.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f".zenodo.json is invalid JSON: {exc}", failures)
        else:
            raw = zenodo.read_text(encoding="utf-8")
            if PLACEHOLDER.search(raw):
                fail(".zenodo.json still contains placeholders", failures)
            if not payload.get("title"):
                fail(".zenodo.json missing title", failures)
            if not payload.get("creators"):
                fail(".zenodo.json missing creators", failures)
            if payload.get("version") != EXPECTED_VERSION:
                fail(f".zenodo.json version must be {EXPECTED_VERSION}", failures)

    template = ROOT / "CITATION.cff.template"
    if template.exists() and cff.exists():
        if template.read_text(encoding="utf-8") == cff.read_text(encoding="utf-8"):
            fail("CITATION.cff is still identical to the placeholder template", failures)

    if failures:
        print("Zenodo/GitHub release gate: BLOCKED")
        for item in failures:
            print(f" - {item}")
        return 1

    print("Zenodo/GitHub release gate: READY")
    print(f"License and {EXPECTED_VERSION} release metadata are present with no obvious placeholders.")
    print("This check does not verify whether the repository has been enabled in the user's Zenodo account.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
