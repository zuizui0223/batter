#!/usr/bin/env python3
"""Source B all-individual top-level day-count audit.

Contract: SOURCE_B_ALL_INDIVIDUAL_DAYCOUNT_AMENDMENT_V1.md

Only Mendeley folder/file metadata and scipy.io.whosmat top-level variable
directory metadata are opened. No MATLAB struct field values are loaded.
"""
from __future__ import annotations
import hashlib, json, tempfile, urllib.parse, urllib.request
from math import prod

import scipy.io

BASE="https://data.mendeley.com/public-api"
DS="n9d8gbz3xr"
VERSION=1
UA="batter-source-b-daycount/1.0"

ROOTS={
    "GPS_2016_2017":"e92b9150-3ee7-49c7-9f1f-b34e6aba6ac9",
    "GPS_2017_2018":"d66d9326-798c-4d88-9491-85d903cf1b75",
}

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.mendeley-public-dataset.1+json"})
    with urllib.request.urlopen(req,timeout=45) as r:
        return json.load(r)

def get_bytes(url,max_bytes=12_000_000):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=90) as r:
        n=r.headers.get("Content-Length")
        if n and int(n)>max_bytes:
            raise RuntimeError(f"refuse content length {n}>{max_bytes}")
        b=r.read(max_bytes+1)
    if len(b)>max_bytes:
        raise RuntimeError(f"refuse downloaded bytes {len(b)}>{max_bytes}")
    return b

def all_folders():
    rows=get_json(f"{BASE}/datasets/{DS}/folders/{VERSION}")
    if isinstance(rows,dict):
        rows=rows.get("folders") or rows.get("items") or rows.get("results") or []
    return rows

def folder_files(folder_id):
    url=f"{BASE}/datasets/{DS}/files?folder_id={urllib.parse.quote(folder_id)}&version={VERSION}&$start=0&$limit=1000"
    rows=get_json(url)
    return rows if isinstance(rows,list) else rows.get("files") or rows.get("items") or rows.get("results") or []

def file_meta(file_id):
    return get_json(f"{BASE}/datasets/{DS}/files/{file_id}")

def whosmat_data_shape(b):
    # whosmat reads only the MATLAB variable directory/header metadata.
    with tempfile.NamedTemporaryFile(suffix=".mat") as tmp:
        tmp.write(b); tmp.flush()
        rows=scipy.io.whosmat(tmp.name)
    hits=[(name,shape,cls) for name,shape,cls in rows if name=="data"]
    if len(hits)!=1:
        return {"status":"NO_UNIQUE_DATA_VARIABLE","variables":[{"name":n,"shape":list(s),"class":c} for n,s,c in rows]}
    n,shape,cls=hits[0]
    return {"status":"PASS","data_shape":list(shape),"data_class":cls,"n_day_objects":int(prod(shape))}

def main():
    folders=all_folders()
    by_parent={}
    for f in folders:
        by_parent.setdefault(str(f.get("parent_id")),[]).append(f)

    out={
        "contract":"SOURCE_B_ALL_INDIVIDUAL_DAYCOUNT_AMENDMENT_V1.md",
        "route_geometry_opened":False,
        "mat_struct_field_values_loaded":False,
        "roots":{},
        "individuals":[],
    }

    for cohort,root_id in ROOTS.items():
        kids=sorted(by_parent.get(root_id,[]),key=lambda x:str(x.get("name")))
        out["roots"][cohort]={
            "root_id":root_id,
            "direct_individual_folder_count":len(kids),
            "individual_names":[k.get("name") for k in kids],
        }
        for folder in kids:
            fid=str(folder.get("id")); name=folder.get("name")
            files=folder_files(fid)
            data_rows=[r for r in files if (r.get("filename") or "").lower()=="data.mat"]
            rec={"cohort":cohort,"individual":name,"folder_id":fid,"data_mat_count":len(data_rows)}
            if len(data_rows)!=1:
                rec["status"]="STOP_DATA_MAT_NOT_UNIQUE"
                out["individuals"].append(rec); continue
            row=data_rows[0]
            cd=row.get("content_details") or {}
            expected_size=int(cd.get("size") or row.get("size") or 0)
            expected_sha=cd.get("sha256_hash")
            if expected_size<=0 or expected_size>12_000_000 or not expected_sha:
                rec.update({"status":"STOP_BAD_FILE_METADATA","size":expected_size,"sha256":expected_sha})
                out["individuals"].append(rec); continue
            meta=file_meta(row["id"])
            cd2=meta.get("content_details") or {}
            url=cd2.get("download_url")
            if not url:
                rec["status"]="STOP_NO_DOWNLOAD_URL"; out["individuals"].append(rec); continue
            b=get_bytes(url,max_bytes=max(1_000_000,expected_size+4096))
            got_sha=hashlib.sha256(b).hexdigest()
            if len(b)!=expected_size or got_sha!=expected_sha:
                rec.update({"status":"STOP_FILE_IDENTITY_MISMATCH","bytes":len(b),"sha256":got_sha})
                out["individuals"].append(rec); continue
            w=whosmat_data_shape(b)
            rec.update({
                "file_id":row["id"],"bytes":len(b),"sha256":got_sha,
                **w,
            })
            if w.get("status")=="PASS":
                rec["passes_frozen_n_days_ge_6"]=w["n_day_objects"]>=6
            out["individuals"].append(rec)

    passed=[r for r in out["individuals"] if r.get("status")=="PASS" and r.get("passes_frozen_n_days_ge_6")]
    out["n_individual_folders"]=len(out["individuals"])
    out["n_with_valid_data_shape"]=sum(r.get("status")=="PASS" for r in out["individuals"])
    out["n_with_n_days_ge_6"]=len(passed)
    out["individuals_with_n_days_ge_6"]=[r["individual"] for r in passed]
    out["frozen_minimum_individuals"]=5
    out["daycount_gate_verdict"]="PASS_NEXT_STRUCTURAL_GATE" if len(passed)>=5 else "STOP_INSUFFICIENT_DAYCOUNT_SUPPORT"
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
