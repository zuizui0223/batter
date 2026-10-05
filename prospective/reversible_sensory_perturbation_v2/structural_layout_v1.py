#!/usr/bin/env python3
"""String/formula/occupancy-only structural layout opening for reversible sensory XLSX files."""
from __future__ import annotations
import io,json,re,time,urllib.error,urllib.request,zipfile
import xml.etree.ElementTree as ET

URL="https://www.dropbox.com/sh/met5cvcq9nmvxdd/AAAF4saT9FZl01FwWyRgD1pqa?dl=1"
UA="batter-reversible-sensory-layout/1.0"
MAX_BYTES=2_500_000
TARGETS={"Lucy.xlsx","Alvin.xlsx","Betty.xlsx","Stevie.xlsx","Dolores.xlsx","Clementine.xlsx"}
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

def shared(z):
    if "xl/sharedStrings.xml" not in z.namelist():return []
    root=ET.fromstring(z.read("xl/sharedStrings.xml"))
    return ["".join(t.text or "" for t in si.findall(".//m:t",NS)) for si in root.findall("m:si",NS)]

def paths(z):
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    rel=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rm={x.attrib["Id"]:x.attrib["Target"] for x in rel}
    out={}
    for sh in wb.findall("m:sheets/m:sheet",NS):
        rid=sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        p=rm[rid].lstrip("/")
        if not p.startswith("xl/"):p="xl/"+p
        out[sh.attrib["name"]]=p
    return out

def rc(ref):
    m=re.match(r"([A-Z]+)([0-9]+)",ref or "")
    if not m:return None,None
    s=m.group(1);n=0
    for ch in s:n=n*26+ord(ch)-64
    return int(m.group(2)),n

def colname(n):
    s=""
    while n:
        n,r=divmod(n-1,26);s=chr(65+r)+s
    return s

def string_value(c,ss):
    typ=c.attrib.get("t")
    if typ=="inlineStr":
        t=c.find(".//m:t",NS);return (t.text or "") if t is not None else ""
    if typ=="s":
        v=c.find("m:v",NS)
        if v is None:return ""
        ix=int(v.text);return ss[ix] if 0<=ix<len(ss) else ""
    if typ=="str":
        v=c.find("m:v",NS);return (v.text or "") if v is not None else ""
    return None

def one_sheet(z,name,path,ss):
    root=ET.fromstring(z.read(path))
    dim=root.find("m:dimension",NS)
    strings=[];formulas=[];occ=[];styles={}
    for c in root.findall(".//m:c",NS):
        ref=c.attrib.get("r");r,k=rc(ref)
        if r is None:continue
        occ.append((r,k))
        sv=string_value(c,ss)
        if sv is not None and sv!="":strings.append({"ref":ref,"text":sv})
        f=c.find("m:f",NS)
        if f is not None:formulas.append({"ref":ref,"formula":f.text or "","cached_opened":False})
        styles[c.attrib.get("s","none")]=styles.get(c.attrib.get("s","none"),0)+1
    byc={};byr={}
    for r,k in occ:
        byc.setdefault(k,[]).append(r);byr.setdefault(r,[]).append(k)
    cols=[{"col":colname(k),"first_row":min(v),"last_row":max(v),"n_occupied":len(v)} for k,v in sorted(byc.items())]
    rows=[{"row":r,"first_col":colname(min(v)),"last_col":colname(max(v)),"n_occupied":len(v)} for r,v in sorted(byr.items())]
    ks=sorted(byc);runs=[]
    if ks:
        a=b=ks[0]
        for k in ks[1:]:
            if k==b+1:b=k
            else:runs.append({"first_col":colname(a),"last_col":colname(b),"width":b-a+1});a=b=k
        runs.append({"first_col":colname(a),"last_col":colname(b),"width":b-a+1})
    merges=[]
    mc=root.find("m:mergeCells",NS)
    if mc is not None:merges=[x.attrib.get("ref") for x in mc.findall("m:mergeCell",NS)]
    return {"sheet":name,"dimension":dim.attrib.get("ref") if dim is not None else None,
            "strings":strings,"formulas":formulas,"merged_ranges":merges,
            "column_occupancy":cols,"row_occupancy":rows,"occupied_column_runs":runs,
            "style_counts":styles}

def main():
    outer=zipfile.ZipFile(io.BytesIO(fetch()));res=[]
    for n in outer.namelist():
        if n not in TARGETS:continue
        z=zipfile.ZipFile(io.BytesIO(outer.read(n)));ss=shared(z);pp=paths(z)
        sheets=[]
        for s,p in pp.items():
            q=s.lower()
            if "xyz" in q or "no masker foam" in q:
                sheets.append(one_sheet(z,s,p,ss))
        res.append({"member":n,"sheets":sheets})
    print(json.dumps({"contract":"STRUCTURAL_LAYOUT_CONTRACT_V1.md",
                      "numeric_values_opened":False,"members":res},indent=2))

if __name__=="__main__":main()
