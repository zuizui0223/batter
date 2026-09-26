#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, io, json, math, re, urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path

GPS_URL="https://datarepository.movebank.org/server/api/core/bitstreams/9e968b20-bfab-4cb3-a7c4-218ce96cdf2d/content"
GPS_SIZE=110094
GPS_MD5="67a78fb96f765181835f73140b15dfb9"
REF_URL="https://datarepository.movebank.org/server/api/core/bitstreams/dab385b9-e9bf-4208-9388-e968b3245355/content"
REF_MD5="f74699bde7154c7ddeb0ca219284fe96"
HEIGHT_PRIORITY=["height_above_msl","height_above_ellipsoid","height_raw"]
GAP=4*3600
MIN_SESSION=50

def get(url,md5,size=None):
    req=urllib.request.Request(url,headers={"User-Agent":"batter-tbrasiliensis-structural-preflight/1.0"})
    with urllib.request.urlopen(req,timeout=120) as r: data=r.read()
    if size is not None and len(data)!=size: raise RuntimeError(f"size mismatch {len(data)} != {size}")
    if hashlib.md5(data).hexdigest()!=md5: raise RuntimeError("checksum mismatch")
    return data

def canon(x):
    v=str(x).strip().lower().replace("-","_").replace(" ","_").replace(":","_")
    return re.sub(r"_+","_",v).strip("_")

def parse_time(x):
    return datetime.fromisoformat(str(x).strip().replace("Z","+00:00"))

def iid(r):
    return str(r.get("individual_local_identifier") or r.get("animal_id") or r.get("individual_id") or "").strip()

def finite_xy(r):
    try: lon=float(r.get("location_long","")); lat=float(r.get("location_lat",""))
    except: return False
    return math.isfinite(lon) and math.isfinite(lat)

def main():
    gps=get(GPS_URL,GPS_MD5,GPS_SIZE); ref=get(REF_URL,REF_MD5)
    reader=csv.DictReader(io.StringIO(gps.decode("utf-8-sig"),newline=""))
    headers=[canon(h) for h in reader.fieldnames or []]
    rows=[{canon(k):("" if v is None else str(v)) for k,v in row.items() if k is not None} for row in reader]
    refs=[{canon(k):("" if v is None else str(v)) for k,v in row.items() if k is not None}
          for row in csv.DictReader(io.StringIO(ref.decode("utf-8-sig"),newline=""))]
    height=next((h for h in HEIGHT_PRIORITY if h in headers),None)

    times=defaultdict(list)
    presence_count=0
    if height is not None:
      for r in rows:
        animal=iid(r)
        if not animal or not finite_xy(r) or not str(r.get(height,"")).strip(): continue
        try: t=parse_time(r.get("timestamp",""))
        except: continue
        presence_count+=1; times[animal].append(t)

    structure={}; repeat=[]
    for animal,vals in sorted(times.items()):
        vals=sorted(vals); blocks=[]; n=0; prev=None
        for t in vals:
            if prev is not None and (t-prev).total_seconds()>GAP:
                if n: blocks.append(n)
                n=0
            n+=1; prev=t
        if n: blocks.append(n)
        elig=[x for x in blocks if x>=MIN_SESSION]
        structure[animal]={"event_count":len(vals),"block_counts":blocks,"eligible_session_counts":elig,"eligible_session_count":len(elig)}
        if len(elig)>=2: repeat.append(animal)

    payload={
      "preflight_id":"batter-tbrasiliensis-structural-preflight-v1",
      "source":{"gps_md5":GPS_MD5,"gps_bytes":len(gps),"reference_md5":REF_MD5},
      "gps_row_count":len(rows),
      "gps_headers":headers,
      "reference_row_count":len(refs),
      "reference_columns":sorted({k for r in refs for k in r}),
      "native_height_field":height,
      "numeric_height_values_parsed":False,
      "xy_height_presence_event_count":presence_count,
      "individual_count":len(times),
      "repeat_individual_count":len(repeat),
      "repeat_individual_ids":repeat,
      "session_structure":structure,
      "passes_screen_gate":height is not None and len(times)>=8 and len(repeat)>=5,
    }
    out=Path("results/tbrasiliensis_structural_preflight_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:payload[k] for k in ["gps_row_count","native_height_field","numeric_height_values_parsed","xy_height_presence_event_count","individual_count","repeat_individual_count","repeat_individual_ids","passes_screen_gate","gps_headers","reference_row_count","reference_columns"]},sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
