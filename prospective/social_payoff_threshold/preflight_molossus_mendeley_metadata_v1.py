#!/usr/bin/env python3
"""Metadata-only, fail-closed Mendeley source preflight for h7krh54zxc v1.

Does not follow individual download links, open data files, read behavioral
outcomes, or calculate statistical endpoints.
"""
from __future__ import annotations
import argparse
import datetime
import hashlib
import json
import urllib.error
import urllib.request
from pathlib import Path

ID="h7krh54zxc"
VERSION="1"
SOURCES=[
  "https://api.data.mendeley.com/datasets/h7krh54zxc?version=1",
  "https://api.data.mendeley.com/datasets/h7krh54zxc/files?version=1",
]
UA="batter-source-only-functional-payoff-gate/1.0"
MAX_JSON=1_000_000


def get_metadata(url):
    assert url in SOURCES, "Unexpected external source"
    req=urllib.request.Request(
        url, headers={"User-Agent":UA,"Accept":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=35) as res:
            body=res.read(MAX_JSON+1)
            status=res.status
    except urllib.error.HTTPError as e:
        return {"http_status":int(e.code),"metadata_json_ok":False,
                "metadata_sha256":None,"error_kind":"HTTP_ERROR"}
    except Exception as e:
        return {"http_status":None,"metadata_json_ok":False,
                "metadata_sha256":None,"error_kind":type(e).__name__}
    if len(body)>MAX_JSON:
        return {"http_status":status,"metadata_json_ok":False,
                "metadata_sha256":None,"error_kind":"OVERSIZE_STOP"}
    try: data=json.loads(body)
    except Exception:
        return {"http_status":status,"metadata_json_ok":False,
                "metadata_sha256":hashlib.sha256(body).hexdigest(),
                "error_kind":"NON_JSON_STOP"}
    return {"http_status":status,"metadata_json_ok":True,
            "metadata_sha256":hashlib.sha256(body).hexdigest(),
            "error_kind":None,"decoded":data}


def clean_metadata(obj):
    """Only dataset identity/source names/sizes; redact links and outcomes."""
    body=obj.pop("decoded",None)
    if body is None: return obj
    if isinstance(body,list): items=body
    elif isinstance(body,dict):
        items=body.get("files") if isinstance(body.get("files"),list) else []
    else: items=[]
    source_files=[]
    for item in items[:100]:
        if not isinstance(item,dict): continue
        name=item.get("filename") or item.get("name") or ""
        details=item.get("content_details") or {}
        source_files.append({
          "filename":str(name)[:180],
          "extension":str(name).rsplit(".",1)[-1].lower() if "." in str(name) else "",
          "declared_size_bytes":item.get("size",details.get("size")),
          "declared_file_id":str(item.get("id",""))[:80],
        })
    identity={}
    if isinstance(body,dict):
        for k in ("id","version","name","title","publication_date"):
            val=body.get(k)
            if isinstance(val,(str,int,float,bool)) or val is None:
                identity[k]=val
        doi=body.get("doi")
        if isinstance(doi,dict):identity["doi"]=doi.get("id")
        elif isinstance(doi,str):identity["doi"]=doi
    obj["catalog_identity"]=identity
    obj["listed_file_count"]=len(items)
    obj["listed_file_metadata"]=source_files
    return obj


def fake_test():
    fake={"http_status":200,"metadata_json_ok":True,
          "decoded":[{"filename":"somefile.csv","id":"fake-id","size":1000,
            "content_details":{"download_url":"https://BAD_DO_NOT_USE"}}]}
    out=clean_metadata(fake)
    assert out["listed_file_count"]==1
    assert "download_url" not in json.dumps(out)
    assert out["listed_file_metadata"][0]["extension"]=="csv"
    return "PASS"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",default="MOLOSSUS_2024_SOURCE_METADATA_RECEIPT_V1.json")
    args=p.parse_args()
    if args.self_test:
        print(json.dumps({"synthetic_metadata_redaction":fake_test()}))
        return
    check=fake_test()
    records={}
    for label,url in zip(("dataset","file_list"),SOURCES):
        records[label]=clean_metadata(get_metadata(url))
    success=all(z["metadata_json_ok"] and z["http_status"]==200
                for z in records.values())
    identity=records["dataset"].get("catalog_identity",{})
    expected_id=identity.get("id") in (None,ID)
    source_identity_pass=success and expected_id
    status=("HOLD_METADATA_ONLY_NEEDS_ORIGINAL_STRUCTURAL_FILES"
            if source_identity_pass else "STOP_API_OR_SOURCE_INACCESSIBLE")
    if not expected_id: status="STOP_INCORRECT_SOURCE_IDENTITY"
    receipt={
      "source_doi":"10.17632/h7krh54zxc.1",
      "dataset_id":ID,"version":VERSION,
      "timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
      "contract":"MOLOSSUS_2024_PUBLIC_SOURCE_GATE_CONTRACT_V1.md",
      "status":status,
      "synthetic_metadata_redaction":check,
      "biological_outcomes_opened":False,
      "file_downloads_or_views_followed":False,
      "individual_bout_support_verified":False,
      "n_physical_bats_from_published_metadata_only":10,
      "not_confirmed":"independent dates/bouts, stable keys, overlapping density support",
      "endpoints_executed":0,
      "requests":records,
    }
    Path(args.out).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":status,
        "dataset_http":records["dataset"]["http_status"],
        "file_list_http":records["file_list"]["http_status"],
        "listed_files":records["file_list"].get("listed_file_count",0),
        "numeric_bat_data_opened":False,
        "receipt":args.out},sort_keys=True))


if __name__=="__main__":
    main()
