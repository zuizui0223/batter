#!/usr/bin/env python3
"""Guard active JAE submission references against stale package pointers."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

README = ROOT / "README.md"
CURRENT = ROOT / "CURRENT_STATUS.md"
AUDIT = ROOT / "manuscript" / "JAE_INITIAL_SUBMISSION_AUDIT_2026_09_27.md"
MANIFEST_MD = ROOT / "SUBMISSION_MANIFEST_JAE_V0_3_8.md"
MANIFEST_JSON = ROOT / "SUBMISSION_MANIFEST_JAE_V0_3_8.json"
READINESS = ROOT / "manuscript" / "JAE_SUBMISSION_READINESS_V0_3_8.md"
METADATA_GUIDE = ROOT / "FINAL_METADATA_INTAKE_JAE_V0_3_8.md"

EXPECTED_RC = "v0.3.8-rc1"
EXPECTED_MANUSCRIPT = "manuscript/MANUSCRIPT_DRAFT_V0_3_8.md"
EXPECTED_FINAL_TITLE_PAGE = "manuscript/TITLE_PAGE_V0_3_8.md"
EXPECTED_METADATA = "submission/jae_v0_3_8_metadata.json"
EXPECTED_TITLE = "Repeatable individual shapes of vertical space use persist beyond coarse horizontal occupancy in bats"


def need(text: str, phrase: str, label: str, failures: list[str]) -> None:
    if phrase not in text:
        failures.append(f"{label} missing required current reference: {phrase}")


def main() -> int:
    failures: list[str] = []

    readme = README.read_text(encoding="utf-8")
    current = CURRENT.read_text(encoding="utf-8")
    audit = AUDIT.read_text(encoding="utf-8")
    manifest_md = MANIFEST_MD.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    readiness = READINESS.read_text(encoding="utf-8")
    metadata_guide = METADATA_GUIDE.read_text(encoding="utf-8")

    need(readme, EXPECTED_MANUSCRIPT, "README", failures)
    need(readme, "release/jae-v0.3.8-rc1", "README", failures)
    need(readme, EXPECTED_TITLE, "README", failures)

    need(current, EXPECTED_MANUSCRIPT, "CURRENT_STATUS", failures)
    need(current, EXPECTED_TITLE, "CURRENT_STATUS", failures)

    need(audit, EXPECTED_FINAL_TITLE_PAGE, "JAE initial audit", failures)
    need(audit, EXPECTED_METADATA, "JAE initial audit", failures)

    need(manifest_md, "# JAE submission manifest v0.3.8 rc1", "manifest markdown", failures)
    need(manifest_md, EXPECTED_METADATA, "manifest markdown", failures)
    need(manifest_md, EXPECTED_TITLE, "manifest markdown", failures)

    if manifest.get("submission_id") != "batter-jae-v0.3.8-rc1":
        failures.append("machine manifest submission_id is not batter-jae-v0.3.8-rc1")
    if manifest.get("manuscript", {}).get("path") != EXPECTED_MANUSCRIPT:
        failures.append("machine manifest manuscript path is not v0.3.8")
    if manifest.get("manuscript", {}).get("title") != EXPECTED_TITLE:
        failures.append("machine manifest title is not the v0.3.8 ecology-first title")
    if manifest.get("packaging", {}).get("release_candidate") != EXPECTED_RC:
        failures.append("machine manifest packaging.release_candidate is not v0.3.8-rc1")
    if manifest.get("packaging", {}).get("metadata_source") != EXPECTED_METADATA:
        failures.append("machine manifest metadata source is not the one-source JSON")
    remaining = manifest.get("remaining_human_input")
    if not isinstance(remaining, dict) or remaining.get("source") != EXPECTED_METADATA:
        failures.append("machine manifest remaining_human_input is not centralized in the one-source JSON")

    need(readiness, EXPECTED_METADATA, "v0.3.8 readiness", failures)
    need(readiness, "Phase A — before Zenodo", "v0.3.8 readiness", failures)
    need(readiness, "Phase B — after Zenodo", "v0.3.8 readiness", failures)

    need(metadata_guide, "--stage pre-release", "metadata guide", failures)
    need(metadata_guide, "--stage post-doi", "metadata guide", failures)
    need(metadata_guide, EXPECTED_FINAL_TITLE_PAGE, "metadata guide", failures)

    if failures:
        print("Active JAE submission reference guard: BLOCKED")
        for item in failures:
            print(f" - {item}")
        return 1

    print("Active JAE submission reference guard: PASS")
    print(f"Current package: {EXPECTED_RC}")
    print(f"Manuscript: {EXPECTED_MANUSCRIPT}")
    print(f"Final title page: {EXPECTED_FINAL_TITLE_PAGE}")
    print(f"One-source metadata: {EXPECTED_METADATA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
