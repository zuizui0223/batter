#!/usr/bin/env python3
"""Header-only inspection of adaptive-learning public workbooks."""
from __future__ import annotations
import hashlib,io,json,re,urllib.request,zipfile
import xml.etree.ElementTree as ET

BASE="https://data.mendeley.com/public-api";DS="wccbjdrrsg";UA="batter-adaptive-learning-3d-header/1.0"
FILES=[
("Bat1-stage1.xlsx","b0304e74-5801-4b7b-ab28-61239cf5e572",39136,"e93d07e05cb35b790432f24ee08bffee3d924e689da131b420f9facf27f8fdb1"),
("Bat1-stage3.xlsx","e3c1a9b4-79aa-496f-9c0f-7a35a7369e0e",61181,"1219dc8da7886485d95d35e7968711e9009cbf84314d81a0e14677cc5a583c1f"),
("Bat2-stage1.xlsx","22a5767e-0346-442d-b0f7-d7565320ccef",65126,"42b799ac05ea50341399749b6e0fe18ac0c6fe06e2ea44dafdd0267980ced412"),
("Bat2_stage3.xlsx","9c480e6a-f52b-4945-af20-5341f39511aa",192991,"5de38bce30a06ea4a423e902b39702e79ed2e3f4d5656b95ac12ce3d38c86a61"),
("Bat3-stage1.xlsx","da2297e0-1754-4e55-a6c6-14b09a3b0d7f",128261,"2e6469d3cb8190d67523593b3d4af877ec29864be4930827c49ad88e5da3b0c9"),
("Bat3-stage3.xlsx","a2299e67-eaeb-4e04-aafc-1fc74751809b",153791,"0d6aab4aeb41ec75cb24ae3a68c1c07c8768f4191d92bc534f93cd64edb9e52b"),
("Bat4-stage1.xlsx","93e13dfb-3fd5-4372-b9b2-08bc6cea90e7",173748,"7430e6502282ad3175c9424bdcb91d9a6dd8d6213844ffa2a031359a6e883cfc"),
("Bat4-stage3.xlsx","0ef0ee44-39bc-4114-ac1d-ebea0f336a99",290513,"2da55dfccf91370c7fb94dd396222ee6ecd006e236be8d475bc73e828ff45e66"),
("Bat5-stage1.xlsx","e1728b00-7df4-468d-988e-69ccf3bf9151",105329,"c95ff09e2862c1a4a7fcd1c7af7f2769479afe6bbe58d82085425cdf457b7046"),
("Bat5-stage3.xlsx","c2a79269-1722-45ad-bd2f-13395985baba",205963,"548b0256ef4cae59792687c16727780019d3f92d207286f670e3d363e26d2fa2"),
("Clutter Chamber Data.xlsx","68317f75-3a03-4756-b7e5-3f5fd94853d5",1435343,"bc1b2b40c5e3198a2cccd9211fa1e001d8b23e71833b784a9803781a83b31032"),
]
NS={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main","r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships"}

def gj(url):
 req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.mendeley-public-dataset.1+json"})
 with urllib.request.urlopen(req,timeout=45) as r:return json.load(r)
def gb(url,n):
 req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
 with urllib.request.urlopen(req,timeout=90) as r:b=r.read(n+1)
 if len(b)>n:raise RuntimeError("budget")
 return b
def shared(z):
 if "xl/sharedStrings.xml" not in z.namelist():return []
 root=ET.fromstring(z.read("xl/sharedStrings.xml"))
 return ["".join(t.text or "" for t in si.findall(".//m:t",NS)) for si in root.findall("m:si",NS)]
def cv(c,ss):
 t=c.attrib.get("t")
 if t=="inlineStr":
  q=c.find(".//m:t",NS);return q.text if q is not None else None
 v=c.find("m:v",NS)
 if v is None:return None
 return ss[int(v.text)] if t=="s" else v.text
def main():
 out={"contract":"ADAPTIVE_LEARNING_3D_HEADER_PREFLIGHT_V1.md","row2plus_values_opened":False,"files":[]}
 has3d=False
 for name,fid,size,sha in FILES:
  m=gj(f"{BASE}/datasets/{DS}/files/{fid}");cd=m.get("content_details") or {}
  if m.get("filename")!=name:raise RuntimeError(f"name drift {name}")
  b=gb(cd["download_url"],size+4096)
  if len(b)!=size or hashlib.sha256(b).hexdigest()!=sha:raise RuntimeError(f"integrity {name}")
  z=zipfile.ZipFile(io.BytesIO(b));ss=shared(z)
  wb=ET.fromstring(z.read("xl/workbook.xml"));rels=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
  rm={x.attrib["Id"]:x.attrib["Target"] for x in rels};sheets=[]
  for sh in wb.findall("m:sheets/m:sheet",NS):
   rid=sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
   p=rm[rid].lstrip("/")
   if not p.startswith("xl/"):p="xl/"+p
   root=ET.fromstring(z.read(p));dim=root.find("m:dimension",NS)
   row=root.find("m:sheetData/m:row[@r='1']",NS)
   hdr=[]
   if row is not None:
    for c in row.findall("m:c",NS):
     hdr.append({"cell":c.attrib.get("r"),"value":cv(c,ss)})
   vals=[str(x["value"]).strip().lower() for x in hdr if x["value"] is not None]
   if {"time","x","y","z"}.issubset(set(vals)):has3d=True
   sheets.append({"sheet":sh.attrib.get("name"),"dimension":dim.attrib.get("ref") if dim is not None else None,"row1":hdr})
  out["files"].append({"filename":name,"sheets":sheets})
 out["verdict"]="RAW_3D_HEADER_PRESENT" if has3d else "STOP_NO_PUBLIC_3D_MOVEMENT_VALUES"
 print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
