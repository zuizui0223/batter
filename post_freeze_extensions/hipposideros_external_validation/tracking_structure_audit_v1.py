#!/usr/bin/env python3
from __future__ import annotations

import io, json, os
from pathlib import Path
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"post_freeze_extensions/hipposideros_external_validation/tracking_structure_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/hipposideros_external_validation/TRACKING_STRUCTURE_RESULT_V1.md"
FILE_ID=4102381

def present(s):
    txt=s.astype(str).str.strip()
    return s.notna() & txt.ne("") & ~txt.str.lower().isin({"na","nan","null","none"})

def main():
    token=os.environ.get("DRYAD_API_TOKEN","").strip()
    if not token:
        raise RuntimeError("DRYAD_API_TOKEN missing")
    r=requests.get(
        f"https://datadryad.org/api/v2/files/{FILE_ID}/download",
        headers={
            "Authorization":f"Bearer {token}",
            "Accept":"text/csv,*/*",
            "User-Agent":"batter-hipposideros-tracking-structure-v1/1.0",
        },
        timeout=180,allow_redirects=True
    )
    r.raise_for_status()
    # Read exactly two nonvertical columns.
    df=pd.read_csv(io.BytesIO(r.content),usecols=["id","timestamp"],dtype=str,low_memory=False)
    mask=present(df["id"]) & present(df["timestamp"])
    d=df.loc[mask].copy()
    d["id"]=d["id"].astype(str).str.strip()
    d["t"]=pd.to_datetime(d["timestamp"],errors="coerce",format="mixed")
    if d["t"].isna().any():
        raise RuntimeError(f"timestamp parse failures: {int(d['t'].isna().sum())}")
    d["date"]=d["t"].dt.date.astype(str)

    by_id=[]
    by_id_date=[]
    for iid,g in d.groupby("id",sort=True):
        counts=g.groupby("date").size().sort_index()
        by_id.append({
            "id":iid,
            "rows":int(len(g)),
            "dates":int(counts.size),
            "first_date":str(counts.index.min()),
            "last_date":str(counts.index.max()),
            "min_rows_per_date":int(counts.min()),
            "median_rows_per_date":float(counts.median()),
            "max_rows_per_date":int(counts.max()),
            "dates_ge50":int((counts>=50).sum()),
        })
        for date,n in counts.items():
            by_id_date.append({"id":iid,"date":str(date),"rows":int(n)})

    payload={
        "schema_version":1,
        "study_id":"batter-hipposideros-tracking-structure-v1",
        "numeric_height_values_read":False,
        "gps_columns_read":["id","timestamp"],
        "unique_id_count":int(d["id"].nunique()),
        "by_id":by_id,
        "by_id_date":by_id_date
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    lines=[
        "# Hipposideros tracking-structure audit v1","",
        "**Outcome-blind. Only GPS id and timestamp were read.**","",
        "| id | rows | dates | dates >=50 rows | min/date | median/date | max/date | first | last |",
        "|---|---:|---:|---:|---:|---:|---:|---|---|"
    ]
    for x in by_id:
        lines.append(
            f"| {x['id']} | {x['rows']} | {x['dates']} | {x['dates_ge50']} | "
            f"{x['min_rows_per_date']} | {x['median_rows_per_date']:.1f} | {x['max_rows_per_date']} | "
            f"{x['first_date']} | {x['last_date']} |"
        )
    OUT_MD.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"by_id":by_id},sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
