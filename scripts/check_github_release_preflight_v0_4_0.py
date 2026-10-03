#!/usr/bin/env python3
"""Fail-closed preflight for the JAE v0.4.0 GitHub release intended for Zenodo.

This script validates the prepared release candidate but never creates a tag or release.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXPECTED_VERSION="v0.4.0"
EXPECTED_TAG="jae-v0.4.0"
EXPECTED_CANDIDATE="release/jae-v0.4.0-rc1"
METADATA=ROOT/"submission"/"jae_v0_4_0_metadata.json"
CFF=ROOT/"CITATION.cff"
NOTES=ROOT/"RELEASE_NOTES_JAE_V0_4_0.md"
MANIFEST=ROOT/"SUBMISSION_MANIFEST_JAE_V0_4_0.json"
TITLE_PAGE=ROOT/"manuscript"/"TITLE_PAGE_V0_4_0.md"
LICENSE_CANDIDATES=("LICENSE","LICENSE.md","LICENSE.txt")
PLACEHOLDER=re.compile(r"\[INSERT\b|\bTBD\b|\bTODO\b",re.IGNORECASE)

def git(*args:str)->str:
    return subprocess.check_output(["git",*args],cwd=ROOT,text=True).strip()

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--candidate-ref",default=EXPECTED_CANDIDATE)
    ap.add_argument("--no-fetch",action="store_true")
    args=ap.parse_args()
    candidate_ref=str(args.candidate_ref)
    failures=[]
    for path in (METADATA,CFF,NOTES,MANIFEST,TITLE_PAGE):
        if not path.is_file():
            failures.append(f"missing required pre-release file: {path.relative_to(ROOT)}")
    licenses=[ROOT/name for name in LICENSE_CANDIDATES if (ROOT/name).is_file()]
    if len(licenses)!=1:
        failures.append(f"expected exactly one LICENSE file among {LICENSE_CANDIDATES}; found {len(licenses)}")
    if failures:
        print("GitHub/Zenodo v0.4.0 release preflight: BLOCKED")
        for item in failures: print(f" - {item}")
        return 1

    metadata=json.loads(METADATA.read_text(encoding="utf-8"))
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    cff=CFF.read_text(encoding="utf-8")
    notes=NOTES.read_text(encoding="utf-8")
    title=TITLE_PAGE.read_text(encoding="utf-8")

    if metadata.get("package_version")!=EXPECTED_VERSION:
        failures.append(f"metadata package_version must be {EXPECTED_VERSION}")
    if metadata.get("manuscript_title")!="Persistent individual vertical strategies need not partition three-dimensional space in bats":
        failures.append("metadata manuscript_title does not match v0.4.0 title")
    if str(metadata.get("archive_doi","")).strip():
        failures.append("archive_doi must still be empty before the Zenodo-minting GitHub release")
    if manifest.get("submission_id")!="batter-jae-v0.4.0-rc1":
        failures.append("machine manifest is not the v0.4.0 rc1 submission package")
    if manifest.get("manuscript",{}).get("path")!="manuscript/MANUSCRIPT_DRAFT_V0_4_0.md":
        failures.append("machine manifest does not point to the frozen v0.4.0-candidate manuscript path")

    for label,text in (("metadata JSON",json.dumps(metadata)),("CITATION.cff",cff),("release notes",notes)):
        if PLACEHOLDER.search(text):
            failures.append(f"{label} still contains placeholder text")
    if not re.search(r"(?m)^version:\s*['\"]?v0\.4\.0['\"]?\s*$",cff):
        failures.append("CITATION.cff version is not v0.4.0")
    if "versioned Zenodo DOI" not in title:
        failures.append("pre-release title page does not state that the Zenodo DOI is pending")

    try:
        if not args.no_fetch:
            git("fetch","origin",candidate_ref,"--no-tags")
        head=git("rev-parse","HEAD")
        candidate=git("rev-parse",f"origin/{candidate_ref}")
        if head!=candidate:
            failures.append(f"checked-out HEAD {head} does not match origin/{candidate_ref} {candidate}")
    except Exception as exc:
        failures.append(f"could not verify release candidate identity: {exc}")

    try:
        if git("status","--porcelain"):
            failures.append("working tree is not clean")
    except Exception as exc:
        failures.append(f"could not inspect working tree: {exc}")

    if failures:
        print("GitHub/Zenodo v0.4.0 release preflight: BLOCKED")
        for item in failures: print(f" - {item}")
        return 1

    print("GitHub/Zenodo v0.4.0 release preflight: READY")
    print(f"Release version: {EXPECTED_VERSION}")
    print(f"Recommended Git tag: {EXPECTED_TAG}")
    print(f"Candidate: {candidate_ref}")
    print("This script does not create or publish the release.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
