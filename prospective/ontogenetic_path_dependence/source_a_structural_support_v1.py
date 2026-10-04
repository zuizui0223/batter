#!/usr/bin/env python3
"""Source A structural support gate for maternal-to-self crossover.

Reads ONLY row values explicitly authorized in
SOURCE_A_STRUCTURAL_COLUMN_VALUE_ALLOWLIST_V1.md.

No GPS coordinate member, route geometry, similarity, entropy, or outcome is opened.
"""
from __future__ import annotations

import binascii
import collections
import io
import json
import math
import re
import struct
import urllib.request
import zipfile
import zlib
import xml.etree.ElementTree as ET

BASE="https://data.mendeley.com/public-api"
DS="gpcg9m5758"
FID="8bb38dce-f2d5-41b1-bb0e-8454957e8eee"
UA="batter-source-a-structural-support/1.0"

MEMBERS={
 "allPairs":{
   "name":"GPS data/allPairs.xlsx","offset":263,"csize":105860,"usize":109357,
   "method":8,"crc":"b5b9b73c",
 },
 "dataInfo":{
   "name":"GPS data/dataInfo_mompup.xlsx","offset":109821,"csize":10180,"usize":12788,
   "method":8,"crc":"9a4ba028",
 },
}

ALLOW_ALLPAIRS={
 "index","Date","dateNum","trackNum","analyze","stage","stagePossible","stagePossible1",
 "source","cave","exitMom","exitPup","enterMom","enterPup","dropOff","pickUp",
 "leaveCaveTogether_","returnTogether","pupExited","drop_off_y_n_","pickup_YN",
 "dropOffNumber","DO_tree","DO_tree_hebrew","visitsPup",
}
ALLOW_DATAINFO={"batFolder","index","analyze"}

TRUTHY={"1","yes","y","true","t"}
MISSING={"","na","nan","none","null","n/a","-"}

def norm(v):
    if v is None: return None
    if isinstance(v,float) and math.isnan(v): return None
    s=str(v).strip()
    return None if s.lower() in MISSING else s

def truthy(v):
    s=norm(v)
    if s is None:return False
    try:
        if float(s)==1.0:return True
    except Exception:
        pass
    return s.lower() in TRUTHY

def as_int(v):
    s=norm(v)
    if s is None:return None
    try:
        x=float(s)
        if x.is_integer(): return int(x)
    except Exception:
        return None
    return None

def has_id(*vals):
    return any(norm(v) is not None for v in vals)

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.mendeley-public-dataset.1+json"})
    with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)

def get_range(url,start,end):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Range":f"bytes={start}-{end}","Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=60) as r:
        data=r.read(end-start+2)
        cr=r.headers.get("Content-Range")
    if len(data)!=end-start+1:
        raise RuntimeError(f"range mismatch {start}-{end}: got={len(data)} content-range={cr}")
    return data

def extract_member(url,m):
    h=get_range(url,m["offset"],m["offset"]+29)
    vals=struct.unpack("<4s5H3I2H",h)
    if vals[0]!=b"PK\x03\x04":raise RuntimeError(f"bad local header {m['name']}")
    method=vals[3]; fnl=vals[9]; exl=vals[10]
    name_b=get_range(url,m["offset"]+30,m["offset"]+30+fnl-1)
    name=name_b.decode("utf-8",errors="replace")
    if name!=m["name"]:raise RuntimeError(f"name mismatch {name} != {m['name']}")
    data_start=m["offset"]+30+fnl+exl
    comp=get_range(url,data_start,data_start+m["csize"]-1)
    raw=zlib.decompress(comp,-15) if method==8 else comp
    if len(raw)!=m["usize"]:raise RuntimeError(f"usize mismatch {m['name']}")
    crc=f"{binascii.crc32(raw)&0xffffffff:08x}"
    if crc!=m["crc"]:raise RuntimeError(f"crc mismatch {m['name']} {crc}")
    return raw

