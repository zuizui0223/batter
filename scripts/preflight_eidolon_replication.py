#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, io, json, math, re, urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path

GPS_URL="https://datarepository.movebank.org/server/api/core/bitstreams/82b726a4-bc78-497a-81d9-a19844cb61fc/content"
GPS_SIZE=4497472
GPS_MD5="5f301a9e28c74d9b4823b6c5aa70cacf"
REF_URL="https://datarepository.movebank.org/server/api/core/bitstreams/245d9c8c-8d79-46b4-9f6f-fb4e2a4087e3/content"
REF_MD5="2d0a9de5564c0547657d8f83bdebce6d"
HEIGHT_PRIORITY=["height_above_msl","height_above_ellipsoid","height_raw"]
GAP=4*3600
MIN_SESSION=50

def get(url,md5,size=None):
    req=urllib.request.Request(url,headers={"User-Agent":"batter-eidolon-structural-preflight/1.0"})
    with urllib.request.urlopen(req,timeout=180) as r:
        data=r.read()
    if size is not None and len(data)!=size: raise RuntimeError(f"size mismatch {len(data)}")
    if hashlib.md5(data).hexdigest()!=md5: raise RuntimeError("checksum mismatch")
    return data

def canon(x):
    v=str(x).strip().lower().replace("-","_").replace(" ","_").replace(":","_")
    return re.sub(r"_+","_",v).strip("_")

def parse_time(x):
    return datetime.fromisoformat(str(x).strip().replace("Z","+00:00"))

def individual(r):
    return str(r.get("individual_local_identifier") or r.get("animal_id") or r.get("individual_id") or "").strip()

def finite_xy(r):
    try: x=float(r.get("location_long","")); y=float(r.get("location_lat",""))
    except: return False
    return math.isfinite(x) and math.isfinite(y)

def main():
    gps=get(GPS_URL,GPS_MD5,GPS_SIZE)
    ref=get(REF_URL,REF_MD5)
    reader=csv.DictReader(io.StringIO(gps.decode("utf-8-sig"),newline=""))
    headers=[canon(h) for h in reader.fieldnames or []]
    rows=[]
    for raw in reader:
        rows.append({canon(k):("" if v is None else str(v)) for k,v in raw.items() if k is not None})
    ref_reader=csv.DictReader(io.StringIO(ref.decode("utf-8-sig"),newline=""))
    refs=[{canon(k):("" if v is None else str(v)) for k,v in r.items() if k is not None} for r in ref_reader]

    height=next((h for h in HEIGHT_PRIORITY if h in headers),None)
    if not height: raise RuntimeError(f"no native height field; headers={headers}")

    times=defaultdict(list)
    xy_height_events=0
    for r in rows:
        iid=individual(r)
        if not iid or not finite_xy(r) or not str(r.get(height,"")).strip():
            continue
        try: t=parse_time(r.get("timestamp",""))
        except: continue
        xy_height_events+=1
        times[iid].append(t)

    structure={}
    repeat=[]
    for iid,vals in sorted(times.items()):
        vals=sorted(vals); blocks=[]; n=0; prev=None
        for t in vals:
            if prev is not None and (t-prev).total_seconds()>GAP:
                blocks.append(n); n=0
            n+=1; prev=t
        if n: blocks.append(n)
        eligible=[x for x in blocks if x>=MIN_SESSION]
        structure[iid]={
            "event_count":len(vals),
            "block_counts":blocks,
            "eligible_session_counts":eligible,
            "eligible_session_count":len(eligible),
        }
        if len(eligible)>=2: repeat.append(iid)

    # Reference metadata only: compact values useful for cohort stratification.
    ref_columns=sorted(set(k for r in refs for k in r))
    compact_refs=[]
    wanted=[
      "animal_id","individual_local_identifier","animal_taxon","animal_sex",
      "deploy_on_date","deploy_off_date","deployment_id",
      "deployment_comments","capture_location","location_lat","location_long",
      "study_site","animal_mass","duty_cycle"
    ]
    for r in refs:
        compact_refs.append({k:r.get(k,"") for k in wanted if k in r and r.get(k,"")!=""})

    payload={
      "preflight_id":"batter-eidolon-independent-replication-structural-v1",
      "source":{"gps_md5":GPS_MD5,"gps_bytes":len(gps),"reference_md5":REF_MD5},
      "gps_headers":headers,
      "gps_row_count":len(rows),
      "native_height_field":height,
      "numeric_height_values_parsed":False,
      "xy_height_presence_event_count":xy_height_events,
      "individual_count":len(times),
      "repeat_individual_count":len(repeat),
      "repeat_individual_ids":repeat,
      "session_structure":structure,
      "reference_row_count":len(refs),
      "reference_columns":ref_columns,
      "reference_compact":compact_refs,
      "passes_gate":len(times)>=8 and len(repeat)>=5,
    }
    out=Path("results/eidolon_structural_preflight_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
      k:payload[k] for k in [
        "gps_row_count","native_height_field","numeric_height_values_parsed",
        "xy_height_presence_event_count","individual_count","repeat_individual_count",
        "repeat_individual_ids","passes_gate","reference_row_count","reference_columns","reference_compact"
      ]
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
