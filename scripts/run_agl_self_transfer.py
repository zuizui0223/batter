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


def download():
    req=urllib.request.Request(URL,headers={"User-Agent":"batter-agl-self-transfer-v1/1.0"})
    with urllib.request.urlopen(req,timeout=120) as response:
        return response.read()


def parse_time(value):
    text=str(value).strip().replace("Z","+00:00")
    return datetime.fromisoformat(text)


def finite_float(value):
    try:
        x=float(value)
    except (TypeError,ValueError):
        return None
    return x if math.isfinite(x) else None


def make_events(rows, cell_size_m):
    transformer=Transformer.from_crs("EPSG:4326","EPSG:3035",always_xy=True)
    parsed=[]
    counts=defaultdict(int)
    finite_agl=0
    for row in rows:
        individual=str(row.get("animal-id","")).strip()
        batday=str(row.get("BatDay","")).strip()
        lon=finite_float(row.get("location-long"))
        lat=finite_float(row.get("location-lat"))
        agl=finite_float(row.get("height_true"))
        if not individual or not batday or lon is None or lat is None or agl is None:
            continue
        try:
            timestamp=parse_time(row.get("timestamp",""))
        except Exception:
            continue
        finite_agl+=1
        x,y=transformer.transform(lon,lat)
        session=f"{individual}::{batday}"
        counts[session]+=1
        parsed.append((individual,timestamp,(math.floor(x/cell_size_m),math.floor(y/cell_size_m)),z_bin(agl,edges=EDGES),session))

    retained={s for s,n in counts.items() if n>=50}
    events=[
        Event(individual=i,timestamp=t,cell=c,zbin=z,session=s)
        for i,t,c,z,s in parsed if s in retained
    ]
    return events,{
        "finite_agl_xy_rows":finite_agl,
        "retained_session_count":len(retained),
        "retained_sessions":dict(sorted((s,counts[s]) for s in retained)),
        "individual_count":len({e.individual for e in events}),
    }


def compact(result):
    d=result["decomposition"]
    return {
        "eligible_individual_count":result["eligible_individual_count"],
        "equal_individual_mean_conditional_identity_gain_nats_per_fix":
            d["equal_individual_mean_conditional_identity_gain_nats_per_fix"],
        "equal_individual_mean_marginal_identity_gain_nats_per_fix":
            d["equal_individual_mean_marginal_identity_gain_nats_per_fix"],
        "equal_individual_mean_identity_x_location_gain_nats_per_fix":
            d["equal_individual_mean_identity_x_location_gain_nats_per_fix"],
        "positive_individual_fraction":result["positive_individual_fraction"],
        "individual_results":result["individual_results"],
    }


def analyze(rows,cell_size_m):
    events,qc=make_events(rows,cell_size_m)
    result=leave_one_session_out(
        events,
        alpha=0.5,
        minimum_scored_fixes=50,
        n_z_bins=len(EDGES)-1,
    )
    return {"qc":qc,"analysis":result}


def main():
    data=download()
    if len(data)!=EXPECTED_SIZE:
        raise RuntimeError(f"source size mismatch {len(data)} != {EXPECTED_SIZE}")
    digest=hashlib.md5(data).hexdigest()
    if digest!=EXPECTED_MD5:
        raise RuntimeError(f"source md5 mismatch {digest}")
    rows=list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"),newline="")))
    if len(rows)!=9873:
        raise RuntimeError(f"row count mismatch {len(rows)}")

    primary=analyze(rows,5000.0)
    sens_2500=analyze(rows,2500.0)
    sens_10000=analyze(rows,10000.0)

    payload={
        "study_id":"batter-agl-self-transfer-v1",
        "source":{"bytes":len(data),"md5":digest,"rows":len(rows)},
        "primary_5000_m":primary,
        "sensitivities":{
            "grid_2500_m":compact(sens_2500["analysis"]),
            "grid_10000_m":compact(sens_10000["analysis"]),
        },
        "primary_summary":compact(primary["analysis"]),
        "claim_boundary":{
            "vertical_axis_is_agl":True,
            "foraging_not_verified":True,
            "individual_is_summary_unit":True,
            "uplift_reaction_norm_result_not_reopened":True,
        },
    }
    out=Path("results/agl_self_transfer_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "source":payload["source"],
        "primary_qc":primary["qc"],
        "primary_summary":payload["primary_summary"],
        "sensitivities":payload["sensitivities"],
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
