#!/usr/bin/env python3
from __future__ import annotations

import json,re,urllib.parse,urllib.request
from pathlib import Path

DATACITE="https://api.datacite.org/dois"
PREFIX="10.5441"
REPO="https://datarepository.movebank.org"
QUERIES=["bat","bats","Chiroptera","flying fox","fruit bat","noctule"]
TOP_RE=re.compile(r"^10\.5441/001/1\.[^/]+$")

def fetch_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"batter-bat-panel-inventory/1.0","Accept":"application/json, application/hal+json"})
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

def discover():
    hits={}
    for q in QUERIES:
        url=DATACITE+"?"+urllib.parse.urlencode({"prefix":PREFIX,"query":q,"page[size]":100,"disable-facets":"true"})
        p=fetch_json(url)
        for item in p.get("data",[]):
            a=item.get("attributes",{})
            doi=str(a.get("doi") or item.get("id") or "").lower()
            if not TOP_RE.match(doi): continue
            title="; ".join(str(x.get("title") or "") for x in a.get("titles") or [] if isinstance(x,dict))
            tl=title.lower()
            if not any(term in tl for term in ["bat","bats","flying fox","noctule"]):
                continue
            h=hits.setdefault(doi,{"doi":doi,"title":title,"registered_url":str(a.get("url") or ""),"matched_queries":[]})
            h["matched_queries"].append(q)
    return [hits[k] for k in sorted(hits)]

def resolve_files(rec):
    doi=rec["doi"]
    urls=[
      f"{REPO}/server/api/pid/find?id={urllib.parse.quote(doi,safe='')}",
      f"{REPO}/server/api/pid/find?id={urllib.parse.quote('https://doi.org/'+doi,safe='')}",
    ]
    item=None
    for url in urls:
        try:
            p=fetch_json(url)
            if link(p,"bundles"):
                item=p; break
        except Exception:
            pass
    if item is None:
        raise RuntimeError("DSpace PID resolution failed")
    bundles=fetch_json(link(item,"bundles"))
    files=[]
    for bundle in embedded(bundles,"bundles"):
        bname=str(bundle.get("name") or "")
        bu=link(bundle,"bitstreams")
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
    files.sort(key=lambda x:(x["bundle_name"],x["filename"]))
    plausible=[]
    for f in files:
        name=f["filename"].lower()
        if f["bundle_name"]!="ORIGINAL" or not name.endswith(".csv"): continue
        if any(x in name for x in ["reference-data","reference_data","-acc","_acc","annotated","code"]): continue
        plausible.append(f)
    return {**rec,"files":files,"plausible_event_csvs":plausible}

def main():
    candidates=discover()
    results=[]
    for rec in candidates:
        try:
            results.append({"status":"resolved",**resolve_files(rec)})
        except Exception as exc:
            results.append({"status":"resolution_failure",**rec,"reason":f"{type(exc).__name__}: {exc}","files":[],"plausible_event_csvs":[]})
    payload={"inventory_id":"batter-bat-panel-source-inventory-v1","candidate_count":len(results),"results":results,"bitstream_contents_fetched":False}
    out=Path("results/bat_panel_source_inventory_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
      "candidate_count":len(results),
      "results":[{
        "doi":r["doi"],"title":r["title"],"status":r["status"],
        "plausible_event_csvs":[{k:f.get(k) for k in ["filename","bitstream_id","size_bytes","checksum_type","checksum","content_url"]} for f in r.get("plausible_event_csvs",[])]
      } for r in results],
      "bitstream_contents_fetched":False
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
