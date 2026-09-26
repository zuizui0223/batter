#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, io, json, math, re, urllib.parse, urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path

REPO="https://datarepository.movebank.org"
CANDIDATES=[
  {"id":"noctule_migration","doi":"10.5441/001/1.5d736bf0","title":"3D migration flights of common noctules"},
  {"id":"noctule_foraging","doi":"10.5441/001/1.7t4b97qf","title":"Foraging heights of common noctules"},
]
HEIGHT_PRIORITY=["height_above_msl","height_above_ellipsoid","height_raw"]
MIN_SESSION=50
GAP=4*3600

def fetch_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"batter-noctule-structural-preflight/1.0"})
    with urllib.request.urlopen(req,timeout=180) as r: return r.read()

def fetch_json(url):
    return json.loads(fetch_bytes(url).decode("utf-8"))

def link(p,name):
    v=p.get("_links",{}).get(name,{})
    return str(v.get("href","")) if isinstance(v,dict) else ""

def embedded(p,name):
    v=p.get("_embedded",{}).get(name,[])
    return [x for x in v if isinstance(x,dict)] if isinstance(v,list) else []

def canon(x):
    v=str(x).strip().lower().replace("-","_").replace(" ","_").replace(":","_")
    return re.sub(r"_+","_",v).strip("_")

def parse_time(x):
    return datetime.fromisoformat(str(x).strip().replace("Z","+00:00"))

def finite_xy(r):
    try: lon=float(r.get("location_long","")); lat=float(r.get("location_lat",""))
    except: return False
    return math.isfinite(lon) and math.isfinite(lat)

def iid(r):
    return str(r.get("individual_local_identifier") or r.get("animal_id") or r.get("individual_id") or "").strip()

def resolve_files(doi):
    item=fetch_json(f"{REPO}/server/api/pid/find?id={urllib.parse.quote(doi,safe='')}")
    bundles=fetch_json(link(item,"bundles"))
    files=[]
    for b in embedded(bundles,"bundles"):
        if str(b.get("name") or "")!="ORIGINAL": continue
        bu=link(b,"bitstreams")
        if not bu: continue
        bp=fetch_json(bu)
        for bs in embedded(bp,"bitstreams"):
            cs=bs.get("checkSum") or {}
            files.append({
              "filename":str(bs.get("name") or ""),
              "bitstream_id":str(bs.get("uuid") or ""),
              "size_bytes":bs.get("sizeBytes"),
              "checksum_type":str(cs.get("checkSumAlgorithm") or ""),
              "checksum":str(cs.get("value") or ""),
              "content_url":link(bs,"content"),
            })
    return files

def select_event_csv(files):
    out=[]
    for f in files:
        name=f["filename"].lower()
        if not name.endswith(".csv"): continue
        if any(x in name for x in ["reference-data","reference_data","-acc","_acc","annotated","code"]): continue
        out.append(f)
    return sorted(out,key=lambda x:(0 if "gps" in x["filename"].lower() else 1,x["size_bytes"] or 0))

def screen_file(spec):
    data=fetch_bytes(spec["content_url"])
    if spec.get("size_bytes") is not None and len(data)!=int(spec["size_bytes"]):
        raise RuntimeError("size mismatch")
    if str(spec.get("checksum_type","")).upper()=="MD5" and spec.get("checksum"):
        if hashlib.md5(data).hexdigest()!=spec["checksum"]: raise RuntimeError("checksum mismatch")
    reader=csv.DictReader(io.StringIO(data.decode("utf-8-sig"),newline=""))
    headers=[canon(h) for h in reader.fieldnames or []]
    rows=[{canon(k):("" if v is None else str(v)) for k,v in row.items() if k is not None} for row in reader]
    height=next((h for h in HEIGHT_PRIORITY if h in headers),None)
    times=defaultdict(list); presence=0
    if height:
        for r in rows:
            individual=iid(r)
            if not individual or not finite_xy(r) or not str(r.get(height,"")).strip(): continue
            try: t=parse_time(r.get("timestamp",""))
            except: continue
            times[individual].append(t); presence+=1
    structure={}; repeat=[]
    for individual,vals in sorted(times.items()):
        vals=sorted(vals); blocks=[]; n=0; prev=None
        for t in vals:
            if prev is not None and (t-prev).total_seconds()>GAP:
                if n: blocks.append(n)
                n=0
            n+=1; prev=t
        if n: blocks.append(n)
        elig=[n for n in blocks if n>=MIN_SESSION]
        structure[individual]={"event_count":len(vals),"block_counts":blocks,"eligible_session_counts":elig,"eligible_session_count":len(elig)}
        if len(elig)>=2: repeat.append(individual)
    return {
      "filename":spec["filename"],"bitstream_id":spec["bitstream_id"],
      "size_bytes":len(data),"checksum":spec.get("checksum"),
      "row_count":len(rows),"headers":headers,"native_height_field":height,
      "numeric_height_values_parsed":False,
      "xy_height_presence_event_count":presence,
      "individual_count":len(times),"repeat_individual_count":len(repeat),
      "repeat_individual_ids":repeat,"session_structure":structure,
      "passes_gate":height is not None and len(times)>=8 and len(repeat)>=5,
    }

def main():
    results=[]
    for cand in CANDIDATES:
        try:
            files=resolve_files(cand["doi"])
            plausible=select_event_csv(files)
            screened=[]
            for spec in plausible:
                # Avoid accidental huge non-GPS tables; these two historical tracking datasets
                # are expected to be small, and >100 MB is left for a separate preflight.
                if spec.get("size_bytes") and int(spec["size_bytes"])>100_000_000:
                    screened.append({"filename":spec["filename"],"size_bytes":spec["size_bytes"],"status":"too_large_for_this_preflight","numeric_height_values_parsed":False})
                    continue
                try:
                    screened.append({"status":"screened",**screen_file(spec)})
                except Exception as exc:
                    screened.append({"filename":spec["filename"],"status":"file_failure","reason":f"{type(exc).__name__}: {exc}","numeric_height_values_parsed":False})
            results.append({**cand,"status":"resolved","original_files":files,"plausible_event_files":screened})
        except Exception as exc:
            results.append({**cand,"status":"resolution_failure","reason":f"{type(exc).__name__}: {exc}","plausible_event_files":[]})

    payload={"preflight_id":"batter-noctule-candidate-structural-v1","results":results,"numeric_height_values_parsed":False}
    out=Path("results/noctule_candidate_structural_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
      "results":[{
        "id":r["id"],"doi":r["doi"],"status":r["status"],
        "files":[{
          k:f.get(k) for k in ["filename","status","row_count","native_height_field","individual_count","repeat_individual_count","passes_gate","size_bytes"]
        } for f in r.get("plausible_event_files",[])]
      } for r in results],
      "numeric_height_values_parsed":False,
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
