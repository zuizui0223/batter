#!/usr/bin/env python3
"""Download all ordinary Source B data.mat files for MATLAB-native structural gate.

This downloader itself computes no movement quantity.
"""
from __future__ import annotations
import csv,hashlib,json,pathlib,urllib.parse,urllib.request

BASE="https://data.mendeley.com/public-api"
DS="n9d8gbz3xr"; VERSION=1
UA="batter-source-b-matlab-structural-download/1.0"
ROOTS={
 "GPS_2016_2017":"e92b9150-3ee7-49c7-9f1f-b34e6aba6ac9",
 "GPS_2017_2018":"d66d9326-798c-4d88-9491-85d903cf1b75",
}
OUT=pathlib.Path("prospective/ontogenetic_path_dependence/matlab_structural")
OUT.mkdir(parents=True,exist_ok=True)

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.mendeley-public-dataset.1+json"})
    with urllib.request.urlopen(req,timeout=45) as r:return json.load(r)

def get_bytes(url,limit):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=120) as r:
        n=r.headers.get("Content-Length")
        if n and int(n)>limit:raise RuntimeError(f"oversize {n}")
        b=r.read(limit+1)
    if len(b)>limit:raise RuntimeError("oversize body")
    return b

def folders():
    r=get_json(f"{BASE}/datasets/{DS}/folders/{VERSION}")
    return r if isinstance(r,list) else r.get("folders") or r.get("items") or r.get("results") or []

def files(folder_id):
    u=f"{BASE}/datasets/{DS}/files?folder_id={urllib.parse.quote(folder_id)}&version={VERSION}&$start=0&$limit=1000"
    r=get_json(u)
    return r if isinstance(r,list) else r.get("files") or r.get("items") or r.get("results") or []

def meta(fid):return get_json(f"{BASE}/datasets/{DS}/files/{fid}")

fs=folders(); by_parent={}
for f in fs:by_parent.setdefault(str(f.get("parent_id")),[]).append(f)
rows=[]
for cohort,rid in ROOTS.items():
    cdir=OUT/cohort;cdir.mkdir(exist_ok=True)
    for folder in sorted(by_parent.get(rid,[]),key=lambda z:str(z.get("name"))):
        individual=str(folder.get("name")); folder_id=str(folder.get("id"))
        rr=[r for r in files(folder_id) if (r.get("filename") or "").lower()=="data.mat"]
        if len(rr)!=1:raise RuntimeError(f"{cohort}/{individual}: data.mat count {len(rr)}")
        row=rr[0]; cd=row.get("content_details") or {}
        size=int(cd.get("size") or row.get("size") or 0); sha=cd.get("sha256_hash")
        mm=meta(row["id"]); url=(mm.get("content_details") or {}).get("download_url")
        if not url or size<=0 or not sha:raise RuntimeError(f"{cohort}/{individual}: incomplete metadata")
        b=get_bytes(url,max(1_000_000,size+4096))
        got=hashlib.sha256(b).hexdigest()
        if len(b)!=size or got!=sha:raise RuntimeError(f"{cohort}/{individual}: identity mismatch")
        fn=cdir/f"{individual}.mat";fn.write_bytes(b)
        rows.append({"cohort":cohort,"individual":individual,"path":str(fn),"file_id":row["id"],"bytes":size,"sha256":sha})
with (OUT/"manifest.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=["cohort","individual","path","file_id","bytes","sha256"]);w.writeheader();w.writerows(rows)
print(json.dumps({"n_files":len(rows),"cohorts":{c:sum(r["cohort"]==c for r in rows) for c in ROOTS}},indent=2))
