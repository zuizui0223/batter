#!/usr/bin/env python3
"""Composite JAE v0.4.0 submission guard: original checks PLUS mandatory policy.

--audit returns exit 0 while reporting HOLD for CI visibility.
--strict returns nonzero on any HOLD. It NEVER submits, tags or uploads.
"""
from __future__ import annotations
import argparse,json,subprocess,sys
from pathlib import Path
from audit_jae_rc2_submission_handoff_2026_10_10 import check as rc2_audit
from audit_jae_v0_4_0_policy_signoff import evaluate as policy_evaluate
from audit_jae_v0_4_0_source_rights_signoff import source_rights_blockers
from audit_jae_v0_4_0_journal_facing_ai_disclosure import check as ai_document_audit

ROOT=Path(__file__).resolve().parents[1]
POLICY=ROOT/"submission/jae_v0_4_0_policy_signoff.json"
RIGHTS=ROOT/"submission/jae_v0_4_0_original_source_rights.json"
POLICY_TEMPLATE=ROOT/"submission/jae_v0_4_0_policy_signoff.template.json"
RIGHTS_TEMPLATE=ROOT/"submission/jae_v0_4_0_original_source_rights.template.json"

def evaluate():
    baseline=rc2_audit()
    ai_doc=ai_document_audit()
    policy_actual=POLICY.is_file()
    rights_actual=RIGHTS.is_file()
    policy=json.loads((POLICY if policy_actual else POLICY_TEMPLATE).read_text(encoding="utf-8"))
    rights=json.loads((RIGHTS if rights_actual else RIGHTS_TEMPLATE).read_text(encoding="utf-8"))
    rights_template=json.loads(RIGHTS_TEMPLATE.read_text(encoding="utf-8"))
    missing_policy=policy_evaluate(policy)
    missing_rights=source_rights_blockers(rights_template,rights)
    missing=[]
    if baseline["errors"]:
        missing.append("SOURCE_FROZEN_RC2_BLOB_TITLE_OR_FORMAT_MISMATCH")
    if baseline["final_human_or_release_blockers"]:
        missing.append("HUMAN_METADATA_LICENSE_ARCHIVE_DOI_OR_GENERATED_FILES_MISSING")
    if not policy_actual or missing_policy:
        missing.append("BES_INCLUSION_GENERATIVE_AI_AND_AUTHORS_HUMAN_SIGNOFF_MISSING")
    if not rights_actual or missing_rights:
        missing.append("DATA_REUSE_RIGHTS_BY_DOI_HUMAN_SIGNOFF_MISSING")
    if ai_doc["blockers"] or ai_doc["status"]!="MATCHED_DISCLOSURE_STILL_REQUIRES_HUMAN_JOURNAL_REVIEW":
        missing.append("AI_USAGE_CLASSIFICATION_OR_ACTUAL_JOURNAL_DISCLOSURE_UNRESOLVED")
    if not ai_doc["frozen_journal_manuscript_intact"]:
        missing.append("FROZEN_SCIENCE_HAS_UNAPPROVED_SHA_CHANGE")
    native={}
    if not missing:
        # No files are generated or uploaded by either native validator.
        for name in ("check_zenodo_release_ready_v0_4_0.py",
                     "check_jae_upload_ready_v0_4_0.py"):
            process=subprocess.run(
                [sys.executable,str(ROOT/"scripts"/name)],
                cwd=str(ROOT),text=True,capture_output=True,timeout=60)
            native[name]={"exit_code":process.returncode,
                           "check_result":"PASS" if process.returncode==0 else "BLOCKED"}
            if process.returncode!=0:
                missing.append("REPOSITORY_NATIVE_FINAL_GATE_BLOCKED:"+name)
    return {
        "status":"HOLD_EDITORIAL_OR_RELEASE_GATES" if missing
                 else "ALL_AUTOMATED_GATES_PASS_FINAL_HUMAN_JOURNAL_REVIEW_REQUIRED",
        "missing_blocker_classes":missing,
        "frozen_science_sha_verified":baseline["frozen_manuscript_identity_verified"],
        "human_metadata_release_blocker_count":len(baseline["final_human_or_release_blockers"]),
        "BES_policy_author_signoff_present":policy_actual,
        "BES_policy_unapproved_field_count":len(missing_policy),
        "ten_source_rights_signoff_present":rights_actual,
        "source_specific_rights_unapproved_count":len(missing_rights),
        "AI_disclosure_matched_approved_text_in_journal_doc":
            ai_doc["substantive_approved_disclosure_present_in_journal_section"],
        "AI_document_disclosure_status":ai_doc["status"],
        "native_zenodo_and_upload_gates":native,
        "artifact_uploaded":False,
        "journal_submitted":False,
        "DOI_minted":False,
        "original_data_recomputed":False
    }

def self_test():
    # Synthetic: no approval can be inferred from an unapproved template.
    assert policy_evaluate(json.loads(POLICY_TEMPLATE.read_text(encoding="utf-8")))
    template=json.loads(RIGHTS_TEMPLATE.read_text(encoding="utf-8"))
    assert source_rights_blockers(template,template)
    assert ai_document_audit()["journal_ready_claimed"] is False
    return "PASS_NO_FAKE_POLICY_OR_RIGHTS_APPROVAL_OR_JOURNAL_READY"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--strict",action="store_true",
                        help="Exit 1 if package remains blocked; never submit/upload")
    parser.add_argument("--out",default="JAE_V0_4_0_INTEGRATED_HUMAN_JOURNAL_READY_AUDIT.json")
    args=parser.parse_args()
    if args.self_test:
        print(json.dumps({"self_test":self_test(),"submitted":False}));return 0
    report=evaluate()
    report["synthetic_test"]=self_test()
    Path(args.out).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:report[k] for k in (
        "status","missing_blocker_classes",
        "human_metadata_release_blocker_count",
        "BES_policy_unapproved_field_count",
        "source_specific_rights_unapproved_count",
        "AI_document_disclosure_status",
        "native_zenodo_and_upload_gates")},sort_keys=True))
    if args.strict and report["status"]!="ALL_AUTOMATED_GATES_PASS_FINAL_HUMAN_JOURNAL_REVIEW_REQUIRED":
        return 1
    return 0

if __name__=="__main__":raise SystemExit(main())
