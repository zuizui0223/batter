#!/usr/bin/env python3
"""Schema-only XLSX opening for Taub & Yovel clutter-recall archive."""
from __future__ import annotations
import hashlib, io, json, re, time, urllib.error, urllib.parse, urllib.request, zipfile
import xml.etree.ElementTree as ET

BASE="https://data.mendeley.com/public-api"
DS="wccbjdrrsg"
VERSION=1
UA="batter-clutter-recall-schema/1.0"
MAX_ROWS=5

NS={
 "m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
 "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

def _open_with_retry(req,timeout):
    last=None
    for attempt in range(5):
        try:
            return urllib.request.urlopen(req,timeout=timeout)
        except urllib.error.HTTPError as e:
            last=e
            if e.code not in (429,500,502,503,504):
                raise
        except urllib.error.URLError as e:
            last=e
        if attempt<4:
            time.sleep(2**attempt)
    raise last

def get_json(url,accept="application/vnd.mendeley-public-dataset.1+json"):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":accept})
    with _open_with_retry(req,60) as r:return json.load(r)

def get_bytes(url,maxn):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/octet-stream"})
    with _open_with_retry(req,90) as r:
        b=r.read(maxn+1)
    if len(b)>maxn:raise RuntimeError("download budget exceeded")
    return b

def file_rows():
    url=f"{BASE}/datasets/{DS}/files?folder_id=root&version={VERSION}&$start=0&$limit=1000"
    rows=get_json(url)
    if isinstance(rows,dict):rows=rows.get("files") or rows.get("items") or rows.get("results") or []
    return rows

def download_url(r):
    cd=r.get("content_details") or {}
    for v in (cd.get("download_url"),r.get("download_url"),cd.get("url"),r.get("file_url")):
        if v:return v
    # public file endpoint fallback using dataset/file identifiers
    fid=r.get("id")
    if fid:
        return f"https://data.mendeley.com/public-files/datasets/{DS}/files/{fid}/file_downloaded"
    raise RuntimeError(f"no download locator for {r.get('filename')}")

def shared_strings(z):
    if "xl/sharedStrings.xml" not in z.namelist():return []
    root=ET.fromstring(z.read("xl/sharedStrings.xml"))
    out=[]
    for si in root.findall("m:si",NS):
        out.append("".join(t.text or "" for t in si.findall(".//m:t",NS)))
    return out

def decode_header_cell(c,ss):
    typ=c.attrib.get("t")
    ref=c.attrib.get("r")
    if typ=="inlineStr":
        t=c.find(".//m:t",NS)
        return {"ref":ref,"type":"string","text":(t.text or "") if t is not None else ""}
    if typ=="s":
        v=c.find("m:v",NS)
        if v is None:return {"ref":ref,"type":"string","text":""}
        ix=int(v.text)
        return {"ref":ref,"type":"string","text":ss[ix] if 0<=ix<len(ss) else ""}
    if typ=="str":
        v=c.find("m:v",NS)
        return {"ref":ref,"type":"string","text":(v.text or "") if v is not None else ""}
    # Never decode numeric/formula values.
    return {"ref":ref,"type":typ or "numeric_or_other","text":None}

def workbook_schema(b):
    z=zipfile.ZipFile(io.BytesIO(b))
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    rel=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap={x.attrib["Id"]:x.attrib["Target"] for x in rel}
    ss=shared_strings(z)
    sheets=[]
    for sh in wb.findall("m:sheets/m:sheet",NS):
        name=sh.attrib.get("name")
        rid=sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        target=relmap[rid].lstrip("/")
        if not target.startswith("xl/"):target="xl/"+target
        root=ET.fromstring(z.read(target))
        dim=root.find("m:dimension",NS)
        dimref=dim.attrib.get("ref") if dim is not None else None
        header=None
        inspected=[]
        for row in root.findall("m:sheetData/m:row",NS):
            rn=int(row.attrib.get("r","0"))
            if rn<1 or rn>MAX_ROWS:continue
            cells=[decode_header_cell(c,ss) for c in row.findall("m:c",NS)]
            inspected.append({"row":rn,"cells":cells})
            strings=[x for x in cells if x["type"]=="string" and (x.get("text") or "").strip()]
            if strings:
                header={"row":rn,"cells":cells}
                break
        sheets.append({"sheet":name,"dimension":dimref,"header_candidate":header,
                       "rows_inspected":len(inspected)})
    return sheets

def main():
    rows=file_rows()
    out=[]
    for r in sorted(rows,key=lambda x:str(x.get("filename"))):
        name=r.get("filename")
        if not str(name).lower().endswith(".xlsx"):continue
        cd=r.get("content_details") or {}
        size=int(cd.get("size") or r.get("size") or 0)
        sha=cd.get("sha256_hash")
        b=get_bytes(download_url(r),size+8192)
        got=hashlib.sha256(b).hexdigest()
        if size and len(b)!=size:raise RuntimeError(f"size mismatch {name}: {len(b)} != {size}")
        if sha and got!=sha:raise RuntimeError(f"sha mismatch {name}")
        out.append({"filename":name,"file_id":r.get("id"),"size":len(b),"sha256":got,
                    "sheets":workbook_schema(b)})
    print(json.dumps({
      "contract":"SCHEMA_OPENING_CONTRACT_V1.md",
      "numeric_data_row_values_opened":False,
      "max_rows_inspected_per_sheet":MAX_ROWS,
      "files":out
    },ensure_ascii=False,indent=2))

if __name__=="__main__":main()
