#!/usr/bin/env python3
"""Preflight guard before creating a GitHub release intended for Zenodo archiving."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LICENSE_CANDIDATES = ("LICENSE", "LICENSE.md", "LICENSE.txt")
PLACEHOLDER = re.compile(r"\[INSERT\b|\bTBD\b|\bTODO\b", re.IGNORECASE)\nEXPECTED_VERSION = "v0.3.5"


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def main() -> int:
    failures: list[str] = []

    licenses = [ROOT / name for name in LICENSE_CANDIDATES if (ROOT / name).is_file()]
    if not licenses:
        fail("no repository LICENSE file; choose the intended software license before release", failures)

    cff = ROOT / "CITATION.cff"
    zenodo = ROOT / ".zenodo.json"
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

    template = ROOT / "CITATION.cff.template"
    if template.exists() and cff.exists() and template.read_text(encoding="utf-8") == cff.read_text(encoding="utf-8"):
        fail("CITATION.cff is still identical to the placeholder template", failures)

    if failures:
        print("Zenodo/GitHub release gate: BLOCKED")
        for item in failures:
            print(f" - {item}")
        return 1

    print("Zenodo/GitHub release gate: READY")
    print("License and release metadata are present with no obvious placeholders.")
    print("This check does not verify whether the repository has been enabled in the user's Zenodo account.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
