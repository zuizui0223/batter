#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, io, json, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CONTRACT=ROOT/"contract/phyllostomus_2023_replication_v1.json"
OUT=ROOT/"post_freeze_extensions/3d_niche_partition/p2023_social_metadata_v1.json"

TARGET_IDS={
 "989001041827562",
 "989001041827563",
 "989001041827573",
 "989001041827588",
 "989001041827592",
 "989001041827637",
}

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"batter-p2023-social-metadata-v1/1.0"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def main():
    c=json.loads(CONTRACT.read_text())
    spec=c["source"]["reference"]
    blob=fetch(spec["url"])
    md5=hashlib.md5(blob).hexdigest()
    if md5!=spec["md5"]:
        raise RuntimeError(f"reference MD5 mismatch {md5}")
    rows=list(csv.DictReader(io.StringIO(blob.decode("utf-8-sig",errors="replace"))))
    fields=rows[0].keys() if rows else []
    id_col="animal-id" if "animal-id" in fields else "individual-local-identifier"
    keep_fields=[
      x for x in [
        id_col,"animal-group-id","study-site","animal-sex",
        "animal-reproductive-condition","deployment-id","deploy-on-date","deploy-off-date"
      ] if x in fields
    ]
    target=[]
    for r in rows:
        iid=str(r.get(id_col,"")).strip()
        if iid in TARGET_IDS:
            target.append({k:r.get(k) for k in keep_fields})
    got={str(r.get(id_col,"")).strip() for r in target}
    if got!=TARGET_IDS:
        raise RuntimeError(f"target metadata mismatch missing={sorted(TARGET_IDS-got)}")
    payload={
      "schema_version":1,
      "study_id":"batter-p2023-social-metadata-v1",
      "reference_md5":md5,
      "target_ids":sorted(TARGET_IDS),
      "fields":keep_fields,
      "rows":sorted(target,key=lambda r:str(r.get(id_col,""))),
    }
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps(payload,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
