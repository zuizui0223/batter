#!/usr/bin/env python3
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path
import re
import urllib.request

CANDIDATES=[
  {
    "id":"hypsignathus",
    "doi":"10.5441/001/1.278",
    "taxon":"Hypsignathus monstrosus",
    "gps":{"url":"https://datarepository.movebank.org/server/api/core/bitstreams/7cc2bd3f-a9d3-4529-bd6d-7fc1fc47e000/content","md5":"e2fd92d7647c745b54191def19131570","size":9383514},
    "ref":{"url":"https://datarepository.movebank.org/server/api/core/bitstreams/90da2331-91a0-48da-9c6d-8b80cbc12480/content","md5":"313cb130df9c69a82526640ad318e24f","size":12509}
  },
  {
    "id":"phyllostomus_2021_2022",
    "doi":"10.5441/001/1.321",
    "taxon":"Phyllostomus hastatus",
    "gps":{"url":"https://datarepository.movebank.org/server/api/core/bitstreams/fa2e42c9-275a-4833-b74f-3e2715c8794d/content","md5":"7bae1d6d59acad98a4df7348c04d5ea6","size":5846425},
    "ref":{"url":"https://datarepository.movebank.org/server/api/core/bitstreams/baae11b3-e466-4f51-b7ee-3119fc51810a/content","md5":"008c0513007d291884d128b7c7af9629","size":15626}
  },
  {
    "id":"phyllostomus_2023",
    "doi":"10.5441/001/1.322",
    "taxon":"Phyllostomus hastatus",
    "gps":{"url":"https://datarepository.movebank.org/server/api/core/bitstreams/a842b308-d4a1-4c31-81db-acf699e5cadb/content","md5":"327c31ea3e129d692bbb527ad32995f1","size":3355955},
    "ref":{"url":"https://datarepository.movebank.org/server/api/core/bitstreams/31403d15-5784-4b01-80bd-9ef9c0a7f4cd/content","md5":"9880d2b155237d61ce6e6391296df1da","size":8384}
  }
]


def canon(x):
    v=str(x).strip().lower().replace("-","_").replace(" ","_").replace(":","_")
    return re.sub(r"_+","_",v).strip("_")


def get(spec):
    req=urllib.request.Request(spec["url"],headers={"User-Agent":"batter-new-panel-context-preflight/1.0"})
    with urllib.request.urlopen(req,timeout=240) as r:
        data=r.read()
    if len(data)!=spec["size"]:
        raise RuntimeError(f"size mismatch {len(data)} != {spec['size']}")
    if hashlib.md5(data).hexdigest()!=spec["md5"]:
        raise RuntimeError("checksum mismatch")
    return data


def parse_csv(data):
    reader=csv.DictReader(io.StringIO(data.decode("utf-8-sig",errors="replace"),newline=""))
    rows=[{canon(k):("" if v is None else str(v)) for k,v in row.items() if k is not None} for row in reader]
    return [canon(h) for h in reader.fieldnames or []],rows


def parse_time(v):
    return datetime.fromisoformat(str(v).strip().replace("Z","+00:00"))


def iid(row):
    return str(row.get("individual_local_identifier") or row.get("animal_id") or row.get("individual_id") or "").strip()


def main():
    results=[]
    for cand in CANDIDATES:
        gps_h,gps=parse_csv(get(cand["gps"]))
        ref_h,refs=parse_csv(get(cand["ref"]))

        years=Counter()
        ids=Counter()
        for row in gps:
            animal=iid(row)
            if animal:
                ids[animal]+=1
            try:
                years[str(parse_time(row.get("timestamp","")).year)]+=1
            except Exception:
                pass

        context_fields=[
          "individual_local_identifier","animal_id","individual_id",
          "animal_taxon","animal_sex","animal_life_stage","animal_mass",
          "animal_reproductive_condition","manipulation_type","deployment_id",
          "deploy_on_date","deploy_off_date","study_site","capture_location",
          "location_lat","location_long","deployment_comments","duty_cycle"
        ]
        compact_refs=[]
        for r in refs:
            compact_refs.append({k:r[k] for k in context_fields if k in r and str(r[k]).strip()})

        results.append({
          "id":cand["id"],"doi":cand["doi"],"taxon":cand["taxon"],
          "gps_headers":gps_h,"gps_rows":len(gps),
          "gps_year_counts":dict(years),
          "gps_individual_count":len(ids),
          "gps_individual_event_counts":dict(ids),
          "reference_headers":ref_h,"reference_rows":len(refs),
          "reference_compact":compact_refs,
          "numeric_height_values_parsed":False,
        })

    payload={"preflight_id":"batter-new-panel-context-preflight-v1","results":results,"numeric_height_values_parsed":False}
    out=Path("results/new_panel_context_preflight_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(payload,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
