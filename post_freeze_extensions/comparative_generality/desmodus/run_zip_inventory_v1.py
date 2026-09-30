#!/usr/bin/env python3
from __future__ import annotations

import json, os, re
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from remotezip import RemoteZip

ROOT=Path(__file__).resolve().parents[3]
CONTRACT=ROOT/"post_freeze_extensions/comparative_generality/desmodus/zip_inventory_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/comparative_generality/desmodus/zip_inventory_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/comparative_generality/desmodus/ZIP_INVENTORY_RESULT_V1.md"

def resolve_file_id(c):
    r=requests.get(c["source"]["landing_url"],headers={"User-Agent":"batter-desmodus-zip-inventory-v1/1.0"},timeout=90)
    r.raise_for_status()
    soup=BeautifulSoup(r.text,"html.parser")
    target=None
    for a in soup.find_all("a",href=True):
        txt=a.get_text(" ",strip=True)
        if txt==c["source"]["archive_name"] or c["source"]["archive_name"] in txt:
            target=urljoin(c["source"]["landing_url"],a["href"])
            break
    if not target:
        raise RuntimeError("could not resolve archive link from Dryad landing page")
    m=re.search(r"/file_stream/(\d+)",target)
    if not m:
        raise RuntimeError(f"could not extract Dryad file id from {target}")
    return int(m.group(1)),target

def main():
    c=json.loads(CONTRACT.read_text())
    token=os.environ.get("DRYAD_API_TOKEN","").strip()
    if not token:
        raise RuntimeError("DRYAD_API_TOKEN missing")
    file_id,landing_download=resolve_file_id(c)
    url=f"https://datadryad.org/api/v2/files/{file_id}/download"
    headers={
        "Authorization":f"Bearer {token}",
        "User-Agent":"batter-desmodus-zip-inventory-v1/1.0"
    }

    rz=RemoteZip(url,headers=headers)
    infos=rz.infolist()
    rows=[]
    for z in infos:
        rows.append({
            "filename":z.filename,
            "file_size":int(z.file_size),
            "compress_size":int(z.compress_size),
            "compress_type":int(z.compress_type),
            "is_dir":bool(z.is_dir())
        })
    rz.close()

    wanted={}
    for basename in ["total22_23_0s.xlsx","Final_GPS_2025.rds"]:
        hits=[x for x in rows if Path(x["filename"]).name==basename]
        wanted[basename]=hits

    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "data_values_read":False,
        "dryad_archive_file_id":file_id,
        "dryad_landing_download":landing_download,
        "archive_api_url":url,
        "inner_entry_count":len(rows),
        "entries":rows,
        "target_members":wanted,
        "decision":(
            "RAW_XLSX_MEMBER_FOUND"
            if len(wanted["total22_23_0s.xlsx"])==1
            else "RAW_XLSX_MEMBER_NOT_UNIQUELY_RESOLVED"
        )
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    lines=[
        "# Desmodus remote ZIP inventory v1","",
        "**Metadata only. No inner file contents or GPS values were read.**","",
        f"- Dryad archive file id: **{file_id}**",
        f"- inner entries: **{len(rows)}**","",
        "## Target members",""
    ]
    for name,hits in wanted.items():
        if not hits:
            lines.append(f"- `{name}`: **not found**")
        else:
            for x in hits:
                lines.append(
                    f"- `{name}`: `{x['filename']}` — "
                    f"{x['file_size']} bytes uncompressed / {x['compress_size']} compressed"
                )
    lines += ["",f"Decision: **{payload['decision']}**",""]
    OUT_MD.write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps({
        "file_id":file_id,
        "inner_entry_count":len(rows),
        "targets":wanted,
        "decision":payload["decision"]
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
