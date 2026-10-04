#!/usr/bin/env python3
"""Source B all-individual MAT-directory support preflight.

Contract: SOURCE_B_ALL_INDIVIDUAL_STRUCT_METADATA_AMENDMENT_V1.md

Only public metadata and scipy.io.whosmat are used.
No MAT variable value is loaded.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
import urllib.parse
import urllib.request

BASE="https://data.mendeley.com/public-api"
DS="n9d8gbz3xr"
VERSION=1
UA="batter-source-b-all-individual-struct-metadata/1.0"

COHORTS={
    "GPS_2016_2017":"e92b9150-3ee7-49c7-9f1f-b34e6aba6ac9",
    "GPS_2017_2018":"d66d9326-798c-4d88-9491-85d903cf1b75",
}
EXPECTED_COUNTS={"GPS_2016_2017":8,"GPS_2017_2018":14}

def get_json(url):
    req=urllib.request.Request(
        url,
        headers={
            "User-Agent":UA,
            "Accept":"application/vnd.mendeley-public-dataset.1+json",
        },
    )
    with urllib.request.urlopen(req,timeout=45) as r:
        return json.load(r)

def get_bytes(url,max_bytes=12_000_000):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=90) as r:
        n=r.headers.get("Content-Length")
        if n and int(n)>max_bytes:
            raise RuntimeError(f"refuse content length {n} > {max_bytes}")
        b=r.read(max_bytes+1)
    if len(b)>max_bytes:
        raise RuntimeError(f"refuse bytes {len(b)} > {max_bytes}")
    return b

def list_folders():
    rows=get_json(f"{BASE}/datasets/{DS}/folders/{VERSION}")
    if isinstance(rows,list): return rows
    return rows.get("folders") or rows.get("items") or rows.get("results") or []

def list_folder_files(folder_id):
    q=urllib.parse.quote(folder_id)
    rows=get_json(f"{BASE}/datasets/{DS}/files?folder_id={q}&version={VERSION}&$start=0&$limit=1000")
    if isinstance(rows,list): return rows
    return rows.get("files") or rows.get("items") or rows.get("results") or []

def whosmat_only(b):
    import scipy.io
    with tempfile.NamedTemporaryFile(suffix=".mat") as tmp:
        tmp.write(b); tmp.flush()
        rows=scipy.io.whosmat(tmp.name)
    return [{"name":n,"shape":list(shape),"class":cls} for n,shape,cls in rows]

def main():
    folders=list_folders()
    out={
        "contract":"SOURCE_B_ALL_INDIVIDUAL_STRUCT_METADATA_AMENDMENT_V1.md",
        "movement_array_values_loaded":False,
        "loadmat_called":False,
        "cohorts":{},
    }
    total_candidates=0
    for cohort,parent_id in COHORTS.items():
        children=sorted(
            [x for x in folders if str(x.get("parent_id"))==parent_id],
            key=lambda x:str(x.get("name")),
        )
        if len(children)!=EXPECTED_COUNTS[cohort]:
            raise RuntimeError(
                f"cohort folder count drift {cohort}: {len(children)} != {EXPECTED_COUNTS[cohort]}"
            )
        indivs=[]
        for child in children:
            name=str(child.get("name"))
            fid=str(child.get("id"))
            files=list_folder_files(fid)
            data_rows=[r for r in files if r.get("filename")=="data.mat"]
            if len(data_rows)!=1:
                indivs.append({
                    "individual":name,
                    "folder_id":fid,
                    "status":"STOP_DATA_MAT_COUNT",
                    "data_mat_count":len(data_rows),
                })
                continue
            row=data_rows[0]
            cd=row.get("content_details") or {}
            size=int(cd.get("size") or row.get("size") or 0)
            sha=cd.get("sha256_hash")
            url=cd.get("download_url")
            if not (0<size<=12_000_000 and sha and url):
                indivs.append({
                    "individual":name,"folder_id":fid,"status":"STOP_METADATA",
                    "size":size,"has_sha":bool(sha),"has_url":bool(url),
                })
                continue
            b=get_bytes(url,max_bytes=size+4096)
            if len(b)!=size:
                raise RuntimeError(f"size mismatch {cohort}/{name}: {len(b)} != {size}")
            got=hashlib.sha256(b).hexdigest()
            if got!=sha:
                raise RuntimeError(f"sha mismatch {cohort}/{name}: {got} != {sha}")
            vars_=whosmat_only(b)
            data_vars=[v for v in vars_ if v["name"]=="data"]
            n_days=None
            if len(data_vars)==1 and data_vars[0]["class"]=="struct":
                sh=data_vars[0]["shape"]
                if len(sh)==2 and 1 in sh:
                    n_days=max(sh)
            pass_pre = n_days is not None and n_days>=6
            if pass_pre: total_candidates+=1
            indivs.append({
                "individual":name,
                "folder_id":fid,
                "data_mat_id":row.get("id"),
                "bytes":size,
                "sha256":sha,
                "variables":vars_,
                "stored_day_records":n_days,
                "pass_ge6_day_records":pass_pre,
                "status":"PASS_STRUCT_METADATA" if n_days is not None else "STOP_DATA_STRUCT",
            })
        out["cohorts"][cohort]={
            "n_individual_folders":len(children),
            "individuals":indivs,
            "n_ge6_day_records":sum(bool(x.get("pass_ge6_day_records")) for x in indivs),
        }

    out["n_individuals_total"]=sum(v["n_individual_folders"] for v in out["cohorts"].values())
    out["n_ge6_day_records_total"]=total_candidates
    out["frozen_minimum_individuals"]=5
    out["verdict"]=(
        "PASS_TO_MINIMAL_CHRONOLOGY_FIELD_GATE"
        if total_candidates>=5
        else "STOP_INSUFFICIENT_STRUCTURAL_REPLICATION"
    )
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
