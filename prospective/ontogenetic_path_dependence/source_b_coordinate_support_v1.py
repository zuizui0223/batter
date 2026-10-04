#!/usr/bin/env python3
"""Source B coordinate-only structural support gate.

Authorized by SOURCE_B_COORDINATE_STRUCTURAL_OPENING_V1.md.
No between-day spatial distance or route outcome is calculated.
"""
from __future__ import annotations
import hashlib, json, tempfile, urllib.parse, urllib.request
import numpy as np
import scipy.io

BASE="https://data.mendeley.com/public-api"
DS="n9d8gbz3xr"; VERSION=1
UA="batter-source-b-coordinate-support/1.0"

ROOTS={
    "GPS_2016_2017":"e92b9150-3ee7-49c7-9f1f-b34e6aba6ac9",
    "GPS_2017_2018":"d66d9326-798c-4d88-9491-85d903cf1b75",
}

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.mendeley-public-dataset.1+json"})
    with urllib.request.urlopen(req,timeout=45) as r:return json.load(r)

def get_bytes(url,max_bytes=15_000_000):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=120) as r:
        n=r.headers.get("Content-Length")
        if n and int(n)>max_bytes: raise RuntimeError(f"refuse size {n}")
        b=r.read(max_bytes+1)
    if len(b)>max_bytes: raise RuntimeError("oversize")
    return b

def folders():
    r=get_json(f"{BASE}/datasets/{DS}/folders/{VERSION}")
    return r if isinstance(r,list) else r.get("folders") or r.get("items") or r.get("results") or []

def files(folder_id):
    u=f"{BASE}/datasets/{DS}/files?folder_id={urllib.parse.quote(folder_id)}&version={VERSION}&$start=0&$limit=1000"
    r=get_json(u)
    return r if isinstance(r,list) else r.get("files") or r.get("items") or r.get("results") or []

def meta(fid): return get_json(f"{BASE}/datasets/{DS}/files/{fid}")

def get_field(obj,name):
    if obj is None: return None
    if isinstance(obj,dict): return obj.get(name)
    if hasattr(obj,name): return getattr(obj,name)
    if isinstance(obj,np.void) and obj.dtype.names and name in obj.dtype.names: return obj[name]
    if isinstance(obj,np.ndarray) and obj.dtype.names and name in obj.dtype.names: return obj[name]
    return None

def numeric_flat(v):
    if v is None:return np.array([],dtype=float)
    try:
        a=np.asarray(v)
        if a.dtype==object:
            vals=[]
            for x in a.ravel():
                try:
                    vals.extend(np.asarray(x,dtype=float).ravel().tolist())
                except Exception:
                    pass
            return np.asarray(vals,dtype=float)
        return np.asarray(a,dtype=float).ravel()
    except Exception:
        return np.array([],dtype=float)

def track_arrays(day):
    tr=get_field(day,"track")
    # Common form: one struct/table-like object with vector x/y/time fields.
    x=numeric_flat(get_field(tr,"x")); y=numeric_flat(get_field(tr,"y")); t=numeric_flat(get_field(tr,"time"))
    if len(x)==len(y)==len(t) and len(x)>0:return x,y,t
    # Alternative form: struct array of fixes.
    try:
        elems=np.asarray(tr,dtype=object).ravel()
    except Exception:
        elems=[]
    xs=[];ys=[];ts=[]
    for e in elems:
        xv=numeric_flat(get_field(e,"x")); yv=numeric_flat(get_field(e,"y")); tv=numeric_flat(get_field(e,"time"))
        if len(xv)==len(yv)==len(tv)==1:
            xs.append(xv[0]);ys.append(yv[0]);ts.append(tv[0])
    return np.asarray(xs,float),np.asarray(ys,float),np.asarray(ts,float)

