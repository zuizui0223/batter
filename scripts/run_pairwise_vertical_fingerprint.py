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
import re
import urllib.request

import numpy as np
from pyproj import Transformer

from batter.analysis import Event, conditional_profile, marginal_profile, z_bin

EDGES=(-math.inf,0.0,50.0,100.0,200.0,400.0,800.0,1600.0,3200.0,math.inf)
K=len(EDGES)-1
ALPHA=0.5
MIN_SESSION=50
MIN_SCORED=50
CELL_SIZE=5000.0

TAD_URL="https://datarepository.movebank.org/server/api/core/bitstreams/a6a6db33-0aca-4902-a58d-f32980c1a3e1/content"
TAD_SIZE=3630088
TAD_MD5="e0f6faedfd1f21bac222d9da430ea5d8"

EID_GPS_URL="https://datarepository.movebank.org/server/api/core/bitstreams/82b726a4-bc78-497a-81d9-a19844cb61fc/content"
EID_GPS_SIZE=4497472
EID_GPS_MD5="5f301a9e28c74d9b4823b6c5aa70cacf"
EID_REF_URL="https://datarepository.movebank.org/server/api/core/bitstreams/245d9c8c-8d79-46b4-9f6f-fb4e2a4087e3/content"
EID_REF_MD5="2d0a9de5564c0547657d8f83bdebce6d"

OUTLIER_FIELDS=("manually_marked_outlier","import_marked_outlier","algorithm_marked_outlier")
CANONICAL_TAD={"Bat8":"Bat8_3D6001852B9A7"}


def get(url,md5,size=None):
    req=urllib.request.Request(url,headers={"User-Agent":"batter-pairwise-vertical-fingerprint-v1/1.0"})
    with urllib.request.urlopen(req,timeout=180) as r: data=r.read()
    if size is not None and len(data)!=size: raise RuntimeError(f"size mismatch {len(data)} != {size}")
    obs=hashlib.md5(data).hexdigest()
    if obs!=md5: raise RuntimeError(f"checksum mismatch {obs} != {md5}")
    return data


def canon(x):
    v=str(x).strip().lower().replace("-","_").replace(" ","_").replace(":","_")
    return re.sub(r"_+","_",v).strip("_")


def read_csv(data):
    reader=csv.DictReader(io.StringIO(data.decode("utf-8-sig"),newline=""))
    return [{canon(k):("" if v is None else str(v)) for k,v in row.items() if k is not None} for row in reader]


def finite_float(v):
    try: x=float(v)
    except (TypeError,ValueError): return None
    return x if math.isfinite(x) else None


def parse_time(v):
    return datetime.fromisoformat(str(v).strip().replace("Z","+00:00"))


def truthy(v):
    return str(v).strip().lower() in {"1","true","t","yes","y"}


def pairwise_score(target,self_train,alternative_train):
    p_self=conditional_profile(self_train,unit="session",alpha=ALPHA,k=K)
    p_alt=conditional_profile(alternative_train,unit="session",alpha=ALPHA,k=K)
    m_self=marginal_profile(self_train,unit="session",alpha=ALPHA,k=K)
    m_alt=marginal_profile(alternative_train,unit="session",alpha=ALPHA,k=K)

    scored=[e for e in target if e.cell in p_self and e.cell in p_alt]
    if len(scored)<MIN_SCORED:
        return {
            "evaluable":False,
            "target_fixes":len(target),
            "scored_fixes":len(scored),
        }
    cond=[
        math.log(float(p_self[e.cell][e.zbin]))-
        math.log(float(p_alt[e.cell][e.zbin]))
        for e in scored
    ]
    marg=[
        math.log(float(m_self[e.zbin]))-
        math.log(float(m_alt[e.zbin]))
        for e in scored
    ]
    cg=float(np.mean(cond)); mg=float(np.mean(marg))
    return {
        "evaluable":True,
        "target_fixes":len(target),
        "scored_fixes":len(scored),
        "coverage":len(scored)/len(target),
        "conditional_gain":cg,
        "marginal_gain":mg,
        "identity_x_location_increment":cg-mg,
        "conditional_self_win":cg>0,
        "marginal_self_win":mg>0,
    }


