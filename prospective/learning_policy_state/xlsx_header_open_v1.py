#!/usr/bin/env python3
"""Header-only opening of Yamada learning XLSX files.

Reads workbook metadata, worksheet dimensions, and row 1 only.
No row 2+ cell is dereferenced.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import urllib.request
import zipfile
import xml.etree.ElementTree as ET

ARTICLE_API="https://api.figshare.com/v2/articles/19102712"
UA="batter-learning-policy-header-open/1.0"

PINNED={
    33969677:{
        "name":"chain and acryl_environments_flight datasets.xlsx",
        "size":932367,
        "md5":"2226ea5b19fb077ddcce66cb6e97088c",
    },
    33969680:{
        "name":"raw_analysis_data_by_yamada.xlsx",
        "size":18023,
        "md5":"cb7e2f738d85ee80becb5949317ff625",
    },
}

NS={
 "m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
 "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.load(r)

def get_bytes(url,maxn):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/octet-stream"})
    with urllib.request.urlopen(req,timeout=90) as r:
        b=r.read(maxn+1)
    if len(b)>maxn:
        raise RuntimeError("download exceeds pinned budget")
    return b

def shared_strings_needed(z, needed):
    if not needed or "xl/sharedStrings.xml" not in z.namelist():
        return {}
    out={}
    idx=-1
    with z.open("xl/sharedStrings.xml") as fh:
        for _,e in ET.iterparse(fh,events=("end",)):
            if e.tag=="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si":
                idx+=1
                if idx in needed:
                    out[idx]="".join(t.text or "" for t in e.findall(".//m:t",NS))
                e.clear()
    missing=set(needed)-set(out)
    if missing:
        raise RuntimeError(f"missing shared strings: {sorted(missing)[:10]}")
    return out

def open_workbook_headers(b):
    z=zipfile.ZipFile(io.BytesIO(b))
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    rel=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap={x.attrib["Id"]:x.attrib["Target"] for x in rel}

    sheets=[]
    for sh in wb.findall("m:sheets/m:sheet",NS):
        name=sh.attrib.get("name")
        rid=sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        target=relmap[rid].lstrip("/")
        if not target.startswith("xl/"):
            target="xl/"+target
        root=ET.fromstring(z.read(target))
        dim=root.find("m:dimension",NS)
        dimension=dim.attrib.get("ref") if dim is not None else None

        row1=root.find("m:sheetData/m:row[@r='1']",NS)
        raw=[]
        needed=set()
        if row1 is not None:
            for c in row1.findall("m:c",NS):
                ref=c.attrib.get("r")
                typ=c.attrib.get("t")
                value=None
                if typ=="inlineStr":
                    t=c.find(".//m:t",NS)
                    value=t.text if t is not None else None
                else:
                    v=c.find("m:v",NS)
                    if v is not None:
                        if typ=="s":
                            ix=int(v.text)
                            needed.add(ix)
                            value=("S",ix)
                        else:
                            value=v.text
                raw.append((ref,value))
        ss=shared_strings_needed(z,needed)
        cells=[]
        for ref,val in raw:
            if isinstance(val,tuple):
                val=ss[val[1]]
            cells.append({"cell":ref,"value":val})
        sheets.append({
            "sheet":name,
            "dimension":dimension,
            "row1_present":row1 is not None,
            "row1_cells":cells,
        })
    return sheets

def main():
    art=get_json(ARTICLE_API)
    byid={int(f["id"]):f for f in art.get("files") or []}
    out={
        "contract":"XLSX_HEADER_OPENING_ALLOWLIST_V1.md",
        "rows_2plus_opened":False,
        "files":{},
    }
    for fid,p in PINNED.items():
        f=byid.get(fid)
        if f is None:
            raise RuntimeError(f"missing file id {fid}")
        if f.get("name")!=p["name"]:
            raise RuntimeError(f"filename drift {fid}")
        size=int(f.get("size") or 0)
        if size!=p["size"]:
            raise RuntimeError(f"size drift {fid}: {size}")
        b=get_bytes(f["download_url"],p["size"]+4096)
        if len(b)!=p["size"]:
            raise RuntimeError(f"byte-size mismatch {fid}: {len(b)}")
        md5=hashlib.md5(b).hexdigest()
        if md5!=p["md5"]:
            raise RuntimeError(f"md5 mismatch {fid}")
        out["files"][p["name"]]={
            "file_id":fid,
            "bytes":len(b),
            "md5":md5,
            "sheets":open_workbook_headers(b),
        }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
