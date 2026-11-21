"""Goldshtein et al. 2020 DOI 10.17632/jxghjjsttw.1:
Official Mendeley API immutable source/file METADATA ONLY; no biological rows.
"""
from __future__ import annotations
import argparse
import json
import pathlib
import re
import urllib.parse
import urllib.request

DATASET="https://api.data.mendeley.com/datasets/jxghjjsttw?version=1"
FILES="https://api.data.mendeley.com/datasets/publics/jxghjjsttw/files?version=1"
DOI="10.17632/jxghjjsttw.1"
PASS="GOLDSHTEIN_ORIGINAL_METADATA_ONLY_PASS"
LIMIT=100

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs): return None

def source_url(url):
    p=urllib.parse.urlparse(url)
    if (p.scheme!="https" or p.netloc!="api.data.mendeley.com" or
        p.path not in ("/datasets/jxghjjsttw","/datasets/publics/jxghjjsttw/files") or
        p.username or p.password or p.fragment):
        raise ValueError("SOURCE_NOT_OFFICIAL_MENDELEY")
    return url

def live_get(url):
    target=source_url(url)
    req=urllib.request.Request(target,headers={
        "Accept":"application/vnd.mendeley-public-dataset.1+json, application/json",
        "User-Agent":"batter-goldshtein-original-source-only/1.0"})
    with urllib.request.build_opener(NoRedirect()).open(req,timeout=30) as r:
        if r.status!=200 or r.url!=target:
            raise RuntimeError("SOURCE_REDIRECT_OR_NON200")
        b=r.read(2_000_001)
    if len(b)>2_000_000: raise RuntimeError("SOURCE_METADATA_OVERSIZE")
    return json.loads(b.decode("utf-8"))

def rows(v):
    if isinstance(v,list): return v
    if isinstance(v,dict):
        for k in ("results","files","data"):
            if isinstance(v.get(k),list): return v[k]
    raise ValueError("SOURCE_FILES_SCHEMA_STOP")

def audit(get=live_get):
    ds=get(DATASET)
    if not isinstance(ds,dict): raise ValueError("SOURCE_DATASET_SCHEMA_STOP")
    doi=ds.get("doi")
    doi=doi.get("id") if isinstance(doi,dict) else doi
    if not isinstance(doi,str) or doi.lower()!=DOI: raise ValueError("SOURCE_DOI_MISMATCH")
    if ds.get("version")!=1: raise ValueError("SOURCE_NOT_VERSION_1")
    if ds.get("short_id","jxghjjsttw")!="jxghjjsttw": raise ValueError("SOURCE_ID_MISMATCH")
    listing=[]
    ids=set()
    pages=0
    for offset in range(0,1000,LIMIT):
        pages+=1
        page=rows(get(FILES+"&%24start="+str(offset)+"&%24limit="+str(LIMIT)))
        if len(page)>LIMIT: raise ValueError("SOURCE_PAGINATION_OVERFLOW")
        for item in page:
            if not isinstance(item,dict): raise ValueError("SOURCE_FILE_RECORD_SCHEMA_STOP")
            fid=item.get("id")
            name=item.get("filename",item.get("name"))
            detail=item.get("content_details") or {}
            if not isinstance(detail,dict): raise ValueError("SOURCE_FILE_DETAILS_BAD")
            size=item.get("size",detail.get("size"))
            sha=detail.get("sha256_hash")
            if not isinstance(fid,str) or not fid or not isinstance(name,str) or not name:
                raise ValueError("SOURCE_FILENAME_OR_ID_MISSING")
            if fid in ids: raise ValueError("SOURCE_DUPLICATE_ID")
            if type(size) is not int or size<0: raise ValueError("SOURCE_SIZE_MISSING")
            if sha is not None and not re.fullmatch("[0-9a-fA-F]{64}",str(sha)):
                raise ValueError("SOURCE_SHA256_BAD")
            ids.add(fid)
            listing.append({"file_id":fid,"filename":name,"size_bytes":size,
                            "publisher_sha256":sha,"original_values_read":False})
        if len(page)<LIMIT: break
    else: raise RuntimeError("SOURCE_MAX_PAGES_STOP")
    if not listing: raise ValueError("SOURCE_FILE_LIST_EMPTY")
    return {"schema":"batter.goldshtein_mendeley_source_meta.v1","status":PASS,
            "doi":DOI,"version":1,"pages":pages,"file_count":len(listing),"files":listing,
            "original_bat_rows_opened":False,"original_resource_rows_opened":False,
            "event_level_resource_height_join_verified":False,
            "high_dimensional_ecological_gain":None}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="prospective/resource_behavior_sdm/goldshtein_metadata_receipt_v1.json")
    args=ap.parse_args()
    try:
        receipt=audit()
    except Exception as e:
        receipt={"schema":"batter.goldshtein_mendeley_source_meta.v1",
                 "status":"SOURCE_METADATA_STOP","reason":(type(e).__name__+": "+str(e))[:220],
                 "doi":DOI,"original_bat_rows_opened":False,
                 "original_resource_rows_opened":False,"high_dimensional_ecological_gain":None}
    dest=pathlib.Path(args.out)
    dest.parent.mkdir(exist_ok=True,parents=True)
    dest.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("GOLDSHTEIN",receipt["status"],flush=True)
    if receipt["status"]!="SOURCE_METADATA_STOP":
        print("FILE_COUNT",receipt["file_count"],flush=True)
    else: print("STOP_REASON",receipt["reason"],flush=True)
    return 0 if receipt["status"]==PASS else 3

if __name__=="__main__": raise SystemExit(main())
