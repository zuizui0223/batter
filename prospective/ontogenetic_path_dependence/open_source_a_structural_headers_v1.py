#!/usr/bin/env python3
"""Extract only three frozen structural XLSX members from Source A GPS data.zip
and report workbook/sheet/first-row header metadata.

No worksheet row 2+ is accessed or emitted.
Contract: SOURCE_A_STRUCTURAL_MEMBER_HEADER_OPENING_V1.md
"""
from __future__ import annotations
import binascii, io, json, struct, urllib.request, zipfile, zlib
import xml.etree.ElementTree as ET

BASE="https://data.mendeley.com/public-api"
DS="gpcg9m5758"; FID="8bb38dce-f2d5-41b1-bb0e-8454957e8eee"
UA="batter-source-a-structural-headers/1.0"
MEMBERS=[
 {"name":"GPS data/allPairs.xlsx","offset":263,"csize":105860,"usize":109357,"method":8,"crc":"b5b9b73c"},
 {"name":"GPS data/dataInfo_mompup.xlsx","offset":109821,"csize":10180,"usize":12788,"method":8,"crc":"9a4ba028"},
 {"name":"GPS data/trees_mompup.xlsx","offset":175510,"csize":54839,"usize":57673,"method":8,"crc":"19979c40"},
]

def get_json(url):
    import json
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.mendeley-public-dataset.1+json"})
    with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)

def get_range(url,start,end):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Range":f"bytes={start}-{end}","Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=60) as r:
        data=r.read(end-start+2)
        cr=r.headers.get("Content-Range")
    if len(data)!=end-start+1: raise RuntimeError(f"range mismatch {start}-{end}: {len(data)} {cr}")
    return data

def extract_member(url,m):
    h=get_range(url,m["offset"],m["offset"]+29)
    vals=struct.unpack("<4s5H3I2H",h)
    if vals[0]!=b"PK\x03\x04":raise RuntimeError(f"bad local header {m['name']}")
    method=vals[3]; fnl=vals[9]; exl=vals[10]
    name_bytes=get_range(url,m["offset"]+30,m["offset"]+30+fnl-1)
    name=name_bytes.decode("utf-8",errors="replace")
    if name!=m["name"]:raise RuntimeError(f"name mismatch {name} != {m['name']}")
    data_start=m["offset"]+30+fnl+exl
    comp=get_range(url,data_start,data_start+m["csize"]-1)
    if method==8: raw=zlib.decompress(comp,-15)
    elif method==0: raw=comp
    else: raise RuntimeError(f"unsupported method {method}")
    if len(raw)!=m["usize"]:raise RuntimeError(f"usize mismatch {m['name']}")
    crc=f"{binascii.crc32(raw)&0xffffffff:08x}"
    if crc!=m["crc"]:raise RuntimeError(f"crc mismatch {m['name']} {crc}")
    return raw

def headers_only(xlsx_bytes):
    z=zipfile.ZipFile(io.BytesIO(xlsx_bytes))
    ns={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        "p":"http://schemas.openxmlformats.org/package/2006/relationships"}
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    relroot=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap={r.attrib["Id"]:r.attrib["Target"] for r in relroot}

    # Resolve shared strings only as a dictionary used by row 1. Never emit any
    # non-header shared string and never access worksheet row 2+.
    shared=[]
    if "xl/sharedStrings.xml" in z.namelist():
        root=ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall("m:si",ns):
            shared.append("".join(t.text or "" for t in si.findall(".//m:t",ns)))

    sheets=[]
    for sh in wb.findall("m:sheets/m:sheet",ns):
        rid=sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        target=relmap[rid]
        p=target.lstrip("/")
        if not p.startswith("xl/"):p="xl/"+p
        root=ET.fromstring(z.read(p))
        dim=root.find("m:dimension",ns)
        row1=root.find("m:sheetData/m:row[@r='1']",ns)
        out=[]
        if row1 is not None:
            for c in row1.findall("m:c",ns):
                typ=c.attrib.get("t")
                val=None
                if typ=="inlineStr":
                    t=c.find(".//m:t",ns); val=t.text if t is not None else None
                else:
                    v=c.find("m:v",ns)
                    if v is not None:
                        val=v.text
                        if typ=="s":
                            val=shared[int(val)]
                out.append({"cell":c.attrib.get("r"),"header":val})
        sheets.append({"sheet":sh.attrib.get("name"),"dimension":dim.attrib.get("ref") if dim is not None else None,"headers":out})
    return sheets

def main():
    meta=get_json(f"{BASE}/datasets/{DS}/files/{FID}")
    url=(meta.get("content_details") or {}).get("download_url")
    if not url:raise RuntimeError("no download URL")
    out={"contract":"SOURCE_A_STRUCTURAL_MEMBER_HEADER_OPENING_V1.md","worksheet_rows_after_1_opened":False,"members":[]}
    for m in MEMBERS:
        raw=extract_member(url,m)
        out["members"].append({"name":m["name"],"verified_uncompressed_bytes":len(raw),"sheets":headers_only(raw)})
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
