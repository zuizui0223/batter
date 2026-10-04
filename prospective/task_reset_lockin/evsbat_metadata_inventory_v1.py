#!/usr/bin/env python3
"""Metadata-only inventory of evsBat Figshare article 29150924."""
from __future__ import annotations
import json, urllib.request

ARTICLE=29150924
API=f"https://api.figshare.com/v2/articles/{ARTICLE}"
UA="batter-evsbat-morphology-linkage-metadata/1.0"

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
          "supplied_md5":f.get("supplied_md5"),
          "computed_md5":f.get("computed_md5"),
          "is_link_only":f.get("is_link_only"),
          "description":f.get("description"),
        })
    out={
      "contract":"MORPHOLOGY_LINKAGE_PREFLIGHT_V1.md",
      "file_contents_downloaded":False,
      "article":{
        "id":a.get("id"),"title":a.get("title"),"doi":a.get("doi"),
        "version":a.get("version"),"published_date":a.get("published_date"),
        "modified_date":a.get("modified_date"),"description":a.get("description"),
        "keywords":a.get("keywords"),"license":a.get("license"),
      },
      "file_count":len(files),
      "files":sorted(files,key=lambda x:str(x.get("name"))),
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
