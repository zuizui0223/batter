#!/usr/bin/env python3
from __future__ import annotations

import hashlib, io, json, math
from collections import defaultdict
from pathlib import Path

import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
CONTRACT=ROOT/"post_freeze_extensions/nyctalus_central_place/structural_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/nyctalus_central_place/structural_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/nyctalus_central_place/STRUCTURAL_RESULT_V1.md"
UA={"User-Agent":"batter-nyctalus-central-place-preflight-v1/1.0"}

def present(s):
    txt=s.astype(str).str.strip()
    return s.notna() & txt.ne("") & ~txt.str.lower().isin({"na","nan","null","none"})

def fetch(c):
    meta=requests.get(f"https://zenodo.org/api/records/{c['source']['record_id']}",headers=UA,timeout=90)
    meta.raise_for_status()
    rec=meta.json()
    target=None
    for f in rec.get("files",[]):
        if (f.get("key") or f.get("filename"))==c["source"]["file"]:
            target=f;break
    if target is None:
        raise RuntimeError("source file missing")
    url=(target.get("links") or {}).get("content") or (target.get("links") or {}).get("self")
    r=requests.get(url,headers=UA,timeout=180)
    r.raise_for_status()
    raw=r.content
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=c["source"]["sha256"]:
        raise RuntimeError(f"source SHA mismatch: {sha}")
    return pd.read_csv(io.BytesIO(raw),dtype=str,low_memory=False),sha

def parse_bins(vals):
    out=[]
    for x in vals:
        if x=="inf":
            out.append(math.inf)
        else:
            out.append(float(x))
    return out

def bin_index(x,edges):
    for i in range(len(edges)-1):
        if edges[i] <= x < edges[i+1]:
            return i
    return len(edges)-2

def evaluate(d,edges,min_events):
    q=d[d["move_state"].isin(["ARM","COM"])].copy()
    q["cx"]=(q["x_num"]/5000.0).apply(math.floor).astype(int)
    q["cy"]=(q["y_num"]/5000.0).apply(math.floor).astype(int)
    q["dbin"]=[bin_index(float(x),edges) for x in q["dist_start_num"]]
    q["stratum"]=list(zip(q["cx"],q["cy"],q["move_state"].astype(str),q["dbin"]))

    by_track={}
    tracks_by_ind=defaultdict(list)
    tracks_by_cohort=defaultdict(list)
    for (cohort,tid),g in q.groupby(["cohort","trackid"],sort=True):
        bats=sorted(g["bat_id"].unique())
        if len(bats)!=1:
            raise RuntimeError(f"track {tid} maps to {bats}")
        iid=bats[0]
        rec={
            "cohort":cohort,
            "trackid":tid,
            "bat_id":iid,
            "strata":set(g["stratum"].tolist()),
            "target_strata":g["stratum"].tolist(),
            "event_count":int(len(g))
        }
        key=(cohort,tid)
        by_track[key]=rec
        tracks_by_ind[(cohort,iid)].append(key)
        tracks_by_cohort[cohort].append(key)

    rows=[]
    eligible_ids=set()
    for key,rec in sorted(by_track.items()):
        cohort=rec["cohort"]; iid=rec["bat_id"]
        self_keys=[k for k in tracks_by_ind[(cohort,iid)] if k!=key]
        other_keys=[k for k in tracks_by_cohort[cohort] if by_track[k]["bat_id"]!=iid]
        if not self_keys or not other_keys:
            rows.append({"cohort":cohort,"trackid":rec["trackid"],"bat_id":iid,"supported_events":0,"evaluable":False})
            continue
        self_support=set().union(*(by_track[k]["strata"] for k in self_keys))
        other_support=set().union(*(by_track[k]["strata"] for k in other_keys))
        supported=sum(s in self_support and s in other_support for s in rec["target_strata"])
        ok=supported>=min_events
        if ok:
            eligible_ids.add(iid)
        rows.append({
            "cohort":cohort,"trackid":rec["trackid"],"bat_id":iid,
            "target_events":rec["event_count"],
            "supported_events":int(supported),
            "evaluable":bool(ok)
        })

    cohort_stats={}
    for cohort in sorted(tracks_by_cohort):
        ids=sorted({r["bat_id"] for r in rows if r["cohort"]==cohort and r["evaluable"]})
        cohort_stats[cohort]={
            "eligible_individuals":len(ids),
            "eligible_ids":ids,
            "eligible_tracks":sum(1 for r in rows if r["cohort"]==cohort and r["evaluable"])
        }
    return {
        "eligible_individual_count":len(eligible_ids),
        "eligible_individual_ids":sorted(eligible_ids),
        "eligible_track_count":sum(1 for r in rows if r["evaluable"]),
        "cohort_stats":cohort_stats,
        "track_support":rows
    }

