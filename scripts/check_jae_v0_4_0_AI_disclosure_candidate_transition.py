#!/usr/bin/env python3
"""Check a distinct human-approved JAE AI disclosure candidate WITHOUT changing RC2.

Input: original immutable RC2 manuscript + OPTIONAL separate candidate file and
human policy signoff. A PASS means only the approved paragraph was inserted;
it does not pass journal submission/release or establish human analytical QA.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from audit_jae_v0_4_0_policy_signoff import evaluate as policy_evaluate

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=ROOT/"manuscript/MANUSCRIPT_DRAFT_V0_4_0.md"
CANDIDATE=ROOT/"manuscript/MANUSCRIPT_DRAFT_V0_4_0_AI_DISCLOSURE_CANDIDATE.md"
POLICY=ROOT/"submission/jae_v0_4_0_policy_signoff.json"
FROZEN_SHA="c4ef51a7f3f291a6f203d303dbf73f5b54fb7683"
METHODS="## Materials and Methods\n"
ACK="## Acknowledgements\n"
ACK_US="## Acknowledgments\n"
DATA_SECTION="## Data and code availability\n"
UNVERIFIED=re.compile(r"(?i)\[INSERT\b|\bTODO\b|\bTBD\b|\[SPECIFY\b|\[DESCRIBE\b|\[VERIFY\b")

def git_sha(src):
    return hashlib.sha1(b"blob "+str(len(src)).encode()+b"\0"+src).hexdigest()

def candidate_forms(original,text,where):
    """All allowable editorial modifications, exactly once at fixed headings."""
    if not text or UNVERIFIED.search(text):return []
    if where=="METHODS":
        if original.count(METHODS)!=1:return []
        return [original.replace(METHODS,METHODS+"\n"+text+"\n",1)]
    if where=="ACKNOWLEDGEMENTS":
        forms=[]
        for key in (ACK,ACK_US):
            if original.count(key)==1:
                forms.append(original.replace(key,key+"\n"+text+"\n",1))
        if not forms and original.count(DATA_SECTION)==1:
            # Keep the original textual body, including any trailing newline.
            new=ACK+"\n"+text+"\n\n"
            forms.append(original.replace(DATA_SECTION,new+DATA_SECTION,1))
        return forms
    return []

def validate_candidate(original,candidate,approved,where):
    forms=candidate_forms(original,approved,where)
    if not forms:
        return False,"INVALID_PLACEMENT_OR_PLACEHOLDER"
    if candidate not in forms:
        return False,"STOP_UNAUTHORIZED_CANDIDATE_CONTENT_DIFF"
    if candidate==original:
        return False,"NO_DISCLOSURE_INSERTION"
    return True,"ALLOWED_EXACT_ONE_DISCLOSURE_PARAGRAPH_INSERTION_ONLY"

def test():
    source="## Materials and Methods\nOriginal science: effect 4/4.\n## Results\nNo changes.\n## Data and code availability\nArchived.\n"
    disclosure="OpenAI ChatGPT assisted author-reviewed scientific writing and script development."
    m=candidate_forms(source,disclosure,"METHODS")[0]
    assert validate_candidate(source,m,disclosure,"METHODS")[0]
    assert not validate_candidate(source,m.replace("4/4","3/4"),disclosure,"METHODS")[0]
    assert not validate_candidate(source,source,disclosure,"METHODS")[0]
    assert not validate_candidate(source,m,disclosure,"ACKNOWLEDGEMENTS")[0]
    a=candidate_forms(source,disclosure,"ACKNOWLEDGEMENTS")[0]
    assert validate_candidate(source,a,disclosure,"ACKNOWLEDGEMENTS")[0]
    assert not validate_candidate(source,a+"NEW RESULT",disclosure,"ACKNOWLEDGEMENTS")[0]
    assert not candidate_forms(source,"Authors [SPECIFY verification]","METHODS")
    assert git_sha(b"hello")==hashlib.sha1(b"blob 5\0hello").hexdigest()
    return "PASS_ONLY_APPROVED_DISCLOSURE_INSERTION_AND_NO_OTHER_SCIENCE_DIFF"

def check():
    original=ORIGINAL.read_bytes()
    digest=git_sha(original)
    original_text=original.decode("utf-8")
    blockers=[]
    if digest!=FROZEN_SHA:
        blockers.append("STOP_ORIGINAL_RC2_SCIENTIFIC_SHA_CHANGED")
    exists_policy=POLICY.is_file()
    exists_candidate=CANDIDATE.is_file()
    if not exists_policy:
        blockers.append("HOLD_REAL_HUMAN_POLICY_APPROVAL_MISSING")
    if not exists_candidate:
        blockers.append("HOLD_SEPARATE_VERSIONED_MANUSCRIPT_CANDIDATE_MISSING")
    signoff={}
    if exists_policy:
        signoff=json.loads(POLICY.read_text(encoding="utf-8"))
        if policy_evaluate(signoff):
            blockers.append("HOLD_POLICY_SIGNOFF_NOT_COMPLETE")
    ai=signoff.get("generative_ai") or {}
    classification=ai.get("human_approved_use_classification","UNREVIEWED")
    placement=str(ai.get("disclosure_placement") or "")
    approved=str(ai.get("author_approved_disclosure_text") or "").strip()
    candidate_sha=None
    insertion_ok=False
    if exists_candidate:
        raw=CANDIDATE.read_bytes()
        candidate_sha=git_sha(raw)
        if not exists_policy:
            blockers.append("NO_AUTHORIZED_DISCLOSURE_TO_COMPARE")
        elif classification!="SUBSTANTIVE":
            blockers.append("CANDIDATE_NOT_AUTHORIZED_UNDER_NON_SUBSTANTIVE_CLASSIFICATION")
        else:
            insertion_ok,verdict=validate_candidate(
                original_text,raw.decode("utf-8"),approved,placement)
            if not insertion_ok:blockers.append(verdict)
    if exists_policy and classification not in ("SUBSTANTIVE","LANGUAGE_ONLY","NOT_USED"):
        blockers.append("HUMAN_AI_USE_CLASSIFICATION_NOT_FINAL")
    if exists_policy and classification=="SUBSTANTIVE" and not exists_candidate:
        blockers.append("SUBSTANTIVE_AI_TEXT_NOT_YET_IN_VERSIONED_JOURNAL_SOURCE")
    if exists_policy and classification in ("LANGUAGE_ONLY","NOT_USED") and not exists_candidate:
        # Not a failed disclosure candidate per se. For this specialized gate
        # no modified draft is required; downstream author signoff still applies.
        blockers=[z for z in blockers if z!="HOLD_SEPARATE_VERSIONED_MANUSCRIPT_CANDIDATE_MISSING"]
    status=("STOP_ORIGINAL_SCIENTIFIC_BLOB_CHANGED" if digest!=FROZEN_SHA
        else "STOP_UNAUTHORIZED_CANDIDATE_CONTENT_DIFF" if exists_candidate and not insertion_ok
        else "AUTHOR_APPROVED_EXACT_DISCLOSURE_INSERTION_CANDIDATE_ONLY" if
             exists_candidate and insertion_ok and not blockers
        else "HUMAN_APPROVED_NON_SUBSTANTIVE_USAGE_CANDIDATE_NOT_NEEDED" if
             exists_policy and classification in ("LANGUAGE_ONLY","NOT_USED") and not blockers
        else "HOLD_HUMAN_AI_USE_AND_VERSIONED_CANDIDATE")
    return {
      "status":status,
      "frozen_rc2_scientific_SHA_valid":digest==FROZEN_SHA,
      "immutable_rc2_sha":digest,
      "separate_candidate_exists":exists_candidate,
      "candidate_git_blob_sha":candidate_sha,
      "policy_author_signoff_exists":exists_policy,
      "human_AI_classification":classification,
      "human_disclosure_placement":placement or None,
      "only_human_approved_paragraph_added_to_science":insertion_ok,
      "unapproved_or_missing_requirements":blockers,
      "new_release_candidate_needed_if_changed":bool(insertion_ok),
      "official_JAE_release_or_upload_gate_passed":False,
      "manuscript_or_journal_files_written":False,
      "journal_submitted":False,
      "synthetic_test":test(),
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--out",default="JAE_RC2_AI_DISCLOSURE_REVISION_CANDIDATE_GATE.json")
    args=parser.parse_args()
    if args.self_test:
        print(json.dumps({"self_test":test(),"human_AI_scope_inferred":False}));return
    receipt=check()
    Path(args.out).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:receipt[k] for k in (
        "status","frozen_rc2_scientific_SHA_valid",
        "policy_author_signoff_exists","separate_candidate_exists",
        "only_human_approved_paragraph_added_to_science",
        "unapproved_or_missing_requirements")},sort_keys=True))
if __name__=="__main__":main()
