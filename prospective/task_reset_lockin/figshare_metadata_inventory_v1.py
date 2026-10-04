#!/usr/bin/env python3
"""Metadata-only Figshare inventory for task-reset lock-in source.

No file content is downloaded.
"""
from __future__ import annotations
import json, urllib.request

ARTICLE_ID=29209493
API=f"https://api.figshare.com/v2/articles/{ARTICLE_ID}"
UA="batter-task-reset-lockin-metadata/1.0"

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.load(r)

def main():
    a=get(API)
    versions=None
    try:
        versions=get(API+"/versions")
    except Exception as e:
        versions={"error":repr(e)}
    files=[]
    for f in a.get("files") or []:
        files.append({
            "id":f.get("id"),
            "name":f.get("name"),
            "size":f.get("size"),
            "is_link_only":f.get("is_link_only"),
            "download_url":f.get("download_url"),
            "supplied_md5":f.get("supplied_md5"),
            "computed_md5":f.get("computed_md5"),
        })
    out={
        "contract":"METADATA_PREFLIGHT_CONTRACT_V1.md",
        "file_contents_downloaded":False,
        "article":{
            "id":a.get("id"),
            "title":a.get("title"),
            "doi":a.get("doi"),
            "url_private_api":None,
            "url_public_api":API,
            "published_date":a.get("published_date"),
            "modified_date":a.get("modified_date"),
            "version":a.get("version"),
            "license":a.get("license"),
            "description":a.get("description"),
            "defined_type_name":a.get("defined_type_name"),
            "keywords":a.get("keywords"),
        },
        "versions":versions,
        "file_count":len(files),
        "files":files,
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
