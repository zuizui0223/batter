#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"post_freeze_extensions/3d_niche_partition/resource_metadata_audit_v1.json"

CONTRACTS={
 "hypsignathus":"contract/hypsignathus_replication_v1.json",
 "phyllostomus_2022":"contract/phyllostomus_replication_v1.json",
 "phyllostomus_2023":"contract/phyllostomus_2023_replication_v1.json",
 "phyllostomus_2016":"contract/phyllostomus_2016_dry_architecture_v1.json",
}

TERMS=re.compile(r"(behav|activity|state|feed|forag|resource|site|tree|roost|lek|habitat|patch|location|place|annotation|comment|class|mode|type)",re.I)
EXCLUDE_EXAMPLES=re.compile(r"(timestamp|time|longitude|latitude|height|speed|accel|temperature|hdop|vdop)",re.I)

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"batter-resource-metadata-audit-v1/1.0"})
    with urllib.request.urlopen(req,timeout=300) as r:
        return r.read()

def norm(v):
    return str(v).strip()

def audit_csv(blob, expected_md5=None, max_unique=101):
    if expected_md5:
        md5=hashlib.md5(blob).hexdigest()
        if md5!=expected_md5:
            raise RuntimeError(f"MD5 mismatch {md5} != {expected_md5}")
    text=blob.decode("utf-8-sig",errors="replace")
    reader=csv.DictReader(io.StringIO(text))
    fields=reader.fieldnames or []
    stats={f:{"nonempty":0,"unique":set(),"capped":False} for f in fields}
    n=0
    for row in reader:
        n+=1
        for f in fields:
            v=norm(row.get(f,""))
            if v=="" or v.lower() in {"na","nan","null","none"}:
                continue
            st=stats[f]
            st["nonempty"]+=1
            if not st["capped"]:
                st["unique"].add(v)
                if len(st["unique"])>=max_unique:
                    st["capped"]=True
                    st["unique"]=set(list(st["unique"])[:max_unique])
    cols=[]
    for f in fields:
        st=stats[f]
        vals=sorted(st["unique"])
        named=bool(TERMS.search(f))
        low=(not st["capped"] and 1 < len(vals) <= 30)
        include=named or low
        if not include:
            continue
        examples=[]
        if not EXCLUDE_EXAMPLES.search(f):
            examples=[x[:120] for x in vals[:20]]
        cols.append({
            "column":f,
            "matched_semantic_term":named,
            "low_cardinality_complete":low,
            "nonempty":st["nonempty"],
            "unique_count":(">="+str(max_unique)) if st["capped"] else len(vals),
            "examples":examples,
        })
    return {"rows":n,"columns":fields,"candidate_columns":cols}

def main():
    out={"schema_version":1,"study_id":"batter-resource-metadata-audit-v1","sources":{}}
    for key,path in CONTRACTS.items():
        c=json.loads((ROOT/path).read_text())
        src={}
        for kind in ("gps","reference"):
            spec=c["source"][kind]
            blob=fetch(spec["url"])
            src[kind]=audit_csv(blob,spec.get("md5"))
            src[kind]["md5"]=hashlib.md5(blob).hexdigest()
            src[kind]["size_bytes"]=len(blob)
        out["sources"][key]=src
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      k:{
        kind:[x["column"] for x in v[kind]["candidate_columns"]]
        for kind in ("gps","reference")
      } for k,v in out["sources"].items()
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