def summarize_pairwise(events_by_cohort):
    pairs=[]
    for cohort,events in sorted(events_by_cohort.items()):
        by_session=defaultdict(list); by_ind=defaultdict(list)
        for e in events:
            by_session[e.session].append(e)
            by_ind[e.individual].append(e)
        for session,target in sorted(by_session.items()):
            iid=target[0].individual
            self_train=[e for e in by_ind[iid] if e.session!=session]
            if not self_train: continue
            for alt,alt_events in sorted(by_ind.items()):
                if alt==iid: continue
                scored=pairwise_score(target,self_train,alt_events)
                scored.update({
                    "cohort":cohort,
                    "target_session":session,
                    "target_individual":iid,
                    "alternative_individual":alt,
                })
                pairs.append(scored)

    session_results=[]
    keys=sorted({(r["cohort"],r["target_session"],r["target_individual"]) for r in pairs})
    for cohort,session,iid in keys:
        vals=[r for r in pairs if r["cohort"]==cohort and r["target_session"]==session and r["target_individual"]==iid and r.get("evaluable")]
        if not vals:
            session_results.append({"cohort":cohort,"session":session,"individual":iid,"evaluable":False,"evaluable_alternatives":0})
            continue
        cond=np.array([r["conditional_gain"] for r in vals],dtype=float)
        marg=np.array([r["marginal_gain"] for r in vals],dtype=float)
        inter=np.array([r["identity_x_location_increment"] for r in vals],dtype=float)
        session_results.append({
            "cohort":cohort,
            "session":session,
            "individual":iid,
            "evaluable":True,
            "evaluable_alternatives":len(vals),
            "mean_conditional_pairwise_gain":float(cond.mean()),
            "conditional_self_win_fraction":float(np.mean(cond>0)),
            "mean_marginal_pairwise_gain":float(marg.mean()),
            "marginal_self_win_fraction":float(np.mean(marg>0)),
            "mean_identity_x_location_increment":float(inter.mean()),
        })

    individual_results={}
    for iid in sorted({r["individual"] for r in session_results}):
        vals=[r for r in session_results if r["individual"]==iid and r.get("evaluable")]
        if not vals:
            individual_results[iid]={
                "evaluable_sessions":0,
                "mean_conditional_pairwise_gain":None,
                "conditional_self_win_fraction":None,
                "mean_marginal_pairwise_gain":None,
                "marginal_self_win_fraction":None,
                "mean_identity_x_location_increment":None,
            }
            continue
        individual_results[iid]={
            "evaluable_sessions":len(vals),
            "mean_conditional_pairwise_gain":float(np.mean([v["mean_conditional_pairwise_gain"] for v in vals])),
            "conditional_self_win_fraction":float(np.mean([v["conditional_self_win_fraction"] for v in vals])),
            "mean_marginal_pairwise_gain":float(np.mean([v["mean_marginal_pairwise_gain"] for v in vals])),
            "marginal_self_win_fraction":float(np.mean([v["marginal_self_win_fraction"] for v in vals])),
            "mean_identity_x_location_increment":float(np.mean([v["mean_identity_x_location_increment"] for v in vals])),
        }

    eligible=[v for v in individual_results.values() if v["evaluable_sessions"]>0]
    def mean(field):
        vals=[v[field] for v in eligible if v[field] is not None]
        return float(np.mean(vals)) if vals else None
    return {
        "pair_results":pairs,
        "session_results":session_results,
        "individual_results":individual_results,
        "evaluable_individual_count":len(eligible),
        "equal_individual_mean_conditional_pairwise_gain":mean("mean_conditional_pairwise_gain"),
        "equal_individual_conditional_self_win_fraction":mean("conditional_self_win_fraction"),
        "equal_individual_mean_marginal_pairwise_gain":mean("mean_marginal_pairwise_gain"),
        "equal_individual_marginal_self_win_fraction":mean("marginal_self_win_fraction"),
        "equal_individual_mean_identity_x_location_increment":mean("mean_identity_x_location_increment"),
    }


def build_tadarida(rows,field):
    tr=Transformer.from_crs("EPSG:4326","EPSG:3035",always_xy=True)
    counts=Counter()
    parsed=[]
    for row in rows:
        raw_iid=str(row.get("animal_id","")).strip()
        iid=CANONICAL_TAD.get(raw_iid,raw_iid)
        day=str(row.get("batday","")).strip()
        lon=finite_float(row.get("location_long")); lat=finite_float(row.get("location_lat")); z=finite_float(row.get(field))
        if not iid or not day or lon is None or lat is None or z is None: continue
        try: t=parse_time(row.get("timestamp",""))
        except Exception: continue
        x,y=tr.transform(lon,lat)
        session=f"{iid}::{day}"
        counts[session]+=1
        parsed.append((iid,t,(math.floor(x/CELL_SIZE),math.floor(y/CELL_SIZE)),z_bin(z,edges=EDGES),session))
    retained={s for s,n in counts.items() if n>=MIN_SESSION}
    events=[Event(i,t,c,z,s) for i,t,c,z,s in parsed if s in retained]
    return {"tadarida":[*events]}


def shifted_night(t):
    return (t-timedelta(hours=12)).date().isoformat()


