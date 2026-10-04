#!/usr/bin/env python3
"""Outcome-blind file/folder inventory for Source C Mendeley dataset.

Reads public metadata only. Does not download data file contents.
"""
from __future__ import annotations
import json, urllib.parse, urllib.request

BASE="https://data.mendeley.com/public-api"
DS="wh7c636y3t"
VERSION=1
UA="batter-source-c-schema-preflight/1.0"

def get_json(url):
    req=urllib.request.Request(url,headers={
        "User-Agent":UA,
        "Accept":"application/vnd.mendeley-public-dataset.1+json, application/json"
    })
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.load(r)

def slim_file(f):
    cd=f.get("content_details") or {}
    return {
        "id":f.get("id"),
        "filename":f.get("filename") or f.get("name"),
        "folder_id":f.get("folder_id"),
        "size":cd.get("size") or f.get("size"),
        "sha256_hash":cd.get("sha256_hash"),
        "content_type":cd.get("content_type") or f.get("content_type"),
    }

def main():
    meta=get_json(f"{BASE}/datasets/{DS}?version={VERSION}")
    folders=get_json(f"{BASE}/datasets/{DS}/folders/{VERSION}")
    files=get_json(f"{BASE}/datasets/{DS}/files?version={VERSION}&$start=0&$limit=1000")
    if isinstance(folders,dict):
        folders=folders.get("folders") or folders.get("items") or folders.get("results") or []
    if isinstance(files,dict):
        files=files.get("files") or files.get("items") or files.get("results") or []
    out={
        "contract":"SCHEMA_PREFLIGHT_CONTRACT_V1.md",
        "file_contents_opened":False,
        "dataset":{
            "id":meta.get("id"),"version":meta.get("version"),"name":meta.get("name"),
            "doi":meta.get("doi"),"description":meta.get("description"),
        },
        "folders":[{"id":f.get("id"),"name":f.get("name"),"parent_id":f.get("parent_id")} for f in folders],
        "files":[slim_file(f) for f in files],
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