NS={
 "m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
 "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

def col_letters(ref):
    m=re.match(r"([A-Z]+)",ref or "")
    return m.group(1) if m else None

def parse_shared_targets(z, needed):
    if not needed or "xl/sharedStrings.xml" not in z.namelist(): return {}
    out={}
    idx=-1
    # Iterate and only materialize text for needed indices.
    for ev,elem in ET.iterparse(z.open("xl/sharedStrings.xml"),events=("end",)):
        if elem.tag=="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si":
            idx+=1
            if idx in needed:
                out[idx]="".join(t.text or "" for t in elem.findall(".//m:t",NS))
            elem.clear()
    missing=needed-set(out)
    if missing: raise RuntimeError(f"shared-string indices missing: {sorted(missing)[:10]}")
    return out

def locate_sheet(z,sheet_name):
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    relroot=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap={r.attrib["Id"]:r.attrib["Target"] for r in relroot}
    for sh in wb.findall("m:sheets/m:sheet",NS):
        if sh.attrib.get("name")==sheet_name:
            rid=sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
            target=relmap[rid].lstrip("/")
            return target if target.startswith("xl/") else "xl/"+target
    raise RuntimeError(f"sheet not found {sheet_name}")

def sheet_allowed_rows(xlsx_bytes,sheet_name,allowed_headers):
    z=zipfile.ZipFile(io.BytesIO(xlsx_bytes))
    path=locate_sheet(z,sheet_name)
    root=ET.fromstring(z.read(path))
    rows=root.findall("m:sheetData/m:row",NS)
    if not rows:return []

    # Row 1 headers are already authorized by the parent header-opening contract.
    hdr={}
    row1=rows[0]
    shared_header_needed=set()
    raw_header={}
    for c in row1.findall("m:c",NS):
        col=col_letters(c.attrib.get("r"))
        typ=c.attrib.get("t")
        if typ=="inlineStr":
            t=c.find(".//m:t",NS); raw_header[col]=t.text if t is not None else None
        else:
            v=c.find("m:v",NS)
            if v is not None:
                if typ=="s":
                    shared_header_needed.add(int(v.text)); raw_header[col]=("S",int(v.text))
                else: raw_header[col]=v.text
    sh=parse_shared_targets(z,shared_header_needed)
    for col,v in raw_header.items():
        val=sh[v[1]] if isinstance(v,tuple) else v
        if val in allowed_headers: hdr[col]=val

    # Collect only allowed-cell raw values and only the shared string indices those cells reference.
    tmp=[]
    needed=set()
    for row in rows[1:]:
        d={}
        for c in row.findall("m:c",NS):
            col=col_letters(c.attrib.get("r"))
            if col not in hdr: continue
            typ=c.attrib.get("t")
            if typ=="inlineStr":
                t=c.find(".//m:t",NS); d[hdr[col]]=t.text if t is not None else None
            else:
                v=c.find("m:v",NS)
                if v is None: continue
                if typ=="s":
                    idx=int(v.text); needed.add(idx); d[hdr[col]]=("S",idx)
                elif typ=="b":
                    d[hdr[col]]="1" if v.text=="1" else "0"
                else:
                    d[hdr[col]]=v.text
        if d: tmp.append(d)

    shared=parse_shared_targets(z,needed)
    out=[]
    for d in tmp:
        out.append({k:(shared[v[1]] if isinstance(v,tuple) else v) for k,v in d.items()})
    return out

def main():
    meta=get_json(f"{BASE}/datasets/{DS}/files/{FID}")
    url=(meta.get("content_details") or {}).get("download_url")
    if not url:raise RuntimeError("no public download URL")

    all_raw=extract_member(url,MEMBERS["allPairs"])
    info_raw=extract_member(url,MEMBERS["dataInfo"])
    rows=sheet_allowed_rows(all_raw,"Sheet1",ALLOW_ALLPAIRS)
    info=sheet_allowed_rows(info_raw,"Sheet1",ALLOW_DATAINFO)

    # Freeze explicit vocabulary only for fields permitted by the value allowlist.
    vocab={}
    for key in ["analyze","stage","stagePossible","stagePossible1","source","cave",
                "drop_off_y_n_","pickup_YN","pupExited","visitsPup"]:
        cnt=collections.Counter(norm(r.get(key)) for r in rows)
        vocab[key]={"unique_nonmissing":sorted([x for x in cnt if x is not None]),
                    "counts":{str(k):v for k,v in sorted(cnt.items(),key=lambda kv:str(kv[0]))}}
    info_vocab=collections.Counter(norm(r.get("analyze")) for r in info)

    # Map allowed dataInfo rows. Prefer rows explicitly admitted by analyze; retain all mappings for audit.
    folder_by_index=collections.defaultdict(list)
    admitted_folder_by_index=collections.defaultdict(list)
    for r in info:
        idx=norm(r.get("index")); folder=norm(r.get("batFolder"))
        if idx is None or folder is None: continue
        folder_by_index[idx].append(folder)
        if truthy(r.get("analyze")): admitted_folder_by_index[idx].append(folder)

    by_index=collections.defaultdict(list)
    for r in rows:
        idx=norm(r.get("index"))
        if idx is not None: by_index[idx].append(r)

    summaries=[]
    for idx,rr in sorted(by_index.items(),key=lambda kv:(float(kv[0]) if re.fullmatch(r"\d+(?:\.0+)?",kv[0]) else 1e99,kv[0])):
        admitted=[r for r in rr if truthy(r.get("analyze"))]
        # If source uses no truthy analyze vocabulary at all this will fail closed rather than silently include all rows.
        stage_dates=collections.defaultdict(set)
        for r in admitted:
            st=as_int(r.get("stage")); date=norm(r.get("Date")) or norm(r.get("dateNum"))
            if st is not None and date is not None: stage_dates[st].add(date)

        maternal=[]
        revisit=[]
        for r in admitted:
            st=as_int(r.get("stage"))
            if st==2 and has_id(r.get("dropOffNumber"),r.get("DO_tree")):
                maternal.append(r)
                if truthy(r.get("visitsPup")): revisit.append(r)

        independent_dates=set()
        for st in (4,5): independent_dates |= stage_dates.get(st,set())

        folders=sorted(set(admitted_folder_by_index.get(idx) or folder_by_index.get(idx) or []))
        has_folder=len(folders)>0
        has_maternal=len(maternal)>=1
        n_ind=len(independent_dates)
        has_history=n_ind>=4  # implies first-two/later-two and >=2 prior dates for a later target
        has_revisit=len(revisit)>=1

        passed=all([has_folder,has_maternal,n_ind>=4,has_history,has_revisit])
        summaries.append({
            "index":idx,
            "batFolders":folders,
            "n_admitted_unique_dates":len(set((norm(r.get("Date")) or norm(r.get("dateNum"))) for r in admitted if (norm(r.get("Date")) or norm(r.get("dateNum"))) is not None)),
            "stage_date_counts":{str(st):len(ds) for st,ds in sorted(stage_dates.items())},
            "n_stage2_dropoff_exposure_rows":len(maternal),
            "has_stage2_maternal_dropoff":has_maternal,
            "n_stage4_5_independent_dates":n_ind,
            "has_four_independent_dates":n_ind>=4,
            "has_early2_later2_chronology":n_ind>=4,
            "has_source_coded_independent_revisit":has_revisit,
            "pass_full_structural_gate":passed,
        })

    passed=[x for x in summaries if x["pass_full_structural_gate"]]
    out={
        "contract":"SOURCE_A_STRUCTURAL_COLUMN_VALUE_ALLOWLIST_V1.md",
        "route_geometry_opened":False,
        "forbidden_columns_read":False,
        "coding":{
            "truthy":"numeric 1 or case-insensitive {1,yes,y,true,t}; missing/other is false",
            "independent_stage":"source stage exactly 4 or 5",
            "maternal_dropoff":"source stage exactly 2 and nonmissing dropOffNumber or DO_tree",
            "task_revisit":"maternal-dropoff row with truthy visitsPup",
            "date_key":"Date if nonmissing else dateNum",
        },
        "allPairs_rows_with_allowed_values":len(rows),
        "dataInfo_rows_with_allowed_values":len(info),
        "allowed_value_vocabularies":vocab,
        "dataInfo_analyze_vocabulary":{str(k):v for k,v in sorted(info_vocab.items(),key=lambda kv:str(kv[0]))},
        "individual_summaries":summaries,
        "n_structurally_eligible_pups":len(passed),
        "eligible_indices":[x["index"] for x in passed],
        "frozen_minimum_pups":5,
        "verdict":"PASS_OPEN_ESTIMATOR_FREEZE" if len(passed)>=5 else "STOP_INSUFFICIENT_STRUCTURAL_SUPPORT",
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
