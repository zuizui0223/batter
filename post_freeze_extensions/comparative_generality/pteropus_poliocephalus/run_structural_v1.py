#!/usr/bin/env python3
from __future__ import annotations

import hashlib, io, json, re
from collections import defaultdict
from pathlib import Path

import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[3]
CONTRACT=ROOT/"post_freeze_extensions/comparative_generality/pteropus_poliocephalus/structural_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/comparative_generality/pteropus_poliocephalus/structural_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/comparative_generality/pteropus_poliocephalus/STRUCTURAL_RESULT_V1.md"
UA={"User-Agent":"batter-pteropus-poliocephalus-structural-v1/1.0"}

def present(s):
    txt=s.astype(str).str.strip()
    return s.notna() & txt.ne("") & ~txt.str.lower().isin({"na","nan","null","none"})

def is_true(x):
    return str(x).strip().lower() in {"true","1","t","yes","y"}

def main():
    c=json.loads(CONTRACT.read_text())
    r=requests.get(c["source"]["content_url"],headers=UA,timeout=180)
    r.raise_for_status()
    raw=r.content
    sha=hashlib.sha256(raw).hexdigest()

    required=["timestamp","location-long","location-lat","individual-local-identifier","height-above-msl"]
    header=pd.read_csv(io.BytesIO(raw),nrows=0)
    missing=[x for x in required if x not in header.columns]
    if missing:
        raise RuntimeError(f"missing frozen fields {missing}")

    # Load height strictly as string for presence; never convert it numerically.
    usecols=required+([ "algorithm-marked-outlier" ] if "algorithm-marked-outlier" in header.columns else [])
    df=pd.read_csv(io.BytesIO(raw),usecols=usecols,dtype=str,low_memory=False)

    mask=pd.Series(True,index=df.index)
    for col in required:
        mask &= present(df[col])
    if "algorithm-marked-outlier" in df.columns:
        outlier=df["algorithm-marked-outlier"].map(is_true)
        mask &= ~outlier
    d=df.loc[mask,required].copy()

    # Parse only nonvertical fields.
    d["t"]=pd.to_datetime(d["timestamp"],errors="coerce",utc=True,format="mixed")
    d["lon"]=pd.to_numeric(d["location-long"],errors="coerce")
    d["lat"]=pd.to_numeric(d["location-lat"],errors="coerce")
    bad=d["t"].isna()|d["lon"].isna()|d["lat"].isna()
    if bad.any():
        raise RuntimeError(f"nonvertical parse failures: {int(bad.sum())}")
    d["iid"]=d["individual-local-identifier"].astype(str).str.strip()

    sessions=[]
    structure={}
    for iid,g in d.groupby("iid",sort=True):
        g=g.sort_values("t").copy()
        gaps=g["t"].diff().dt.total_seconds().div(3600)
        session_no=(gaps.gt(4).fillna(False)).cumsum().astype(int)
        counts=g.groupby(session_no).size()
        all_counts=[int(x) for x in counts.tolist()]
        eligible=[int(x) for x in counts[counts>=50].tolist()]
        structure[iid]={
            "presence_qualified_rows":int(len(g)),
            "all_session_counts":all_counts,
            "eligible_session_counts":eligible,
            "eligible_session_count":len(eligible),
        }
        for sn,n in counts.items():
            sessions.append({"id":iid,"session_index":int(sn),"events":int(n),"eligible":bool(n>=50)})

    repeat=sorted(iid for iid,x in structure.items() if x["eligible_session_count"]>=2)
    passes=len(repeat)>=5
    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "raw_sha256":sha,
        "rows_in_file":int(len(df)),
        "presence_qualified_rows":int(len(d)),
        "numeric_height_values_parsed":False,
        "individuals_with_presence":int(d["iid"].nunique()),
        "eligible_session_count_total":int(sum(x["eligible_session_count"] for x in structure.values())),
        "repeat_individual_count":len(repeat),
        "repeat_individual_ids":repeat,
        "session_structure":structure,
        "decision":"PASS_TO_SOURCE_PREFLIGHT" if passes else "STRUCTURAL_STOP",
        "passes":bool(passes),
        "claim_boundary":c["claim_boundary"]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    lines=[
        "# Pteropus poliocephalus outcome-blind structural preflight v1","",
        "**Numeric height-above-msl was never parsed or summarized.**","",
        f"- raw SHA256: `{sha}`",
        f"- rows in event file: **{len(df)}**",
        f"- presence-qualified rows: **{len(d)}**",
        f"- individuals with presence: **{d['iid'].nunique()}**",
        f"- >=50-event sessions: **{payload['eligible_session_count_total']}**",
        f"- repeat individuals (>=2 eligible sessions): **{len(repeat)}** — {', '.join(repeat) if repeat else 'none'}",
        f"- frozen gate: **{'PASS' if passes else 'STRUCTURAL STOP'}**","",
        "| individual | presence rows | all session counts | eligible session counts |",
        "|---|---:|---|---|"
    ]
    for iid,x in structure.items():
        lines.append(f"| {iid} | {x['presence_qualified_rows']} | {x['all_session_counts']} | {x['eligible_session_counts']} |")
    lines += ["",f"**Decision: {payload['decision']}**",""]
    OUT_MD.write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps({
        "rows":len(df),
        "presence_rows":len(d),
        "individuals":int(d["iid"].nunique()),
        "eligible_sessions":payload["eligible_session_count_total"],
        "repeat_n":len(repeat),
        "repeat_ids":repeat,
        "decision":payload["decision"]
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