def utm_epsg(lon,lat):
    zone=max(1,min(60,int((lon+180.0)//6.0)+1))
    return (32600 if lat>=0 else 32700)+zone


def build_eidolon(rows,refs):
    ref_by={}
    excluded_manipulated=set()
    for r in refs:
        iid=str(r.get("animal_id") or r.get("individual_local_identifier") or "").strip()
        if not iid: continue
        ref_by[iid]=r
        manipulation=str(r.get("manipulation_type","")).strip().lower()
        if manipulation not in {"","none"}: excluded_manipulated.add(iid)

    explicit=any(any(f in r for f in OUTLIER_FIELDS) for r in rows[:100])
    candidates=defaultdict(list)
    for idx,row in enumerate(rows):
        iid=str(row.get("individual_local_identifier") or row.get("animal_id") or row.get("individual_id") or "").strip()
        if not iid or iid in excluded_manipulated: continue
        if explicit and any(truthy(row.get(f,"")) for f in OUTLIER_FIELDS if f in row): continue
        if not explicit and "visible" in row and str(row.get("visible","")).strip() and not truthy(row.get("visible","")): continue
        lon=finite_float(row.get("location_long")); lat=finite_float(row.get("location_lat"))
        if lon is None or lat is None or not str(row.get("height_above_ellipsoid","")).strip(): continue
        try: t=parse_time(row.get("timestamp",""))
        except Exception: continue
        candidates[iid].append((idx,t,lon,lat))

    session_for_row={}; session_meta={}; eligible=[]
    for iid,vals in sorted(candidates.items()):
        vals=sorted(vals,key=lambda x:x[1]); blocks=[]; cur=[]; prev=None
        for item in vals:
            if prev is not None and (item[1]-prev).total_seconds()>4*3600:
                if cur: blocks.append(cur)
                cur=[]
            cur.append(item); prev=item[1]
        if cur: blocks.append(cur)
        for sidx,block in enumerate(blocks,1):
            sid=f"{iid}::S{sidx}"
            night=Counter(shifted_night(x[1]) for x in block).most_common(1)[0][0]
            site=str(ref_by.get(iid,{}).get("study_site","")).strip()
            cohort=f"{site}::{night[:4]}" if site else None
            status="eligible" if len(block)>=MIN_SESSION and cohort else "excluded"
            session_meta[sid]={"individual":iid,"cohort":cohort,"rows":len(block),"status":status}
            if status=="eligible":
                eligible.append(sid)
                for idx,*_ in block: session_for_row[idx]=sid

    cohort_sids=defaultdict(list)
    for sid in eligible: cohort_sids[session_meta[sid]["cohort"]].append(sid)
    admitted=[]
    for cohort,sids in cohort_sids.items():
        ids={session_meta[s]["individual"] for s in sids}
        counts=Counter(session_meta[s]["individual"] for s in sids)
        repeats={i for i,n in counts.items() if n>=2}
        if len(ids)>=4 and len(repeats)>=3: admitted.append(cohort)

    projections={}
    for cohort in admitted:
        sids=set(cohort_sids[cohort])
        coords=[(lon,lat) for vals in candidates.values() for idx,t,lon,lat in vals if session_for_row.get(idx) in sids]
        lon=float(np.median([x for x,y in coords])); lat=float(np.median([y for x,y in coords]))
        projections[cohort]=Transformer.from_crs("EPSG:4326",f"EPSG:{utm_epsg(lon,lat)}",always_xy=True)

    events=defaultdict(list)
    for idx,row in enumerate(rows):
        sid=session_for_row.get(idx)
        if sid is None: continue
        meta=session_meta[sid]; cohort=meta["cohort"]
        if cohort not in admitted: continue
        h=finite_float(row.get("height_above_ellipsoid")); lon=finite_float(row.get("location_long")); lat=finite_float(row.get("location_lat"))
        if h is None or lon is None or lat is None: continue
        try: t=parse_time(row.get("timestamp",""))
        except Exception: continue
        x,y=projections[cohort].transform(lon,lat)
        events[cohort].append(Event(meta["individual"],t,(math.floor(x/CELL_SIZE),math.floor(y/CELL_SIZE)),z_bin(h,edges=EDGES),sid))
    return events


def compact(summary):
    return {k:v for k,v in summary.items() if k not in {"pair_results","session_results"}}


def main():
    tad_rows=read_csv(get(TAD_URL,TAD_MD5,TAD_SIZE))
    eid_rows=read_csv(get(EID_GPS_URL,EID_GPS_MD5,EID_GPS_SIZE))
    eid_refs=read_csv(get(EID_REF_URL,EID_REF_MD5))

    tad_agl=summarize_pairwise(build_tadarida(tad_rows,"height_true"))
    tad_msl=summarize_pairwise(build_tadarida(tad_rows,"height_above_msl"))
    eid=summarize_pairwise(build_eidolon(eid_rows,eid_refs))

    payload={
        "study_id":"batter-pairwise-vertical-fingerprint-v1",
        "results":{
            "tadarida_agl":tad_agl,
            "tadarida_msl":tad_msl,
            "eidolon_ellipsoid":eid,
        },
        "summary":{
            "tadarida_agl":compact(tad_agl),
            "tadarida_msl":compact(tad_msl),
            "eidolon_ellipsoid":compact(eid),
        },
        "claim_boundary":{"post_primary":True,"foraging_not_inferred":True}
    }
    out=Path("results/pairwise_vertical_fingerprint_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(payload["summary"],sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
