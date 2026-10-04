#!/usr/bin/env python3
"""Metadata-only Figshare inventory for naive-to-familiar learning source."""
from __future__ import annotations
import json, urllib.request

ARTICLE_ID=19102712
API=f"https://api.figshare.com/v2/articles/{ARTICLE_ID}"
UA="batter-naive-to-familiar-metadata/1.0"

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.load(r)

def main():
    a=get(API)
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
        "id":a.get("id"),"title":a.get("title"),"doi":a.get("doi"),
        "version":a.get("version"),"published_date":a.get("published_date"),
        "modified_date":a.get("modified_date"),"license":a.get("license"),
        "description":a.get("description"),"keywords":a.get("keywords"),
      },
      "file_count":len(files),
      "files":files,
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
