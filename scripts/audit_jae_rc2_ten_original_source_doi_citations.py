#!/usr/bin/env python3
"""JAE RC2 citation/attribution consistency for its ten fixed source DOIs.

Scientific read-only manuscript SHA; source DOI and original first-primary
external boundary checks; no licence inference, no bat downloads.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
M=ROOT/"manuscript/MANUSCRIPT_DRAFT_V0_4_0.md"
T=ROOT/"manuscript/TITLE_PAGE_TEMPLATE_V0_4_0.md"
R=ROOT/"submission/jae_v0_4_0_original_source_rights.template.json"
L=ROOT/"submission/JAE_RC2_EXECUTED_TEN_SOURCE_DATACITE_RIGHTS_RESULT_2026_10_10.md"
EXPECTED_SHA="c4ef51a7f3f291a6f203d303dbf73f5b54fb7683"
NYCTALUS="10.5281/zenodo.7535030"

def blob_sha(src):
    return hashlib.sha1(b"blob "+str(len(src)).encode()+b"\0"+src).hexdigest()

def score():
    manifest=json.loads(R.read_text(encoding="utf-8"))
    resources=manifest["frozen_source_DOIs"]
    m=M.read_bytes()
    t=T.read_text(encoding="utf-8")
    ledger=L.read_text(encoding="utf-8")
    txt=m.decode("utf-8")
    failures=[]
    if manifest.get("expected_frozen_manuscript_blob")!=EXPECTED_SHA or blob_sha(m)!=EXPECTED_SHA:
        failures.append("CANONICAL_FROZEN_JAE_MANUSCRIPT_IDENTITY_CHANGED")
    if len(resources)!=10 or len({v["doi"] for v in resources})!=10:
        failures.append("EXPECTED_TEN_ORIGINAL_SOURCE_DOIS_NOT_UNIQUE")
    if sum(v["analysis_scope"]=="original" for v in resources)!=6:
        failures.append("EXPECTED_SIX_PRIMARY_SOURCE_DOIS_CHANGED")
    if sum(v["analysis_scope"]=="external_boundary" for v in resources)!=4:
        failures.append("EXPECTED_FOUR_EXTERNAL_BOUNDARY_DOIS_CHANGED")
    rows=[]
    for v in resources:
        doi=v["doi"]
        presence={"doi":doi,"scope":v["analysis_scope"],
                  "in_main_manuscript":doi in txt,
                  "in_separate_title_page_template":doi in t,
                  "in_source_rights_provenance_ledger":doi in ledger,
                  "human_source_rights_approved":False}
        rows.append(presence)
        for k in ("in_main_manuscript","in_separate_title_page_template",
                  "in_source_rights_provenance_ledger"):
            if not presence[k]:
                failures.append("MISSING_ORIGINAL_DATASET_CITATION:"+doi+":"+k)
    focus=next((v for v in resources if v["doi"]==NYCTALUS),None)
    if not focus or focus["analysis_scope"]!="external_boundary":
        failures.append("CC_BY_NYCTALUS_EXTERNAL_BOUNDARY_SOURCE_GONE")
    if "CC BY 4.0" not in ledger or NYCTALUS not in ledger:
        failures.append("NYCTALUS_DATACITE_CC_BY_CITATION_LEDGER_MISSING")
    # The author's original first predeclared primary is a FAIL. Keep its p.
    # Tests are source-text assertions, not recalculated statistical outcomes.
    key_markers=("N. noctula","0.05175","p=0.1224","did not meet its criterion")
    for marker in key_markers:
        if marker not in txt:
            failures.append("NYCTALUS_FIRST_PRIMARY_NON_SUPPORT_MISSING:"+marker)
    return {
       "status":"STOP_ORIGINAL_DOI_OR_SCIENCE_CITATION_DRIFT" if failures
                 else "PASS_TEN_SOURCE_CITATION_COMPLETENESS_ONLY",
       "original_manuscript_immutable_sha":blob_sha(m),
       "original_six_sources":sum(v["analysis_scope"]=="original" for v in resources),
       "external_four_sources":sum(v["analysis_scope"]=="external_boundary" for v in resources),
       "doi_presence":rows,
       "specific_nyctalus_CC_BY_first_primary_boundary_retained":
           all(k in txt for k in key_markers) and "CC BY 4.0" in ledger,
       "any_owner_permission_or_software_licence_granted":False,
       "bat_data_files_opened":0,
       "errors":failures
    }

def test():
    assert blob_sha(b"hello")==hashlib.sha1(b"blob 5\0hello").hexdigest()
    fake="10.5281/zenodo.7535030"
    assert fake not in "10.5281/zenodo.7535031"
    sample=json.loads(R.read_text(encoding="utf-8"))
    assert len(sample["frozen_source_DOIs"])==10
    assert all(x["exact_dataset_license"]=="UNVERIFIED" for x in sample["frozen_source_DOIs"])
    return "PASS_SOURCE_DOI_IDENTITY_AND_UNAPPROVED_LICENSE_CONTRACT"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",default="JAE_RC2_TEN_DATASET_CITATION_INTEGRITY_RESULT.json")
    args=p.parse_args()
    if args.self_test:
        print(json.dumps({"self_test":test(),"bat_source_events_read":False}));return 0
    z=score()
    z["test"]=test()
    Path(args.out).write_text(json.dumps(z,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":z["status"],
         "n_source_DOI_in_main":sum(x["in_main_manuscript"] for x in z["doi_presence"]),
         "n_source_DOI_in_title":sum(x["in_separate_title_page_template"] for x in z["doi_presence"]),
         "nyctalus_frozen_fail_citation_retained":z["specific_nyctalus_CC_BY_first_primary_boundary_retained"],
         "errors":z["errors"],
         "no_licence_permission_claim":True},sort_keys=True))
    return 1 if z["errors"] else 0

if __name__=="__main__":raise SystemExit(main())
