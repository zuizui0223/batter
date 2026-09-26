#!/usr/bin/env python3
from __future__ import annotations

import json, urllib.parse, urllib.request
from pathlib import Path

QUERIES=["bat","bats","Chiroptera","flying fox","fruit bat","free-tailed bat"]
DATACITE="https://api.datacite.org/dois"

def fetch_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"batter-bat-datacite-discovery/1.0","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))

def main():
    hits={}
    for q in QUERIES:
        url=DATACITE+"?"+urllib.parse.urlencode({"prefix":"10.5441","query":q,"page[size]":100,"disable-facets":"true"})
        payload=fetch_json(url)
        for item in payload.get("data",[]):
            attrs=item.get("attributes",{})
            doi=str(attrs.get("doi") or item.get("id") or "").lower()
            registered=str(attrs.get("url") or "")
            if not doi.startswith("10.5441/"):
                continue
            if "movebank" not in registered.lower():
                continue
            titles=attrs.get("titles") or []
            title="; ".join(str(x.get("title") or "") for x in titles if isinstance(x,dict))
            creators=attrs.get("creators") or []
            creator_names=[str(x.get("name") or "") for x in creators if isinstance(x,dict)]
            descriptions=attrs.get("descriptions") or []
            desc=" ".join(str(x.get("description") or "") for x in descriptions if isinstance(x,dict))
            rec=hits.setdefault(doi,{
                "doi":doi,"registered_url":registered,"title":title,
                "creator_names":creator_names,"description":desc,
                "matched_queries":[]
            })
            rec["matched_queries"].append(q)
    results=sorted(hits.values(),key=lambda x:x["doi"])
    payload={"discovery_id":"batter-movebank-bat-datacite-discovery-v1","queries":QUERIES,"candidate_count":len(results),"candidates":results}
    out=Path("results/movebank_bat_datacite_discovery_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
      "candidate_count":len(results),
      "candidates":[{"doi":x["doi"],"title":x["title"],"registered_url":x["registered_url"],"matched_queries":x["matched_queries"]} for x in results]
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
