#!/usr/bin/env python3
"""Metadata-only inventory for Yamada et al. naive repeated-learning dataset."""
from __future__ import annotations
import json, urllib.request

ARTICLE=19102712
API=f"https://api.figshare.com/v2/articles/{ARTICLE}"
UA="batter-naive-learning-policy-metadata/1.0"

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.load(r)

def main():
    a=get(API)
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
          "supplied_md5":f.get("supplied_md5"),
          "computed_md5":f.get("computed_md5"),
          "is_link_only":f.get("is_link_only"),
          "download_url_present":bool(f.get("download_url")),
          "description":f.get("description"),
        })
    out={
      "contract":"METADATA_PREFLIGHT_CONTRACT_V1.md",
      "file_contents_downloaded":False,
      "article":{
        "id":a.get("id"),"title":a.get("title"),"doi":a.get("doi"),
        "version":a.get("version"),"published_date":a.get("published_date"),
        "modified_date":a.get("modified_date"),"description":a.get("description"),
        "defined_type_name":a.get("defined_type_name"),"keywords":a.get("keywords"),
        "license":a.get("license"),
      },
      "versions":versions,
      "file_count":len(files),
      "files":sorted(files,key=lambda x:str(x.get("name"))),
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
