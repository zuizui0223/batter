#!/usr/bin/env python3
"""Prevent signoff-only AI compliance: verify author-approved text in a journal section.

No manuscript edits, animal records, reviewer claims or release actions.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from audit_jae_v0_4_0_policy_signoff import evaluate as policy_blockers

ROOT=Path(__file__).resolve().parents[1]
MANUSCRIPT=ROOT/"manuscript/MANUSCRIPT_DRAFT_V0_4_0.md"
TITLE_PAGE=ROOT/"manuscript/TITLE_PAGE_V0_4_0.md"
SIGNOFF=ROOT/"submission/jae_v0_4_0_policy_signoff.json"
TEMPLATE=ROOT/"submission/jae_v0_4_0_policy_signoff.template.json"
EXPECTED_SHA="c4ef51a7f3f291a6f203d303dbf73f5b54fb7683"
AI_MARKER=re.compile(
    r"(?i)\b(?:ChatGPT|OpenAI|generative[\s-]+AI|large[\s-]+language[\s-]+model)\b"
)

def sha_of_git_blob(payload):
    return hashlib.sha1(b"blob "+str(len(payload)).encode()+b"\x00"+payload).hexdigest()

def normalize_prose(s):
    # Whitespace and Markdown emphasis normalization ONLY.
    return " ".join(re.sub(r"[*_]+"," ",s).replace(chr(96)," ").split()).casefold()

def section(document,which):
    names=("Acknowledgements","Acknowledgments") if which=="ACKNOWLEDGEMENTS" else ("Materials and Methods",)
    for name in names:
        match=re.search(r"(?m)^##\s+"+re.escape(name)+r"\s*$",document)
        if match:
            tail=document[match.end():]
            end=re.search(r"(?m)^##\s+",tail)
            return tail[:end.start()] if end else tail
    return ""

def disclosure_present(text,placement,manuscript,title_page=""):
    needle=normalize_prose(text)
    if not needle:return False,"EMPTY_APPROVED_DISCLOSURE"
    if placement=="METHODS":
        return needle in normalize_prose(section(manuscript,"METHODS")),"MANUSCRIPT_METHODS"
    if placement=="ACKNOWLEDGEMENTS":
        if needle in normalize_prose(section(manuscript,"ACKNOWLEDGEMENTS")):
            return True,"MANUSCRIPT_ACKNOWLEDGEMENTS"
        if needle in normalize_prose(section(title_page,"ACKNOWLEDGEMENTS")):
            return True,"TITLE_PAGE_ACKNOWLEDGEMENTS"
        return False,"NO_APPROVED_ACKNOWLEDGEMENT_PARAGRAPH"
    return False,"INVALID_APPROVED_PLACEMENT"

def self_test():
    x="## Materials and Methods\nFirst.\n### AI disclosure\nWe used ChatGPT for coding and writing.\n## Results\n"
    assert "AI disclosure" in section(x,"METHODS")
    assert disclosure_present("We used ChatGPT for coding and writing.","METHODS",x)[0]
    assert not disclosure_present("We used ChatGPT for coding and writing.","METHODS","## Materials and Methods\nNothing\n")[0]
    title="## Acknowledgements\n**We used ChatGPT for coding and writing.**\n## Funding\n"
    assert disclosure_present("We used ChatGPT for coding and writing.","ACKNOWLEDGEMENTS",x,title)[0]
    assert not disclosure_present("We used ChatGPT for coding and writing.","METHODS",title)[0]
    assert sha_of_git_blob(b"hello")==hashlib.sha1(b"blob 5\x00hello").hexdigest()
    return "PASS_SECTION_MATCH_AND_FALSE_GREEN_PREVENTION"

def check():
    original=MANUSCRIPT.read_bytes()
    sha=sha_of_git_blob(original)
    text=original.decode("utf-8")
    title=TITLE_PAGE.read_text(encoding="utf-8") if TITLE_PAGE.is_file() else ""
    actual=SIGNOFF.is_file()
    signed=json.loads((SIGNOFF if actual else TEMPLATE).read_text(encoding="utf-8"))
    ai=signed.get("generative_ai") or {}
    klass=str(ai.get("human_approved_use_classification") or "UNREVIEWED")
    validation=policy_blockers(signed)
    problems=[]
    if sha!=EXPECTED_SHA:
        problems.append("FROZEN_MANUSCRIPT_SHA_CHANGED_REQUIRES_NEW_VERSION_AND_REVIEW")
    if not actual:
        problems.append("HUMAN_POLICY_SIGNOFF_NOT_PRESENT")
    if actual and validation:
        problems.append("POLICY_SIGNOFF_FIELDS_STILL_UNAPPROVED")
    valid_doc=False
    where="NO_APPROVED_DISCLOSURE"
    if klass=="SUBSTANTIVE":
        valid_doc,where=disclosure_present(
            str(ai.get("author_approved_disclosure_text") or ""),
            str(ai.get("disclosure_placement") or ""),text,title)
        if not valid_doc:
            problems.append("SUBSTANTIVE_AI_DISCLOSURE_MISSING_FROM_METHODS_OR_ACKNOWLEDGEMENTS")
    elif klass in ("LANGUAGE_ONLY","NOT_USED"):
        # A human must actually verify the true usage history.
        problems.append("NONSUBSTANTIVE_AI_CLASSIFICATION_NEEDS_FACTUAL_HISTORY_REVIEW")
    else:
        problems.append("AI_INVOLVEMENT_CLASSIFICATION_AWAITING_HUMAN_REVIEW")
    status=("HOLD_HUMAN_POLICY_AND_JOURNAL_DISCLOSURE" if not actual
            else "STOP_CHANGED_FROZEN_RC2_REQUIRES_VERSIONED_CANDIDATE" if sha!=EXPECTED_SHA
            else "HOLD_DISCLOSURE_CONTENT_OR_POLICY" if problems
            else "MATCHED_DISCLOSURE_STILL_REQUIRES_HUMAN_JOURNAL_REVIEW")
    return {
        "status":status,
        "original_journal_manuscript_blob":sha,
        "frozen_journal_manuscript_intact":sha==EXPECTED_SHA,
        "explicit_AI_keyword_matches_in_frozen_journal_text":len(AI_MARKER.findall(text)),
        "human_policy_signoff_present":actual,
        "human_recorded_AI_classification":klass,
        "substantive_approved_disclosure_present_in_journal_section":valid_doc,
        "required_document_location":where,
        "human_signoff_fields_incomplete":len(validation),
        "blockers":problems,
        "journal_ready_claimed":False,
        "AI_disclosure_text_inserted_or_generated":False,
        "scientific_data_or_results_changed":False,
        "test":self_test(),
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",default="JAE_RC2_JOURNAL_FACING_AI_DISCLOSURE_GATE.json")
    args=p.parse_args()
    if args.self_test:
        print(json.dumps({"self_test":self_test(),"AI_text_inserted":False}));return
    result=check()
    Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:result[k] for k in (
        "status","frozen_journal_manuscript_intact",
        "explicit_AI_keyword_matches_in_frozen_journal_text",
        "human_policy_signoff_present",
        "substantive_approved_disclosure_present_in_journal_section",
        "blockers")},sort_keys=True))

if __name__=="__main__":main()
