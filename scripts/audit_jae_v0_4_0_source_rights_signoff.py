#!/usr/bin/env python3
"""Fail-closed source-specific licence/credit signoff for ten JAE source DOIs.

DataCite CC metadata gives candidate licence, NOT human rights clearance.
No personal permissions, animal tracks, or original wildlife GPS files handled.
"""
from __future__ import annotations
import argparse,json,re,sys,urllib.parse
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TEMPLATE=ROOT/"submission/jae_v0_4_0_original_source_rights.template.json"
APPROVED=ROOT/"submission/jae_v0_4_0_original_source_rights.json"
FROZEN_BLOB="c4ef51a7f3f291a6f203d303dbf73f5b54fb7683"

def source_rights_blockers(tpl,actual):
    holds=[]
    if actual.get("schema_version")!=tpl.get("schema_version"):
        holds.append("rights signoff wrong schema")
    if actual.get("expected_frozen_manuscript_blob")!=FROZEN_BLOB:
        holds.append("rights signoff wrong frozen scientific manuscript")
    expected={x["doi"].lower():x for x in tpl["frozen_source_DOIs"]}
    src=actual.get("frozen_source_DOIs")
    if not isinstance(src,list) or len(src)!=len(expected):
        return holds+["rights signoff must include all exact 10 canonical dataset DOIs"]
    got={}
    for item in src:
        if not isinstance(item,dict):
            holds.append("invalid source row structure")
            continue
        doi=item.get("doi","")
        if not isinstance(doi,str) or doi.lower() in got:
            holds.append("invalid or duplicated dataset DOI")
            continue
        got[doi.lower()]=item
    if set(got)!=set(expected):
        holds.append("source DOI set changed relative to frozen JAE RC2")
    for doi,spec in expected.items():
        row=got.get(doi)
        if row is None:continue
        if row.get("analysis_scope")!=spec["analysis_scope"]:
            holds.append(doi+": source scope changed")
        license_name=str(row.get("exact_dataset_license") or "")
        if license_name.upper() in ("UNVERIFIED","UNKNOWN","") or len(license_name)<4:
            holds.append(doi+": actual source licence not author verified")
        url=str(row.get("licence_evidence_url") or "")
        parsed=urllib.parse.urlsplit(url)
        if parsed.scheme!="https" or not parsed.hostname or len(url)>800:
            holds.append(doi+": no HTTPS repository/owner rights evidence URL")
        if row.get("permission_required_under_actual_terms") not in ("YES","NO"):
            holds.append(doi+": original data owner permission applicability unreviewed")
        if row.get("source_citation_attribution_verified_by_authors") is not True:
            holds.append(doi+": scholarly citation attribution not author verified")
        if row.get("intended_reuse_covered_by_license_or_permission") is not True:
            holds.append(doi+": proposed JAE reuse has not been cleared")
        if row.get("owner_contact_or_credit_assessed_by_authors") is not True:
            holds.append(doi+": owner scholarly contact/credit not considered")
        if len(str(row.get("source_rights_notes") or "").strip())<15:
            holds.append(doi+": source-specific conditions/rights notes not reviewed")
    if actual.get("authors_final_permissions_checked") is not True:
        holds.append("all ten source reuse conditions lack final author approval")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}",str(actual.get("authors_final_signoff_date") or "")):
        holds.append("final author source rights signoff date not confirmed")
    return holds

def test():
    data=json.loads(TEMPLATE.read_text(encoding="utf-8"))
    assert data["expected_frozen_manuscript_blob"]==FROZEN_BLOB
    assert len(data["frozen_source_DOIs"])==10
    assert len(source_rights_blockers(data,data))>=40
    synthetic=json.loads(json.dumps(data))
    for row in synthetic["frozen_source_DOIs"]:
        row.update({"exact_dataset_license":"CC0-1.0",
                    "licence_evidence_url":"https://example.org/dataset/rights",
                    "permission_required_under_actual_terms":"NO",
                    "source_citation_attribution_verified_by_authors":True,
                    "intended_reuse_covered_by_license_or_permission":True,
                    "owner_contact_or_credit_assessed_by_authors":True,
                    "source_rights_notes":"fictional test of source-specific publisher terms"})
    synthetic["authors_final_permissions_checked"]=True
    synthetic["authors_final_signoff_date"]="2026-10-10"
    assert source_rights_blockers(data,synthetic)==[]
    synthetic["frozen_source_DOIs"][6]["exact_dataset_license"]="UNVERIFIED"
    assert any("10.5281/zenodo.7535030: actual source licence" in s for s in source_rights_blockers(data,synthetic))
    return "PASS_FIXED_TEN_LICENSE_MATRIX_REQUIRED_AND_UNVERIFIED_TEMPLATES_BLOCKED"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",default="JAE_RC2_TEN_SOURCE_RIGHTS_HUMAN_GATE.json")
    args=p.parse_args()
    guard=test()
    if args.self_test:
        print(json.dumps({"self_test":guard,"real_permissions_claimed":False}));return 0
    tpl=json.loads(TEMPLATE.read_text(encoding="utf-8"))
    actual=APPROVED.is_file()
    data=json.loads((APPROVED if actual else TEMPLATE).read_text(encoding="utf-8"))
    holds=source_rights_blockers(tpl,data)
    state="HOLD_TEN_SOURCE_RIGHTS_HUMAN_SIGNOFF" if not actual or holds else "SOURCE_RIGHTS_APPROVED_BY_HUMANS_NEEDS_JOURNAL_CONTENT_REVIEW"
    report={"status":state,
       "actual_human_signed_source_file_present":actual,
       "frozen_manuscript_blob":FROZEN_BLOB,
       "total_cited_dataset_DOIs":len(tpl["frozen_source_DOIs"]),
       "n_unapproved_conditions":len(holds),
       "unapproved_conditions":holds,
       "data_metadata_candidates_are_not_permissions":True,
       "no_wildlife_tracking_records_or_owner_private_correspondence_opened":True,
       "no_rights_status_manufactured":True,
       "self_test":guard}
    Path(args.out).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":state,
       "sources_expected":len(tpl["frozen_source_DOIs"]),
       "n_unapproved_source_rights_issues":len(holds),
       "human_rights_signoff_present":actual,
       "no_source_approval_claimed":not (actual and not holds)},sort_keys=True))
    return 0
if __name__=="__main__":sys.exit(main())
