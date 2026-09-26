#!/usr/bin/env python3
from __future__ import annotations

import json, urllib.parse, urllib.request
from pathlib import Path

DOIS=[
  "10.5441/001/1.k8n02jn8",
  "10.5441/001/1.td71sn54",
]
REPOSITORY="https://datarepository.movebank.org"

def fetch_json(url):
    req=urllib.request.Request(url,headers={
        "User-Agent":"batter-replication-package-resolver/1.0",
        "Accept":"application/json, application/hal+json",
    })
    with urllib.request.urlopen(req,timeout=120) as r:
        raw=r.read()
        final=r.geturl()
    obj=json.loads(raw.decode("utf-8"))
    return obj,final

def resolve_doi(doi):
    dc, _ = fetch_json("https://api.datacite.org/dois/"+urllib.parse.quote(doi,safe=""))
    attrs=dc.get("data",{}).get("attributes",{})
    registered_url=str(attrs.get("url") or "")
    req=urllib.request.Request("https://doi.org/"+doi,headers={"User-Agent":"batter-replication-package-resolver/1.0"})
    with urllib.request.urlopen(req,timeout=120) as r:
        final_url=r.geturl()
    handle=None
    for value in (registered_url,final_url):
        marker="/handle/"
        if marker in value:
            handle=value.split(marker,1)[1].split("?",1)[0].strip("/")
            break
    if not handle:
        raise RuntimeError(f"cannot resolve handle from {registered_url!r} or {final_url!r}")
    item,_=fetch_json(f"{REPOSITORY}/server/api/pid/find?id={urllib.parse.quote(handle,safe='')}")
    bundles_url=item.get("_links",{}).get("bundles",{}).get("href")
    bundles,_=fetch_json(bundles_url)
    files=[]
    for bundle in bundles.get("_embedded",{}).get("bundles",[]):
        bname=str(bundle.get("name") or "")
        burl=bundle.get("_links",{}).get("bitstreams",{}).get("href")
        if not burl: continue
        bss,_=fetch_json(burl)
        for bs in bss.get("_embedded",{}).get("bitstreams",[]):
            cs=bs.get("checkSum") or bs.get("checksum") or {}
            files.append({
                "bundle_name":bname,
                "bitstream_id":str(bs.get("uuid") or bs.get("id") or ""),
                "filename":str(bs.get("name") or ""),
                "description":str(bs.get("description") or ""),
                "mime_type":str(bs.get("mimeType") or bs.get("mime_type") or ""),
                "size_bytes":bs.get("sizeBytes"),
                "checksum_type":str(cs.get("checkSumAlgorithm") or cs.get("algorithm") or ""),
                "checksum":str(cs.get("value") or ""),
                "content_url":str(bs.get("_links",{}).get("content",{}).get("href") or ""),
            })
    files.sort(key=lambda x:(x["bundle_name"],x["filename"],x["bitstream_id"]))
    return {
       "doi":doi,
       "datacite_registered_url":registered_url,
       "doi_final_url":final_url,
       "handle":handle,
       "file_count":len(files),
       "files":files,
       "bitstream_contents_fetched":False,
    }

def main():
    results=[]
    for doi in DOIS:
        try:
            results.append(resolve_doi(doi))
        except Exception as exc:
            results.append({"doi":doi,"status":"resolution_failure","reason":f"{type(exc).__name__}: {exc}","bitstream_contents_fetched":False})
    payload={"resolver_id":"batter-replication-package-resolver-v1","results":results,"bitstream_contents_fetched":False}
    out=Path("results/replication_package_resolver_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(payload,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
