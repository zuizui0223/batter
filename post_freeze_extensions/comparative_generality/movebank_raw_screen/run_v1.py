#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[3]
CONTRACT=ROOT/"post_freeze_extensions/comparative_generality/movebank_raw_screen/contract_v1.json"
OUT=ROOT/"post_freeze_extensions/comparative_generality/movebank_raw_screen/result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/comparative_generality/movebank_raw_screen/RESULT_V1.md"
UA={"User-Agent":"batter-movebank-raw-panel-screen-v1/1.0"}
BASE="https://datarepository.movebank.org"

def canon(x):
    return "_".join(str(x).strip().lower().replace("-","_").replace(" ","_").replace(".","_").split("_"))

def fetch_json(url):
    r=requests.get(url,headers={**UA,"Accept":"application/hal+json,application/json"},timeout=120)
    r.raise_for_status()
    return r.json(),r.content,r.url

def link(obj,name):
    x=(obj.get("_links") or {}).get(name,{})
    return str(x.get("href","")) if isinstance(x,dict) else ""

def embedded(obj,name):
    x=(obj.get("_embedded") or {}).get(name,[])
    return [v for v in x if isinstance(v,dict)] if isinstance(x,list) else []

def checksum(bs):
    c=bs.get("checkSum") or bs.get("checksum") or {}
    if not isinstance(c,dict):
        return None
    return {
        "algorithm":c.get("checkSumAlgorithm") or c.get("algorithm"),
        "value":c.get("value")
    }

def resolve_doi(doi):
    last=None
    for ident in [doi,"https://doi.org/"+doi]:
        try:
            item,raw,url=fetch_json(f"{BASE}/server/api/pid/find?id={quote(ident,safe='')}")
            if link(item,"bundles"):
                break
        except Exception as e:
            last=e
    else:
        raise RuntimeError(f"PID resolution failed: {last}")

    bundles,_,_=fetch_json(link(item,"bundles"))
    files=[]
    for b in embedded(bundles,"bundles"):
        bu=link(b,"bitstreams")
        if not bu:
            continue
        bp,_,_=fetch_json(bu)
        for bs in embedded(bp,"bitstreams"):
            files.append({
                "bundle":str(b.get("name","")),
                "bitstream_id":str(bs.get("uuid") or bs.get("id") or ""),
                "filename":str(bs.get("name") or ""),
                "description":str(bs.get("description") or ""),
                "mime_type":str(bs.get("mimeType") or ""),
                "size_bytes":bs.get("sizeBytes"),
                "checksum":checksum(bs),
                "content_url":link(bs,"content"),
            })
    return item,files

def first_line(url,max_bytes=262144):
    with requests.get(url,headers=UA,timeout=180,stream=True) as r:
        r.raise_for_status()
        buf=b""
        for chunk in r.iter_content(8192):
            if not chunk:
                continue
            buf+=chunk
            if b"\n" in buf or len(buf)>=max_bytes:
                break
    line=buf.splitlines()[0] if buf else b""
    return line.decode("utf-8-sig",errors="replace")

def header_info(line,height_priority):
    try:
        raw=next(csv.reader([line]))
    except Exception:
        raw=[]
    mapping={}
    for name in raw:
        mapping.setdefault(canon(name),name)
    names=set(mapping)
    has_time="timestamp" in names
    has_xy="location_lat" in names and "location_long" in names
    iid=None
    for k in ["individual_local_identifier","individual_id"]:
        if k in names:
            iid=k;break
    heights=[h for h in height_priority if h in names]
    return {
        "raw_header":raw,
        "canonical_header":sorted(names),
        "has_timestamp":has_time,
        "has_xy":has_xy,
        "individual_field":iid,
        "height_fields":heights,
        "mapping":mapping,
        "tracking_like":bool(has_time and has_xy and iid)
    }

def present(s):
    txt=s.astype(str).str.strip()
    return s.notna() & txt.ne("") & ~txt.str.lower().isin({"na","nan","null","none"})

def parse_time_series(s):
    return pd.to_datetime(s,errors="coerce",utc=True,format="mixed")

def structural_screen(raw,hi,c):
    mp=hi["mapping"]
    tcol=mp["timestamp"]
    latcol=mp["location_lat"]
    loncol=mp["location_long"]
    iidcol=mp[hi["individual_field"]]
    hcanon=hi["height_fields"][0]
    hcol=mp[hcanon]
    use=[tcol,latcol,loncol,iidcol,hcol]
    df=pd.read_csv(io.BytesIO(raw),dtype=str,usecols=use,low_memory=False)
    mask=present(df[tcol])&present(df[latcol])&present(df[loncol])&present(df[iidcol])&present(df[hcol])
    d=df.loc[mask].copy()
    d["iid"]=d[iidcol].astype(str).str.strip()
    d["t"]=parse_time_series(d[tcol])
    d["lon"]=pd.to_numeric(d[loncol],errors="coerce")
    d["lat"]=pd.to_numeric(d[latcol],errors="coerce")
    bad=d["t"].isna()|d["lon"].isna()|d["lat"].isna()
    d=d.loc[~bad].copy()

    gap=pd.Timedelta(hours=4)
    min_n=int(c["session_screen"]["minimum_presence_qualified_events_per_session"])
    sess_by_iid={}
    repeat=[]
    all_counts=[]
    for iid,g in d.groupby("iid",sort=True):
        ts=sorted(g["t"].tolist())
        counts=[]
        cur=0;prev=None
        for t in ts:
            if prev is not None and t-prev>gap:
                counts.append(cur);cur=0
            cur+=1;prev=t
        if cur:counts.append(cur)
        elig=[int(x) for x in counts if x>=min_n]
        sess_by_iid[str(iid)]={
            "all_block_counts":[int(x) for x in counts],
            "eligible_session_counts":elig,
            "eligible_session_count":len(elig)
        }
        all_counts.extend(elig)
        if len(elig)>=2:
            repeat.append(str(iid))
    return {
        "selected_height_field":hcanon,
        "numeric_height_values_parsed":False,
        "rows_in_file":int(len(df)),
        "presence_qualified_rows":int(len(d)),
        "individuals_with_presence":int(d["iid"].nunique()),
        "repeat_individual_count":len(repeat),
        "repeat_individual_ids":repeat,
        "eligible_session_count_total":len(all_counts),
        "eligible_session_size_min":min(all_counts) if all_counts else None,
        "eligible_session_size_median":float(pd.Series(all_counts).median()) if all_counts else None,
        "eligible_session_size_max":max(all_counts) if all_counts else None,
        "session_structure":sess_by_iid,
        "passes":len(repeat)>=int(c["session_screen"]["minimum_repeat_individuals_for_candidate"])
    }

