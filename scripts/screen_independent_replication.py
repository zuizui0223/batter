#!/usr/bin/env python3
from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
import io
import json
import math
from pathlib import Path
import urllib.parse
import urllib.request

BASE="https://www.movebank.org/movebank/service/direct-read"
GPS_SENSOR=653
CANDIDATES=[
    {"study_id":404939825,"taxon":"Eidolon helvum","doi":"10.5441/001/1.k8n02jn8"},
    {"study_id":433126,"taxon":"Tadarida brasiliensis","doi":"10.5441/001/1.td71sn54"},
]
HEIGHT_PRIORITY=["height_above_msl","height_above_ellipsoid","height_raw"]
MIN_SESSION=50
GAP_SECONDS=4*3600
MIN_INDIVIDUALS=8
MIN_REPEAT=5


def fetch(params):
    url=BASE+"?"+urllib.parse.urlencode(params,doseq=True)
    req=urllib.request.Request(url,headers={"User-Agent":"batter-replication-screen-v1/1.0"})
    with urllib.request.urlopen(req,timeout=180) as r:
        data=r.read()
    if data.lstrip().lower().startswith(b"<html") or b"license terms:" in data[:1000].lower():
        raise RuntimeError("Movebank returned HTML/license gate")
    text=data.decode("utf-8-sig")
    reader=csv.DictReader(io.StringIO(text,newline=""))
    return list(reader)


def canon(name):
    return "_".join(str(name).strip().lower().replace("-","_").replace(" ","_").split("_"))


def parse_time(value):
    text=str(value).strip().replace("Z","+00:00")
    return datetime.fromisoformat(text)


def finite_xy(row):
    try:
        lon=float(row.get("location_long",""))
        lat=float(row.get("location_lat",""))
    except (TypeError,ValueError):
        return False
    return math.isfinite(lon) and math.isfinite(lat)


def individual(row):
    return str(row.get("individual_local_identifier") or row.get("individual_id") or "").strip()


def choose_height(attribute_names):
    for field in HEIGHT_PRIORITY:
        if field in attribute_names:
            return field
    return None


def screen(candidate):
    study_id=candidate["study_id"]
    study_rows=fetch({
        "entity_type":"study",
        "study_id":study_id,
        "attributes":"id,name,license_type,number_of_individuals,number_of_deployed_locations,sensor_type_ids"
    })
    if len(study_rows)!=1:
        raise RuntimeError(f"study metadata rows={len(study_rows)}")
    study={canon(k):v for k,v in study_rows[0].items() if k is not None}

    attrs=fetch({
        "entity_type":"study_attribute",
        "study_id":study_id,
        "sensor_type_id":GPS_SENSOR,
    })
    names=sorted({
        canon(r.get("short_name",""))
        for r in attrs
        if str(r.get("short_name","")).strip()
    })
    height=choose_height(set(names))
    if height is None:
        return {
            **candidate,
            "study_name":study.get("name"),
            "license_type":study.get("license_type"),
            "native_height_field":None,
            "status":"no_native_height_field",
            "passes":False,
            "numeric_height_values_parsed":False,
        }

    requested=[
        "timestamp","location_long","location_lat",
        "individual_local_identifier","individual_id",height
    ]
    raw=fetch({
        "entity_type":"event",
        "study_id":study_id,
        "sensor_type_id":GPS_SENSOR,
        "attributes":",".join(requested),
    })
    rows=[{canon(k):("" if v is None else str(v)) for k,v in r.items() if k is not None} for r in raw]

    eligible_events=defaultdict(list)
    events_xy_height=0
    for row in rows:
        iid=individual(row)
        if not iid or not finite_xy(row):
            continue
        # Presence only: do not parse the height value.
        if not str(row.get(height,"")).strip():
            continue
        try:
            t=parse_time(row.get("timestamp",""))
        except Exception:
            continue
        events_xy_height+=1
        eligible_events[iid].append(t)

    sessions_by_individual={}
    for iid,times in eligible_events.items():
        times=sorted(times)
        counts=[]
        current=0
        prev=None
        for t in times:
            if prev is not None and (t-prev).total_seconds()>GAP_SECONDS:
                counts.append(current)
                current=0
            current+=1
            prev=t
        if current:
            counts.append(current)
        eligible_counts=[n for n in counts if n>=MIN_SESSION]
        sessions_by_individual[iid]={
            "all_block_counts":counts,
            "eligible_session_counts":eligible_counts,
            "eligible_session_count":len(eligible_counts),
        }

    n_individuals=len(eligible_events)
    repeat_ids=sorted(iid for iid,v in sessions_by_individual.items() if v["eligible_session_count"]>=2)
    passes=n_individuals>=MIN_INDIVIDUALS and len(repeat_ids)>=MIN_REPEAT
    return {
        **candidate,
        "study_name":study.get("name"),
        "license_type":study.get("license_type"),
        "native_height_field":height,
        "event_row_count":len(rows),
        "xy_height_presence_event_count":events_xy_height,
        "individuals_with_xy_height_presence":n_individuals,
        "repeat_session_individual_count":len(repeat_ids),
        "repeat_session_individual_ids":repeat_ids,
        "session_structure":sessions_by_individual,
        "passes":passes,
        "status":"eligible" if passes else "fails_structural_gate",
        "numeric_height_values_parsed":False,
    }


def main():
    results=[]
    for candidate in CANDIDATES:
        try:
            results.append(screen(candidate))
        except Exception as exc:
            results.append({
                **candidate,
                "status":"transport_or_schema_failure",
                "reason":f"{type(exc).__name__}: {exc}",
                "passes":False,
                "numeric_height_values_parsed":False,
            })

    eligible=[r for r in results if r.get("passes")]
    selected=None
    if eligible:
        eligible=sorted(
            eligible,
            key=lambda r:(int(r["repeat_session_individual_count"]),int(r["event_row_count"])),
            reverse=True,
        )
        selected=eligible[0]["study_id"]

    payload={
        "screen_id":"batter-independent-bat-replication-screen-v1",
        "results":results,
        "selected_study_id":selected,
        "numeric_height_values_parsed":False,
    }
    out=Path("results/independent_replication_screen_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "selected_study_id":selected,
        "results":[{
            k:r.get(k) for k in [
                "study_id","taxon","study_name","license_type","native_height_field",
                "event_row_count","individuals_with_xy_height_presence",
                "repeat_session_individual_count","passes","status","reason"
            ]
        } for r in results],
        "numeric_height_values_parsed":False,
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
