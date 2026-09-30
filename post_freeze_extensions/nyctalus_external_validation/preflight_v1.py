#!/usr/bin/env python3
from __future__ import annotations

import hashlib, io, json, math, sys
from collections import defaultdict
from pathlib import Path
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
CONTRACT=ROOT/"post_freeze_extensions/nyctalus_external_validation/preflight_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/nyctalus_external_validation/preflight_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/nyctalus_external_validation/PREFLIGHT_RESULT_V1.md"
HEADERS={"User-Agent":"batter-nyctalus-validation-preflight-v1/1.0"}

def present(s):
    x=s.notna()
    txt=s.astype(str).str.strip()
    x &= txt.ne("")
    x &= ~txt.str.lower().isin({"na","nan","null","none"})
    return x

def fetch_source(c):
    meta=requests.get(f"https://zenodo.org/api/records/{c['source']['record_id']}",headers=HEADERS,timeout=90)
    meta.raise_for_status()
    j=meta.json()
    target=None
    for f in j.get("files",[]):
        if (f.get("key") or f.get("filename"))==c["source"]["file"]:
            target=f
            break
    if target is None:
        raise RuntimeError("source file missing")
    url=(target.get("links") or {}).get("content") or (target.get("links") or {}).get("self")
    r=requests.get(url,headers=HEADERS,timeout=180)
    r.raise_for_status()
    data=r.content
    sha=hashlib.sha256(data).hexdigest()
    if sha!=c["source"]["sha256"]:
        raise RuntimeError(f"sha mismatch {sha}")
    return data,sha

def base_rows(df):
    req=["bat_id","trackid","utc","x","y","Height","Year","field_period","move_state"]
    missing=[x for x in req if x not in df.columns]
    if missing:
        raise RuntimeError(f"missing columns {missing}")
    mask=pd.Series(True,index=df.index)
    for col in ["bat_id","trackid","utc","x","y","Height","Year","field_period"]:
        mask &= present(df[col])
    d=df.loc[mask,req].copy()
    # Numeric conversion is permitted only for x/y and time; Height remains unopened string.
    d["x_num"]=pd.to_numeric(d["x"],errors="coerce")
    d["y_num"]=pd.to_numeric(d["y"],errors="coerce")
    d["t"]=pd.to_datetime(d["utc"],errors="coerce",utc=True)
    d=d[d["x_num"].notna() & d["y_num"].notna() & d["t"].notna()].copy()
    d["bat_id"]=d["bat_id"].astype(str)
    d["trackid"]=d["trackid"].astype(str)
    d["cohort"]=d["Year"].astype(str).str.strip()+"::"+d["field_period"].astype(str).str.strip()
    d["move_state"]=d["move_state"].astype(str).str.strip()
    return d

def add_stratum(d,grid,state=False):
    x=(d["x_num"]/float(grid)).apply(math.floor).astype(int)
    y=(d["y_num"]/float(grid)).apply(math.floor).astype(int)
    out=d.copy()
    if state:
        out["stratum"]=list(zip(x,y,out["move_state"].astype(str)))
    else:
        out["stratum"]=list(zip(x,y))
    return out

