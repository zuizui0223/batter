#!/usr/bin/env python3
"""Public file/folder inventory for the auditory-feedback developmental dataset.

Metadata only. No research values are opened.
"""

from __future__ import annotations
from pathlib import Path
import json, urllib.parse, urllib.request

HERE=Path(__file__).resolve().parent
OUT=HERE/"PUBLIC_FILE_INVENTORY_V1.json"
OUTMD=HERE/"PUBLIC_FILE_INVENTORY_V1.md"

DATASET="h5ff9vv5pc"
VERSION=1
HEADERS={"User-Agent":"Mozilla/5.0 batter-auditory-feedback-inventory/1.0","Accept":"application/json"}

def get_json(url):
    req=urllib.request.Request(url,headers=HEADERS)
    with urllib.request.urlopen(req,timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))

def rows(x):
    if isinstance(x,list): return x
    if isinstance(x,dict):
        for k in ("items","files","results","data"):
            if isinstance(x.get(k),list): return x[k]
    return []

def compact(x):
    cd=x.get("content_details") or {}
    return {
        "id":x.get("id"),
        "filename":x.get("filename") or x.get("name"),
        "description":x.get("description"),
        "folder_id":x.get("folder_id"),
        "size":x.get("size") or cd.get("size"),
        "content_type":x.get("content_type") or cd.get("content_type"),
        "sha256":x.get("sha256_hash") or cd.get("sha256_hash"),
        "download_url_present":bool(x.get("download_url") or cd.get("download_url")),
        "raw_keys":sorted(x.keys()),
    }

def fetch_endpoint(base,folder=None):
    q={"version":VERSION,"$start":0,"$limit":1000}
    if folder is not None: q["folder_id"]=folder
    url=base+"?"+urllib.parse.urlencode(q)
    data=get_json(url)
    return url,data,[compact(x) for x in rows(data) if isinstance(x,dict)]

def main():
    attempts=[]
    endpoints=[
        f"https://data.mendeley.com/public-api/datasets/{DATASET}/files",
        f"https://data.mendeley.com/api/datasets/{DATASET}/files",
    ]
    selected=None
    for base in endpoints:
        for folder in ("root",None):
            try:
                url,data,items=fetch_endpoint(base,folder)
                attempts.append({"url":url,"ok":True,"count":len(items)})
                if items and selected is None:
                    selected={"url":url,"items":items,"envelope_keys":sorted(data.keys()) if isinstance(data,dict) else []}
            except Exception as e:
                attempts.append({"url":base,"folder":folder,"ok":False,"error":repr(e)})

    if selected is None:
        raise SystemExit("STOP: no public file endpoint returned items")

    result={
        "dataset":DATASET,"version":VERSION,
        "selected_url":selected["url"],
        "envelope_keys":selected["envelope_keys"],
        "item_count":len(selected["items"]),
        "items":selected["items"],
        "attempts":attempts,
    }
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")

    lines=[
        "# Auditory-feedback public file inventory v1","",
        "**METADATA ONLY — NO RESEARCH VALUES OPENED.**","",
        f"- items: **{len(selected['items'])}**",
        f"- selected endpoint: `{selected['url']}`","",
        "| name | bytes | content type | download URL | folder |",
        "|---|---:|---|---|---|",
    ]
    for x in selected["items"]:
        lines.append(
            f"| {x['filename']} | {x['size']} | {x['content_type']} | "
            f"{'yes' if x['download_url_present'] else 'no'} | {x['folder_id']} |"
        )
    OUTMD.write_text("\n".join(lines)+"\n")
    print(OUTMD.read_text())

if __name__=="__main__": main()
