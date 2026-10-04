#!/usr/bin/env python3
from __future__ import annotations
import hashlib, io, json, urllib.request, zipfile
import xml.etree.ElementTree as ET

BASE="https://data.mendeley.com/public-api"
DS="wh7c636y3t"
UA="batter-early-experience-schema-open/1.0"

FILES={
"All seasons personality data.xlsx":("97b85935-2a81-4af3-be1e-7ff8cfa1eccc",44838,"8155be769fc3e6cf9d3cc0d59fa7c216a176999662cd8272dd99d7741acd723f","xlsx"),
"Exploraion in squares.xlsx":("74189289-f4ba-4db4-8b33-24be7589dc8f",13056,"0e276042876b537df07807fbc6784dfe0ec93fdd034df9f4b095bb6b25a558d0","xlsx"),
"Outdoor data.xlsx":("48df4e40-8f31-4bbd-a854-4078274e8fb1",52518,"03a89b2c7de5db56b9776c34a1827f6063da1074909c081e1dbb942f88c9bd0f","xlsx"),
"Calculate_time_and_distance.py":("ebefaa74-0669-4750-8082-15fefc804468",7845,"d62ed4c02899749a1deb8d863b0e93aa9b8d0e7e526d253518d77ab2be785d2b","code"),
}

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.mendeley-public-dataset.1+json"})
    with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)

def get_bytes(url,maxn):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=60) as r:b=r.read(maxn+1)
    if len(b)>maxn:raise RuntimeError("size budget exceeded")
    return b

def fetch(name,spec):
    fid,size,sha,mode=spec
    m=get_json(f"{BASE}/datasets/{DS}/files/{fid}")
    cd=m.get("content_details") or {}
    if m.get("filename")!=name:raise RuntimeError("name mismatch")
    b=get_bytes(cd["download_url"],size+4096)
    if len(b)!=size:raise RuntimeError(f"size mismatch {name}")
    if hashlib.sha256(b).hexdigest()!=sha:raise RuntimeError(f"hash mismatch {name}")
    return b

def headers(b):
    z=zipfile.ZipFile(io.BytesIO(b))
    ns={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
    shared=[]
    if "xl/sharedStrings.xml" in z.namelist():
        root=ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall("m:si",ns):
            shared.append("".join(t.text or "" for t in si.findall(".//m:t",ns)))
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    rel=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap={x.attrib["Id"]:x.attrib["Target"] for x in rel}
    out=[]
    for sh in wb.findall("m:sheets/m:sheet",ns):
        rid=sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        p=relmap[rid].lstrip("/")
        if not p.startswith("xl/"):p="xl/"+p
        root=ET.fromstring(z.read(p))
        dim=root.find("m:dimension",ns)
        row=root.find("m:sheetData/m:row[@r='1']",ns)
        hs=[]
        if row is not None:
            for c in row.findall("m:c",ns):
                typ=c.attrib.get("t"); val=None
                if typ=="inlineStr":
                    t=c.find(".//m:t",ns); val=t.text if t is not None else None
                else:
                    v=c.find("m:v",ns)
                    if v is not None:
                        val=v.text
                        if typ=="s":val=shared[int(val)]
                hs.append({"cell":c.attrib.get("r"),"header":val})
        out.append({"sheet":sh.attrib.get("name"),"dimension":dim.attrib.get("ref") if dim is not None else None,"headers":hs})
    return out

def code_summary(txt):
    keys=("read","csv","xlsx","excel","gps","lat","lon","time","date","night","bat","id","distance","coordinate","file","path")
    rows=[]
    for n,line in enumerate(txt.splitlines(),1):
        if any(k in line.lower() for k in keys):
            rows.append({"line":n,"text":line.strip()[:700]})
    return rows

def main():
    out={"contract":"SCHEMA_FILE_OPENING_ALLOWLIST_V1.md","row_values_after_header_opened":False,"files":{}}
    for name,spec in FILES.items():
        b=fetch(name,spec)
        if spec[3]=="xlsx":
            out["files"][name]={"sheets":headers(b)}
        else:
            out["files"][name]={"source_structure":code_summary(b.decode("utf-8",errors="replace"))}
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
