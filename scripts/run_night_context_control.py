#!/usr/bin/env python3
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import hashlib
import io
import json
import math
from pathlib import Path
import urllib.request

import numpy as np
from pyproj import Transformer

from batter.analysis import Event, conditional_profile, z_bin

URL="https://datarepository.movebank.org/server/api/core/bitstreams/a6a6db33-0aca-4902-a58d-f32980c1a3e1/content"
EXPECTED_SIZE=3630088
EXPECTED_MD5="e0f6faedfd1f21bac222d9da430ea5d8"
EDGES=(-math.inf,0.0,50.0,100.0,200.0,400.0,800.0,1600.0,3200.0,math.inf)
FIELDS={"agl":"height_true","msl":"height-above-msl"}
CELL_SIZE=5000.0
MIN_ROWS=50
MIN_NIGHT_PURITY=0.95
ALPHA=0.5

CANONICAL_ID={"Bat8":"Bat8_3D6001852B9A7"}


def get():
    req=urllib.request.Request(URL,headers={"User-Agent":"batter-night-context-control-v1/1.0"})
    with urllib.request.urlopen(req,timeout=120) as r:
        data=r.read()
    if len(data)!=EXPECTED_SIZE:
        raise RuntimeError(f"size mismatch {len(data)}")
    if hashlib.md5(data).hexdigest()!=EXPECTED_MD5:
        raise RuntimeError("checksum mismatch")
    return data


def finite_float(value):
    try:
        x=float(value)
    except (TypeError,ValueError):
        return None
    return x if math.isfinite(x) else None


def parse_time(value):
    return datetime.fromisoformat(str(value).strip().replace("Z","+00:00"))


def shifted_night(timestamp):
    return (timestamp - timedelta(hours=12)).date().isoformat()


def build_axis(rows,field):
    transformer=Transformer.from_crs("EPSG:4326","EPSG:3035",always_xy=True)
    raw=[]
    session_nights=defaultdict(Counter)
    session_counts=Counter()
    for row in rows:
        iid=CANONICAL_ID.get(str(row.get("animal-id","")).strip(),str(row.get("animal-id","")).strip())
        batday=str(row.get("BatDay","")).strip()
        lon=finite_float(row.get("location-long"))
        lat=finite_float(row.get("location-lat"))
        value=finite_float(row.get(field))
        if not iid or not batday or lon is None or lat is None or value is None:
            continue
        try:
            t=parse_time(row.get("timestamp",""))
        except Exception:
            continue
        x,y=transformer.transform(lon,lat)
        session=f"{iid}::{batday}"
        night=shifted_night(t)
        session_counts[session]+=1
        session_nights[session][night]+=1
        raw.append((iid,t,(math.floor(x/CELL_SIZE),math.floor(y/CELL_SIZE)),z_bin(value,edges=EDGES),session,night))

    session_meta={}
    retained=set()
    for session,n in session_counts.items():
        night,count=session_nights[session].most_common(1)[0]
        purity=count/n
        status="eligible" if n>=MIN_ROWS and purity>=MIN_NIGHT_PURITY else (
            "too_few_rows" if n<MIN_ROWS else "night_impure"
        )
        session_meta[session]={"rows":n,"night_id":night,"night_purity":purity,"status":status}
        if status=="eligible":
            retained.add(session)

    events=[]
    event_night={}
    for iid,t,cell,z,session,night in raw:
        if session not in retained:
            continue
        # Keep only rows assigned to the session's dominant shifted night.
        target_night=session_meta[session]["night_id"]
        if night!=target_night:
            continue
        e=Event(iid,t,cell,z,session)
        events.append(e)
        event_night[(iid,t,cell,z,session)]=target_night
    return events,session_meta