def main():
    c=json.loads(CONTRACT.read_text())
    df,sha=fetch(c)
    req=["bat_id","trackid","x","y","dist_start","move_state","Year","field_period","Height"]
    missing=[x for x in req if x not in df.columns]
    if missing:
        raise RuntimeError(f"missing fields: {missing}")
    mask=pd.Series(True,index=df.index)
    for col in ["bat_id","trackid","x","y","dist_start","Year","field_period","Height"]:
        mask &= present(df[col])
    d=df.loc[mask,req].copy()

    # Parse only nonvertical fields. Height remains unopened string.
    d["x_num"]=pd.to_numeric(d["x"],errors="coerce")
    d["y_num"]=pd.to_numeric(d["y"],errors="coerce")
    d["dist_start_num"]=pd.to_numeric(d["dist_start"],errors="coerce")
    if d[["x_num","y_num","dist_start_num"]].isna().any().any():
        raise RuntimeError("nonvertical numeric parse failure")
    d["bat_id"]=d["bat_id"].astype(str)
    d["trackid"]=d["trackid"].astype(str)
    d["move_state"]=d["move_state"].astype(str).str.strip()
    d["cohort"]=d["Year"].astype(str).str.strip()+"::"+d["field_period"].astype(str).str.strip()

    min_events=int(c["fixed_nonvertical_context"]["minimum_supported_target_events"])
    results={}
    for name,vals in c["candidate_distance_bins_km"].items():
        edges=parse_bins(vals)
        results[name]={
            "edges_km":vals,
            **evaluate(d,edges,min_events)
        }

    required=int(c["selection_rule"]["required_n"])
    order=["near_mid_far","near_intermediate","near_only"]
    selected=None
    for name in order:
        if results[name]["eligible_individual_count"]>=required:
            selected=name
            break

    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "source_sha256":sha,
        "numeric_height_values_read":False,
        "rows_presence_qualified":int(len(d)),
        "candidate_results":results,
        "required_n":required,
        "selected_binset":selected,
        "vertical_test_may_open":selected is not None,
        "decision":(
            f"PASS: freeze {selected} distance bins for one paired support-matched vertical attribution test"
            if selected else
            "STRUCTURAL STOP: no candidate retains required support; do not open vertical outcome"
        ),
        "claim_boundary":c["claim_boundary"]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    lines=[
        "# Nyctalus central-place structural preflight v1","",
        "**Numeric Height values were never parsed.**","",
        f"Required evaluable individuals: **{required}** (70% of the existing state-5km n=27, rounded up).","",
        "| candidate | distance bins (km) | evaluable individuals | eligible tracks | gate |",
        "|---|---|---:|---:|---|"
    ]
    for name in ["near_only","near_intermediate","near_mid_far"]:
        x=results[name]
        lines.append(f"| {name} | {x['edges_km']} | {x['eligible_individual_count']} | {x['eligible_track_count']} | {'PASS' if x['eligible_individual_count']>=required else 'FAIL'} |")
    lines += ["",f"Selected binset: **{selected if selected else 'NONE / STOP'}**","",payload["decision"],""]
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps({
        "required_n":required,
        "candidate_n":{k:v["eligible_individual_count"] for k,v in results.items()},
        "selected_binset":selected,
        "vertical_test_may_open":selected is not None
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
