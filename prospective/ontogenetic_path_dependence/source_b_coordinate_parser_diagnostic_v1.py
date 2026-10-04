#!/usr/bin/env python3
"""Deterministic Source B coordinate parser diagnostic.

Prints field names, container classes, and shapes only. No numeric values.
"""
from __future__ import annotations
import json,tempfile,urllib.request
import numpy as np
import scipy.io

BASE="https://data.mendeley.com/public-api"
DS="n9d8gbz3xr"
UA="batter-source-b-coordinate-parser-diagnostic/1.0"
FILES={
 "Ali":{"id":"fc81e848-da86-433c-a225-43831c4d06c0","cohort":"GPS_2016_2017"},
 "Anka":{"id":"e292081d-f5f8-462f-a986-0625626146a1","cohort":"GPS_2017_2018"},
}

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.mendeley-public-dataset.1+json"})
    with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)

def get_bytes(url,max_bytes=8_000_000):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=60) as r:return r.read(max_bytes+1)

def fields(obj):
    if obj is None:return []
    if isinstance(obj,dict):return sorted(obj.keys())
    if hasattr(obj,"_fieldnames"):return sorted(getattr(obj,"_fieldnames") or [])
    if isinstance(obj,np.void) and obj.dtype.names:return sorted(obj.dtype.names)
    if isinstance(obj,np.ndarray) and obj.dtype.names:return sorted(obj.dtype.names)
    return []

def shape_of(v):
    try:return list(np.asarray(v).shape)
    except Exception:return None

def class_of(v):
    if v is None:return "None"
    return f"{type(v).__module__}.{type(v).__name__}"

def get_field(obj,name):
    if isinstance(obj,dict):return obj.get(name)
    if hasattr(obj,name):return getattr(obj,name)
    if isinstance(obj,np.void) and obj.dtype.names and name in obj.dtype.names:return obj[name]
    if isinstance(obj,np.ndarray) and obj.dtype.names and name in obj.dtype.names:return obj[name]
    return None

def inspect_one(name,spec):
    m=get_json(f"{BASE}/datasets/{DS}/files/{spec['id']}")
    url=(m.get("content_details") or {}).get("download_url")
    b=get_bytes(url)
    with tempfile.NamedTemporaryFile(suffix=".mat") as tmp:
        tmp.write(b);tmp.flush()
        mat=scipy.io.loadmat(tmp.name,squeeze_me=True,struct_as_record=False,variable_names=["data"])
    d=mat["data"]
    arr=np.asarray(d,dtype=object).ravel()
    day=arr[0]
    tr=get_field(day,"track")
    out={
      "cohort":spec["cohort"],"individual":name,
      "data_container_class":class_of(d),"data_shape":shape_of(d),
      "day1_class":class_of(day),"day1_fields":fields(day),
      "track_class":class_of(tr),"track_shape":shape_of(tr),"track_fields":fields(tr),
      "frozen_fields":{}
    }
    for k in ["x","y","time"]:
        v=get_field(tr,k)
        out["frozen_fields"][k]={"present":v is not None,"class":class_of(v),"shape":shape_of(v)}
    # If track is a container array, inspect first element field names only.
    try:
        ta=np.asarray(tr,dtype=object).ravel()
        if len(ta):
            out["track_first_element"]={
                "class":class_of(ta[0]),"fields":fields(ta[0])
            }
            for k in ["x","y","time"]:
                v=get_field(ta[0],k)
                out["track_first_element"].setdefault("frozen_fields",{})[k]={
                    "present":v is not None,"class":class_of(v),"shape":shape_of(v)
                }
    except Exception:
        pass
    return out

def main():
    print(json.dumps({n:inspect_one(n,s) for n,s in FILES.items()},ensure_ascii=False,indent=2))

if __name__=="__main__":main()
