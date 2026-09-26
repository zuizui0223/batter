#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, io, json, urllib.request
from collections import defaultdict
from pathlib import Path

ANNOTATED_URL="https://datarepository.movebank.org/server/api/core/bitstreams/a6a6db33-0aca-4902-a58d-f32980c1a3e1/content"
ANNOTATED_MD5="e0f6faedfd1f21bac222d9da430ea5d8"
REFERENCE_URL="https://datarepository.movebank.org/server/api/core/bitstreams/8141174e-c65d-4e9f-84a0-f0da3f68f8ce/content"
REFERENCE_MD5="1712fd40d5b321630f7b08259169c842"

def get(url, md5):
    req=urllib.request.Request(url,headers={"User-Agent":"batter-individual-covariate-audit/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        data=r.read()
    obs=hashlib.md5(data).hexdigest()
    if obs!=md5:
        raise RuntimeError(f"checksum mismatch {obs}")
    return data

def main():
    annotated=get(ANNOTATED_URL,ANNOTATED_MD5)
    reference=get(REFERENCE_URL,REFERENCE_MD5)
    rows=list(csv.DictReader(io.StringIO(annotated.decode("utf-8-sig"),newline="")))
    refs=list(csv.DictReader(io.StringIO(reference.decode("utf-8-sig"),newline="")))

    sessions=defaultdict(lambda: {"rows":0,"sexes":set()})
    individuals=defaultdict(lambda: {"rows":0,"sexes":set(),"batdays":set()})
    for r in rows:
        iid=str(r.get("animal-id","")).strip()
        day=str(r.get("BatDay","")).strip()
        sex=str(r.get("animal-sex","")).strip()
        if not iid: continue
        individuals[iid]["rows"]+=1
        if sex: individuals[iid]["sexes"].add(sex)
        if day: individuals[iid]["batdays"].add(day)
        if day:
            s=sessions[(iid,day)]
            s["rows"]+=1
            if sex: s["sexes"].add(sex)

    payload={
      "study_id":"batter-individual-covariate-audit-v1",
      "annotated_rows":len(rows),
      "reference_rows":len(refs),
      "reference_columns":list(refs[0].keys()) if refs else [],
      "reference_data":refs,
      "individuals":{
        iid:{
          "rows":v["rows"],
          "sexes":sorted(v["sexes"]),
          "batdays":sorted(v["batdays"],key=lambda x:float(x) if x.replace(".","",1).isdigit() else x),
          "session_count":len(v["batdays"])
        } for iid,v in sorted(individuals.items())
      },
      "sessions":{
        f"{iid}::{day}":{"rows":v["rows"],"sexes":sorted(v["sexes"])}
        for (iid,day),v in sorted(sessions.items())
      }
    }
    out=Path("results/individual_covariate_audit_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(payload,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
