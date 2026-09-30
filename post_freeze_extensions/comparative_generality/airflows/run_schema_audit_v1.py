#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import math
import time
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import requests
from remotezip import RemoteZip

ROOT=Path(__file__).resolve().parents[3]
CONTRACT=ROOT/"post_freeze_extensions/comparative_generality/airflows/schema_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/comparative_generality/airflows/schema_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/comparative_generality/airflows/SCHEMA_RESULT_V1.md"
UA={"User-Agent":"batter-airflows-multispecies-schema-v1/1.0"}

def zenodo_file_url(record_id,name):
    r=requests.get(f"https://zenodo.org/api/records/{record_id}",headers=UA,timeout=90)
    r.raise_for_status()
    j=r.json()
    for f in j.get("files",[]):
        key=f.get("key") or f.get("filename")
        if key==name:
            return (f.get("links") or {}).get("content") or (f.get("links") or {}).get("self"), {
                "size":f.get("size"),
                "checksum":f.get("checksum"),
                "key":key,
            }
    raise RuntimeError(f"Zenodo file not found: {name}")

def gbif_match(name):
    url="https://api.gbif.org/v1/species/match?name="+quote(name)
    r=requests.get(url,headers=UA,timeout=60)
    r.raise_for_status()
    j=r.json()
    return {
        "usageKey":j.get("usageKey"),
        "scientificName":j.get("scientificName"),
        "canonicalName":j.get("canonicalName"),
        "rank":j.get("rank"),
        "status":j.get("status"),
        "matchType":j.get("matchType"),
        "confidence":j.get("confidence"),
        "order":j.get("order"),
        "family":j.get("family"),
    }

def norm_study_id(x):
    if pd.isna(x):
        return None
    s=str(x).strip()
    if s.lower() in {"","na","nan","none","null"}:
        return None
    # read_csv may turn integer-like IDs into 123.0
    try:
        f=float(s)
        if math.isfinite(f) and f.is_integer():
            return str(int(f))
    except Exception:
        pass
    return s

