#!/usr/bin/env python3
from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
import hashlib
import io
import json
import math
from pathlib import Path
import urllib.request

from pyproj import Transformer

from batter.analysis import Event, leave_one_session_out, z_bin

URL = "https://datarepository.movebank.org/server/api/core/bitstreams/a6a6db33-0aca-4902-a58d-f32980c1a3e1/content"
EXPECTED_SIZE = 3630088
EXPECTED_MD5 = "e0f6faedfd1f21bac222d9da430ea5d8"
EDGES = (-math.inf,0.0,50.0,100.0,200.0,400.0,800.0,1600.0,3200.0,math.inf)
FIELDS = {
    "terrain":"height_terrain",
    "agl":"height_true",
    "msl":"height-above-msl",
}


def download():
    req=urllib.request.Request(URL,headers={"User-Agent":"batter-three-component-transfer-v1/1.0"})
    with urllib.request.urlopen(req,timeout=120) as response:
        return response.read()


def finite_float(value):
    try:
        x=float(value)
    except (TypeError,ValueError):
        return None
    return x if math.isfinite(x) else None


def parse_time(value):
    return datetime.fromisoformat(str(value).strip().replace("Z","+00:00"))


def make_events(rows, field, cell_size):
    transformer=Transformer.from_crs("EPSG:4326","EPSG:3035",always_xy=True)
    parsed=[]
    counts=defaultdict(int)
    for row in rows:
        individual=str(row.get("animal-id","")).strip()
        batday=str(row.get("BatDay","")).strip()
        lon=finite_float(row.get("location-long"))
        lat=finite_float(row.get("location-lat"))
        value=finite_float(row.get(field))
        if not individual or not batday or lon is None or lat is None or value is None:
            continue
        try:
            timestamp=parse_time(row.get("timestamp",""))
        except Exception:
            continue
        x,y=transformer.transform(lon,lat)
        session=f"{individual}::{batday}"
        counts[session]+=1
        parsed.append((individual,timestamp,(math.floor(x/cell_size),math.floor(y/cell_size)),z_bin(value,edges=EDGES),session))
    retained={s for s,n in counts.items() if n>=50}
    return [
        Event(individual=i,timestamp=t,cell=c,zbin=z,session=s)
        for i,t,c,z,s in parsed if s in retained
    ]


def compact(result):
    d=result["decomposition"]
    return {
        "eligible_individual_count":result["eligible_individual_count"],
        "conditional_identity_gain":d["equal_individual_mean_conditional_identity_gain_nats_per_fix"],
        "marginal_identity_gain":d["equal_individual_mean_marginal_identity_gain_nats_per_fix"],
        "identity_x_location_gain":d["equal_individual_mean_identity_x_location_gain_nats_per_fix"],
        "positive_individual_fraction":result["positive_individual_fraction"],
        "individual_results":result["individual_results"],
    }


def analyze(rows, field, cell_size):
    events=make_events(rows,field,cell_size)
    result=leave_one_session_out(events,alpha=0.5,minimum_scored_fixes=50,n_z_bins=len(EDGES)-1)
    return compact(result)


def main():
    data=download()
    if len(data)!=EXPECTED_SIZE:
        raise RuntimeError("source size mismatch")
    if hashlib.md5(data).hexdigest()!=EXPECTED_MD5:
        raise RuntimeError("source md5 mismatch")
    rows=list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"),newline="")))
    if len(rows)!=9873:
        raise RuntimeError(f"row count mismatch {len(rows)}")

    result={"study_id":"batter-three-component-transfer-v1","source_md5":EXPECTED_MD5,"results":{}}
    for scale_name,cell_size in [("5000_m",5000.0),("2500_m",2500.0)]:
        result["results"][scale_name]={}
        for axis,field in FIELDS.items():
            result["results"][scale_name][axis]=analyze(rows,field,cell_size)

    out=Path("results/three_component_transfer_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
