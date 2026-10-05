#!/usr/bin/env python3
"""Metadata-only inventory for Taub & Yovel 2021 Mendeley dataset."""
from __future__ import annotations
import json, urllib.parse, urllib.request

BASE="https://data.mendeley.com/public-api"
DS="wccbjdrrsg"
VERSION=1
UA="batter-clutter-recall-metadata/1.0"

def get(url):
    req=urllib.request.Request(
        url,
        headers={"User-Agent":UA,"Accept":"application/vnd.mendeley-public-dataset.1+json"},
    )
    with urllib.request.urlopen(req,timeout=45) as r:
        return json.load(r)

def files(folder_id):
    q=urllib.parse.quote(folder_id)
    rows=get(f"{BASE}/datasets/{DS}/files?folder_id={q}&version={VERSION}&$start=0&$limit=1000")
    if isinstance(rows,list): return rows
    return rows.get("files") or rows.get("items") or rows.get("results") or []

def slim(r):
    cd=r.get("content_details") or {}
    return {
      "id":r.get("id"),
      "filename":r.get("filename"),
      "folder_id":r.get("folder_id"),
      "size":cd.get("size") or r.get("size"),
      "sha256":cd.get("sha256_hash"),
      "content_type":cd.get("content_type") or r.get("content_type"),
      "description":r.get("description"),
    }

def main():
    snap=get(f"{BASE}/datasets/{DS}/snapshot/{VERSION}")
    folders=get(f"{BASE}/datasets/{DS}/folders/{VERSION}")
    if isinstance(folders,dict):
        folders=folders.get("folders") or folders.get("items") or folders.get("results") or []
    allf=[]
    for r in files("root"): allf.append(slim(r))
    for f in folders:
        for r in files(str(f.get("id"))): allf.append(slim(r))
    out={
      "contract":"METADATA_PREFLIGHT_CONTRACT_V1.md",
      "file_contents_downloaded":False,
      "dataset":{
        "id":snap.get("id"),"version":snap.get("version"),
        "name":snap.get("name"),"doi":snap.get("doi"),
        "publish_date":snap.get("publish_date"),"license":snap.get("license")
      },
      "folder_count":len(folders),
      "folders":[{"id":f.get("id"),"name":f.get("name"),"parent_id":f.get("parent_id")} for f in folders],
      "file_count":len(allf),
      "files":sorted(allf,key=lambda x:(str(x.get("folder_id")),str(x.get("filename"))))
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