def evaluate(d,grid,state=False,lag_days=None,min_events=50):
    q=d.copy()
    if state:
        q=q[q["move_state"].isin(["ARM","COM"])].copy()
    q=add_stratum(q,grid,state=state)

    by_track={}
    tracks_by_ind=defaultdict(list)
    tracks_by_cohort=defaultdict(list)
    for (cohort,tid),g in q.groupby(["cohort","trackid"],sort=True):
        bats=sorted(g["bat_id"].unique())
        if len(bats)!=1:
            raise RuntimeError(f"track {tid} in {cohort} maps to {bats}")
        iid=bats[0]
        med=g["t"].sort_values().iloc[len(g)//2]
        rec={
            "cohort":cohort,"trackid":tid,"bat_id":iid,
            "median_utc":med,
            "event_count":int(len(g)),
            "strata":set(g["stratum"].tolist()),
            "target_strata":g["stratum"].tolist()
        }
        by_track[(cohort,tid)]=rec
        tracks_by_ind[(cohort,iid)].append((cohort,tid))
        tracks_by_cohort[cohort].append((cohort,tid))

    eligible_tracks=[]
    session_rows=[]
    for key,rec in sorted(by_track.items()):
        cohort=rec["cohort"];iid=rec["bat_id"]
        target_time=rec["median_utc"]
        self_keys=[]
        for k in tracks_by_ind[(cohort,iid)]:
            if k==key:
                continue
            if lag_days is not None:
                dt=abs((by_track[k]["median_utc"]-target_time).total_seconds())/86400.0
                if dt<float(lag_days):
                    continue
            self_keys.append(k)
        other_keys=[k for k in tracks_by_cohort[cohort] if by_track[k]["bat_id"]!=iid]
        if not self_keys:
            session_rows.append({"cohort":cohort,"trackid":rec["trackid"],"bat_id":iid,"evaluable":False,"supported_events":0,"reason":"no_self_history"})
            continue
        if not other_keys:
            session_rows.append({"cohort":cohort,"trackid":rec["trackid"],"bat_id":iid,"evaluable":False,"supported_events":0,"reason":"no_other_individual"})
            continue
        self_support=set().union(*(by_track[k]["strata"] for k in self_keys))
        other_support=set().union(*(by_track[k]["strata"] for k in other_keys))
        supported=sum(s in self_support and s in other_support for s in rec["target_strata"])
        ok=supported>=int(min_events)
        if ok:
            eligible_tracks.append(key)
        session_rows.append({
            "cohort":cohort,"trackid":rec["trackid"],"bat_id":iid,
            "target_events":rec["event_count"],"self_history_tracks":len(self_keys),
            "other_tracks":len(other_keys),"supported_events":int(supported),
            "support_fraction":float(supported/rec["event_count"]) if rec["event_count"] else None,
            "evaluable":bool(ok),"reason":"eligible" if ok else "insufficient_common_support"
        })

    eligible_ids=sorted({by_track[k]["bat_id"] for k in eligible_tracks})
    cohort_stats={}
    for cohort in sorted(tracks_by_cohort):
        ids=sorted({r["bat_id"] for r in session_rows if r["cohort"]==cohort and r["evaluable"]})
        cohort_stats[cohort]={
            "eligible_individuals":len(ids),
            "eligible_individual_ids":ids,
            "eligible_tracks":sum(1 for r in session_rows if r["cohort"]==cohort and r["evaluable"])
        }
    return {
        "grid_m":int(grid),
        "state_conditioned":bool(state),
        "minimum_self_lag_days":lag_days,
        "event_count_after_nonvertical_filters":int(len(q)),
        "track_count":int(len(by_track)),
        "eligible_track_count":len(eligible_tracks),
        "eligible_individual_count":len(eligible_ids),
        "eligible_individual_ids":eligible_ids,
        "cohort_stats":cohort_stats,
        "track_support":session_rows
    }

def main():
    c=json.loads(CONTRACT.read_text())
    data,sha=fetch_source(c)
    df=pd.read_csv(io.BytesIO(data),dtype=str,low_memory=False)
    d=base_rows(df)
    min_events=int(c["primary_structure"]["minimum_supported_target_events"])

    primary=evaluate(d,5000,state=False,min_events=min_events)
    state5=evaluate(d,5000,state=True,min_events=min_events)
    state500=evaluate(d,500,state=True,min_events=min_events)
    lag1=evaluate(d,5000,state=True,lag_days=1,min_events=min_events)

    n_primary=primary["eligible_individual_count"]
    req_primary=8
    req_state=max(5,math.ceil(0.70*n_primary))
    n_state=state5["eligible_individual_count"]
    req_state500=max(5,math.ceil(0.70*n_state))
    req_lag=max(5,math.ceil(0.70*n_state))

    gates={
        "primary_5km":{"required_n":req_primary,"observed_n":n_primary,"pass":n_primary>=req_primary},
        "state_5km":{"required_n":req_state,"observed_n":n_state,"pass":n_state>=req_state},
        "state_500m":{"required_n":req_state500,"observed_n":state500["eligible_individual_count"],"pass":state500["eligible_individual_count"]>=req_state500},
        "persistence_1d":{"required_n":req_lag,"observed_n":lag1["eligible_individual_count"],"pass":lag1["eligible_individual_count"]>=req_lag}
    }

    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "source_sha256":sha,
        "numeric_height_values_read":False,
        "cohort_definition":c["cohort_definition"],
        "base_row_count":int(len(d)),
        "primary_5km":primary,
        "state_5km":state5,
        "state_500m":state500,
        "persistence_1d":lag1,
        "gates":gates,
        "passing_stages":[k for k,v in gates.items() if v["pass"]]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    lines=[
        "# Nyctalus independent-validation structural preflight v1","",
        "**OUTCOME-BLIND: numeric Height magnitudes were never parsed.**","",
        "| stage | eligible individuals | required | gate |",
        "|---|---:|---:|---|"
    ]
    for k,v in gates.items():
        lines.append(f"| {k} | {v['observed_n']} | {v['required_n']} | **{'PASS' if v['pass'] else 'FAIL'}** |")
    lines += ["","## Cohort definition","",f"`{c['cohort_definition']}`",""]
    OUT_MD.write_text("\n".join(lines),encoding="utf-8")

    print(json.dumps({
        "gates":gates,
        "passing_stages":payload["passing_stages"],
        "cohort_primary":primary["cohort_stats"],
        "cohort_state":state5["cohort_stats"],
        "cohort_500m":state500["cohort_stats"],
        "cohort_lag1d":lag1["cohort_stats"],
        "sha256":sha
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
