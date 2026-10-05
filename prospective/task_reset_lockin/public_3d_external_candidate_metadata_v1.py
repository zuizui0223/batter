#!/usr/bin/env python3
"""Metadata-only inventory of two public Mendeley external 3-D candidates."""
from __future__ import annotations
import json, urllib.parse, urllib.request

BASE="https://data.mendeley.com/public-api"
UA="batter-public-3d-external-candidate-preflight/1.0"
DATASETS=[
 {"label":"pregnancy_2023","id":"hbb2t3dnbc","version":1,"doi":"10.17632/hbb2t3dnbc.1"},
 {"label":"adaptive_learning_2021","id":"wccbjdrrsg","version":1,"doi":"10.17632/wccbjdrrsg.1"},
]

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.mendeley-public-dataset.1+json"})
    with urllib.request.urlopen(req,timeout=60) as r:return json.load(r)

def files(ds,version,folder):
    q=urllib.parse.quote(folder)
    x=get(f"{BASE}/datasets/{ds}/files?folder_id={q}&version={version}&$start=0&$limit=1000")
    if isinstance(x,list):return x
    return x.get("files") or x.get("items") or x.get("results") or []

def main():
    out={"contract":"PUBLIC_3D_EXTERNAL_CANDIDATE_PREFLIGHT_V1.md","file_contents_downloaded":False,"datasets":[]}
    for d in DATASETS:
        snap=get(f"{BASE}/datasets/{d['id']}/snapshot/{d['version']}")
        folders=get(f"{BASE}/datasets/{d['id']}/folders/{d['version']}")
        if isinstance(folders,dict):
            folders=folders.get("folders") or folders.get("items") or folders.get("results") or []
        ff=[]
        for row in files(d["id"],d["version"],"root"):
            cd=row.get("content_details") or {}
            ff.append({"id":row.get("id"),"filename":row.get("filename"),"folder_id":row.get("folder_id"),
                       "size":cd.get("size") or row.get("size"),"sha256":cd.get("sha256_hash"),
                       "content_type":cd.get("content_type") or row.get("content_type")})
        for f in folders:
            for row in files(d["id"],d["version"],str(f.get("id"))):
                cd=row.get("content_details") or {}
                ff.append({"id":row.get("id"),"filename":row.get("filename"),"folder_id":row.get("folder_id"),
                           "size":cd.get("size") or row.get("size"),"sha256":cd.get("sha256_hash"),
                           "content_type":cd.get("content_type") or row.get("content_type")})
        out["datasets"].append({
          "label":d["label"],"requested_id":d["id"],"requested_doi":d["doi"],
          "snapshot":{"id":snap.get("id"),"name":snap.get("name"),"doi":snap.get("doi"),
                      "version":snap.get("version"),"publish_date":snap.get("publish_date"),
                      "description":snap.get("description")},
          "folders":[{"id":f.get("id"),"name":f.get("name"),"parent_id":f.get("parent_id")} for f in folders],
          "files":sorted(ff,key=lambda x:(str(x.get("folder_id")),str(x.get("filename")))),
          "file_count":len(ff),
        })
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
