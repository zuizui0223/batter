#!/usr/bin/env python3
"""Human-only BES/JAE policy gate. Does not change scientific RC2 manuscript.

Missing/incomplete signoff is HOLD (never fake a declaration). No authored
AI-disclosure / inclusion statement or licence is inferred automatically.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TEMPLATE=ROOT/"submission/jae_v0_4_0_policy_signoff.template.json"
SIGNOFF=ROOT/"submission/jae_v0_4_0_policy_signoff.json"
GUIDE=ROOT/"submission/JAE_V0_4_0_AI_INCLUSION_AND_DATA_RIGHTS_POLICY_GATE_2026_10_10.md"
EXPECTED_SHA="c4ef51a7f3f291a6f203d303dbf73f5b54fb7683"

def evaluate(data):
    blocked=[]
    if data.get("schema_version")!=1 or data.get("package_version")!="v0.4.0":
        blocked.append("unapproved schema/version")
    if data.get("frozen_manuscript_git_blob")!=EXPECTED_SHA:
        blocked.append("incorrect immutable manuscript reference")
    inclusion=data.get("inclusion_statement") or {}
    if inclusion.get("reviewed_and_factually_approved_by_authors") is not True:
        blocked.append("Statement on inclusion not approved")
    if len(str(inclusion.get("statement_for_submission") or "").strip())<30:
        blocked.append("Statement on inclusion text missing")
    ai=data.get("generative_ai") or {}
    usage=ai.get("human_approved_use_classification")
    if usage not in {"SUBSTANTIVE","LANGUAGE_ONLY","NOT_USED"}:
        blocked.append("AI usage scope not factually confirmed")
    if ai.get("actual_tasks_and_tools_verified_by_authors") is not True:
        blocked.append("AI tasks/tools not factually verified")
    if ai.get("factual_claims_and_code_checked_by_responsible_authors") is not True:
        blocked.append("human responsibility/source and code verification not signed off")
    placement=ai.get("disclosure_placement")
    if usage=="SUBSTANTIVE":
        if placement not in {"METHODS","ACKNOWLEDGEMENTS"}:
            blocked.append("required substantive AI disclosure placement not approved")
        if len(str(ai.get("author_approved_disclosure_text") or "").strip())<50:
            blocked.append("required substantive AI disclosure details unapproved")
    if usage in {"LANGUAGE_ONLY","NOT_USED"} and placement!="NOT_REQUIRED_LANGUAGE_ONLY_OR_NO_USE":
        blocked.append("non-substantive/no-AI classification not confirmed")
    rights=data.get("third_party_data_reuse") or {}
    for k in ("source_permissions_and_licenses_reviewed_by_humans",
              "original_datasets_attributed_and_necessary_permissions_confirmed",
              "restricted_reuse_problems_resolved_or_documented"):
        if rights.get(k) is not True:
            blocked.append("third-party source rights approval missing: "+k)
    authors=data.get("author_approval") or {}
    for k in ("all_authors_approved_final_manuscript",
              "contributors_credit_and_conflicts_reviewed"):
        if authors.get(k) is not True:
            blocked.append("human author approval missing: "+k)
    return blocked

def test():
    assert TEMPLATE.is_file() and GUIDE.is_file()
    original=json.loads(TEMPLATE.read_text(encoding="utf-8"))
    assert original["frozen_manuscript_git_blob"]==EXPECTED_SHA
    assert original["generative_ai"]["human_approved_use_classification"]=="UNREVIEWED"
    assert len(evaluate(original))>=8, "template must fail closed"
    example=json.loads(json.dumps(original))
    example["inclusion_statement"]["reviewed_and_factually_approved_by_authors"]=True
    example["inclusion_statement"]["statement_for_submission"]="Author reviewed this fictional secondary data inclusion statement"
    a=example["generative_ai"]
    a.update({"human_approved_use_classification":"SUBSTANTIVE",
              "actual_tasks_and_tools_verified_by_authors":True,
              "factual_claims_and_code_checked_by_responsible_authors":True,
              "disclosure_placement":"ACKNOWLEDGEMENTS",
              "author_approved_disclosure_text":"Fictional test only: substantive AI used for drafting and code help, human-verified"})
    for k in example["third_party_data_reuse"]:
        if k!="none": example["third_party_data_reuse"][k]=True
    for k in example["author_approval"]:
        example["author_approval"][k]=True
    assert evaluate(example)==[]
    example["generative_ai"]["author_approved_disclosure_text"]=""
    assert "required substantive AI disclosure details unapproved" in evaluate(example)
    return "PASS_HOLD_UNAPPROVED_AND_VALIDATE_HUMAN_CONSENT_CONDITIONALS"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--out",default="JAE_V0_4_0_AUTHOR_POLICY_COMPLIANCE_RECEIPT.json")
    a=ap.parse_args()
    if a.self_test:
        print(json.dumps({"synthetic_policy_test":test(),
                          "human_declarations_created":False}));return 0
    guard=test()
    actual=SIGNOFF.is_file()
    data=json.loads((SIGNOFF if actual else TEMPLATE).read_text(encoding="utf-8"))
    holds=evaluate(data)
    state="HOLD_HUMAN_POLICY_SIGNOFF" if not actual or holds else "AUTHOR_RECORDED_APPROVAL_NEEDS_JOURNAL_CONTENT_REVIEW"
    result={"status":state,"frozen_manuscript_blob":EXPECTED_SHA,
            "human_signoff_file_present":actual,
            "human_policy_gates_unapproved":holds,
            "BES_inclusion_statement_required":True,
            "BES_substantive_generative_AI_disclosure_required_if_used":True,
            "BES_third_party_data_reuse_rights_review_required":True,
            "repository_scientific_data_modified":False,
            "author_factual_declaration_generated":False,
            "journal_submission_performed":False,
            "synthetic_policy_guard":guard}
    Path(a.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":state,
          "human_signoff_file_present":actual,
          "n_human_gates_unapproved":len(holds),
          "human_policy_gates_unapproved":holds,
          "no_declarations_auto_generated":True},sort_keys=True))
    return 0

if __name__=="__main__":sys.exit(main())