def valid_fix_count(day):
    x,y,t=track_arrays(day)
    if not (len(x)==len(y)==len(t)) or len(x)==0:return 0
    ok=np.isfinite(x)&np.isfinite(y)&np.isfinite(t)
    x=x[ok];y=y[ok];t=t[ok]
    if len(t)==0:return 0
    o=np.argsort(t,kind="mergesort"); t=t[o]
    # Source code compares track.time to MATLAB datenum values; units are days.
    sec=(t-t[0])*86400.0
    bins=np.floor(sec/30.0+1e-9).astype(np.int64)
    # first fix per bin
    if len(bins)==0:return 0
    return int(1+np.sum(bins[1:]!=bins[:-1]))

def load_data_days(b):
    with tempfile.NamedTemporaryFile(suffix=".mat") as tmp:
        tmp.write(b);tmp.flush()
        m=scipy.io.loadmat(tmp.name,squeeze_me=True,struct_as_record=False,variable_names=["data"])
    d=m.get("data")
    if d is None:return []
    return list(np.asarray(d,dtype=object).ravel())

def main():
    fs=folders(); by_parent={}
    for f in fs:by_parent.setdefault(str(f.get("parent_id")),[]).append(f)
    out={"contract":"SOURCE_B_COORDINATE_STRUCTURAL_OPENING_V1.md",
         "primary_spatial_outcome_opened":False,"between_day_distance_calculated":False,
         "reported_coordinate_values":False,"individuals":[]}
    for cohort,rid in ROOTS.items():
        kids=sorted(by_parent.get(rid,[]),key=lambda z:str(z.get("name")))
        for folder in kids:
            name=folder.get("name"); fid=str(folder.get("id"))
            rr=[x for x in files(fid) if (x.get("filename") or "").lower()=="data.mat"]
            rec={"cohort":cohort,"individual":name}
            if len(rr)!=1:
                rec["status"]="STOP_DATA_MAT_NOT_UNIQUE";out["individuals"].append(rec);continue
            row=rr[0]; cd=row.get("content_details") or {}; sz=int(cd.get("size") or row.get("size") or 0); sha=cd.get("sha256_hash")
            mm=meta(row["id"]); url=(mm.get("content_details") or {}).get("download_url")
            if not url or sz<=0 or not sha:
                rec["status"]="STOP_FILE_METADATA";out["individuals"].append(rec);continue
            b=get_bytes(url,max(1_000_000,sz+4096))
            if len(b)!=sz or hashlib.sha256(b).hexdigest()!=sha:
                rec["status"]="STOP_FILE_IDENTITY";out["individuals"].append(rec);continue
            try:
                days=load_data_days(b)
                counts=[valid_fix_count(day) for day in days]
                nvalid=sum(c>=20 for c in counts)
                rec.update({"status":"PASS","n_source_day_objects":len(days),
                            "n_valid_movement_days":nvalid,
                            "passes_n_valid_days_ge_20":nvalid>=20})
            except Exception as e:
                rec.update({"status":"STOP_PARSE","error_type":type(e).__name__})
            out["individuals"].append(rec)
    passing=[r for r in out["individuals"] if r.get("status")=="PASS" and r.get("passes_n_valid_days_ge_20")]
    cohort_pass={}
    for c in ROOTS:
        cohort_pass[c]=sum(r.get("cohort")==c and r.get("status")=="PASS" and r.get("passes_n_valid_days_ge_20") for r in out["individuals"])
    out["n_individuals_with_20_valid_days"]=len(passing)
    out["cohort_pass_counts"]=cohort_pass
    out["eligible_individuals"]=[r["individual"] for r in passing]
    out["frozen_minimum_individuals"]=5
    out["frozen_minimum_same_cohort_donors"]=3
    donor_ok=all(v>=4 for v in cohort_pass.values()) # target + 3 donors
    out["donor_gate_by_cohort"]=donor_ok
    out["verdict"]="PASS_OPEN_PRIMARY_OUTCOME" if len(passing)>=5 and donor_ok else "STOP_COORDINATE_STRUCTURAL_SUPPORT"
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
