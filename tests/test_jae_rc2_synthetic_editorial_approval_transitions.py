#!/usr/bin/env python3
"""Fictional editorial approval state-machine tests; no real approval assertions.

Only test-only fixtures in temporary folders. No bat outcomes, journal actions
or release/DOI calls. Real frozen JAE RC2 manuscript only READ for diff tests.
"""
from __future__ import annotations
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

import audit_jae_v0_4_0_policy_signoff as policy
import audit_jae_v0_4_0_source_rights_signoff as rights
import audit_jae_v0_4_0_journal_facing_ai_disclosure as disclosure
import check_jae_v0_4_0_AI_disclosure_candidate_transition as candidate
import check_jae_v0_4_0_integrated_final_editorial_gate as combined

FROZEN_SHA="c4ef51a7f3f291a6f203d303dbf73f5b54fb7683"
DUMMY_TEXT=(
    "Fictional test paragraph ONLY: the hypothetical authors used a "
    "language model to assist drafting and verified specified content."
)

def mocked_policy(substantive=True):
    obj=json.loads(policy.TEMPLATE.read_text(encoding="utf-8"))
    obj["inclusion_statement"].update({
        "reviewed_and_factually_approved_by_authors":True,
        "statement_for_submission":"Fictional test inclusion statement, not a real researcher declaration.",
    })
    ai=obj["generative_ai"]
    ai.update({
        "human_approved_use_classification":"SUBSTANTIVE" if substantive else "LANGUAGE_ONLY",
        "actual_tasks_and_tools_verified_by_authors":True,
        "factual_claims_and_code_checked_by_responsible_authors":True,
        "disclosure_placement":"METHODS" if substantive else "NOT_REQUIRED_LANGUAGE_ONLY_OR_NO_USE",
        "author_approved_disclosure_text":DUMMY_TEXT if substantive else "",
        "usage_and_human_validation_summary":"Fictional example for code unit tests only",
    })
    obj["third_party_data_reuse"].update({
        "source_permissions_and_licenses_reviewed_by_humans":True,
        "original_datasets_attributed_and_necessary_permissions_confirmed":True,
        "restricted_reuse_problems_resolved_or_documented":True,
    })
    obj["author_approval"].update({
        "all_authors_approved_final_manuscript":True,
        "contributors_credit_and_conflicts_reviewed":True,
    })
    return obj

def mocked_rights():
    template=json.loads(rights.TEMPLATE.read_text(encoding="utf-8"))
    source=copy.deepcopy(template)
    for row in source["frozen_source_DOIs"]:
        row.update({
            "exact_dataset_license":"CC-BY-4.0" if
                row["doi"]=="10.5281/zenodo.7535030" else "CC0-1.0",
            "licence_evidence_url":"https://example.org/FAKE-TEST-ONLY",
            "source_citation_attribution_verified_by_authors":True,
            "intended_reuse_covered_by_license_or_permission":True,
            "permission_required_under_actual_terms":"NO",
            "owner_contact_or_credit_assessed_by_authors":True,
            "source_rights_notes":"Fictional source-use review, test fixture only",
        })
    source.update({
        "authors_final_permissions_checked":True,
        "authors_final_signoff_date":"2026-10-11",
    })
    return source

