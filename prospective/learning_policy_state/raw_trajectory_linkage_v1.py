#!/usr/bin/env python3
"""Outcome-blind linkage of Yamada trajectory sheet names to 14 source subjects."""
from __future__ import annotations

import collections, hashlib, io, json, re, urllib.request, zipfile
import xml.etree.ElementTree as ET

API="https://api.figshare.com/v2/articles/19102712"
UA="batter-yamada-raw-linkage/1.0"

BIG={
 "id":33969677,
 "name":"chain and acryl_environments_flight datasets.xlsx",
 "size":932367,
 "md5":"2226ea5b19fb077ddcce66cb6e97088c",
}
SMALL={
 "id":33969680,
 "name":"raw_analysis_data_by_yamada.xlsx",
 "size":18023,
 "md5":"cb7e2f738d85ee80becb5949317ff625",
}

NS={
 "m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
 "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:return json.load(r)

def get_bytes(url,maxn):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/octet-stream"})
    with urllib.request.urlopen(req,timeout=90) as r:b=r.read(maxn+1)
    if len(b)>maxn:raise RuntimeError("download budget exceeded")
    return b

def fetch(spec,files):
    f=files.get(spec["id"])
    if f is None:raise RuntimeError(f"missing file {spec['id']}")
    if f.get("name")!=spec["name"] or int(f.get("size") or 0)!=spec["size"]:
        raise RuntimeError(f"metadata drift {spec['id']}")
    b=get_bytes(f["download_url"],spec["size"]+4096)
    if len(b)!=spec["size"] or hashlib.md5(b).hexdigest()!=spec["md5"]:
        raise RuntimeError(f"integrity {spec['id']}")
    return b

def normid(s):
    if s is None:return None
    return re.sub(r"[_\s]+","",str(s).strip().lower())

def shared(z,need):
    if not need:return {}
    out={};idx=-1
    with z.open("xl/sharedStrings.xml") as fh:
        for _,e in ET.iterparse(fh,events=("end",)):
            if e.tag=="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si":
                idx+=1
                if idx in need:
                    out[idx]="".join(t.text or "" for t in e.findall(".//m:t",NS))
                e.clear()
    return out

def read_structural_summary(b):
    # Reads only already-authorized C,D,E,N,O.
    z=zipfile.ZipFile(io.BytesIO(b))
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    rel=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap={x.attrib["Id"]:x.attrib["Target"] for x in rel}
    target=None
    for sh in wb.findall("m:sheets/m:sheet",NS):
        if sh.attrib.get("name")=="1st_table":
            rid=sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
            target=relmap[rid].lstrip("/")
            break
    if target is None:raise RuntimeError("1st_table missing")
    if not target.startswith("xl/"):target="xl/"+target
    root=ET.fromstring(z.read(target))
    allowed={"C":"condition","D":"bats_id","E":"trial","N":"origin_name","O":"dataset_name"}
    tmp=[];need=set()
    for row in root.findall("m:sheetData/m:row",NS):
        rn=int(row.attrib.get("r","0"))
        if rn<2 or rn>29:continue
        d={}
        for c in row.findall("m:c",NS):
            m=re.match(r"([A-Z]+)",c.attrib.get("r",""))
            col=m.group(1) if m else None
            if col not in allowed:continue
            typ=c.attrib.get("t");v=c.find("m:v",NS)
            if typ=="inlineStr":
                t=c.find(".//m:t",NS);d[allowed[col]]=t.text if t is not None else None
            elif v is not None:
                if typ=="s":
                    ix=int(v.text);need.add(ix);d[allowed[col]]=("S",ix)
                else:d[allowed[col]]=v.text
        tmp.append(d)
    ss=shared(z,need)
    rows=[]
    for d in tmp:
        q={k:(ss[v[1]] if isinstance(v,tuple) else v) for k,v in d.items()}
        try:q["condition"]=int(float(q["condition"]))
        except Exception:continue
        try:q["trial"]=int(float(q["trial"]))
        except Exception:continue
        q["bats_id"]=str(q.get("bats_id","")).strip()
        rows.append(q)

    # Collapse duplicated trial rows into one subject record; require design consistency.
    by=collections.defaultdict(list)
    for r in rows:by[r["bats_id"]].append(r)
    subjects={}
    for bid,rr in by.items():
        conds=set(r["condition"] for r in rr)
        ds=set(str(r.get("dataset_name","")).strip() for r in rr if str(r.get("dataset_name","")).strip())
        os=set(str(r.get("origin_name","")).strip() for r in rr if str(r.get("origin_name","")).strip())
        if len(conds)!=1 or len(ds)!=1 or len(os)!=1:
            raise RuntimeError(f"structural linkage drift for bat {bid}")
        subjects[bid]={
          "bats_id":bid,
          "condition":next(iter(conds)),
          "dataset_name":next(iter(ds)),
          "origin_name":next(iter(os)),
          "dataset_norm":normid(next(iter(ds))),
          "origin_norm":normid(next(iter(os))),
        }
    return subjects

def read_sheet_names_only(b):
    z=zipfile.ZipFile(io.BytesIO(b))
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    return [sh.attrib.get("name") for sh in wb.findall("m:sheets/m:sheet",NS)]

def parse_sheet(name):
    m=re.search(r"(bat_[A-Za-z]+)_(chain|acril|ac)_(1st|12th)",name,re.I)
    if not m:return None
    token=m.group(1)
    kind=m.group(2).lower()
    trialtok=m.group(3).lower()
    cond=1 if kind=="chain" else 2
    trial=1 if trialtok=="1st" else 12
    return {"sheet":name,"sheet_bat_token":token,"sheet_norm":normid(token),"condition":cond,"trial":trial}

def main():
    art=get_json(API);files={int(f["id"]):f for f in art.get("files") or []}
    bsmall=fetch(SMALL,files);bbig=fetch(BIG,files)
    subjects=read_structural_summary(bsmall)
    parsed=[x for x in (parse_sheet(n) for n in read_sheet_names_only(bbig)) if x is not None]

    links=[];errors=[]
    used=collections.Counter()
    for sh in parsed:
        candidates=[s for s in subjects.values() if s["condition"]==sh["condition"]]
        ds=[s for s in candidates if s["dataset_norm"]==sh["sheet_norm"]]
        method=None;match=None
        if len(ds)==1:
            match=ds[0];method="dataset_name"
        elif len(ds)>1:
            errors.append({"sheet":sh["sheet"],"error":"multiple_dataset_matches","ids":[x["bats_id"] for x in ds]})
            continue
        else:
            os=[s for s in candidates if s["origin_norm"]==sh["sheet_norm"]]
            if len(os)==1:
                match=os[0];method="origin_name_fallback"
            elif len(os)>1:
                errors.append({"sheet":sh["sheet"],"error":"multiple_origin_matches","ids":[x["bats_id"] for x in os]})
                continue
            else:
                errors.append({"sheet":sh["sheet"],"error":"no_match"})
                continue
        key=(match["bats_id"],sh["trial"])
        used[key]+=1
        links.append({
          **sh,
          "bats_id":match["bats_id"],
          "dataset_name":match["dataset_name"],
          "origin_name":match["origin_name"],
          "link_method":method,
        })

    expected={(bid,t) for bid in subjects for t in (1,12)}
    got=set(used)
    duplicates=[{"bats_id":b,"trial":t,"n":n} for (b,t),n in used.items() if n!=1]
    missing=[{"bats_id":b,"trial":t} for b,t in sorted(expected-got,key=lambda x:(int(x[0]),x[1]))]
    extra=[{"bats_id":b,"trial":t} for b,t in sorted(got-expected,key=lambda x:(int(x[0]),x[1]))]

    passed=(len(parsed)==28 and len(links)==28 and not errors and not duplicates and not missing and not extra and len(subjects)==14)
    out={
      "contract":"RAW_TRAJECTORY_LINKAGE_CONTRACT_V1.md",
      "trajectory_cell_values_opened":False,
      "n_source_subjects":len(subjects),
      "n_parsed_trajectory_sheets":len(parsed),
      "n_linked_sheets":len(links),
      "links":sorted(links,key=lambda x:(int(x["bats_id"]),x["trial"])),
      "errors":errors,
      "duplicates":duplicates,
      "missing_subject_trials":missing,
      "extra_subject_trials":extra,
      "verdict":"PASS_RAW_TRAJECTORY_LINKAGE" if passed else "STOP_RAW_TRAJECTORY_LINKAGE"
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
