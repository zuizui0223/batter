#!/usr/bin/env python3
"""Guard active JAE v0.4.0 submission references against stale package pointers."""
from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

README=ROOT/"README.md"
CURRENT=ROOT/"CURRENT_STATUS.md"
MANIFEST_MD=ROOT/"SUBMISSION_MANIFEST_JAE_V0_4_0.md"
MANIFEST_JSON=ROOT/"SUBMISSION_MANIFEST_JAE_V0_4_0.json"
READINESS=ROOT/"manuscript"/"JAE_SUBMISSION_READINESS_V0_4_0.md"
METADATA_GUIDE=ROOT/"FINAL_METADATA_INTAKE_JAE_V0_4_0.md"
RELEASE_NOTES=ROOT/"RELEASE_NOTES_JAE_V0_4_0.md"
METADATA_TEMPLATE=ROOT/"submission"/"jae_v0_4_0_metadata.template.json"

EXPECTED_RC="release/jae-v0.4.0-rc1"
EXPECTED_SUBMISSION_ID="batter-jae-v0.4.0-rc1"
EXPECTED_MANUSCRIPT="manuscript/MANUSCRIPT_DRAFT_V0_4_0.md"
EXPECTED_FINAL_TITLE_PAGE="manuscript/TITLE_PAGE_V0_4_0.md"
EXPECTED_METADATA="submission/jae_v0_4_0_metadata.json"
EXPECTED_TEMPLATE="submission/jae_v0_4_0_metadata.template.json"
EXPECTED_TITLE="Persistent individual vertical strategies need not partition three-dimensional space in bats"
EXPECTED_TAG="jae-v0.4.0"

def need(text,phrase,label,failures):
    if phrase not in text:
        failures.append(f"{label} missing current reference: {phrase}")

def main():
    failures=[]
    for path in (README,CURRENT,MANIFEST_MD,MANIFEST_JSON,READINESS,METADATA_GUIDE,RELEASE_NOTES,METADATA_TEMPLATE):
        if not path.exists():
            failures.append(f"missing active package file: {path.relative_to(ROOT)}")
    if failures:
        print("Active JAE v0.4.0 reference guard: BLOCKED")
        for x in failures: print(f" - {x}")
        return 1

    readme=README.read_text(encoding="utf-8")
    current=CURRENT.read_text(encoding="utf-8")
    manifest_md=MANIFEST_MD.read_text(encoding="utf-8")
    manifest=json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    readiness=READINESS.read_text(encoding="utf-8")
    guide=METADATA_GUIDE.read_text(encoding="utf-8")
    notes=RELEASE_NOTES.read_text(encoding="utf-8")
    template=json.loads(METADATA_TEMPLATE.read_text(encoding="utf-8"))

    for label,text in (("README",readme),("CURRENT_STATUS",current),("manifest markdown",manifest_md),("readiness",readiness),("metadata guide",guide),("release notes",notes)):
        need(text,EXPECTED_TITLE,label,failures)

    need(readme,EXPECTED_MANUSCRIPT,"README",failures)
    need(readme,EXPECTED_RC,"README",failures)
    need(current,EXPECTED_RC,"CURRENT_STATUS",failures)
    need(readiness,EXPECTED_RC,"readiness",failures)
    need(guide,EXPECTED_RC,"metadata guide",failures)
    need(guide,"--stage pre-release","metadata guide",failures)
    need(guide,"--stage post-doi","metadata guide",failures)
    need(guide,EXPECTED_FINAL_TITLE_PAGE,"metadata guide",failures)
    need(notes,EXPECTED_RC,"release notes",failures)
    need(notes,EXPECTED_TAG,"release notes",failures)

    if manifest.get("submission_id")!=EXPECTED_SUBMISSION_ID:
        failures.append("machine manifest submission_id is not v0.4.0 rc1")
    if manifest.get("manuscript",{}).get("path")!=EXPECTED_MANUSCRIPT:
        failures.append("machine manifest manuscript path is not the frozen v0.4.0 candidate path")
    if manifest.get("manuscript",{}).get("title")!=EXPECTED_TITLE:
        failures.append("machine manifest title is stale")
    pkg=manifest.get("packaging",{})
    if pkg.get("release_candidate")!=EXPECTED_RC:
        failures.append("machine manifest release_candidate is stale")
    if pkg.get("expected_tag")!=EXPECTED_TAG:
        failures.append("machine manifest expected_tag is stale")
    if pkg.get("status")!="validated_candidate_ready_for_rc1":
        failures.append("machine manifest packaging status is not validated_candidate_ready_for_rc1")

    if template.get("package_version")!="v0.4.0":
        failures.append("metadata template package_version is stale")
    if template.get("manuscript_title")!=EXPECTED_TITLE:
        failures.append("metadata template title is stale")

    stale_current=[
        "Current release packaging target: `release/jae-v0.3.8-rc1`",
        "The current manuscript is `manuscript/MANUSCRIPT_DRAFT_V0_4_0.md`, titled **“Repeatable individual shapes",
    ]
    for phrase in stale_current:
        if phrase in readme:
            failures.append(f"README still asserts superseded current package: {phrase}")

    if failures:
        print("Active JAE v0.4.0 reference guard: BLOCKED")
        for x in failures: print(f" - {x}")
        return 1

    print("Active JAE v0.4.0 reference guard: PASS")
    print(f"Current package: {EXPECTED_RC}")
    print(f"Manuscript: {EXPECTED_MANUSCRIPT}")
    print(f"Final title page: {EXPECTED_FINAL_TITLE_PAGE}")
    print(f"Human metadata source: {EXPECTED_METADATA}")
    print(f"Expected tag: {EXPECTED_TAG}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
