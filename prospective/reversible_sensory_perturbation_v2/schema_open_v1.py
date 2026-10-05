#!/usr/bin/env python3
"""Header-only XLSX schema opening for reversible sensory perturbation archive."""
from __future__ import annotations
import io,json,time,urllib.error,urllib.request,zipfile
import xml.etree.ElementTree as ET

URL="https://www.dropbox.com/sh/met5cvcq9nmvxdd/AAAF4saT9FZl01FwWyRgD1pqa?dl=1"
UA="batter-reversible-sensory-schema/1.0"
MAX_BYTES=2_500_000
TARGETS={
 "Lucy.xlsx","Alvin.xlsx","Betty.xlsx","Stevie.xlsx","Dolores.xlsx","Clementine.xlsx",
 "All bats data.xlsx","All bats_no masker_xy.xlsx"
}
NS={
 "m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
 "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

def op(req,timeout=90):
    last=None
    for a in range(5):
        try:return urllib.request.urlopen(req,timeout=timeout)
        except urllib.error.HTTPError as e:
            last=e
            if e.code not in (429,500,502,503,504):raise
        except urllib.error.URLError as e:last=e
        if a<4:time.sleep(2**a)
    raise last

def fetch():
    req=urllib.request.Request(URL,headers={"User-Agent":UA,"Accept":"application/zip,*/*"})
    with op(req) as r:b=r.read(MAX_BYTES+1)
    if len(b)>MAX_BYTES:raise RuntimeError("archive exceeds frozen byte budget")
    return b

def shared_strings(z):
    if "xl/sharedStrings.xml" not in z.namelist():return []
    root=ET.fromstring(z.read("xl/sharedStrings.xml"))
    out=[]
    for si in root.findall("m:si",NS):
        out.append("".join(t.text or "" for t in si.findall(".//m:t",NS)))
    return out

def decode(c,ss):
    typ=c.attrib.get("t");ref=c.attrib.get("r")
    if typ=="inlineStr":
        t=c.find(".//m:t",NS);txt=(t.text or "") if t is not None else ""
        return {"ref":ref,"type":"string","text":txt}
    if typ=="s":
        v=c.find("m:v",NS)
        if v is None:return {"ref":ref,"type":"string","text":""}
        ix=int(v.text);txt=ss[ix] if 0<=ix<len(ss) else ""
        return {"ref":ref,"type":"string","text":txt}
    if typ=="str":
        v=c.find("m:v",NS)
        return {"ref":ref,"type":"string","text":(v.text or "") if v is not None else ""}
    return {"ref":ref,"type":typ or "numeric_or_other","text":None}

def schema(name,b):
    z=zipfile.ZipFile(io.BytesIO(b))
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    rel=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap={x.attrib["Id"]:x.attrib["Target"] for x in rel}
    ss=shared_strings(z)
    sheets=[]
    for sh in wb.findall("m:sheets/m:sheet",NS):
        sname=sh.attrib.get("name")
        rid=sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        p=relmap[rid].lstrip("/")
        if not p.startswith("xl/"):p="xl/"+p
        root=ET.fromstring(z.read(p))
        dim=root.find("m:dimension",NS)
        row1=root.find("m:sheetData/m:row[@r='1']",NS)
        cells=[] if row1 is None else [decode(c,ss) for c in row1.findall("m:c",NS)]
        sheets.append({"sheet":sname,"dimension":dim.attrib.get("ref") if dim is not None else None,
                       "row1":cells})
    return {"member":name,"sheets":sheets}

def main():
    outer=zipfile.ZipFile(io.BytesIO(fetch()))
    rows=[]
    for n in outer.namelist():
        if n in TARGETS:
            rows.append(schema(n,outer.read(n)))
    found={r["member"] for r in rows}
    missing=sorted(TARGETS-found)
    print(json.dumps({
      "contract":"SCHEMA_OPENING_CONTRACT_V1.md",
      "numeric_data_row_values_opened":False,
      "members_requested":sorted(TARGETS),
      "members_missing":missing,
      "members":rows
    },indent=2))

if __name__=="__main__":main()