def screen_candidate(cand,c):
    item,files=resolve_doi(cand["doi"])
    hp=c["gps_file_detection"]["native_height_priority"]
    inspected=[]
    qualifying=[]
    tracking_no_height=[]
    for f in files:
        fn=f["filename"].lower()
        mt=f["mime_type"].lower()
        if not (fn.endswith(".csv") or "csv" in mt):
            continue
        url=f["content_url"]
        if not url:
            continue
        try:
            line=first_line(url)
            hi=header_info(line,hp)
            rec={**f,"header":{k:v for k,v in hi.items() if k!="mapping"}}
            inspected.append(rec)
            if hi["tracking_like"] and hi["height_fields"]:
                qualifying.append((f,hi))
            elif hi["tracking_like"]:
                tracking_no_height.append(rec)
        except Exception as e:
            inspected.append({**f,"header_error":f"{type(e).__name__}: {e}"})

    base={
        **cand,
        "repository_item_name":item.get("name"),
        "repository_item_uuid":item.get("uuid") or item.get("id"),
        "files":files,
        "csv_headers_inspected":inspected,
        "numeric_height_values_parsed":False
    }
    if len(qualifying)==0:
        return {
            **base,
            "status":"NO_NATIVE_HEIGHT_FIELD" if tracking_no_height else "TRANSPORT_OR_SCHEMA_FAILURE",
            "tracking_csvs_without_native_height":tracking_no_height,
            "passes":False
        }
    if len(qualifying)>1:
        return {
            **base,
            "status":"AMBIGUOUS_EVENT_FILE",
            "qualifying_event_files":[
                {
                    "filename":f["filename"],
                    "bitstream_id":f["bitstream_id"],
                    "height_fields":hi["height_fields"],
                    "canonical_header":hi["canonical_header"]
                } for f,hi in qualifying
            ],
            "passes":False
        }

    f,hi=qualifying[0]
    r=requests.get(f["content_url"],headers=UA,timeout=300)
    r.raise_for_status()
    raw=r.content
    scr=structural_screen(raw,hi,c)
    return {
        **base,
        "selected_event_file":{
            "filename":f["filename"],
            "bitstream_id":f["bitstream_id"],
            "size_bytes":f["size_bytes"],
            "checksum":f["checksum"],
            "sha256":hashlib.sha256(raw).hexdigest(),
            "selected_height_field":scr["selected_height_field"]
        },
        "structural":scr,
        "passes":bool(scr["passes"]),
        "status":"PASS_TO_SOURCE_PREFLIGHT" if scr["passes"] else "STRUCTURAL_STOP"
    }

def main():
    c=json.loads(CONTRACT.read_text())
    results=[]
    for cand in c["candidates"]:
        try:
            results.append(screen_candidate(cand,c))
        except Exception as e:
            results.append({
                **cand,
                "status":"TRANSPORT_OR_SCHEMA_FAILURE",
                "passes":False,
                "reason":f"{type(e).__name__}: {e}",
                "numeric_height_values_parsed":False
            })

    passing=[x for x in results if x.get("passes")]
    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "numeric_height_values_parsed":False,
        "candidate_count":len(results),
        "passing_count":len(passing),
        "passing_candidates":[{"doi":x["doi"],"taxon":x["taxon"]} for x in passing],
        "results":results,
        "claim_boundary":c["claim_boundary"]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    lines=[
        "# Raw Movebank bat candidate screen v1","",
        "**Numeric vertical values were not parsed or summarized.**","",
        "| DOI | taxon | native height | repeat IDs | status |",
        "|---|---|---|---:|---|"
    ]
    for x in results:
        h="—";n="—"
        if x.get("structural"):
            h=x["structural"].get("selected_height_field","—")
            n=x["structural"].get("repeat_individual_count","—")
        elif x.get("qualifying_event_files"):
            h=";".join(sorted({z for q in x["qualifying_event_files"] for z in q.get("height_fields",[])}))
        lines.append(f"| {x['doi']} | {x['taxon']} | {h} | {n} | {x['status']} |")
    lines += ["",f"Passing candidates: **{len(passing)}**",""]
    for x in passing:
        lines.append(f"- {x['taxon']} — {x['doi']}: {x['structural']['repeat_individual_count']} repeat individuals")
    OUT_MD.write_text("\n".join(lines)+"\n",encoding="utf-8")

    print(json.dumps({
        "passing_count":len(passing),
        "results":[{
            "doi":x["doi"],"taxon":x["taxon"],"status":x["status"],
            "height":x.get("structural",{}).get("selected_height_field"),
            "repeat_n":x.get("structural",{}).get("repeat_individual_count"),
            "individuals":x.get("structural",{}).get("individuals_with_presence")
        } for x in results]
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
