#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, io, json, re, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CONTRACT=ROOT/"post_freeze_extensions/behavior_proxy_inventory/contract_v1.json"
OUT=ROOT/"post_freeze_extensions/behavior_proxy_inventory/result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/behavior_proxy_inventory/RESULT_V1.md"

SOURCES={
 "eidolon":{
   "gps":{"url":"https://datarepository.movebank.org/server/api/core/bitstreams/82b726a4-bc78-497a-81d9-a19844cb61fc/content","md5":"5f301a9e28c74d9b4823b6c5aa70cacf"},
   "reference":{"url":"https://datarepository.movebank.org/server/api/core/bitstreams/245d9c8c-8d79-46b4-9f6f-fb4e2a4087e3/content","md5":"2d0a9de5564c0547657d8f83bdebce6d"}
 },
 "hypsignathus":{
   "gps":{"url":"https://datarepository.movebank.org/server/api/core/bitstreams/7cc2bd3f-a9d3-4529-bd6d-7fc1fc47e000/content","md5":"e2fd92d7647c745b54191def19131570"},
   "reference":{"url":"https://datarepository.movebank.org/server/api/core/bitstreams/90da2331-91a0-48da-9c6d-8b80cbc12480/content","md5":"313cb130df9c69a82526640ad318e24f"}
 },
 "phyllostomus_2022":{
   "gps":{"url":"https://datarepository.movebank.org/server/api/core/bitstreams/fa2e42c9-275a-4833-b74f-3e2715c8794d/content","md5":"7bae1d6d59acad98a4df7348c04d5ea6"},
   "reference":{"url":"https://datarepository.movebank.org/server/api/core/bitstreams/baae11b3-e466-4f51-b7ee-3119fc51810a/content","md5":"008c0513007d291884d128b7c7af9629"}
 },
 "phyllostomus_2023":{
   "gps":{"url":"https://datarepository.movebank.org/server/api/core/bitstreams/a842b308-d4a1-4c31-81db-acf699e5cadb/content","md5":"327c31ea3e129d692bbb527ad32995f1"},
   "reference":{"url":"https://datarepository.movebank.org/server/api/core/bitstreams/31403d15-5784-4b01-80bd-9ef9c0a7f4cd/content","md5":"9880d2b155237d61ce6e6391296df1da"}
 },
 "phyllostomus_2016":{
   "gps":{"url":"https://datarepository.movebank.org/server/api/core/bitstreams/40623d69-2787-4aec-8237-4d2264bd665f/content","md5":"58d555f48e07b5e41e2c5d1983b25e80"},
   "reference":{"url":"https://datarepository.movebank.org/server/api/core/bitstreams/35cd7452-fe48-4423-81fb-4ff8e0717da8/content","md5":"17bf1ab59daeb37b5ee1f8f1c127d0b4"}
 }
}

def canon(x):
    return re.sub(r"_+","_",str(x).strip().lower().replace("-","_").replace(" ","_").replace(":","_")).strip("_")

def get(spec,panel,kind):
    req=urllib.request.Request(spec["url"],headers={"User-Agent":"batter-behavior-proxy-inventory-v1/1.0"})
    with urllib.request.urlopen(req,timeout=300) as r:
        data=r.read()
    md5=hashlib.md5(data).hexdigest()
    if md5!=spec["md5"]:
        raise RuntimeError(f"{panel} {kind} checksum mismatch {md5}")
    return data

def header(data):
    text=data.decode("utf-8-sig",errors="replace")
    row=next(csv.reader(io.StringIO(text,newline="")))
    return [canon(x) for x in row]

def main():
    c=json.loads(CONTRACT.read_text())
    kws=[x.lower() for x in c["candidate_keywords"]]
    panels={}
    for panel in c["panels"]:
        rec={}
        for kind in ("gps","reference"):
            data=get(SOURCES[panel][kind],panel,kind)
            h=header(data)
            candidate=[x for x in h if any(k in x.lower() for k in kws)]
            rec[kind]={
                "md5":hashlib.md5(data).hexdigest(),
                "size_bytes":len(data),
                "column_count":len(h),
                "headers":h,
                "candidate_behavior_or_kinematic_fields":candidate
            }
        panels[panel]=rec

    common_gps=set(panels[c["panels"][0]]["gps"]["headers"])
    for p in c["panels"][1:]:
        common_gps &= set(panels[p]["gps"]["headers"])
    common_candidates=[x for x in sorted(common_gps) if any(k in x for k in kws)]

    payload={
      "schema_version":1,
      "study_id":c["study_id"],
      "headers_only_for_proxy_selection":True,
      "panels":panels,
      "gps_fields_common_to_all_five":sorted(common_gps),
      "candidate_proxy_fields_common_to_all_five":common_candidates,
      "restrictions":c["restrictions"]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    lines=["# Behaviour-proxy inventory v1","",
           "**Header-only inventory. No vertical outcome values were summarized.**","",
           "| panel | GPS candidate fields | reference candidate fields |",
           "|---|---|---|"]
    for p in c["panels"]:
        g=", ".join(panels[p]["gps"]["candidate_behavior_or_kinematic_fields"]) or "none"
        q=", ".join(panels[p]["reference"]["candidate_behavior_or_kinematic_fields"]) or "none"
        lines.append(f"| {p} | {g} | {q} |")
    lines += ["","Common candidate proxy fields across all five GPS tables:",
              "",", ".join(common_candidates) if common_candidates else "**none**",""]
    OUT_MD.write_text("\n".join(lines))

    print(json.dumps({
      "candidate_fields":{
        p:{
          "gps":panels[p]["gps"]["candidate_behavior_or_kinematic_fields"],
          "reference":panels[p]["reference"]["candidate_behavior_or_kinematic_fields"]
        } for p in c["panels"]
      },
      "common_candidate_proxy_fields":common_candidates
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
