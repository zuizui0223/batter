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

from batter.analysis import Event, conditional_profile, marginal_profile, z_bin

GPS_URL="https://datarepository.movebank.org/server/api/core/bitstreams/82b726a4-bc78-497a-81d9-a19844cb61fc/content"
GPS_SIZE=4497472
GPS_MD5="5f301a9e28c74d9b4823b6c5aa70cacf"
REF_URL="https://datarepository.movebank.org/server/api/core/bitstreams/245d9c8c-8d79-46b4-9f6f-fb4e2a4087e3/content"
REF_MD5="2d0a9de5564c0547657d8f83bdebce6d"
CONTRACT_BOUNDARY="41f93119036854d4181a073144c2e3ab1d780979"

HEIGHT_FIELD="height_above_ellipsoid"
EDGES=(-math.inf,0.0,50.0,100.0,200.0,400.0,800.0,1600.0,3200.0,math.inf)
GAP_SECONDS=4*3600
MIN_SESSION=50
MIN_COHORT_INDIVIDUALS=4
MIN_COHORT_REPEAT=3
MIN_SCORED=50
ALPHA=0.5
PRIMARY_CELL=5000.0
SENSITIVITY_CELLS=[2500.0,10000.0]

OUTLIER_FIELDS=("manually_marked_outlier","import_marked_outlier","algorithm_marked_outlier")


def get(url,md5,size=None):
    req=urllib.request.Request(url,headers={"User-Agent":"batter-eidolon-independent-replication-v1/1.0"})
    with urllib.request.urlopen(req,timeout=180) as r:
        data=r.read()
    if size is not None and len(data)!=size:
        raise RuntimeError(f"size mismatch {len(data)} != {size}")
    observed=hashlib.md5(data).hexdigest()
    if observed!=md5:
        raise RuntimeError(f"checksum mismatch {observed} != {md5}")
    return data


def canon(x):
    import re
    v=str(x).strip().lower().replace("-","_").replace(" ","_").replace(":","_")
    return re.sub(r"_+","_",v).strip("_")


def read_csv(data):
    reader=csv.DictReader(io.StringIO(data.decode("utf-8-sig"),newline=""))
    return [
        {canon(k):("" if v is None else str(v)) for k,v in row.items() if k is not None}
        for row in reader
    ]


def truthy(v):
    return str(v).strip().lower() in {"1","true","t","yes","y"}


def visible_true(v):
    return str(v).strip().lower() in {"1","true","t","yes","y"}


def source_outlier(row, explicit_outlier_fields_present):
    if explicit_outlier_fields_present:
        return any(truthy(row.get(f,"")) for f in OUTLIER_FIELDS if f in row)
    if "visible" in row and str(row.get("visible","")).strip():
        return not visible_true(row.get("visible",""))
    return False


def finite_float(v):
    try: x=float(v)
    except (TypeError,ValueError): return None
    return x if math.isfinite(x) else None


def parse_time(v):
    return datetime.fromisoformat(str(v).strip().replace("Z","+00:00"))


def iid(row):
    return str(row.get("individual_local_identifier") or row.get("animal_id") or row.get("individual_id") or "").strip()


def shifted_night(t):
    return (t-timedelta(hours=12)).date().isoformat()


