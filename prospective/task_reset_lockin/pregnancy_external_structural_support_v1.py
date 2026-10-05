#!/usr/bin/env python3
"""Header/dimension-only structural support audit for all ten pregnancy workbooks."""
from __future__ import annotations
import hashlib,io,json,re,urllib.request,zipfile
import xml.etree.ElementTree as ET

BASE="https://data.mendeley.com/public-api"
DS="hbb2t3dnbc"
UA="batter-pregnancy-external-structural-support/1.0"

FILES=[
("Bat 1.xlsx","49856030-9ce0-4082-94ea-7725f89aa3b1",1108243,"eb358e554b6c25d4837c99b5b1d957dd9c0ed7daaa8a116e71f77f83713b1943"),
("Bat 2.xlsx","3648b8b4-f29b-44b7-a844-f51d4414c2a6",945590,"02edd8b5d64c1ac75bc3dbdd6cf81ac0da80a0ee41b4da90aa3ef556d0752c75"),
("Bat 3.xlsx","4fe0e3aa-397e-416f-b211-574a0af4f7d6",1232373,"4f09052e1d9c10a5f1ac51f4f3afc17c48b6aecc4677c6ea7130396ffbcce254"),
("Bat 4.xlsx","f92a41a6-5b80-4584-a543-3aeb5cc3bc6f",955859,"af896b24ed43cf4f2db4f1ecabbb963cb7599d8ed9210f8355ce0114bd5ced9"),
("Bat 5.xlsx","4f646af4-8430-4ee9-b207-d14259496da6",1593787,"daa53f235b1d3056ee87b9449a13e48246c5e67202561d2c84816e780544bf16"),
("Bat 6.xlsx","1952636e-f052-4e13-a4bc-c5c4c71f1845",484690,"be3abb145cc9dd9c9c1881fcadc056462b2817f9e6bb1860cbbb935c0e5f08a1"),
("Bat 7.xlsx","5a05372d-0cff-4535-96ee-c63f57eacb24",615557,"964613f3b64a5d8593ed4c49ee783f2c6c2deb2544b27bf78c11c85c687eacd1"),
("Bat 8.xlsx","88799a4b-eb6e-492f-8ef9-dd7e3f558d2c",636717,"7b62277666bae703c08d280c192a652f51753475fa32c5aba5561cd38083af13"),
("Bat 9.xlsx","08cb4de9-b114-4f65-8f3a-27aa95c6fc98",1440600,"c8959a134b2282579a538176e855b0b85e119c643a9549e1b2c9be7e97c124a4"),
("Bat 10.xlsx","9726518e-8433-441e-86c8-5009102afbcf",1846191,"8d18da29b1e5bdc3ba35b2e11683fef1d9591a38373a9147d4c4314770dac003"),
]

NS={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
REQ={"Call no.","Time","x","y","z"}

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
def hval(c,ss):
 typ=c.attrib.get("t")
 if typ=="inlineStr":
  t=c.find(".//m:t",NS);return t.text if t is not None else None
 v=c.find("m:v",NS)
 if v is None:return None
 return ss[int(v.text)] if typ=="s" else v.text
def nrows_dim(ref):
 if not ref:return None
 tail=ref.split(":")[-1]
 m=re.search(r"(\d+)$",tail)
 return int(m.group(1)) if m else None
def inspect(b):
 z=zipfile.ZipFile(io.BytesIO(b));ss=shared(z)
 wb=ET.fromstring(z.read("xl/workbook.xml"));rels=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
 rm={x.attrib["Id"]:x.attrib["Target"] for x in rels};out=[]
 for sh in wb.findall("m:sheets/m:sheet",NS):
  rid=sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
  p=rm[rid].lstrip("/")
  if not p.startswith("xl/"):p="xl/"+p
  root=ET.fromstring(z.read(p));dim=root.find("m:dimension",NS)
  ref=dim.attrib.get("ref") if dim is not None else None
  row=root.find("m:sheetData/m:row[@r='1']",NS);vals=[]
  if row is not None:
   vals=[hval(c,ss) for c in row.findall("m:c",NS)]
  n=nrows_dim(ref);data_rows=(n-1) if n is not None else None
  has=REQ.issubset(set(v for v in vals if v is not None))
  out.append({"sheet":sh.attrib.get("name"),"dimension":ref,"data_rows_implied":data_rows,
              "has_required_header_set":has,"candidate_ge21_rows":bool(has and data_rows is not None and data_rows>=21)})
 return out
def main():
 out={"contract":"PREGNANCY_EXTERNAL_STRUCTURAL_SUPPORT_CONTRACT_V1.md","row2plus_values_opened":False,"bats":[]}
 for idx,(name,fid,size,sha) in enumerate(FILES,1):
  group="pregnant" if idx<=5 else "post_lactating"
  m=gj(f"{BASE}/datasets/{DS}/files/{fid}");cd=m.get("content_details") or {}
  meta_name=m.get("filename")
  if meta_name!=name:
   out["bats"].append({"bat":idx,"group":group,"status":"STOP_FILENAME_DRIFT",
                       "expected_filename":name,"observed_filename":meta_name,
                       "candidate_eligible_ge5":False})
   continue
  b=gb(cd["download_url"],size+4096)
  got_size=len(b);got_sha=hashlib.sha256(b).hexdigest()
  if got_size!=size or got_sha!=sha:
   out["bats"].append({"bat":idx,"group":group,"status":"STOP_INTEGRITY_MISMATCH",
                       "expected_size":size,"observed_size":got_size,
                       "expected_sha256":sha,"observed_sha256":got_sha,
                       "metadata_size":cd.get("size"),"metadata_sha256":cd.get("sha256_hash"),
                       "candidate_eligible_ge5":False})
   continue
  sheets=inspect(b);n=sum(x["candidate_ge21_rows"] for x in sheets)
  out["bats"].append({"bat":idx,"group":group,"status":"PASS_INTEGRITY",
                      "n_sheets":len(sheets),"n_candidate_ge21":n,
                      "candidate_eligible_ge5":n>=5,"sheets":sheets})
 for g in ("pregnant","post_lactating"):
  out[f"n_{g}_eligible"]=sum(x["group"]==g and x.get("candidate_eligible_ge5",False) for x in out["bats"])
 out["verdict"]="PASS_TO_CALL_SAMPLED_ESTIMATOR_FREEZE" if out["n_pregnant_eligible"]>=4 and out["n_post_lactating_eligible"]>=4 else "STOP_INSUFFICIENT_EXTERNAL_SUPPORT"
 print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
