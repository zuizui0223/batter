#!/usr/bin/env python3
from __future__ import annotations

import csv
import io
import json
import os
import re
from pathlib import Path

import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
CONTRACT=ROOT/"post_freeze_extensions/hipposideros_external_validation/id_provenance_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/hipposideros_external_validation/id_provenance_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/hipposideros_external_validation/ID_PROVENANCE_RESULT_V1.md"

def get_file(file_id,token,accept="*/*"):
    headers={
        "Authorization":f"Bearer {token}",
        "Accept":accept,
        "User-Agent":"batter-hipposideros-id-provenance-v1/1.0"
    }
    r=requests.get(
        f"https://datadryad.org/api/v2/files/{file_id}/download",
        headers=headers,timeout=180,allow_redirects=True
    )
    r.raise_for_status()
    return r.content

def present(s):
    txt=s.astype(str).str.strip()
    return s.notna() & txt.ne("") & ~txt.str.lower().isin({"na","nan","null","none"})

def normalize_id(x):
    return str(x).strip()

def main():
    c=json.loads(CONTRACT.read_text())
    token=os.environ.get("DRYAD_API_TOKEN","").strip()
    if not token:
        raise RuntimeError("DRYAD_API_TOKEN missing")

    gps_raw=get_file(int(c["source"]["gps_file_id"]),token,"text/csv,*/*")
    otu_raw=get_file(int(c["source"]["allotu_file_id"]),token,"text/csv,*/*")
    readme_raw=get_file(int(c["source"]["readme_file_id"]),token,"text/plain,text/markdown,*/*")

    # GPS: read id column only. No other field is loaded.
    gps=pd.read_csv(io.BytesIO(gps_raw),usecols=["id"],dtype=str,low_memory=False)
    gps_ids=sorted(set(gps.loc[present(gps["id"]),"id"].map(normalize_id)))

    # allotu: header only. No dietary count values are read.
    header_line=otu_raw.decode("utf-8-sig",errors="strict").splitlines()[0]
    otu_header=next(csv.reader([header_line]))
    otu_ids=[normalize_id(x) for x in otu_header[1:] if normalize_id(x)]
    otu_ids_unique=sorted(set(otu_ids))

    overlap=sorted(set(gps_ids)&set(otu_ids_unique))
    gps_only=sorted(set(gps_ids)-set(otu_ids_unique))
    otu_only=sorted(set(otu_ids_unique)-set(gps_ids))

    readme=readme_raw.decode("utf-8-sig",errors="replace")
    # Preserve only potentially identifier/species-relevant lines, not the full README.
    relevant=[]
    pats=re.compile(r"(armiger|pratti|species|gps|individual|\bid\b|D\d+|H\d+|Ha\d+|Hp\d+)",re.I)
    for line in readme.splitlines():
        if pats.search(line):
            relevant.append(line.strip())

    # Detect explicit token mappings if README happens to contain a line with both
    # a GPS-style ID and species name. We report; we do not infer from prefix alone.
    explicit=[]
    for line in relevant:
        ids=re.findall(r"\b[A-Za-z]+\d+\b",line)
        species=[]
        if re.search(r"Hipposideros\s+armiger|\bH\.\s*armiger\b|\barmiger\b",line,re.I):
            species.append("Hipposideros armiger")
        if re.search(r"Hipposideros\s+pratti|\bH\.\s*pratti\b|\bpratti\b",line,re.I):
            species.append("Hipposideros pratti")
        if ids and len(species)==1:
            explicit.append({"line":line,"ids":ids,"species":species[0]})

    prefix_counts={}
    for iid in gps_ids:
        m=re.match(r"^([A-Za-z]+)",iid)
        p=m.group(1) if m else ""
        prefix_counts[p]=prefix_counts.get(p,0)+1

    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "numeric_height_values_read":False,
        "gps_columns_read":["id"],
        "dietary_values_read":False,
        "gps_ids":gps_ids,
        "gps_id_count":len(gps_ids),
        "gps_prefix_counts":prefix_counts,
        "allotu_header_ids":otu_ids_unique,
        "allotu_header_id_count":len(otu_ids_unique),
        "gps_allotu_overlap_ids":overlap,
        "gps_allotu_overlap_count":len(overlap),
        "gps_only_ids":gps_only,
        "allotu_only_ids":otu_only,
        "readme_relevant_lines":relevant,
        "readme_explicit_id_species_lines":explicit,
        "mapping_status":"EXPLICIT_MAPPING_FOUND" if explicit else "SPECIES_MAPPING_UNRESOLVED",
        "decision_rule":c["decision_rule"],
        "claim_boundary":c["claim_boundary"]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    lines=[
        "# Hipposideros ID provenance audit v1","",
        "**Outcome-blind. GPS Height and all other GPS fields were not read; dietary values were not read.**","",
        f"- GPS unique IDs: **{len(gps_ids)}** — {', '.join(gps_ids)}",
        f"- GPS prefix counts: **{prefix_counts}**",
        f"- allotu header IDs: **{len(otu_ids_unique)}**",
        f"- GPS/allotu overlap: **{len(overlap)}** — {', '.join(overlap) if overlap else 'none'}",
        f"- GPS-only IDs: **{', '.join(gps_only) if gps_only else 'none'}",
        f"- allotu-only IDs: **{', '.join(otu_only) if otu_only else 'none'}","",
        "## README identifier/species lines",""
    ]
    if relevant:
        lines.extend([f"- {x}" for x in relevant])
    else:
        lines.append("- none")
    lines += ["","## Explicit ID-to-species evidence",""]
    if explicit:
        for x in explicit:
            lines.append(f"- {x['species']}: {', '.join(x['ids'])} — {x['line']}")
    else:
        lines.append("- none found")
    lines += ["",f"**Mapping status: {payload['mapping_status']}**",""]
    OUT_MD.write_text("\n".join(lines),encoding="utf-8")

    print(json.dumps({
        "gps_ids":gps_ids,
        "prefix_counts":prefix_counts,
        "otu_header_ids":otu_ids_unique,
        "overlap":overlap,
        "gps_only":gps_only,
        "otu_only":otu_only,
        "explicit":explicit,
        "mapping_status":payload["mapping_status"]
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
