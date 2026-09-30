#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"post_freeze_extensions/nyctalus_source_inventory/RESULT_V1.md"
OUTJ=ROOT/"post_freeze_extensions/nyctalus_source_inventory/result_v1.json"
UA={"User-Agent":"batter-nyctalus-source-inventory-v1/1.0"}
RECORD_ID=7535030

def main():
    r=requests.get(f"https://zenodo.org/api/records/{RECORD_ID}",headers=UA,timeout=90)
    r.raise_for_status()
    j=r.json()
    files=[]
    for f in j.get("files",[]):
        files.append({
            "key":f.get("key") or f.get("filename"),
            "size":f.get("size"),
            "checksum":f.get("checksum"),
            "type":f.get("type"),
            "content_url":(f.get("links") or {}).get("content"),
        })
    payload={
        "schema_version":1,
        "study_id":"batter-nyctalus-source-inventory-v1",
        "record_id":RECORD_ID,
        "title":(j.get("metadata") or {}).get("title"),
        "file_count":len(files),
        "files":files,
        "data_values_read":False
    }
    OUTJ.parent.mkdir(parents=True,exist_ok=True)
    OUTJ.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    lines=[
        "# Nyctalus Zenodo source-file inventory v1","",
        "**Metadata-only inventory. No data-file values were read.**","",
        f"- record: **{RECORD_ID}**",
        f"- files: **{len(files)}**","",
        "| file | size (bytes) | checksum |",
        "|---|---:|---|"
    ]
    for x in files:
        lines.append(f"| `{x['key']}` | {x['size'] if x['size'] is not None else ''} | `{x['checksum'] or ''}` |")
    lines.append("")
    OUT.write_text("\n".join(lines))
    print(json.dumps({"file_count":len(files),"files":[x["key"] for x in files]},sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
