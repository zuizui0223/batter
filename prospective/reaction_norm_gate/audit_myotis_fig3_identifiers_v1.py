#!/usr/bin/env python3
"""Original 2025 Myotis Figure-3 MAT source: outcome-blind identity schema audit.

Read ONLY dataset names/shapes/attributes and MATLAB-class char data of
the pinned deposited file. Numeric behavioral values, object references, and
physiological magnitudes are not accessed. A table without bat/day columns
cannot establish a repeated individual reaction norm.
"""
from __future__ import annotations
import hashlib
import io
import json
import os
import time
import urllib.request
from pathlib import Path

DATASET = "8b57pz6bpj"
FILE_ID = "9c19d9a7-a23f-4e0a-8a30-e19c485babf4"
SHA256 = "24a47604ffe2a034162f7b64d6fa0a49ae96e0086e8a00c6bf84fcd0561fe75c"
SOURCE = f"https://data.mendeley.com/public-files/datasets/{DATASET}/files/{FILE_ID}/file_downloaded"
OUT = Path(__file__).with_name("MYOTIS_FIG3_ORIGINAL_ID_SCHEMA_RECEIPT_V1.json")
WORDS = ("bat","day","date","tag","session","depl","trial","treat",
         "speed","distance","time","norm","ci","buzz","motor","mov")


def verify_original(retries=5):
    """No bypass: every attempt must match the author's manifest SHA256."""
    failures=[]
    for attempt in range(1, retries+1):
        try:
            req=urllib.request.Request(SOURCE,headers={
                "User-Agent":"batter-fig3-2025-structural-audit/1.0",
                "Accept":"application/octet-stream,*/*"})
            with urllib.request.urlopen(req,timeout=50) as r:
                b=r.read(300000+1)
            digest=hashlib.sha256(b).hexdigest()
            if len(b)>300000:
                failures.append(f"attempt {attempt}: exceeds 300k budget")
            elif digest==SHA256:
                return b,attempt,failures
            else:
                failures.append(f"attempt {attempt}: manifest digest mismatch (no source accepted)")
        except Exception as e:
            failures.append(f"attempt {attempt}: {type(e).__name__}")
        if attempt<retries:
            time.sleep(attempt*1.5)
    raise ValueError("; ".join(failures))


def short_meta(v):
    try:
        import numpy as np
        if isinstance(v,bytes):return v.decode("utf-8","replace")[:200]
        if isinstance(v,str):return v[:200]
        if isinstance(v,np.ndarray):
            if v.size<=80 and v.dtype.kind in ("S","U"):
                return [short_meta(z) for z in v.reshape(-1)]
            if v.size<=16 and v.dtype.kind in ("i","u"):
                return v.tolist()
            return {"shape":list(v.shape),"dtype":str(v.dtype)}
        return str(v)[:160]
    except Exception:
        return "UNAVAILABLE_META"


def audit_h5(data):
    import h5py
    result={"source_sha256":SHA256,"file_len":len(data),
            "source_outcome_magnitudes_read":False,
            "source_numeric_datasets_read":False,
            "root_labels":[],"objects":[],"schema_labels":[],"fields_attrs":[]}
    with h5py.File(io.BytesIO(data),'r') as f:
        result["root_labels"]=list(f.keys())
        def visit(name,obj):
            is_dataset=isinstance(obj,h5py.Dataset)
            row={"path":name,"type":"dataset" if is_dataset else "group"}
            if is_dataset:
                row.update({"shape":list(obj.shape),"dtype":str(obj.dtype)})
            attrs={str(k):short_meta(v) for k,v in obj.attrs.items()
                   if str(k).startswith("MATLAB") or
                      ("field" in str(k).lower() and "timestamp" not in str(k).lower())}
            if attrs:
                row["matlab_metadata"]=attrs
                if any("field" in k.lower() for k in attrs):
                    result["fields_attrs"].append({"path":name,"metadata":attrs})
            if (is_dataset and obj.size<=160 and
                obj.dtype.kind in ("i","u") and
                short_meta(obj.attrs.get("MATLAB_class",b""))=="char"):
                # Numeric physiological arrays are strictly excluded.
                word="".join(chr(int(c)) for c in obj[()].reshape(-1) if int(c)>0)
                if len(word)<=160 and word.isprintable():
                    row["matlab_char"]=word
                    if any(t in word.lower() for t in WORDS):
                        result["schema_labels"].append({"path":name,"schema_text":word})
            result["objects"].append(row)
        f.visititems(visit)
    result["hdf_object_count"]=len(result["objects"])
    result["lab_mat_has_direct_bat_day_field"] = any(
        any(k in item.get("schema_text","").lower() for k in
            ("bat_num","tag_depl_num","session_date","batid","bat_id"))
        for item in result["schema_labels"])
    # Absence of label is NOT proof of absence of a hidden reference.
    result["conclusion"]="SCHEMA_ONLY_NESTED_REFERENCES_MAY_REQUIRE_MORE_STRUCTURE" 
    return result


def run():
    result={"status":"HOLD_UNVERIFIED","source":SOURCE,
            "sha256_pinned":SHA256,
            "biological_values_examined":False,
            "source":"Foskolos 2025 v3 original fig3_lData.mat"}
    try:
        b,tries,failures=verify_original()
        result.update(audit_h5(b))
        result.update({"status":"ORIGINAL_SOURCE_METADATA_AUDITED",
                       "download_attempts":tries,"failed_attempts":failures})
        status=0
    except Exception as e:
        result.update({"status":"HOLD_SOURCE_ACCESS_OR_FORMAT",
                       "error_type":type(e).__name__,"error":str(e)[:700]})
        status=2
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"n_objects":result.get("hdf_object_count"),
                      "n_schema_labels":len(result.get("schema_labels",[])),
                      "recovered_labels":result.get("schema_labels",[])[:70],
                      "fields_attrs":result.get("fields_attrs",[])[:20],
                      "error":result.get("error")},ensure_ascii=False))
    return status

if __name__=="__main__":
    raise SystemExit(run())