class FrozenScienceSyntheticTransitions(unittest.TestCase):
    def test_exact_frozen_manuscript_blob_and_only_approved_paragraph(self):
        original=candidate.ORIGINAL.read_bytes()
        self.assertEqual(candidate.git_sha(original),FROZEN_SHA)
        original=original.decode("utf-8")
        self.assertNotIn(DUMMY_TEXT,original)
        for where in ("METHODS","ACKNOWLEDGEMENTS"):
            approved_variants=candidate.candidate_forms(original,DUMMY_TEXT,where)
            self.assertTrue(approved_variants)
            for form in approved_variants:
                self.assertTrue(candidate.validate_candidate(
                    original,form,DUMMY_TEXT,where)[0])
                self.assertNotEqual(form,original)
                self.assertFalse(candidate.validate_candidate(
                    original,form.replace("four", "three",1),DUMMY_TEXT,where)[0])
                self.assertFalse(candidate.validate_candidate(
                    original,form+"\nNew unsupported result.\n",DUMMY_TEXT,where)[0])
                self.assertFalse(candidate.validate_candidate(
                    original,form,DUMMY_TEXT,("ACKNOWLEDGEMENTS" if where=="METHODS" else "METHODS"))[0])
        self.assertFalse(candidate.candidate_forms(original,
               "Human authors [SPECIFY WHO VERIFIED]","METHODS"))
        self.assertEqual(candidate.git_sha(candidate.ORIGINAL.read_bytes()),FROZEN_SHA)

    def test_public_templates_fail_closed_but_fictional_fixtures_are_supported(self):
        original=json.loads(policy.TEMPLATE.read_text(encoding="utf-8"))
        template=json.loads(rights.TEMPLATE.read_text(encoding="utf-8"))
        self.assertGreater(len(policy.evaluate(original)),5)
        self.assertGreater(len(rights.source_rights_blockers(template,template)),30)
        self.assertEqual(policy.evaluate(mocked_policy()),[])
        self.assertEqual(policy.evaluate(mocked_policy(substantive=False)),[])
        self.assertEqual(rights.source_rights_blockers(template,mocked_rights()),[])
        bad=mocked_rights()
        bad["frozen_source_DOIs"][6]["exact_dataset_license"]="UNVERIFIED"
        self.assertTrue(rights.source_rights_blockers(template,bad))
        self.assertFalse(disclosure.disclosure_present(
             DUMMY_TEXT,"METHODS",candidate.ORIGINAL.read_text(encoding="utf-8"))[0])
        fake_manuscript=candidate.candidate_forms(
            candidate.ORIGINAL.read_text(encoding="utf-8"),
            DUMMY_TEXT,"METHODS")[0]
        self.assertTrue(disclosure.disclosure_present(
             DUMMY_TEXT,"METHODS",fake_manuscript)[0])

