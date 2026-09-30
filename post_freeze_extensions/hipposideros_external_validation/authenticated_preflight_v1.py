#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import io
import json
import os
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
MAP_CONTRACT=ROOT/"post_freeze_extensions/hipposideros_external_validation/species_mapping_contract_v1.json"
PRIMARY_DESIGN=ROOT/"post_freeze_extensions/hipposideros_external_validation/primary_design_v1.json"
OUT=ROOT/"post_freeze_extensions/hipposideros_external_validation/authenticated_preflight_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/hipposideros_external_validation/AUTHENTICATED_PREFLIGHT_V1.md"
RECEIPT=ROOT/"post_freeze_extensions/hipposideros_external_validation/height_opening_receipt_v1.json"

FILE_ID=4102381
FILE_NAME="GPS_data.csv"
DOWNLOAD=f"https://datadryad.org/api/v2/files/{FILE_ID}/download"
META=f"https://datadryad.org/api/v2/files/{FILE_ID}"

def present(s):
    txt=s.astype(str).str.strip()
    return s.notna() & txt.ne("") & ~txt.str.lower().isin({"na","nan","null","none"})

def leading_prefix(x):
    m=re.match(r"^([A-Za-z]+)",str(x).strip())
    return m.group(1) if m else ""

def main():
    token=os.environ.get("DRYAD_API_TOKEN","").strip()
    if not token:
        raise RuntimeError("DRYAD_API_TOKEN is missing; do not fall back to unauthenticated download")

    headers={
        "Accept":"application/json",
        "Authorization":f"Bearer {token}",
        "User-Agent":"batter-hipposideros-authenticated-preflight-v1/1.0",
    }

    # Authenticated metadata read: provenance only.
    mr=requests.get(META,headers=headers,timeout=90)
    mr.raise_for_status()
    meta=mr.json()

    # Authenticated file download. Numeric height is never parsed below.
    r=requests.get(DOWNLOAD,headers=headers,timeout=180,allow_redirects=True)
    r.raise_for_status()
    raw=r.content
    if len(raw)<1000:
        raise RuntimeError(f"download too small: {len(raw)} bytes")
    first=raw[:4096].decode("utf-8",errors="ignore").splitlines()[0] if raw else ""
    required_header=["id","timestamp","longitude","latitude","height"]
    if not all(x in first for x in required_header):
        raise RuntimeError(f"download is not expected GPS CSV; first line={first[:300]!r}")

    sha=hashlib.sha256(raw).hexdigest()
    df=pd.read_csv(io.BytesIO(raw),dtype=str,low_memory=False)
    required=["id","timestamp","longitude","latitude","height"]
    missing=[x for x in required if x not in df.columns]
    if missing:
        raise RuntimeError(f"missing required columns {missing}")

    # Species mapping: ID strings only.
    ids=sorted(set(df.loc[present(df["id"]),"id"].astype(str).str.strip()))
    groups=defaultdict(list)
    for iid in ids:
        p=leading_prefix(iid)
        if not p:
            raise RuntimeError(f"id has no leading alphabetic prefix: {iid!r}")
        groups[p].append(iid)
    counts={p:len(v) for p,v in sorted(groups.items())}

    mapping_contract=json.loads(MAP_CONTRACT.read_text())
    expected=sorted(mapping_contract["published_species_counts"].values())
    got=sorted(counts.values())
    mapping_ok=(len(counts)==2 and got==expected)
    species_by_prefix={}
    if mapping_ok:
        for p,n in counts.items():
            if n==9:
                species_by_prefix[p]="Hipposideros armiger"
            elif n==8:
                species_by_prefix[p]="Hipposideros pratti"
            else:
                mapping_ok=False
    if not mapping_ok:
        raise RuntimeError(
            f"MAPPING_UNRESOLVED: prefix counts {counts} are not uniquely {{9,8}}; "
            "do not infer species from any other field"
        )

    id_to_species={}
    for p,vals in groups.items():
        for iid in vals:
            id_to_species[iid]=species_by_prefix[p]

    # Structural gate. Height is presence-only.
    mask=pd.Series(True,index=df.index)
    for col in required:
        mask &= present(df[col])
    d=df.loc[mask,required].copy()

    # Numeric parsing is allowed only for timestamp/lon/lat, never height.
    d["t"]=pd.to_datetime(d["timestamp"],errors="coerce")
    d["lon_num"]=pd.to_numeric(d["longitude"],errors="coerce")
    d["lat_num"]=pd.to_numeric(d["latitude"],errors="coerce")
    nonvertical_bad=d["t"].isna()|d["lon_num"].isna()|d["lat_num"].isna()
    if nonvertical_bad.any():
        raise RuntimeError(f"nonvertical parse failures: {int(nonvertical_bad.sum())}")

    has_time=bool(((d["t"].dt.hour!=0)|(d["t"].dt.minute!=0)|(d["t"].dt.second!=0)).any())
    if has_time:
        d["session_date"]=(d["t"]-pd.Timedelta(hours=12)).dt.date.astype(str)
        session_rule="timestamp_minus_12h_then_date"
    else:
        d["session_date"]=d["t"].dt.date.astype(str)
        session_rule="raw_calendar_date"

    d["id"]=d["id"].astype(str).str.strip()
    d["species"]=d["id"].map(id_to_species)
    if d["species"].isna().any():
        raise RuntimeError("species mapping missing for retained ID")

    minfix=50
    counts_night=(
        d.groupby(["species","id","session_date"],sort=True)
        .size().rename("n").reset_index()
    )
    qual=counts_night[counts_night["n"]>=minfix].copy()

    repeat_ids={}
    frozen_sessions={}
    for species in sorted(d["species"].unique()):
        ids_sp=sorted(d.loc[d["species"]==species,"id"].unique())
        repeat=[]
        sess={}
        for iid in ids_sp:
            q=qual[(qual["species"]==species)&(qual["id"]==iid)]
            if len(q)>=2:
                repeat.append(iid)
                sess[iid]=[
                    {"session_date":str(x.session_date),"presence_qualified_fixes":int(x.n)}
                    for x in q.itertuples(index=False)
                ]
        repeat_ids[species]=repeat
        frozen_sessions[species]=sess

    total_repeat=sum(len(v) for v in repeat_ids.values())
    source_gate=total_repeat>=5
    panel_gate={sp:len(v)>=3 for sp,v in repeat_ids.items()}
    eligible_species=[sp for sp,ok in panel_gate.items() if ok]
    primary_may_open=bool(source_gate and eligible_species)

    if not primary_may_open:
        decision="STRUCTURAL_FAIL"
    else:
        decision="STRUCTURAL_PASS_HEIGHT_STILL_UNOPENED"

    payload={
        "schema_version":1,
        "study_id":"batter-hipposideros-authenticated-preflight-v1",
        "numeric_height_values_read":False,
        "dryad_file_id":FILE_ID,
        "dryad_metadata":meta,
        "file_name_expected":FILE_NAME,
        "raw_sha256":sha,
        "raw_size_bytes":len(raw),
        "rows_total":int(len(df)),
        "rows_presence_qualified":int(len(d)),
        "unique_ids":ids,
        "prefix_counts":counts,
        "species_by_prefix":species_by_prefix,
        "species_mapping_resolved":True,
        "session_rule":session_rule,
        "qualified_nights_ge50":int(len(qual)),
        "repeat_ids_by_species":repeat_ids,
        "repeat_id_count_total":int(total_repeat),
        "species_panel_gate":panel_gate,
        "eligible_species_panels":eligible_species,
        "source_gate_pass":bool(source_gate),
        "primary_may_open":primary_may_open,
        "decision":decision,
        "height_column_operation":"presence/nonblank only",
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    receipt={
        "schema_version":1,
        "study_id":"batter-hipposideros-height-opening-receipt-v1",
        "status":"HEIGHT_MAY_OPEN" if primary_may_open else "STOP",
        "raw_sha256":sha,
        "dryad_file_id":FILE_ID,
        "species_by_prefix":species_by_prefix,
        "eligible_species_panels":eligible_species,
        "eligible_repeat_ids_by_species":{
            sp:repeat_ids[sp] for sp in eligible_species
        },
        "eligible_ge50_sessions_by_species":{
            sp:frozen_sessions[sp] for sp in eligible_species
        },
        "session_rule":session_rule,
        "minimum_presence_qualified_fixes_per_session":50,
        "primary_design":"post_freeze_extensions/hipposideros_external_validation/primary_design_v1.json",
        "primary_design_sha256":hashlib.sha256(PRIMARY_DESIGN.read_bytes()).hexdigest(),
        "species_mapping_contract_sha256":hashlib.sha256(MAP_CONTRACT.read_bytes()).hexdigest(),
        "numeric_height_values_read":False,
        "next_step":(
            "Freeze this receipt unchanged in git, then and only then run the primary vertical validator."
            if primary_may_open else
            "STOP. Do not lower gates or alter species mapping/session definition."
        )
    }
    RECEIPT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    lines=[
        "# Hipposideros authenticated outcome-blind preflight v1","",
        "**Numeric height values were not parsed or summarized.**","",
        f"- raw SHA256: `{sha}`",
        f"- rows: **{len(df)}**",
        f"- ID prefix counts: **{counts}**",
        f"- species mapping: **{species_by_prefix}**",
        f"- session rule: **{session_rule}**",
        f"- >=50-fix nights: **{len(qual)}**",
        f"- repeat individuals total: **{total_repeat}**",
        f"- repeat IDs by species: **{repeat_ids}**",
        f"- eligible species panels (>=3 repeat IDs): **{eligible_species}**",
        f"- source structural gate: **{'PASS' if source_gate else 'FAIL'}**",
        f"- primary Height may open: **{primary_may_open}**","",
        "If PASS, the exact IDs and >=50-fix sessions are pinned in `height_opening_receipt_v1.json`.",""
    ]
    OUT_MD.write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps({
        "raw_sha256":sha,
        "prefix_counts":counts,
        "species_by_prefix":species_by_prefix,
        "repeat_counts":{k:len(v) for k,v in repeat_ids.items()},
        "eligible_species_panels":eligible_species,
        "source_gate_pass":source_gate,
        "primary_may_open":primary_may_open,
        "decision":decision
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
