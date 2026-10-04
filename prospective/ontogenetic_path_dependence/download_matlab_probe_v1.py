#!/usr/bin/env python3
"""Download two identity-pinned Source B data.mat files for MATLAB-native parser diagnostic.

The downstream MATLAB step is constrained by SOURCE_B_MATLAB_NATIVE_READER_AMENDMENT_V1.md.
"""
from __future__ import annotations
import hashlib,json,pathlib,urllib.request

BASE="https://data.mendeley.com/public-api"
DS="n9d8gbz3xr"
UA="batter-source-b-matlab-native-diagnostic/1.0"
FILES={
 "Ali":{"id":"fc81e848-da86-433c-a225-43831c4d06c0"},
 "Anka":{"id":"e292081d-f5f8-462f-a986-0625626146a1"},
}
OUT=pathlib.Path("prospective/ontogenetic_path_dependence/matlab_probe")
OUT.mkdir(parents=True,exist_ok=True)

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.mendeley-public-dataset.1+json"})
    with urllib.request.urlopen(req,timeout=45) as r:return json.load(r)

def get_bytes(url,limit=15_000_000):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=120) as r:
        n=r.headers.get("Content-Length")
        if n and int(n)>limit: raise RuntimeError(f"oversize metadata {n}")
        b=r.read(limit+1)
    if len(b)>limit: raise RuntimeError("oversize body")
    return b

receipt={}
for name,spec in FILES.items():
    m=get_json(f"{BASE}/datasets/{DS}/files/{spec['id']}")
    if (m.get("filename") or "").lower()!="data.mat":
        raise RuntimeError(f"{name}: filename mismatch {m.get('filename')}")
    cd=m.get("content_details") or {}
    url=cd.get("download_url")
    expected_size=int(cd.get("size") or m.get("size") or 0)
    expected_sha=cd.get("sha256_hash")
    if not url or expected_size<=0 or not expected_sha:
        raise RuntimeError(f"{name}: incomplete metadata")
    b=get_bytes(url,max(1_000_000,expected_size+4096))
    got=hashlib.sha256(b).hexdigest()
    if len(b)!=expected_size or got!=expected_sha:
        raise RuntimeError(f"{name}: file identity mismatch")
    path=OUT/f"{name}_data.mat"
    path.write_bytes(b)
    receipt[name]={"file_id":spec["id"],"bytes":len(b),"sha256":got}
(OUT/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2))