def utm_epsg(lon,lat):
    zone=max(1,min(60,int((lon+180.0)//6.0)+1))
    return (32600 if lat>=0 else 32700)+zone


def mean_probs_by_session_or_individual(events, unit, k):
    return conditional_profile(events,unit=unit,alpha=ALPHA,k=k)


def build_pre_numeric(rows,refs):
    ref_by_id={}
    excluded_manipulated=set()
    for r in refs:
        animal=str(r.get("animal_id") or r.get("individual_local_identifier") or "").strip()
        if not animal: continue
        ref_by_id[animal]=r
        manipulation=str(r.get("manipulation_type","")).strip().lower()
        if manipulation not in {"","none"}:
            excluded_manipulated.add(animal)

    explicit_outlier_fields_present=any(any(f in r for f in OUTLIER_FIELDS) for r in rows[:100])
    candidates=defaultdict(list)
    excluded_outliers=0
    excluded_manipulated_rows=0

    for idx,row in enumerate(rows):
        individual=iid(row)
        if not individual or individual in excluded_manipulated:
            if individual in excluded_manipulated:
                excluded_manipulated_rows+=1
            continue
        if source_outlier(row,explicit_outlier_fields_present):
            excluded_outliers+=1
            continue
        lon=finite_float(row.get("location_long"))
        lat=finite_float(row.get("location_lat"))
        if lon is None or lat is None:
            continue
        if not str(row.get(HEIGHT_FIELD,"")).strip():
            continue
        try: t=parse_time(row.get("timestamp",""))
        except Exception: continue
        candidates[individual].append((idx,t,lon,lat))

    session_for_row={}
    session_meta={}
    eligible_sessions=[]
    for individual,vals in sorted(candidates.items()):
        vals=sorted(vals,key=lambda x:x[1])
        blocks=[]; current=[]; prev=None
        for item in vals:
            if prev is not None and (item[1]-prev).total_seconds()>GAP_SECONDS:
                if current: blocks.append(current)
                current=[]
            current.append(item); prev=item[1]
        if current: blocks.append(current)

        for sidx,block in enumerate(blocks,1):
            sid=f"{individual}::S{sidx}"
            nights=Counter(shifted_night(x[1]) for x in block)
            night=nights.most_common(1)[0][0]
            site=str(ref_by_id.get(individual,{}).get("study_site","")).strip()
            cohort=f"{site}::{night[:4]}" if site else None
            status="eligible" if len(block)>=MIN_SESSION and cohort else (
                "too_few_rows" if len(block)<MIN_SESSION else "missing_site"
            )
            meta={
                "individual":individual,"rows":len(block),"night_id":night,
                "study_site":site or None,"cohort":cohort,"status":status
            }
            session_meta[sid]=meta
            if status=="eligible":
                eligible_sessions.append(sid)
                for row_idx,*_ in block:
                    session_for_row[row_idx]=sid

    cohort_sessions=defaultdict(list)
    for sid in eligible_sessions:
        cohort_sessions[session_meta[sid]["cohort"]].append(sid)

    admitted=[]
    cohort_meta={}
    for cohort,sids in sorted(cohort_sessions.items()):
        individuals=sorted({session_meta[s]["individual"] for s in sids})
        counts=Counter(session_meta[s]["individual"] for s in sids)
        repeat=sorted(i for i,n in counts.items() if n>=2)
        ok=len(individuals)>=MIN_COHORT_INDIVIDUALS and len(repeat)>=MIN_COHORT_REPEAT
        cohort_meta[cohort]={
            "eligible_session_count":len(sids),
            "individual_count":len(individuals),
            "repeat_individual_count":len(repeat),
            "repeat_individuals":repeat,
            "admitted":ok,
        }
        if ok: admitted.append(cohort)

    # Projection is chosen from x-y only, before heights are numerically parsed.
    projections={}
    for cohort in admitted:
        sids=set(cohort_sessions[cohort])
        coords=[
            (lon,lat)
            for individual,vals in candidates.items()
            for idx,t,lon,lat in vals
            if session_for_row.get(idx) in sids
        ]
        lon_med=float(np.median([x[0] for x in coords]))
        lat_med=float(np.median([x[1] for x in coords]))
        projections[cohort]={
            "median_lon":lon_med,"median_lat":lat_med,
            "epsg":utm_epsg(lon_med,lat_med)
        }

    return {
        "ref_by_id":ref_by_id,
        "excluded_manipulated_individuals":sorted(excluded_manipulated),
        "excluded_manipulated_rows":excluded_manipulated_rows,
        "excluded_source_outlier_rows":excluded_outliers,
        "explicit_outlier_fields_present":explicit_outlier_fields_present,
        "session_for_row":session_for_row,
        "session_meta":session_meta,
        "cohort_meta":cohort_meta,
        "admitted_cohorts":admitted,
        "projections":projections,
    }


def build_events(rows,pre,cell_size):
    transformers={
        cohort:Transformer.from_crs("EPSG:4326",f"EPSG:{spec['epsg']}",always_xy=True)
        for cohort,spec in pre["projections"].items()
    }
    events_by_cohort=defaultdict(list)
    numeric_failures=0
    for idx,row in enumerate(rows):
        sid=pre["session_for_row"].get(idx)
        if sid is None: continue
        sm=pre["session_meta"][sid]
        cohort=sm["cohort"]
        if cohort not in pre["admitted_cohorts"]: continue
        h=finite_float(row.get(HEIGHT_FIELD))
        lon=finite_float(row.get("location_long")); lat=finite_float(row.get("location_lat"))
        if h is None or lon is None or lat is None:
            numeric_failures+=1; continue
        try: t=parse_time(row.get("timestamp",""))
        except Exception:
            numeric_failures+=1; continue
        x,y=transformers[cohort].transform(lon,lat)
        cell=(math.floor(x/cell_size),math.floor(y/cell_size))
        individual=sm["individual"]
        events_by_cohort[cohort].append(Event(individual,t,cell,z_bin(h,edges=EDGES),sid))
    return events_by_cohort,numeric_failures


def score_target(target,self_train,pop_train):
    k=len(EDGES)-1
    p_self=conditional_profile(self_train,unit="session",alpha=ALPHA,k=k)
    p_pop=conditional_profile(pop_train,unit="individual",alpha=ALPHA,k=k)
    m_self=marginal_profile(self_train,unit="session",alpha=ALPHA,k=k)
    m_pop=marginal_profile(pop_train,unit="individual",alpha=ALPHA,k=k)
    scored=[e for e in target if e.cell in p_self and e.cell in p_pop]
    if len(scored)<MIN_SCORED:
        return {"evaluable":False,"target_fixes":len(target),"scored_fixes":len(scored)}
    cond=[]; marg=[]
    for e in scored:
        cond.append(math.log(float(p_self[e.cell][e.zbin]))-math.log(float(p_pop[e.cell][e.zbin])))
        marg.append(math.log(float(m_self[e.zbin]))-math.log(float(m_pop[e.zbin])))
    cg=float(np.mean(cond)); mg=float(np.mean(marg))
    return {
        "evaluable":True,"target_fixes":len(target),"scored_fixes":len(scored),
        "coverage":len(scored)/len(target),
        "conditional_identity_gain":cg,
        "marginal_identity_gain":mg,
        "identity_x_location_increment":cg-mg,
    }


def analyze(rows,pre,cell_size):
    events_by_cohort,numeric_failures=build_events(rows,pre,cell_size)
    session_results=[]
    for cohort,events in sorted(events_by_cohort.items()):
        by_session=defaultdict(list); by_ind=defaultdict(list)
        for e in events:
            by_session[e.session].append(e); by_ind[e.individual].append(e)
        for sid,target in sorted(by_session.items()):
            individual=target[0].individual
            self_train=[e for e in by_ind[individual] if e.session!=sid]
            if not self_train:
                session_results.append({"cohort":cohort,"session":sid,"individual":individual,"evaluable":False,"reason":"no_other_self_session"})
                continue
            pop_train=[e for e in events if e.individual!=individual]
            if not pop_train:
                session_results.append({"cohort":cohort,"session":sid,"individual":individual,"evaluable":False,"reason":"no_cohort_population"})
                continue
            result=score_target(target,self_train,pop_train)
            result.update({"cohort":cohort,"session":sid,"individual":individual})
            session_results.append(result)

    per_individual={}
    for individual in sorted({r["individual"] for r in session_results}):
        vals=[r for r in session_results if r["individual"]==individual and r.get("evaluable")]
        cond=[r["conditional_identity_gain"] for r in vals]
        marg=[r["marginal_identity_gain"] for r in vals]
        inter=[r["identity_x_location_increment"] for r in vals]
        per_individual[individual]={
            "cohort":vals[0]["cohort"] if vals else None,
            "evaluable_sessions":len(vals),
            "mean_conditional_identity_gain":float(np.mean(cond)) if cond else None,
            "mean_marginal_identity_gain":float(np.mean(marg)) if marg else None,
            "mean_identity_x_location_increment":float(np.mean(inter)) if inter else None,
            "positive_conditional_session_fraction":float(np.mean(np.array(cond)>0)) if cond else None,
        }

    evaluable=[v for v in per_individual.values() if v["mean_conditional_identity_gain"] is not None]
    cond=[v["mean_conditional_identity_gain"] for v in evaluable]
    marg=[v["mean_marginal_identity_gain"] for v in evaluable]
    inter=[v["mean_identity_x_location_increment"] for v in evaluable]

    cohort_summaries={}
    for cohort in pre["admitted_cohorts"]:
        iv=[v for v in evaluable if v["cohort"]==cohort]
        cv=[v["mean_conditional_identity_gain"] for v in iv]
        mv=[v["mean_marginal_identity_gain"] for v in iv]
        xv=[v["mean_identity_x_location_increment"] for v in iv]
        cohort_summaries[cohort]={
            "evaluable_individual_count":len(iv),
            "mean_conditional_identity_gain":float(np.mean(cv)) if cv else None,
            "mean_marginal_identity_gain":float(np.mean(mv)) if mv else None,
            "mean_identity_x_location_increment":float(np.mean(xv)) if xv else None,
            "positive_conditional_individual_fraction":float(np.mean(np.array(cv)>0)) if cv else None,
        }

    summary={
        "cell_size_m":cell_size,
        "numeric_height_parse_failures":numeric_failures,
        "evaluable_individual_count":len(evaluable),
        "equal_individual_mean_conditional_identity_gain":float(np.mean(cond)) if cond else None,
        "equal_individual_mean_marginal_identity_gain":float(np.mean(marg)) if marg else None,
        "equal_individual_mean_identity_x_location_increment":float(np.mean(inter)) if inter else None,
        "positive_conditional_individual_fraction":float(np.mean(np.array(cond)>0)) if cond else None,
        "individual_results":per_individual,
        "cohort_summaries":cohort_summaries,
        "session_results":session_results,
    }
    return summary


def main():
    gps=get(GPS_URL,GPS_MD5,GPS_SIZE)
    ref=get(REF_URL,REF_MD5)
    rows=read_csv(gps); refs=read_csv(ref)

    pre=build_pre_numeric(rows,refs)
    if not pre["admitted_cohorts"]:
        raise RuntimeError("no admitted site-year cohorts under frozen structural rules")

    # Numeric height values are first parsed inside analyze(), after all cohort,
    # session, projection and exclusion choices above are fixed.
    primary=analyze(rows,pre,PRIMARY_CELL)
    sensitivities={str(int(cs)):analyze(rows,pre,cs) for cs in SENSITIVITY_CELLS}

    s=primary
    required={
        "minimum_evaluable_individuals":s["evaluable_individual_count"]>=15,
        "mean_conditional_positive":(s["equal_individual_mean_conditional_identity_gain"] or -math.inf)>0,
        "majority_individuals_positive":(s["positive_conditional_individual_fraction"] or 0)>0.5,
        "mean_identity_x_location_positive":(s["equal_individual_mean_identity_x_location_increment"] or -math.inf)>0,
        "conditional_exceeds_marginal":(
            s["equal_individual_mean_conditional_identity_gain"] is not None and
            s["equal_individual_mean_marginal_identity_gain"] is not None and
            s["equal_individual_mean_conditional_identity_gain"]>s["equal_individual_mean_marginal_identity_gain"]
        ),
    }
    replicated=all(required.values())

    serial_pre={
        k:v for k,v in pre.items()
        if k not in {"ref_by_id","session_for_row"}
    }
    payload={
        "study_id":"batter-eidolon-independent-replication-v1",
        "contract_boundary":CONTRACT_BOUNDARY,
        "source":{"gps_md5":GPS_MD5,"gps_rows":len(rows),"reference_md5":REF_MD5},
        "pre_numeric_structure":serial_pre,
        "numeric_height_opened":True,
        "primary":primary,
        "sensitivities":sensitivities,
        "replication_rule_checks":required,
        "replication_supported":replicated,
        "claim_boundary":{
            "height_is_ellipsoid_not_agl":True,
            "foraging_not_inferred":True,
            "site_year_population_baseline":True,
            "sensitivities_cannot_override_primary":True,
        }
    }
    out=Path("results/eidolon_independent_replication_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "admitted_cohorts":pre["admitted_cohorts"],
        "excluded_manipulated_individuals":pre["excluded_manipulated_individuals"],
        "excluded_source_outlier_rows":pre["excluded_source_outlier_rows"],
        "primary":{
          k:primary[k] for k in [
            "evaluable_individual_count",
            "equal_individual_mean_conditional_identity_gain",
            "equal_individual_mean_marginal_identity_gain",
            "equal_individual_mean_identity_x_location_increment",
            "positive_conditional_individual_fraction",
            "cohort_summaries"
          ]
        },
        "sensitivity_summaries":{
          k:{x:v[x] for x in [
            "evaluable_individual_count",
            "equal_individual_mean_conditional_identity_gain",
            "equal_individual_mean_marginal_identity_gain",
            "equal_individual_mean_identity_x_location_increment",
            "positive_conditional_individual_fraction"
          ]} for k,v in sensitivities.items()
        },
        "replication_rule_checks":required,
        "replication_supported":replicated,
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
