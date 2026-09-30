#!/usr/bin/env python3
from __future__ import annotations

import hashlib, io, json
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
CONTRACT=ROOT/"post_freeze_extensions/nyctalus_context_audit/contract_v1.json"
OUT=ROOT/"post_freeze_extensions/nyctalus_context_audit/result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/nyctalus_context_audit/RESULT_V1.md"
UA={"User-Agent":"batter-nyctalus-context-audit-v1/1.0"}

def present(s):
    txt=s.astype(str).str.strip()
    return s.notna() & txt.ne("") & ~txt.str.lower().isin({"na","nan","null","none"})

def fetch(c):
    meta=requests.get(f"https://zenodo.org/api/records/{c['source']['record_id']}",headers=UA,timeout=90)
    meta.raise_for_status()
    rec=meta.json()
    target=None
    for f in rec.get("files",[]):
        if (f.get("key") or f.get("filename"))==c["source"]["file"]:
            target=f;break
    if target is None:
        raise RuntimeError("source file missing")
    url=(target.get("links") or {}).get("content") or (target.get("links") or {}).get("self")
    r=requests.get(url,headers=UA,timeout=180)
    r.raise_for_status()
    raw=r.content
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=c["source"]["sha256"]:
        raise RuntimeError(f"source SHA mismatch: {sha}")
    return pd.read_csv(io.BytesIO(raw),dtype=str,low_memory=False),sha,len(raw)

def safe_num(s,name):
    x=pd.to_numeric(s,errors="coerce")
    if x.isna().any():
        raise RuntimeError(f"{name} parse failures: {int(x.isna().sum())}")
    return x.astype(float)

def main():
    c=json.loads(CONTRACT.read_text())
    df,sha,size=fetch(c)
    cols=c["allowed_fields"]
    missing=[x for x in cols if x not in df.columns]
    if missing:
        raise RuntimeError(f"missing allowed fields {missing}")

    # Explicitly subset before any numeric conversion so vertical columns are never read.
    d=df.loc[:,cols].copy()
    req=["bat_id","trackid","utc","x","y","dist_start"]
    mask=pd.Series(True,index=d.index)
    for col in req:
        mask &= present(d[col])
    d=d.loc[mask].copy()

    d["t"]=pd.to_datetime(d["utc"],errors="coerce",utc=True)
    if d["t"].isna().any():
        raise RuntimeError(f"timestamp parse failures: {int(d['t'].isna().sum())}")
    d["x_num"]=safe_num(d["x"],"x")
    d["y_num"]=safe_num(d["y"],"y")
    d["dist_start_num"]=safe_num(d["dist_start"],"dist_start")
    d["bat_id"]=d["bat_id"].astype(str)
    d["trackid"]=d["trackid"].astype(str)

    rows=[]
    track_first=[]
    for (iid,tid),g in d.groupby(["bat_id","trackid"],sort=True):
        g=g.sort_values("t").copy()
        x0=float(g["x_num"].iloc[0]); y0=float(g["y_num"].iloc[0])
        calc=np.hypot(g["x_num"].to_numpy()-x0,g["y_num"].to_numpy()-y0)
        src=g["dist_start_num"].to_numpy()
        for a,b in zip(calc,src):
            rows.append((a,b))
        track_first.append({
            "bat_id":iid,"trackid":tid,
            "first_dist_start":float(src[0]),
            "n":int(len(g))
        })

    arr=np.asarray(rows,dtype=float)
    calc=arr[:,0]; src=arr[:,1]
    summaries={}
    denom=np.maximum(calc,1.0)
    for scale in c["candidate_unit_scales_to_m"]:
        pred=src*float(scale)
        err=pred-calc
        rel=np.abs(err)/denom
        corr=float(np.corrcoef(calc,pred)[0,1]) if np.std(pred)>0 and np.std(calc)>0 else None
        summaries[str(scale)]={
            "scale_to_m":float(scale),
            "pearson_r":corr,
            "mae_m":float(np.mean(np.abs(err))),
            "median_abs_error_m":float(np.median(np.abs(err))),
            "median_relative_error":float(np.median(rel)),
            "q95_relative_error":float(np.quantile(rel,0.95))
        }

    best=min(
        summaries.values(),
        key=lambda z:(z["median_relative_error"],z["median_abs_error_m"])
    )
    first=np.asarray([x["first_dist_start"] for x in track_first],dtype=float)
    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "source_sha256":sha,
        "source_size_bytes":size,
        "numeric_vertical_values_read":False,
        "rows_used":int(len(d)),
        "tracks":int(len(track_first)),
        "individuals":int(d["bat_id"].nunique()),
        "first_record_dist_start":{
            "median":float(np.median(first)),
            "max_abs":float(np.max(np.abs(first))),
            "fraction_abs_le_1e_9":float(np.mean(np.abs(first)<=1e-9))
        },
        "candidate_scale_results":summaries,
        "best_scale_to_m":best["scale_to_m"],
        "best_match":best,
        "semantic_interpretation":(
            "dist_start is numerically consistent with Euclidean distance from the first x-y point of each track"
            if best["median_relative_error"]<=0.01 and best["pearson_r"] is not None and best["pearson_r"]>=0.999
            else "dist_start is not established as simple Euclidean distance from the first x-y point under the frozen audit rule"
        ),
        "claim_boundary":c["claim_boundary"]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    lines=[
        "# Nyctalus nonvertical context-field audit v1","",
        "**No numeric Height or other vertical-derived field was read.**","",
        f"- rows used: **{len(d)}**",
        f"- tracks: **{len(track_first)}**",
        f"- individuals: **{d['bat_id'].nunique()}**",
        f"- first-record dist_start = 0 fraction: **{payload['first_record_dist_start']['fraction_abs_le_1e_9']:.3f}**","",
        "| source dist_start scale to metres | Pearson r | median abs error (m) | median relative error | q95 relative error |",
        "|---:|---:|---:|---:|---:|"
    ]
    for k,v in summaries.items():
        lines.append(f"| {v['scale_to_m']:g} | {v['pearson_r']:.6f} | {v['median_abs_error_m']:.6f} | {v['median_relative_error']:.6f} | {v['q95_relative_error']:.6f} |")
    lines += ["",f"Best scale to metres: **{best['scale_to_m']:g}**","",payload["semantic_interpretation"],""]
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps({
        "best_scale_to_m":best["scale_to_m"],
        "best_match":best,
        "first_zero_fraction":payload["first_record_dist_start"]["fraction_abs_le_1e_9"],
        "semantic_interpretation":payload["semantic_interpretation"]
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
