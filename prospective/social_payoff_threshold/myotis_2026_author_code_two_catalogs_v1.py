#!/usr/bin/env python3
"""One-time author CODE metadata catalogs only (two source-frozen OSF folders).

Never follows download/file content links; no bat event/receiver/coordinate/
family/UD data read. Source URLs and ids frozen in separate pre-data contract.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

BASE="https://api.osf.io/v2/nodes/sg6dz/files/osfstorage/"
ALLOWLIST={
    "sub_functions":BASE+"698db56f1300e956dfbc8a54/",
    "analysis":BASE+"698dbe01fae4711f5ac72f78/",
}
VIEW_ONLY="4624cf1757b34e87bf7a4aca9d889319"
MAX_BYTES=500_000

class StrictRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, hdr, dest):
        p=urllib.parse.urlsplit(dest)
        if p.scheme!="https" or p.hostname not in ("api.osf.io","osf.io"):
            raise ValueError("UNAPPROVED_REDIRECT")
        return super().redirect_request(req,fp,code,msg,hdr,dest)

def get_metadata(original_url,token=False):
    if original_url not in ALLOWLIST.values():raise ValueError("NON_ALLOWLIST_URL")
    url=original_url+("?view_only="+VIEW_ONLY if token else "")
    request=urllib.request.Request(url,headers={
        "Accept":"application/vnd.api+json",
        "User-Agent":"batter-Myotis-2026-Author-Code-Directory-Catalog/1.0"})
    try:
        with urllib.request.build_opener(StrictRedirect()).open(request,timeout=22) as r:
            raw=r.read(MAX_BYTES+1)
            http=r.status
        if len(raw)>MAX_BYTES:raise ValueError("OVERSIZE_CATALOG")
        obj=json.loads(raw)
        if not isinstance(obj,dict) or not isinstance(obj.get("data"),list):
            raise ValueError("BAD_OSF_CATALOG")
        result=[]
        for v in obj["data"][:100]:
            attrs=v.get("attributes") or {}
            if not isinstance(attrs,dict):continue
            result.append({
                "original_name":str(attrs.get("name") or "")[:140],
                "type":str(attrs.get("kind") or "")[:25],
                "id":str(v.get("id") or "")[:100],
                "metadata_size":attrs.get("size") if isinstance(attrs.get("size"),int) else None,
            })
        return {"source_http":http,"catalog_available":True,
            "items_on_first_page":len(obj["data"]),
            "next_page_present":bool((obj.get("links") or {}).get("next")),
            "sha256_json":hashlib.sha256(raw).hexdigest(),
            "source_catalog_items":result}
    except urllib.error.HTTPError as exc:
        return {"catalog_available":False,"source_http":exc.code,"error":"HTTP_ERROR"}
    except Exception as exc:
        return {"catalog_available":False,"source_http":None,
                "error":type(exc).__name__}

def self_test():
    assert len(ALLOWLIST)==2
    assert all(url.startswith(BASE) for url in ALLOWLIST.values())
    assert len({x.split("/")[-2] for x in ALLOWLIST.values()})==2
    return "PASS_TWO_FIXED_ORIGINAL_OSF_CODE_DIRECTORIES_ONLY"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",default="MYOTIS_2026_AUTHOR_CODE_CATALOG_V1.json")
    args=p.parse_args()
    check=self_test()
    if args.self_test:
        print(json.dumps({"check":check,"bat_observations_opened":False}));return
    catalogs={}
    for label,url in ALLOWLIST.items():
        x=get_metadata(url)
        if not x["catalog_available"]:x=get_metadata(url,True)
        catalogs[label]=x
    okay=all(z["catalog_available"] for z in catalogs.values())
    receipt={
        "status":"HOLD_AUTHOR_CODE_FILE_NAMES_ONLY" if okay else "HOLD_NO_SOURCE_CALIBRATION",
        "contract":"MYOTIS_2026_AUTHOR_SUBFUNCTIONS_ANALYSIS_CATALOG_CONTRACT_V1.md",
        "osf_original_id":"sg6dz",
        "metadata_catalogs":catalogs,
        "raw_animal_times_or_positions_read":False,
        "original_site_coordinates_or_receiver_ids_read":False,
        "data_file_downloads":0,"source_file_code_contents_opened":False,
        "bat_statistical_tests":0,"check":check}
    Path(args.out).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":receipt["status"],
         "names":{k:z.get("source_catalog_items",[]) for k,z in catalogs.items()},
         "bat_observations_opened":False},sort_keys=True))
if __name__=="__main__":main()
