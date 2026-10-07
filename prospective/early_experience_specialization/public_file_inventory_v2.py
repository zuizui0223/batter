#!/usr/bin/env python3
"""Inventory the verified anonymous Mendeley public file endpoint.

Names/metadata only. No research data values are opened.
"""

from pathlib import Path
import json, urllib.request, urllib.parse

HERE=Path(__file__).resolve().parent
OUT=HERE/"PUBLIC_FILE_INVENTORY_V2.json"
OUTMD=HERE/"PUBLIC_FILE_INVENTORY_V2.md"

DATASET="wh7c636y3t"
VERSION=1
ROOT_URL=(
    f"https://data.mendeley.com/public-api/datasets/{DATASET}/files?"
    + urllib.parse.urlencode({
        "folder_id":"root",
        "version":VERSION,
        "$start":0,
        "$limit":1000,
    })
)

HEADERS={"User-Agent":"Mozilla/5.0 batter-file-inventory/2.0","Accept":"application/json"}

def get_json(url):
    req=urllib.request.Request(url,headers=HEADERS)
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def compact(row):
    cd=row.get("content_details") or {}
    return {
        "id":row.get("id"),
        "filename":row.get("filename") or row.get("name"),
        "description":row.get("description"),
        "folder_id":row.get("folder_id"),
        "size":row.get("size") or cd.get("size"),
        "content_type":row.get("content_type") or cd.get("content_type"),
        "sha256":row.get("sha256_hash") or cd.get("sha256_hash"),
        "download_url_present":bool(cd.get("download_url") or row.get("download_url")),
    }

def main():
    data=get_json(ROOT_URL)
    if isinstance(data,dict):
        rows=data.get("items") or data.get("files") or data.get("results") or data.get("data") or []
        envelope_keys=sorted(data.keys())
    else:
        rows=data
        envelope_keys=[]
    files=[compact(x) for x in rows if isinstance(x,dict)]

    result={
        "source_url":ROOT_URL,
        "envelope_keys":envelope_keys,
        "file_count":len(files),
        "files":files,
    }
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")

    lines=[
        "# Early-experience public file inventory v2","",
        "**PUBLIC FILE METADATA ONLY — NO RESEARCH VALUES OPENED.**","",
        f"- file count: **{len(files)}**",
        f"- envelope keys: {envelope_keys}","",
        "| filename | bytes | content type | download URL |",
        "|---|---:|---|---|",
    ]
    for f in files:
        lines.append(
            f"| {f['filename']} | {f['size']} | {f['content_type']} | "
            f"{'yes' if f['download_url_present'] else 'no'} |"
        )
    OUTMD.write_text("\n".join(lines)+"\n")
    print(OUTMD.read_text())

if __name__=="__main__":
    main()
