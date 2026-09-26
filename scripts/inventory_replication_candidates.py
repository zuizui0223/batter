#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, urllib.parse, urllib.request
from pathlib import Path

REPO="https://datarepository.movebank.org"
DOIS=[
    {"study_id":404939825,"taxon":"Eidolon helvum","doi":"10.5441/001/1.k8n02jn8"},
    {"study_id":433126,"taxon":"Tadarida brasiliensis","doi":"10.5441/001/1.td71sn54"},
]

def fetch_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"batter-replication-inventory/1.0","Accept":"application/hal+json, application/json"})
    with urllib.request.urlopen(req,timeout=120) as r:
        raw=r.read(); final=r.geturl()
    payload=json.loads(raw.decode("utf-8"))
    return payload,raw,final

def link(p,name):
    x=p.get("_links",{}).get(name,{})
    return str(x.get("href","")) if isinstance(x,dict) else ""

def embedded(p,name):
    x=p.get("_embedded",{}).get(name,[])
    return [v for v in x if isinstance(v,dict)] if isinstance(x,list) else []

def checksum(bs):
    c=bs.get("checkSum") or bs.get("checksum") or {}
    if not isinstance(c,dict): return "",""
    return str(c.get("checkSumAlgorithm") or c.get("algorithm") or ""),str(c.get("value") or "")

def resolve(candidate):
    doi=candidate["doi"]
    # DSpace PID resolver accepts persistent identifiers; try DOI first.
    urls=[
      f"{REPO}/server/api/pid/find?id={urllib.parse.quote(doi,safe='')}",
      f"{REPO}/server/api/pid/find?id={urllib.parse.quote('https://doi.org/'+doi,safe='')}",
    ]
    last=None
    for url in urls:
        try:
            item,item_raw,item_url=fetch_json(url)
            if link(item,"bundles"):
                break
        except Exception as exc:
            last=exc
    else:
        raise RuntimeError(f"PID resolution failed: {last}")

    bundles,braw,burl=fetch_json(link(item,"bundles"))
    files=[]
    hashes={"item":hashlib.sha256(item_raw).hexdigest(),"bundles":hashlib.sha256(braw).hexdigest()}
    for bundle in embedded(bundles,"bundles"):
        name=str(bundle.get("name",""))
        bsu=link(bundle,"bitstreams")
        if not bsu: continue
        bp,br,_=fetch_json(bsu)
        hashes[f"bitstreams:{bundle.get('uuid') or name}"]=hashlib.sha256(br).hexdigest()
        for bs in embedded(bp,"bitstreams"):
            alg,val=checksum(bs)
            files.append({
              "bundle_name":name,
              "bitstream_id":str(bs.get("uuid") or bs.get("id") or ""),
              "filename":str(bs.get("name") or ""),
              "description":str(bs.get("description") or ""),
              "mime_type":str(bs.get("mimeType") or ""),
              "size_bytes":bs.get("sizeBytes"),
              "checksum_type":alg,
              "checksum":val,
              "content_url":link(bs,"content"),
            })
    return {**candidate,"resolved_item_url":item_url,"metadata_sha256":hashes,"files":sorted(files,key=lambda x:(x["bundle_name"],x["filename"]))}

def main():
    results=[]
    for c in DOIS:
        try:
            results.append({"status":"resolved",**resolve(c)})
        except Exception as exc:
            results.append({**c,"status":"resolution_failure","reason":f"{type(exc).__name__}: {exc}"})
    payload={"inventory_id":"batter-independent-replication-repository-inventory-v1","results":results,"bitstream_contents_fetched":False}
    out=Path("results/independent_replication_repository_inventory_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
      "results":[{
        "study_id":r["study_id"],"taxon":r["taxon"],"status":r["status"],
        "files":[{k:f.get(k) for k in ("bundle_name","filename","bitstream_id","size_bytes","checksum_type","checksum","content_url")} for f in r.get("files",[])]
      } for r in results],
      "bitstream_contents_fetched":False
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
