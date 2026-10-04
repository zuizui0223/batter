#!/usr/bin/env python3
"""Header-only schema opening for Yamada Figshare workbooks.

Only sheet names, used dimensions and row-1 headers are materialized.
"""
from __future__ import annotations
import hashlib, io, json, re, urllib.request, zipfile
import xml.etree.ElementTree as ET

BASE="https://api.figshare.com/v2/file/download"
UA="batter-yamada-schema-open/1.0"
FILES=[
 {"name":"chain and acryl_environments_flight datasets.xlsx","id":33969677,"size":932367,"md5":"2226ea5b19fb077ddcce66cb6e97088c"},
 {"name":"raw_analysis_data_by_yamada.xlsx","id":33969680,"size":18023,"md5":"cb7e2f738d85ee80becb5949317ff625"},
]
NS={
 "m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
 "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
RELNS="{http://schemas.openxmlformats.org/package/2006/relationships}"

def download(fid,size):
    # Public Figshare file endpoint; no auth.
    url=f"https://ndownloader.figshare.com/files/{fid}"
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/octet-stream"})
    with urllib.request.urlopen(req,timeout=90) as r:
        b=r.read(size+4097)
    if len(b)!=size:
        raise RuntimeError(f"size mismatch id={fid}: {len(b)} != {size}")
    return b

def shared_targets(z,needed):
    if not needed:
        return {}
    if "xl/sharedStrings.xml" not in z.namelist():
        raise RuntimeError("sharedStrings missing")
    out={}; idx=-1
    with z.open("xl/sharedStrings.xml") as fh:
        for _,e in ET.iterparse(fh,events=("end",)):
            if e.tag=="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si":
                idx+=1
                if idx in needed:
                    out[idx]="".join(t.text or "" for t in e.findall(".//m:t",NS))
                e.clear()
    missing=needed-set(out)
    if missing:
        raise RuntimeError(f"unresolved shared string indices: {sorted(missing)}")
    return out

def inspect_xlsx(b):
    z=zipfile.ZipFile(io.BytesIO(b))
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    rel=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap={x.attrib["Id"]:x.attrib["Target"] for x in rel}

    out=[]
    for sh in wb.findall("m:sheets/m:sheet",NS):
        name=sh.attrib.get("name")
        rid=sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        target=relmap[rid].lstrip("/")
        if not target.startswith("xl/"):
            target="xl/"+target
        root=ET.fromstring(z.read(target))
        dim=root.find("m:dimension",NS)
        dimref=dim.attrib.get("ref") if dim is not None else None

        row1=root.find("m:sheetData/m:row[@r='1']",NS)
        raw=[]
        need=set()
        if row1 is not None:
            for c in row1.findall("m:c",NS):
                ref=c.attrib.get("r"); typ=c.attrib.get("t")
                if typ=="inlineStr":
                    t=c.find(".//m:t",NS)
                    val=t.text if t is not None else None
                    raw.append((ref,val))
                else:
                    v=c.find("m:v",NS)
                    if v is None:
                        raw.append((ref,None))
                    elif typ=="s":
                        ix=int(v.text); need.add(ix); raw.append((ref,("S",ix)))
                    else:
                        raw.append((ref,v.text))
        ss=shared_targets(z,need)
        headers=[]
        for ref,val in raw:
            if isinstance(val,tuple):
                val=ss[val[1]]
            headers.append({"cell":ref,"header":val})
        out.append({"sheet":name,"dimension":dimref,"headers":headers})
    return out

def main():
    report={"contract":"SCHEMA_OPENING_CONTRACT_V1.md","row2plus_values_opened":False,"files":[]}
    for f in FILES:
        b=download(f["id"],f["size"])
        got=hashlib.md5(b).hexdigest()
        if got!=f["md5"]:
            raise RuntimeError(f"MD5 mismatch {f['name']}: {got}")
        report["files"].append({
            "name":f["name"],"id":f["id"],"bytes":len(b),"md5":got,
            "sheets":inspect_xlsx(b),
        })
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
