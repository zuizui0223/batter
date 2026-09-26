#!/usr/bin/env python3
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import io
import json
import math
from pathlib import Path
import re
import urllib.request

CONFIG=Path("config/bat_panel_sources_v1.json")
HEIGHT_PRIORITY=["height_above_msl","height_above_ellipsoid","height_raw","height_above_ground","height_above_ground_level"]
OUTLIER_FIELDS=("manually_marked_outlier","import_marked_outlier","algorithm_marked_outlier")
GAP_SECONDS=4*3600
MIN_SESSION=50
MIN_INDIVIDUALS=8
MIN_REPEAT=5


def canon(x):
    v=str(x).strip().lower().replace("-","_").replace(" ","_").replace(":","_")
    return re.sub(r"_+","_",v).strip("_")


def truthy(v):
    return str(v).strip().lower() in {"1","true","t","yes","y"}


def parse_time(v):
    return datetime.fromisoformat(str(v).strip().replace("Z","+00:00"))


def finite_xy(row):
    try:
        lon=float(row.get("location_long",""))
        lat=float(row.get("location_lat",""))
    except (TypeError,ValueError):
        return False
    return math.isfinite(lon) and math.isfinite(lat)


def individual(row):
    return str(
        row.get("individual_local_identifier")
        or row.get("animal_id")
        or row.get("individual_id")
        or row.get("tag_local_identifier")
        or ""
    ).strip()


def source_outlier(row, explicit_present):
    if explicit_present:
        return any(truthy(row.get(f,"")) for f in OUTLIER_FIELDS if f in row)
    if "visible" in row and str(row.get("visible","")).strip():
        return not truthy(row.get("visible",""))
    return False


def download(spec):
    req=urllib.request.Request(spec["content_url"],headers={"User-Agent":"batter-bat-panel-structural-screen-v1/1.0"})
    with urllib.request.urlopen(req,timeout=240) as r:
        data=r.read()
    if len(data)!=int(spec["size_bytes"]):
        raise RuntimeError(f"size mismatch {len(data)} != {spec['size_bytes']}")
    if hashlib.md5(data).hexdigest()!=str(spec["checksum"]):
        raise RuntimeError("MD5 mismatch")
    return data


def split_sessions(times):
    times=sorted(times)
    counts=[]
    current=0
    prev=None
    for t in times:
        if prev is not None and (t-prev).total_seconds()>GAP_SECONDS:
            if current:
                counts.append(current)
            current=0
        current+=1
        prev=t
    if current:
        counts.append(current)
    return counts


def screen(spec):
    data=download(spec)
    text=data.decode("utf-8-sig",errors="replace")
    reader=csv.DictReader(io.StringIO(text,newline=""))
    original_headers=list(reader.fieldnames or [])
    headers=[canon(h) for h in original_headers]
    if len(set(headers))!=len(headers):
        raise RuntimeError("header canonicalization collision")

    height=next((h for h in HEIGHT_PRIORITY if h in headers),None)
    explicit_present=any(h in headers for h in OUTLIER_FIELDS)

    row_count=0
    excluded_outliers=0
    usable_presence=0
    times=defaultdict(list)
    taxon_counts=Counter()

    for raw in reader:
        row_count+=1
        row={canon(k):("" if v is None else str(v)) for k,v in raw.items() if k is not None}

        if source_outlier(row,explicit_present):
            excluded_outliers+=1
            continue
        if height is None:
            continue

        iid=individual(row)
        if not iid or not finite_xy(row):
            continue

        # IMPORTANT: height is only checked as a non-empty string here.
        # Its numeric value is never parsed in this structural screen.
        if not str(row.get(height,"")).strip():
            continue

        try:
            t=parse_time(row.get("timestamp",""))
        except Exception:
            continue

        usable_presence+=1
        times[iid].append(t)
        taxon=str(
            row.get("individual_taxon_canonical_name")
            or row.get("animal_taxon")
            or row.get("taxon_canonical_name")
            or ""
        ).strip()
        if taxon:
            taxon_counts[taxon]+=1

    structure={}
    repeat=[]
    for iid,vals in sorted(times.items()):
        blocks=split_sessions(vals)
        eligible=[n for n in blocks if n>=MIN_SESSION]
        structure[iid]={
            "event_count":len(vals),
            "block_counts":blocks,
            "eligible_session_counts":eligible,
            "eligible_session_count":len(eligible),
        }
        if len(eligible)>=2:
            repeat.append(iid)

    passes=(
        height is not None
        and len(times)>=MIN_INDIVIDUALS
        and len(repeat)>=MIN_REPEAT
    )

    return {
        "doi":spec["doi"],
        "title":spec["title"],
        "bitstream_id":spec["bitstream_id"],
        "filename":spec["filename"],
        "size_bytes":len(data),
        "checksum":spec["checksum"],
        "row_count":row_count,
        "headers":headers,
        "native_height_field":height,
        "numeric_height_values_parsed":False,
        "source_outlier_rows_excluded":excluded_outliers,
        "xy_height_presence_event_count":usable_presence,
        "individual_count":len(times),
        "repeat_individual_count":len(repeat),
        "repeat_individual_ids":repeat,
        "taxon_presence_counts":dict(taxon_counts),
        "session_structure":structure,
        "passes_gate":passes,
        "status":"passes_gate" if passes else (
            "no_native_height_field" if height is None else "fails_replication_structure"
        ),
    }


def main():
    cfg=json.loads(CONFIG.read_text(encoding="utf-8"))
    results=[]
    for spec in cfg["sources"]:
        try:
            results.append(screen(spec))
        except Exception as exc:
            results.append({
                "doi":spec["doi"],
                "title":spec["title"],
                "bitstream_id":spec["bitstream_id"],
                "filename":spec["filename"],
                "status":"transport_or_schema_failure",
                "reason":f"{type(exc).__name__}: {exc}",
                "numeric_height_values_parsed":False,
                "passes_gate":False,
            })

    passing=[r for r in results if r.get("passes_gate")]
    payload={
        "screen_id":"batter-bat-panel-structural-screen-v1",
        "source_config_inventory_boundary":cfg["inventory_boundary_commit"],
        "source_count":len(cfg["sources"]),
        "results":results,
        "passing_source_count":len(passing),
        "passing_sources":[{
            "doi":r["doi"],
            "title":r["title"],
            "native_height_field":r["native_height_field"],
            "row_count":r["row_count"],
            "individual_count":r["individual_count"],
            "repeat_individual_count":r["repeat_individual_count"],
            "taxon_presence_counts":r["taxon_presence_counts"],
        } for r in passing],
        "numeric_height_values_parsed":False,
    }
    out=Path("results/bat_panel_structural_screen_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "source_count":payload["source_count"],
        "passing_source_count":payload["passing_source_count"],
        "passing_sources":payload["passing_sources"],
        "all_results":[{
            k:r.get(k) for k in [
                "doi","title","status","native_height_field","row_count",
                "individual_count","repeat_individual_count","passes_gate","reason"
            ]
        } for r in results],
        "numeric_height_values_parsed":False,
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