def score_axis(events,session_meta):
    by_session=defaultdict(list)
    by_individual=defaultdict(list)
    by_night=defaultdict(list)
    for e in events:
        by_session[e.session].append(e)
        by_individual[e.individual].append(e)
        night=session_meta[e.session]["night_id"]
        by_night[night].append(e)

    results=[]
    for session,target in sorted(by_session.items()):
        iid=target[0].individual
        night=session_meta[session]["night_id"]
        self_train=[e for e in by_individual[iid] if e.session!=session]
        if not self_train:
            results.append({"session":session,"individual":iid,"night_id":night,"evaluable":False,"reason":"no_other_self_session"})
            continue
        night_other=[e for e in by_night[night] if e.individual!=iid]
        night_other_ids=sorted({e.individual for e in night_other})
        if not night_other_ids:
            results.append({"session":session,"individual":iid,"night_id":night,"evaluable":False,"reason":"no_same_night_other_bat"})
            continue

        p_self=conditional_profile(self_train,unit="session",alpha=ALPHA,k=len(EDGES)-1)
        p_night=conditional_profile(night_other,unit="individual",alpha=ALPHA,k=len(EDGES)-1)
        supported=[e for e in target if e.cell in p_self and e.cell in p_night]
        if len(supported)<MIN_ROWS:
            results.append({
                "session":session,"individual":iid,"night_id":night,"evaluable":False,
                "reason":"insufficient_common_support","target_rows":len(target),"scored_rows":len(supported),
                "same_night_other_individuals":night_other_ids,
            })
            continue
        gains=[
            math.log(float(p_self[e.cell][e.zbin]))-math.log(float(p_night[e.cell][e.zbin]))
            for e in supported
        ]
        results.append({
            "session":session,"individual":iid,"night_id":night,"evaluable":True,
            "target_rows":len(target),"scored_rows":len(supported),
            "coverage":len(supported)/len(target),
            "same_night_other_individuals":night_other_ids,
            "same_night_other_individual_count":len(night_other_ids),
            "self_vs_same_night_gain_nats_per_fix":float(np.mean(gains)),
        })

    per_individual={}
    for iid in sorted(by_individual):
        vals=[
            r["self_vs_same_night_gain_nats_per_fix"] for r in results
            if r.get("individual")==iid and r.get("evaluable")
        ]
        per_individual[iid]={
            "evaluable_sessions":len(vals),
            "mean_gain_nats_per_fix":float(np.mean(vals)) if vals else None,
            "positive_session_fraction":float(np.mean(np.array(vals)>0)) if vals else None,
        }
    ivals=[v["mean_gain_nats_per_fix"] for v in per_individual.values() if v["mean_gain_nats_per_fix"] is not None]
    return {
        "session_results":results,
        "individual_results":per_individual,
        "eligible_individual_count":len(ivals),
        "equal_individual_mean_gain_nats_per_fix":float(np.mean(ivals)) if ivals else None,
        "positive_individual_fraction":float(np.mean(np.array(ivals)>0)) if ivals else None,
    }


def main():
    data=get()
    rows=list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"),newline="")))
    payload={
        "study_id":"batter-night-context-control-v1",
        "source":{"md5":EXPECTED_MD5,"rows":len(rows)},
        "results":{},
    }
    for axis,field in FIELDS.items():
        events,meta=build_axis(rows,field)
        payload["results"][axis]={
            "session_meta":meta,
            "analysis":score_axis(events,meta),
        }
    out=Path("results/night_context_control_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        axis:{
          "eligible_individual_count":value["analysis"]["eligible_individual_count"],
          "equal_individual_mean_gain_nats_per_fix":value["analysis"]["equal_individual_mean_gain_nats_per_fix"],
          "positive_individual_fraction":value["analysis"]["positive_individual_fraction"],
          "individual_results":value["analysis"]["individual_results"],
          "evaluable_sessions":[
            {k:r[k] for k in ("session","individual","night_id","scored_rows","same_night_other_individual_count","self_vs_same_night_gain_nats_per_fix")}
            for r in value["analysis"]["session_results"] if r.get("evaluable")
          ],
        } for axis,value in payload["results"].items()
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
