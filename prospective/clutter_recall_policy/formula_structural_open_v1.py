#!/usr/bin/env python3
"""Formula-only + bat-info structural opening for clutter-recall workbook."""
from __future__ import annotations
import hashlib, importlib.util, io, json, math, re, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("S",HERE/"schema_open_v1.py")
S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)

TARGET_NAME="Clutter Chamber Data.xlsx"
TARGET_SHA="bc1b2b40c5e3198a2cccd9211fa1e001d8b23e71833b784a9803781a83b31032"
TARGET_SIZE=1435343

NS=S.NS

def shared_strings(z):
    return S.shared_strings(z)

def workbook_paths(z):
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    rel=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap={x.attrib["Id"]:x.attrib["Target"] for x in rel}
    out={}
    for sh in wb.findall("m:sheets/m:sheet",NS):
        rid=sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        target=relmap[rid].lstrip("/")
        if not target.startswith("xl/"):target="xl/"+target
        out[sh.attrib.get("name")]=target
    return out

def col(ref):
    m=re.match(r"([A-Z]+)",ref or "")
    return m.group(1) if m else None

def decode_structural(c,ss):
    typ=c.attrib.get("t")
    v=c.find("m:v",NS)
    if typ=="inlineStr":
        t=c.find(".//m:t",NS)
        return {"kind":"string","value":(t.text or "") if t is not None else ""}
    if typ=="s":
        if v is None:return {"kind":"string","value":""}
        ix=int(v.text)
        return {"kind":"string","value":ss[ix] if 0<=ix<len(ss) else ""}
    if typ=="str":
        return {"kind":"string","value":(v.text or "") if v is not None else ""}
    f=c.find("m:f",NS)
    if f is not None:
        return {"kind":"formula","formula":f.text or "","cached_value_opened":False}
    if v is None:return {"kind":"blank","value":None}
    raw=v.text
    try:
        x=float(raw)
        if math.isfinite(x):
            return {"kind":"numeric_structural","value":x,"style_index":c.attrib.get("s")}
    except Exception:
        pass
    return {"kind":"other","value":raw}

def formulas_and_merges(root):
    formulas=[]
    for c in root.findall(".//m:c",NS):
        f=c.find("m:f",NS)
        if f is not None:
            formulas.append({"ref":c.attrib.get("r"),"formula":f.text or "",
                             "cached_value_opened":False})
    merges=[]
    mc=root.find("m:mergeCells",NS)
    if mc is not None:
        merges=[x.attrib.get("ref") for x in mc.findall("m:mergeCell",NS)]
    return formulas,merges

def main():
    rows=S.file_rows()
    rec=None
    for r in rows:
        if r.get("filename")==TARGET_NAME:
            rec=r;break
    if rec is None:raise RuntimeError("target workbook missing")
    cd=rec.get("content_details") or {}
    size=int(cd.get("size") or rec.get("size") or 0)
    sha=cd.get("sha256_hash")
    if size!=TARGET_SIZE or sha!=TARGET_SHA:
        raise RuntimeError(f"metadata drift size={size} sha={sha}")
    b=S.get_bytes(S.download_url(rec),TARGET_SIZE+8192)
    if len(b)!=TARGET_SIZE or hashlib.sha256(b).hexdigest()!=TARGET_SHA:
        raise RuntimeError("integrity failure")

    z=zipfile.ZipFile(io.BytesIO(b))
    ss=shared_strings(z)
    paths=workbook_paths(z)
    sheets=[]
    batinfo=[]
    for name,path in paths.items():
        root=ET.fromstring(z.read(path))
        formulas,merges=formulas_and_merges(root)
        sheets.append({"sheet":name,"merged_ranges":merges,"formulas":formulas})
        if name=="bat info":
            for row in root.findall("m:sheetData/m:row",NS):
                rn=int(row.attrib.get("r","0"))
                vals={}
                for c in row.findall("m:c",NS):
                    cc=col(c.attrib.get("r"))
                    if cc not in set("ABCDEFGH"):continue
                    vals[cc]=decode_structural(c,ss)
                if vals:
                    batinfo.append({"row":rn,"cells":vals})

    print(json.dumps({
      "contract":"FORMULA_STRUCTURAL_OPENING_CONTRACT_V1.md",
      "target_file":TARGET_NAME,
      "sha256":TARGET_SHA,
      "acoustic_numeric_outcomes_opened":False,
      "formula_cached_results_opened":False,
      "sheets":sheets,
      "bat_info_A_to_H":batinfo
    },ensure_ascii=False,indent=2))

if __name__=="__main__":main()
