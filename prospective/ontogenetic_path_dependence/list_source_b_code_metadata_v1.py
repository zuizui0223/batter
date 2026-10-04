#!/usr/bin/env python3
"""List Source B Codes subtree metadata only; do not download file contents."""
from __future__ import annotations
import json, urllib.parse, urllib.request
BASE="https://data.mendeley.com/public-api"
DS="n9d8gbz3xr"; V=1; CODES="b631669c-ca26-4e6b-8f4a-dd5bee172cdc"
UA="batter-source-b-code-metadata/1.0"

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.mendeley-public-dataset.1+json"})
    with urllib.request.urlopen(req,timeout=30) as r: return json.load(r)

def files(folder):
    url=f"{BASE}/datasets/{DS}/files?folder_id={urllib.parse.quote(folder)}&version={V}&$start=0&$limit=1000"
    x=get(url)
    return x if isinstance(x,list) else x.get("files") or x.get("items") or x.get("results") or []

def main():
    folders=get(f"{BASE}/datasets/{DS}/folders/{V}")
    if isinstance(folders,dict): folders=folders.get("folders") or folders.get("items") or folders.get("results") or []
    children=[x for x in folders if x.get("parent_id")==CODES]
    targets=[{"id":CODES,"name":"Codes"}]+[{"id":x["id"],"name":x.get("name")} for x in children]
    out=[]
    for t in targets:
        rows=files(t["id"])
        out.append({
            **t,
            "files":[{
                "id":r.get("id"),
                "filename":r.get("filename"),
                "size":(r.get("content_details") or {}).get("size") or r.get("size"),
                "sha256":(r.get("content_details") or {}).get("sha256_hash"),
                "content_type":(r.get("content_details") or {}).get("content_type"),
            } for r in rows]
        })
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
