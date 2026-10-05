#!/usr/bin/env python3
"""Metadata-only preflight for Diebold et al. 2024 Zenodo record."""
from __future__ import annotations
import json, urllib.request

URL="https://zenodo.org/api/records/13857870"
UA="batter-neural-silencing-metadata/1.0"

def cls(name):
    q=name.lower()
    if any(x in q for x in ["traj","trajectory","flight","position","track"]):
        return "TRAJECTORY_PLAUSIBLE"
    if any(x in q for x in ["behavior","behaviour","session","trial","performance"]):
        return "BEHAVIOR_PLAUSIBLE"
    if any(x in q for x in ["vocal","audio","call","echo"]):
        return "VOCAL_PLAUSIBLE"
    if "abr" in q:
        return "ABR_PLAUSIBLE"
    if any(q.endswith(x) for x in [".m",".py",".r",".ipynb",".zip"]) and any(x in q for x in ["code","script","analysis","figure","fig"]):
        return "CODE_PLAUSIBLE"
    if any(x in q for x in ["code","script"]):
        return "CODE_PLAUSIBLE"
    return "UNKNOWN"

def main():
    req=urllib.request.Request(URL,headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        rec=json.load(r)
    md=rec.get("metadata") or {}
    rows=[]
    for f in rec.get("files") or []:
        links=f.get("links") or {}
        rows.append({
          "key":f.get("key"),
          "size":f.get("size"),
          "checksum":f.get("checksum"),
          "type":f.get("type"),
          "filename_class":cls(str(f.get("key") or "")),
          "content_link_present":bool(links.get("content")),
          "self_link_present":bool(links.get("self")),
        })
    out={
      "contract":"METADATA_PREFLIGHT_CONTRACT_V1.md",
      "file_contents_downloaded":False,
      "record":{
        "id":rec.get("id"),
        "doi":md.get("doi") or rec.get("doi"),
        "conceptdoi":md.get("conceptdoi"),
        "title":md.get("title"),
        "publication_date":md.get("publication_date"),
        "version":md.get("version"),
        "license":md.get("license"),
        "creators":[x.get("name") for x in (md.get("creators") or [])],
      },
      "file_count":len(rows),
      "total_bytes":sum(int(x["size"] or 0) for x in rows),
      "files":rows,
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
