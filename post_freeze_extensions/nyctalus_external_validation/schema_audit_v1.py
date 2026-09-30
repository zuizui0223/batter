#!/usr/bin/env python3
from __future__ import annotations

import hashlib, io, json, re, sys
from pathlib import Path
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
CONTRACT=ROOT/"post_freeze_extensions/nyctalus_external_validation/schema_audit_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/nyctalus_external_validation/schema_audit_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/nyctalus_external_validation/SCHEMA_AUDIT_RESULT_V1.md"
HEADERS={"User-Agent":"batter-nyctalus-schema-audit-v1/1.0"}

def norm(x):
    return re.sub(r"[^a-z0-9]+","_",str(x).strip().lower()).strip("_")

def present(s):
    x=s.notna()
    txt=s.astype(str).str.strip()
    x &= txt.ne("")
    x &= ~txt.str.lower().isin({"na","nan","null","none"})
    return x

def main():
    c=json.loads(CONTRACT.read_text())
    meta=requests.get(f"https://zenodo.org/api/records/{c['source']['record_id']}",headers=HEADERS,timeout=90)
    meta.raise_for_status()
    j=meta.json()
    target=None
    for f in j.get("files",[]):
        if (f.get("key") or f.get("filename"))==c["source"]["file"]:
            target=f
            break
    if target is None:
        raise RuntimeError("target file not found in Zenodo record")
    url=(target.get("links") or {}).get("content") or (target.get("links") or {}).get("self")
    r=requests.get(url,headers=HEADERS,timeout=180)
    r.raise_for_status()
    data=r.content
    sha=hashlib.sha256(data).hexdigest()
    if sha!=c["source"]["sha256"]:
        raise RuntimeError(f"sha256 mismatch {sha}")
    df=pd.read_csv(io.BytesIO(data),dtype=str,low_memory=False)
    cols=list(df.columns)

    # Exact canonical fields already identified by the structural admission screen.
    required=["bat_id","trackid","utc","Height"]
    missing=[x for x in required if x not in cols]
    if missing:
        raise RuntimeError(f"missing required fields {missing}; columns={cols}")

    # Never parse Height. Presence only.
    height_presence=int(present(df["Height"]).sum())

    # Timestamp audit is allowed and outcome-blind.
    times=pd.to_datetime(df["utc"],errors="coerce",utc=True)
    valid_time=times.notna()
    year_counts={str(k):int(v) for k,v in times[valid_time].dt.year.value_counts().sort_index().items()}
    month_counts={str(k):int(v) for k,v in times[valid_time].dt.month.value_counts().sort_index().items()}

    track_df=pd.DataFrame({
        "bat_id":df["bat_id"].astype(str),
        "trackid":df["trackid"].astype(str),
        "utc":times,
    }).dropna(subset=["utc"])
    track_meta=[]
    for (iid,tid),g in track_df.groupby(["bat_id","trackid"],sort=True):
        ts=g["utc"].sort_values()
        med=ts.iloc[len(ts)//2]
        month=int(med.month)
        if month in (5,6):
            season="late_spring"
        elif month in (8,9):
            season="late_summer"
        else:
            season="other"
        track_meta.append({
            "bat_id":str(iid),
            "trackid":str(tid),
            "row_count":int(len(g)),
            "start_utc":ts.iloc[0].isoformat(),
            "end_utc":ts.iloc[-1].isoformat(),
            "median_utc":med.isoformat(),
            "year":int(med.year),
            "month":month,
            "source_season":season,
            "calendar_cohort":f"{int(med.year)}::{season}",
        })

    # Audit low-cardinality, non-vertical context columns only.
    protected={norm(x) for x in ["Height","bat_id","trackid","utc","longitude","latitude","x","y","utm_x","utm_y"]}
    context={}
    for col in cols:
        if norm(col) in protected or "height" in norm(col) or "alt" in norm(col):
            continue
        vals=df.loc[present(df[col]),col].astype(str).str.strip()
        nunq=int(vals.nunique())
        if 1<=nunq<=20:
            context[col]={
                "nonempty_n":int(len(vals)),
                "unique_n":nunq,
                "values":sorted(vals.unique().tolist())[:20]
            }

    cohort_counts={}
    for rec in track_meta:
        cohort_counts.setdefault(rec["calendar_cohort"],{"tracks":0,"individuals":set()})
        cohort_counts[rec["calendar_cohort"]]["tracks"]+=1
        cohort_counts[rec["calendar_cohort"]]["individuals"].add(rec["bat_id"])
    cohort_counts={k:{"tracks":v["tracks"],"individuals":len(v["individuals"])} for k,v in sorted(cohort_counts.items())}

    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "source":c["source"],
        "downloaded_sha256":sha,
        "size_bytes":len(data),
        "row_count":int(len(df)),
        "columns":cols,
        "height_presence_rows":height_presence,
        "numeric_height_values_read":False,
        "individual_count":int(df.loc[present(df["bat_id"]),"bat_id"].nunique()),
        "track_count":int(df.loc[present(df["trackid"]),"trackid"].nunique()),
        "year_counts":year_counts,
        "month_counts":month_counts,
        "low_cardinality_nonvertical_context_fields":context,
        "track_metadata":track_meta,
        "calendar_cohort_counts":cohort_counts
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    lines=[
        "# Nyctalus outcome-blind schema audit v1","",
        "**Numeric Height values were not parsed.**","",
        f"- rows: **{len(df)}**",
        f"- individuals: **{payload['individual_count']}**",
        f"- tracks: **{payload['track_count']}**",
        f"- Height nonblank rows: **{height_presence}**","",
        "## Columns","",
        ", ".join(f"`{x}`" for x in cols),"",
        "## Calendar cohorts from track median UTC","",
        "| cohort | tracks | individuals |",
        "|---|---:|---:|"
    ]
    for k,v in cohort_counts.items():
        lines.append(f"| {k} | {v['tracks']} | {v['individuals']} |")
    lines += ["","## Low-cardinality nonvertical context fields",""]
    for k,v in context.items():
        lines.append(f"- `{k}`: {v['unique_n']} values — {', '.join(v['values'])}")
    lines.append("")
    OUT_MD.write_text("\n".join(lines),encoding="utf-8")

    print(json.dumps({
        "columns":cols,
        "cohorts":cohort_counts,
        "context_fields":context,
        "rows":len(df),
        "individuals":payload["individual_count"],
        "tracks":payload["track_count"],
        "height_presence_rows":height_presence,
        "sha256":sha
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
