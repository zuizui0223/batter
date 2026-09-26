#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import urllib.parse
import urllib.request

REPO="https://datarepository.movebank.org"
CANDIDATES=[
  {"id":"grey_headed_flying_fox","doi":"10.5441/001/1.5bd6pq55/1","handle":"10255/move.1219","taxon_hint":"Pteropus poliocephalus"},
  {"id":"common_noctule_3d_migration","doi":"10.5441/001/1.5d736bf0/1","handle":"10255/move.841","taxon_hint":"Nyctalus noctula"},
  {"id":"christmas_island_flying_fox","doi":"10.5441/001/1.mn019k4d/1","handle":"10255/move.1406","taxon_hint":"Pteropus melanotus natalis"},
  {"id":"lyles_flying_fox","doi":"10.5441/001/1.j25661td/1","handle":"10255/move.870","taxon_hint":"Pteropus lylei"},
]

def fetch_json(url):
    req=urllib.request.Request(url,headers={
      "User-Agent":"batter-child-doi-source-resolver/1.0",
      "Accept":"application/json, application/hal+json",
    })
    with urllib.request.urlopen(req,timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))

def link(p,name):
    v=p.get("_links",{}).get(name,{})
    return str(v.get("href","")) if isinstance(v,dict) else ""

def embedded(p,name):
    v=p.get("_embedded",{}).get(name,[])
    return [x for x in v if isinstance(x,dict)] if isinstance(v,list) else []

def checksum(bs):
    c=bs.get("checkSum") or bs.get("checksum") or {}
    if not isinstance(c,dict): return "",""
    return str(c.get("checkSumAlgorithm") or c.get("algorithm") or ""),str(c.get("value") or "")

def resolve(c):
    urls=[
      f"{REPO}/server/api/pid/find?id={urllib.parse.quote(c['handle'],safe='')}",
      f"{REPO}/server/api/pid/find?id={urllib.parse.quote(c['doi'],safe='')}",
      f"{REPO}/server/api/pid/find?id={urllib.parse.quote('https://doi.org/'+c['doi'],safe='')}",
    ]
    item=None
    chosen=None
    errors=[]
    for url in urls:
        try:
            p=fetch_json(url)
            item=p
            chosen=url
            break
        except Exception as exc:
            errors.append(f"{type(exc).__name__}: {exc}")
    if item is None:
        return {**c,"status":"pid_failure","errors":errors,"bitstream_contents_fetched":False}

    files=[]
    bundles_url=link(item,"bundles")
    if bundles_url:
        bundles=fetch_json(bundles_url)
        for b in embedded(bundles,"bundles"):
            bname=str(b.get("name") or "")
            bu=link(b,"bitstreams")
            if not bu: continue
            bp=fetch_json(bu)
            for bs in embedded(bp,"bitstreams"):
                alg,val=checksum(bs)
                files.append({
                  "bundle_name":bname,
                  "bitstream_id":str(bs.get("uuid") or bs.get("id") or ""),
                  "filename":str(bs.get("name") or ""),
                  "size_bytes":bs.get("sizeBytes"),
                  "checksum_type":alg,
                  "checksum":val,
                  "content_url":link(bs,"content"),
                })
    else:
        # Some child identifiers may resolve directly to a bitstream-like object.
        content=link(item,"content")
        if content:
            alg,val=checksum(item)
            files.append({
              "bundle_name":"DIRECT",
              "bitstream_id":str(item.get("uuid") or item.get("id") or ""),
              "filename":str(item.get("name") or ""),
              "size_bytes":item.get("sizeBytes"),
              "checksum_type":alg,
              "checksum":val,
              "content_url":content,
            })

    return {
      **c,
      "status":"resolved" if files else "resolved_without_files",
      "pid_url":chosen,
      "item_links":sorted((item.get("_links") or {}).keys()),
      "files":files,
      "bitstream_contents_fetched":False,
    }

def main():
    results=[resolve(c) for c in CANDIDATES]
    payload={"resolver_id":"batter-child-doi-source-resolver-v1","results":results,"bitstream_contents_fetched":False}
    out=Path("results/child_doi_source_resolver_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(payload,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
