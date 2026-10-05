#!/usr/bin/env python3
"""Header-only XLSX opening for frozen public 3-D external candidates."""
from __future__ import annotations
import hashlib,io,json,re,urllib.request,zipfile
import xml.etree.ElementTree as ET

BASE="https://data.mendeley.com/public-api"
UA="batter-public-3d-xlsx-header-opening/1.0"

FILES=[
 {"dataset":"hbb2t3dnbc","label":"pregnancy_bat1","id":"49856030-9ce0-4082-94ea-7725f89aa3b1",
  "name":"Bat 1.xlsx","size":1108243,"sha":"eb358e554b6c25d4837c99b5b1d957dd9c0ed7daaa8a116e71f77f83713b1943"},
 {"dataset":"hbb2t3dnbc","label":"pregnancy_bat10","id":"9726518e-8433-441e-86c8-5009102afbcf",
  "name":"Bat 10.xlsx","size":1846191,"sha":"8d18da29b1e5bdc3ba35b2e11683fef1d9591a38373a9147d4c4314770dac003"},
 {"dataset":"wccbjdrrsg","label":"adaptive_bat1_stage1","id":"b0304e74-5801-4b7b-ab28-61239cf5e572",
  "name":"Bat1-stage1.xlsx","size":39136,"sha":"e93d07e05cb35b790432f24ee08bffee3d924e689da131b420f9facf27f8fdb1"},
 {"dataset":"wccbjdrrsg","label":"adaptive_bat1_stage3","id":"e3c1a9b4-79aa-496f-9c0f-7a35a7369e0e",
  "name":"Bat1-stage3.xlsx","size":61181,"sha":"1219dc8da7886485d95d35e7968711e9009cbf84314d81a0e14677cc5a583c1f"},
 {"dataset":"wccbjdrrsg","label":"adaptive_clutter","id":"68317f75-3a03-4756-b7e5-3f5fd94853d5",
  "name":"Clutter Chamber Data.xlsx","size":1435343,"sha":"bc1b2b40c5e3198a2cccd9211fa1e001d8b23e71833b784a9803781a83b31032"},
]

NS={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships"}

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.mendeley-public-dataset.1+json"})
    with urllib.request.urlopen(req,timeout=45) as r:return json.load(r)

def get_bytes(url,maxn):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=90) as r:b=r.read(maxn+1)
    if len(b)>maxn:raise RuntimeError("download budget exceeded")
    return b

def shared_strings(z):
    if "xl/sharedStrings.xml" not in z.namelist():return []
    root=ET.fromstring(z.read("xl/sharedStrings.xml"))
    return ["".join(t.text or "" for t in si.findall(".//m:t",NS)) for si in root.findall("m:si",NS)]

def header_value(c,shared):
    typ=c.attrib.get("t")
    if typ=="inlineStr":
        t=c.find(".//m:t",NS);return t.text if t is not None else None
    v=c.find("m:v",NS)
    if v is None:return None
    if typ=="s":
        ix=int(v.text);return shared[ix]
    return v.text

def inspect_xlsx(b):
    z=zipfile.ZipFile(io.BytesIO(b))
    shared=shared_strings(z)
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    rel=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap={x.attrib["Id"]:x.attrib["Target"] for x in rel}
    out=[]
    for sh in wb.findall("m:sheets/m:sheet",NS):
        rid=sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        target=relmap[rid].lstrip("/")
        if not target.startswith("xl/"):target="xl/"+target
        root=ET.fromstring(z.read(target))
        dim=root.find("m:dimension",NS)
        row1=root.find("m:sheetData/m:row[@r='1']",NS)
        headers=[]
        if row1 is not None:
            for c in row1.findall("m:c",NS):
                headers.append({"cell":c.attrib.get("r"),"value":header_value(c,shared)})
        out.append({"sheet":sh.attrib.get("name"),
                    "dimension":dim.attrib.get("ref") if dim is not None else None,
                    "row1":headers})
    return out

def main():
    out={"contract":"PUBLIC_3D_XLSX_HEADER_OPENING_V1.md","row2plus_values_opened":False,"files":[]}
    for f in FILES:
        meta=get_json(f"{BASE}/datasets/{f['dataset']}/files/{f['id']}")
        cd=meta.get("content_details") or {}
        if meta.get("filename")!=f["name"]:raise RuntimeError(f"name drift {f['label']}")
        b=get_bytes(cd["download_url"],f["size"]+4096)
        if len(b)!=f["size"]:raise RuntimeError(f"size drift {f['label']}")
        if hashlib.sha256(b).hexdigest()!=f["sha"]:raise RuntimeError(f"hash drift {f['label']}")
        out["files"].append({"label":f["label"],"dataset":f["dataset"],"filename":f["name"],
                             "sheets":inspect_xlsx(b)})
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
