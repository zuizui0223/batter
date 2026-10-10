#!/usr/bin/env python3
"""Non-invasive JAE v0.4.0 rc2 handoff preflight; never fills human metadata.

Safety contract:
 - verify frozen JAE manuscript Git blob against its committed manifest;
 - validate optional short cover letter <=500 whitespace words;
 - report genuinely absent human / license / release DOI items as HOLD;
 - DO NOT mint tag, fill author/ORCID/affiliation, edit RC2 or send submission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"SUBMISSION_MANIFEST_JAE_V0_4_0.json"
MANUSCRIPT=ROOT/"manuscript/MANUSCRIPT_DRAFT_V0_4_0.md"
TEMPLATE=ROOT/"submission/jae_v0_4_0_metadata.template.json"
ACTUAL_METADATA=ROOT/"submission/jae_v0_4_0_metadata.json"
TITLE_PAGE=ROOT/"manuscript/TITLE_PAGE_V0_4_0.md"
COVER=ROOT/"submission/JAE_V0_4_0_EDITORIAL_SHORT_COVER_LETTER_PROPOSAL_2026_10_10.md"
LICENSE=ROOT/"LICENSE"
CITATION=ROOT/"CITATION.cff"
MAX_ARTICLE_WORDS=8500
MAX_ABSTRACT_WORDS=350
MAX_COVER_WORDS=500
EXPECTED_MANUSCRIPT_BLOB="c4ef51a7f3f291a6f203d303dbf73f5b54fb7683"
EXPECTED_TITLE="Persistent individual vertical strategies need not partition three-dimensional space in two tropical bat species"


def git_blob_sha(payload:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(payload)).encode()+b"\x00"+payload).hexdigest()


def cover_body(path:Path)->str:
    txt=path.read_text(encoding="utf-8")
    match=re.search(r"(?ms)^---\s*\n(.*?)\n---\s*$",txt)
    if match is None:
        raise ValueError("cover draft body must have two Markdown --- delimiters")
    return match.group(1).strip()


def check()->dict:
    problems=[]
    for p in (MANIFEST,MANUSCRIPT,TEMPLATE,COVER):
        if not p.is_file():
            problems.append("missing handoff input: "+str(p.relative_to(ROOT)))
    if problems:
        return {"status":"STOP_REPOSITORY_INPUT_MISSING","errors":problems}

    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    m=MANUSCRIPT.read_bytes()
    sha=git_blob_sha(m)
    if sha != EXPECTED_MANUSCRIPT_BLOB or manifest["manuscript"].get("blob_sha")!=sha:
        problems.append("FROZEN_MANUSCRIPT_BLOB_SHA_MISMATCH")
    if manifest["manuscript"].get("title")!=EXPECTED_TITLE:
        problems.append("FROZEN_TITLE_MISMATCH")
    if EXPECTED_TITLE not in m.decode("utf-8"):
        problems.append("FROZEN_TITLE_NOT_IN_MANUSCRIPT")
    if manifest.get("submission_id")!="batter-jae-v0.4.0-rc2":
        problems.append("RELEASE_CANDIDATE_MANIFEST_ID_MISMATCH")

    abstract=int(manifest["manuscript"].get("abstract_words",100000))
    mcount=int(manifest["manuscript"].get("ci_word_estimate",100000))
    if abstract>MAX_ABSTRACT_WORDS:
        problems.append("REPO_ABSTRACT_COUNT_OVER_JAE_LIMIT")
    if mcount>MAX_ARTICLE_WORDS:
        problems.append("REPO_CI_MANUSCRIPT_ESTIMATE_OVER_JAE_LIMIT")

    short=cover_body(COVER)
    cover_words=len(short.split())
    if cover_words>MAX_COVER_WORDS:
        problems.append("OPTIONAL_COVER_LETTER_OVER_500_WHITESPACE_WORDS")
    if EXPECTED_TITLE not in short:
        problems.append("OPTIONAL_COVER_LETTER_TITLE_MISMATCH")
    if "Dear Editors" not in short:
        problems.append("COVER_LETTER_OPENING_MISSING")
    if re.search(r"(?i)\[(?:INSERT|TBD|TODO)",short):
        problems.append("OPTIONAL_COVER_DRAFT_CONTAINS_PLACEHOLDER")

    tmpl=json.loads(TEMPLATE.read_text(encoding="utf-8"))
    if tmpl.get("manuscript_title")!=EXPECTED_TITLE or tmpl.get("package_version")!="v0.4.0":
        problems.append("METADATA_TEMPLATE_TITLE_OR_VERSION_MISMATCH")
    blocked=[]
    if not ACTUAL_METADATA.exists():
        blocked.append("human-approved submission/jae_v0_4_0_metadata.json is absent")
    else:
        meta=json.loads(ACTUAL_METADATA.read_text(encoding="utf-8"))
        if re.search(r"\[INSERT",json.dumps(meta)):
            blocked.append("human metadata still has unapproved placeholders")
        if not meta.get("archive_doi"):
            blocked.append("versioned archive_doi not recorded")
    if not LICENSE.exists():
        blocked.append("one rights-holder-approved root LICENSE file is absent")
    if not CITATION.exists():
        blocked.append("generated final CITATION.cff not yet present")
    if not TITLE_PAGE.exists():
        blocked.append("generated final human-approved title page not yet present")

    return {
      "status":"STOP_FROZEN_ASSET_OR_EDITORIAL_MISMATCH" if problems
               else "HOLD_HUMAN_METADATA_LICENSE_DOI" if blocked
               else "HOLD_REQUIRES_FINAL_RELEASE_GATES",
      "repo_manifest_submission_id":manifest["submission_id"],
      "immutable_manuscript_blob_sha":sha,
      "frozen_manuscript_identity_verified":not any(x.startswith(("FROZEN_","RELEASE_")) for x in problems),
      "repo_abstract_words_from_existing_manifest":abstract,
      "repo_manuscript_words_before_final_titlepage":mcount,
      "journal_current_max_abstract":MAX_ABSTRACT_WORDS,
      "journal_current_max_research_article":MAX_ARTICLE_WORDS,
      "optional_short_letter_whitespace_words":cover_words,
      "journal_current_max_optional_cover_letter":MAX_COVER_WORDS,
      "final_human_or_release_blockers":blocked,
      "errors":problems,
      "human_author_metadata_filled_or_generated":False,
      "release_tag_or_DOI_minted":False,
      "journal_submission_performed":False,
      "frozen_scientific_estimates_recomputed":False,
      "note":"Format checks and existing manifest counts only. Use existing strict v0.4.0 final-upload/release validators after approved human metadata."
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--out",default="JAE_V0_4_0_RC2_HANDOFF_PREFLIGHT_2026_10_10.json")
    args=ap.parse_args()
    if args.self_test:
        assert git_blob_sha(b"hello")==hashlib.sha1(b"blob 5\x00hello").hexdigest()
        assert len("Dear Editors,\nThank you.".split())==3
        print(json.dumps({"synthetic_git_blob_and_word_check":"PASS","human_metadata_generated":False}))
        return 0
    result=check()
    Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in (
        "status","frozen_manuscript_identity_verified",
        "repo_abstract_words_from_existing_manifest",
        "repo_manuscript_words_before_final_titlepage",
        "optional_short_letter_whitespace_words",
        "final_human_or_release_blockers","errors"
    )},sort_keys=True))
    return 1 if result["status"].startswith("STOP") else 0


if __name__=="__main__":
    sys.exit(main())
