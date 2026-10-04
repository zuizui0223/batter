#!/usr/bin/env python3
"""Compact Mendeley folder topology summary; metadata only, no file contents."""
from __future__ import annotations
import json, urllib.parse, urllib.request
from collections import Counter, defaultdict

BASE="https://data.mendeley.com/public-api"
DATASETS=[("A","gpcg9m5758",1),("B","n9d8gbz3xr",1)]
UA="batter-ontogenetic-topology/1.0"

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.mendeley-public-dataset.1+json"})
    with urllib.request.urlopen(req,timeout=30) as r:
        return json.load(r)

def main():
    out={}
    for label,ds,v in DATASETS:
        try:
            folders=get(f"{BASE}/datasets/{ds}/folders/{v}")
            if isinstance(folders,dict):
                folders=folders.get("folders") or folders.get("items") or folders.get("results") or []
        except Exception as e:
            out[label]={"status":"FOLDER_METADATA_UNAVAILABLE","error":repr(e)}
            continue
        by_id={str(x.get("id")):x for x in folders if x.get("id")}
        children=defaultdict(list)
        roots=[]
        for x in folders:
            p=x.get("parent_id")
            if p:
                children[str(p)].append(x)
            else:
                roots.append(x)

        def node(x,depth=0):
            xid=str(x.get("id"))
            kids=children.get(xid,[])
            return {
                "id":xid,
                "name":x.get("name"),
                "direct_child_folder_count":len(kids),
                "direct_child_folder_names":[k.get("name") for k in kids[:100]],
            }
        out[label]={
            "status":"PASS",
            "folder_count":len(folders),
            "root_folder_count":len(roots),
            "root_folders":[node(x) for x in roots],
            "orphan_parent_ids":sorted(set(str(x.get("parent_id")) for x in folders if x.get("parent_id") and str(x.get("parent_id")) not in by_id)),
        }
        # also summarize parents with >=3 direct children, useful for cohort/individual layers
        heavy=[]
        for pid,kids in children.items():
            if len(kids)>=3:
                p=by_id.get(pid,{})
                heavy.append({
                    "parent_id":pid,
                    "parent_name":p.get("name"),
                    "parent_parent_id":p.get("parent_id"),
                    "n_children":len(kids),
                    "child_names":[k.get("name") for k in kids[:80]],
                })
        out[label]["multi_child_parents"]=sorted(heavy,key=lambda z:(-z["n_children"],str(z["parent_name"])))[:40]
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