class CompositePositiveAndNegative(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir=Path(self.temp.name)
        self.pfile=self.dir/"FICTIONAL_HUMAN_POLICY_ONLY.json"
        self.rfile=self.dir/"FICTIONAL_OWNER_RIGHTS_ONLY.json"
        self.pfile.write_text(json.dumps(mocked_policy()),encoding="utf-8")
        self.rfile.write_text(json.dumps(mocked_rights()),encoding="utf-8")

    def run_composite(self,ai_status="MATCHED_DISCLOSURE_STILL_REQUIRES_HUMAN_JOURNAL_REVIEW",
                      ai_blockers=None,native_results=(0,0),policy_error=False):
        if policy_error:
            p=mocked_policy()
            p["author_approval"]["all_authors_approved_final_manuscript"]=False
            self.pfile.write_text(json.dumps(p),encoding="utf-8")
        else:
            self.pfile.write_text(json.dumps(mocked_policy()),encoding="utf-8")
        mock_ai={
            "status":ai_status,
            "blockers":ai_blockers or [],
            "frozen_journal_manuscript_intact":True,
            "substantive_approved_disclosure_present_in_journal_section":not ai_blockers,
        }
        baseline={
            "errors":[],
            "final_human_or_release_blockers":[],
            "frozen_manuscript_identity_verified":True,
        }
        outcomes=iter(native_results)
        def fake_native(*args,**kwargs):
            return SimpleNamespace(returncode=next(outcomes))
        with patch.object(combined,"POLICY",self.pfile), \
             patch.object(combined,"RIGHTS",self.rfile), \
             patch.object(combined,"rc2_audit",return_value=baseline), \
             patch.object(combined,"ai_document_audit",return_value=mock_ai), \
             patch.object(combined.subprocess,"run",side_effect=fake_native) as calls:
            receipt=combined.evaluate()
            count=calls.call_count
        return receipt,count

    def test_fictional_approval_can_reach_native_checks(self):
        report,calls=self.run_composite()
        self.assertEqual(report["status"],
            "ALL_AUTOMATED_GATES_PASS_FINAL_HUMAN_JOURNAL_REVIEW_REQUIRED")
        self.assertEqual(calls,2)
        self.assertTrue(all(d["check_result"]=="PASS"
                         for d in report["native_zenodo_and_upload_gates"].values()))
        self.assertFalse(report["journal_submitted"])
        self.assertFalse(report["DOI_minted"])

    def test_missing_author_approval_blocks_before_native(self):
        report,calls=self.run_composite(policy_error=True)
        self.assertEqual(report["status"],"HOLD_EDITORIAL_OR_RELEASE_GATES")
        self.assertIn("BES_INCLUSION_GENERATIVE_AI_AND_AUTHORS_HUMAN_SIGNOFF_MISSING",
                      report["missing_blocker_classes"])
        self.assertEqual(calls,0)

    def test_missing_disclosure_blocks_before_native(self):
        report,calls=self.run_composite(
            ai_status="HOLD_DISCLOSURE_CONTENT_OR_POLICY",
            ai_blockers=["SUBSTANTIVE_AI_DISCLOSURE_MISSING"])
        self.assertIn("AI_USAGE_CLASSIFICATION_OR_ACTUAL_JOURNAL_DISCLOSURE_UNRESOLVED",
                      report["missing_blocker_classes"])
        self.assertEqual(calls,0)

    def test_source_rights_gap_blocks_before_native(self):
        self.rfile.write_text(json.dumps(mocked_rights()),encoding="utf-8")
        altered=mocked_rights()
        altered["frozen_source_DOIs"][6]["exact_dataset_license"]="UNVERIFIED"
        self.rfile.write_text(json.dumps(altered),encoding="utf-8")
        baseline={"errors":[],"final_human_or_release_blockers":[],
                  "frozen_manuscript_identity_verified":True}
        mock_ai={"status":"MATCHED_DISCLOSURE_STILL_REQUIRES_HUMAN_JOURNAL_REVIEW",
                 "blockers":[],"frozen_journal_manuscript_intact":True,
                 "substantive_approved_disclosure_present_in_journal_section":True}
        with patch.object(combined,"POLICY",self.pfile), \
             patch.object(combined,"RIGHTS",self.rfile), \
             patch.object(combined,"rc2_audit",return_value=baseline), \
             patch.object(combined,"ai_document_audit",return_value=mock_ai), \
             patch.object(combined.subprocess,"run") as calls:
            report=combined.evaluate()
            self.assertEqual(calls.call_count,0)
        self.assertIn("DATA_REUSE_RIGHTS_BY_DOI_HUMAN_SIGNOFF_MISSING",
                      report["missing_blocker_classes"])

    def test_native_zenodo_release_failure_blocks(self):
        report,calls=self.run_composite(native_results=(1,0))
        self.assertEqual(report["status"],"HOLD_EDITORIAL_OR_RELEASE_GATES")
        self.assertEqual(calls,2)
        self.assertIn("REPOSITORY_NATIVE_FINAL_GATE_BLOCKED:check_zenodo_release_ready_v0_4_0.py",
                      report["missing_blocker_classes"])

    def test_native_journal_upload_failure_blocks(self):
        report,calls=self.run_composite(native_results=(0,1))
        self.assertEqual(report["status"],"HOLD_EDITORIAL_OR_RELEASE_GATES")
        self.assertEqual(calls,2)
        self.assertIn("REPOSITORY_NATIVE_FINAL_GATE_BLOCKED:check_jae_upload_ready_v0_4_0.py",
                      report["missing_blocker_classes"])

if __name__=="__main__":
    unittest.main(verbosity=2)