def main():
    c=json.loads(CONTRACT.read_text())
    url,meta=zenodo_file_url(int(c["source"]["record_id"]),c["source"]["archive"])

    with RemoteZip(url,headers=UA) as rz:
        names=rz.namelist()
        suffix=c["source"]["segment_table"]
        matches=[x for x in names if x.endswith(suffix) or x.endswith(suffix.split("/",1)[-1])]
        if len(matches)!=1:
            raise RuntimeError(f"segment table match count {len(matches)}: {matches[:20]}")
        member=matches[0]
        with rz.open(member) as fh:
            # Header first so we can fail closed on allowed columns.
            raw=fh.read()
    # This CSV is segment-level and contains no point-level vertical response used here.
    header=pd.read_csv(io.BytesIO(raw),nrows=0)
    allowed=c["allowed_segment_fields"]
    missing=[x for x in allowed if x not in header.columns]
    if missing:
        raise RuntimeError(f"missing allowed segment fields {missing}; columns={list(header.columns)}")

    df=pd.read_csv(io.BytesIO(raw),usecols=allowed,low_memory=False)
    # Explicitly operate only on frozen nonvertical columns.
    df=df.loc[:,allowed].copy()
    for col in ["species","individualID","studyName","dataSource"]:
        if col in df.columns:
            df[col]=df[col].astype(str).str.strip()
    df["studyID_norm"]=[norm_study_id(x) for x in df["studyID"]]
    df["segmentID"]=df["segmentID"].astype(str).str.strip()
    df["totNlocs_num"]=pd.to_numeric(df["totNlocs"],errors="coerce")
    df["start"]=pd.to_datetime(df["segm_timeStart"],errors="coerce",utc=True,format="mixed")
    df["end"]=pd.to_datetime(df["segm_timeEnd"],errors="coerce",utc=True,format="mixed")
    if df["totNlocs_num"].isna().any():
        raise RuntimeError(f"totNlocs parse failures: {int(df['totNlocs_num'].isna().sum())}")

    species=sorted(x for x in df["species"].dropna().astype(str).str.strip().unique() if x)
    taxonomy={}
    for i,sp in enumerate(species):
        try:
            taxonomy[sp]=gbif_match(sp)
        except Exception as e:
            taxonomy[sp]={"error":str(e),"order":None}
        if i and i%10==0:
            time.sleep(0.1)

    bat_species=sorted(sp for sp,t in taxonomy.items() if t.get("order")=="Chiroptera")
    unresolved=sorted(sp for sp,t in taxonomy.items() if not t.get("order"))

    df_bat=df[df["species"].isin(bat_species)].copy()
    if df_bat.empty:
        raise RuntimeError("GBIF-classified bat subset is empty")

    def panel_key(row):
        sid=row["studyID_norm"]
        if sid is not None:
            return f"studyID:{sid}::{row['species']}"
        return f"studyName:{row['studyName']}::{row['species']}"
    df_bat["panel_key"]=[panel_key(r) for _,r in df_bat.iterrows()]

    known_taxa=set(c["known_opened_taxa"])
    known_exact={sp:set(ids) for sp,ids in c["known_exact_movebank_study_ids"].items()}

    panels=[]
    for key,g in df_bat.groupby("panel_key",sort=True):
        sp=str(g["species"].iloc[0])
        study_ids=sorted(set(x for x in g["studyID_norm"] if x is not None))
        study_names=sorted(set(x for x in g["studyName"] if x and x.lower()!="nan"))
        inds=sorted(set(x for x in g["individualID"] if x and x.lower()!="nan"))
        seg_per_ind=g.groupby("individualID")["segmentID"].nunique()
        repeat2=int((seg_per_ind>=2).sum())
        n_ind=len(inds)
        n_seg=int(g["segmentID"].nunique())
        total_points=int(g["totNlocs_num"].sum())
        starts=g["start"].dropna()
        ends=g["end"].dropna()
        exact_overlap=False
        if sp in known_exact and study_ids:
            exact_overlap=any(s in known_exact[sp] for s in study_ids)
        panels.append({
            "panel_key":key,
            "species":sp,
            "study_ids":study_ids,
            "study_names":study_names,
            "data_sources":sorted(set(x for x in g["dataSource"] if x and x.lower()!="nan")),
            "individuals":n_ind,
            "individuals_with_ge2_segments":repeat2,
            "segments":n_seg,
            "sum_totNlocs":total_points,
            "date_start":starts.min().isoformat() if len(starts) else None,
            "date_end":ends.max().isoformat() if len(ends) else None,
            "known_taxon_overlap":sp in known_taxa,
            "known_exact_study_overlap":bool(exact_overlap),
            "necessary_screen_pass":bool(n_ind>=5 and repeat2>=5),
        })

    candidate_panels=[x for x in panels if x["necessary_screen_pass"] and not x["known_exact_study_overlap"]]

    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "numeric_point_level_vertical_values_read":False,
        "point_level_rds_opened":False,
        "zenodo_archive":meta,
        "zip_member_count":len(names),
        "segment_table_member":member,
        "segment_rows":int(len(df)),
        "segment_columns_read":allowed,
        "species_count":len(species),
        "taxonomy":taxonomy,
        "bat_species":bat_species,
        "bat_species_count":len(bat_species),
        "taxonomy_unresolved_species":unresolved,
        "bat_segment_rows":int(len(df_bat)),
        "bat_panels":panels,
        "necessary_screen_candidate_panels":candidate_panels,
        "necessary_screen_candidate_count":len(candidate_panels),
        "claim_boundary":c["claim_boundary"],
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    lines=[
        "# Airflows multispecies nonvertical schema audit v1","",
        "**No point-level RDS file and no numeric vertical value was opened.**","",
        f"- segment rows: **{len(df):,}**",
        f"- unique species in biologging summary: **{len(species)}**",
        f"- GBIF-classified bat species: **{len(bat_species)}**",
        f"- bat study×species panels: **{len(panels)}**",
        f"- necessary-screen candidate panels: **{len(candidate_panels)}**","",
        "## Bat panels","",
        "| panel | species | individuals | >=2 segments | segments | point-count proxy | known taxon? | exact known study? | necessary screen |",
        "|---|---|---:|---:|---:|---:|---|---|---|"
    ]
    for x in panels:
        label=(x["study_ids"][0] if x["study_ids"] else (x["study_names"][0] if x["study_names"] else x["panel_key"]))
        lines.append(
            f"| {label} | {x['species']} | {x['individuals']} | {x['individuals_with_ge2_segments']} | "
            f"{x['segments']} | {x['sum_totNlocs']} | {'yes' if x['known_taxon_overlap'] else 'no'} | "
            f"{'yes' if x['known_exact_study_overlap'] else 'no'} | {'PASS' if x['necessary_screen_pass'] else 'FAIL'} |"
        )
    lines += ["","## Candidate panels for separately frozen point-level preflight",""]
    if candidate_panels:
        for x in candidate_panels:
            lines.append(f"- `{x['panel_key']}`: {x['individuals']} individuals, {x['individuals_with_ge2_segments']} with >=2 segments, {x['segments']} segments")
    else:
        lines.append("- none")
    if unresolved:
        lines += ["","## Taxonomy unresolved","",* [f"- {x}" for x in unresolved]]
    lines.append("")
    OUT_MD.write_text("\n".join(lines),encoding="utf-8")

    print(json.dumps({
        "bat_species":bat_species,
        "bat_panel_count":len(panels),
        "candidate_panel_count":len(candidate_panels),
        "candidate_panels":[
            {
                "panel_key":x["panel_key"],
                "species":x["species"],
                "individuals":x["individuals"],
                "repeat2":x["individuals_with_ge2_segments"],
                "segments":x["segments"],
                "known_taxon_overlap":x["known_taxon_overlap"],
                "known_exact_study_overlap":x["known_exact_study_overlap"]
            } for x in candidate_panels
        ]
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
