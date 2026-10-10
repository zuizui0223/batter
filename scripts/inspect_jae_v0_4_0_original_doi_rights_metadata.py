#!/usr/bin/env python3
"""Source rights METADATA ONLY, ten fixed cited DOIs. Never claim licence grant.

Movebank allows use of CC0/CC BY/CC BY-NC within actual licence conditions,
but DOI metadata alone is not proof that the original owner approved reuse.
No wildlife location records, files, names, study descriptions are opened.
"""
from __future__ import annotations
import argparse
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TEMPLATE=ROOT/"submission/jae_v0_4_0_original_source_rights.template.json"
MAX_BYTES=262144
ALLOWED_CC={"CC0","CC-BY","CC-BY-NC","CC-BY-4.0","CC-BY-NC-4.0"}

class NoOffsiteRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,request,fp,code,msg,headers,newurl):
        p=urllib.parse.urlsplit(newurl)
        if p.scheme!="https" or p.hostname!="api.datacite.org":
            raise ValueError("NON_DATACITE_REDIRECT")
        return super().redirect_request(request,fp,code,msg,headers,newurl)

def safe_value(x,n=160):
    if not isinstance(x,str):return ""
    return x.strip()[:n]

def lookup(doi):
    assert re.fullmatch(r"10\.\d{4,9}/[A-Za-z0-9._;/():-]+",doi,re.I)
    url="https://api.datacite.org/dois/"+urllib.parse.quote(doi,safe="")
    req=urllib.request.Request(url,headers={
       "Accept":"application/vnd.api+json, application/json",
       "User-Agent":"batter-JAE-DOI-licence-metadata-only/1.0"})
    result={"doi":doi,"status":"STOP_METADATA_LOOKUP_OR_IDENTITY",
            "rights_list_from_datacite":[],"source_file_or_location_content_opened":False}
    try:
        with urllib.request.build_opener(NoOffsiteRedirect()).open(req,timeout=22) as response:
            raw=response.read(MAX_BYTES+1)
            status=response.status
        result["http_status"]=status
        if len(raw)>MAX_BYTES:raise ValueError("OVERSIZE_JSON")
        j=json.loads(raw)
        if not isinstance(j,dict) or not isinstance(j.get("data"),dict):
            raise ValueError("INVALID_DATACITE_JSON")
        item=j["data"]
        attrs=item.get("attributes") or {}
        claimed=safe_value(attrs.get("doi"),200)
        if claimed.lower()!=doi.lower():
            result["error"]="DOI_IDENTITY_MISMATCH"
            return result
        rights=attrs.get("rightsList") or []
        if not isinstance(rights,list):raise ValueError("RIGHTSLIST_NOT_ARRAY")
        declarations=[]
        for r in rights[:20]:
            if not isinstance(r,dict):continue
            row={
                "rights":safe_value(r.get("rights")),
                "rights_identifier":safe_value(r.get("rightsIdentifier")),
                "rights_uri":safe_value(r.get("rightsUri"),210),
            }
            declarations.append(row)
        result["rights_list_from_datacite"]=declarations
        result["datacite_DOI_identity_verified"]=True
        year=attrs.get("publicationYear")
        if isinstance(year,int) and 1900<=year<=2100:
            result["publication_year_from_datacite"]=year
        landing=attrs.get("url")
        if isinstance(landing,str):
            parsed=urllib.parse.urlsplit(landing)
            if parsed.scheme=="https" and parsed.hostname and len(landing)<280:
                result["original_dataset_landing_URL"]=urllib.parse.urlunsplit(
                     (parsed.scheme,parsed.netloc,parsed.path,"",""))
        has_cc=any(bool(re.search(r"(?i)\bCC0\b|\bCC[\s-]?BY(?:[\s-]?NC)?\b|creativecommons\.org",
                  " ".join((q["rights"],q["rights_identifier"],q["rights_uri"]))))
                   for q in declarations)
        result["status"]=(
             "METADATA_CC_CANDIDATE_NEEDS_DATASET_TERMS_CONFIRMATION" if has_cc
             else "RIGHTS_DECLARED_NEEDS_DATASET_TERMS_CONFIRMATION" if declarations
             else "NO_MACHINE_READABLE_LICENSE_OWNER_REVIEW_REQUIRED")
    except urllib.error.HTTPError as e:
        result["http_status"]=e.code
        result["error"]="HTTP_ERROR"
    except Exception as e:
        result["error"]=type(e).__name__
    return result

def self_test():
    data=json.loads(TEMPLATE.read_text(encoding="utf-8"))
    rows=data["frozen_source_DOIs"]
    assert data["expected_frozen_manuscript_blob"]=="c4ef51a7f3f291a6f203d303dbf73f5b54fb7683"
    assert len(rows)==10 and len({r["doi"] for r in rows})==10
    assert sum(r["analysis_scope"]=="original" for r in rows)==6
    assert sum(r["analysis_scope"]=="external_boundary" for r in rows)==4
    assert all(r["exact_dataset_license"]=="UNVERIFIED" for r in rows)
    assert all(not r["intended_reuse_covered_by_license_or_permission"] for r in rows)
    assert all(re.fullmatch(r"10\.\d{4,9}/[A-Za-z0-9._;/():-]+",r["doi"]) for r in rows)
    return "PASS_TEN_FROZEN_DIFFERENT_DOIS_SOURCE_RIGHTS_UNVERIFIED"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",default="JAE_RC2_DATACITE_SOURCE_RIGHTS_ONLY_2026_10_10.json")
    a=p.parse_args()
    guard=self_test()
    if a.self_test:
        print(json.dumps({"synthetic_source_guard":guard,"rights_approved":False}));return
    data=json.loads(TEMPLATE.read_text(encoding="utf-8"))
    report=[]
    for row in data["frozen_source_DOIs"]:
        z=lookup(row["doi"])
        z["source_scope"]=row["analysis_scope"]
        z["dataset_rights_human_verified"]=False
        report.append(z)
    result={
      "contract":"JAE_RC2_DATACITE_SOURCE_RIGHTS_METADATA_GATE_2026_10_10.md",
      "status":"HOLD_TEN_DATASET_RIGHTS_HUMAN_REVIEW",
      "sources_checked":len(report),
      "doi_metadata_results":report,
      "public_metadata_only":True,
      "datafiles_tracking_locations_or_bat_timepoints_opened":False,
      "licence_or_owner_permission_finalized":False,
      "license_claims_added_to_research_manuscript":False,
      "source_reuse_review_still_human_required":True,
      "synthetic_source_guard":guard}
    Path(a.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"source_summary":[
       {"doi":r["doi"],"result":r["status"],
        "rights":r.get("rights_list_from_datacite",[]),
        "http":r.get("http_status")} for r in report],
       "individual_licence_approvals_claimed":False,
       "real_data_downloaded":False},sort_keys=True))

if __name__=="__main__":main()
