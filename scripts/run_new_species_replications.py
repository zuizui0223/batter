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

CONTRACTS=[
  Path("contract/hypsignathus_replication_v1.json"),
  Path("contract/phyllostomus_replication_v1.json"),
  Path("contract/phyllostomus_2023_replication_v1.json"),
]
OUTLIER_FIELDS=("manually_marked_outlier","import_marked_outlier","algorithm_marked_outlier")


def canon(x):
    v=str(x).strip().lower().replace("-","_").replace(" ","_").replace(":","_")
    return re.sub(r"_+","_",v).strip("_")


def get(spec, user_agent):
    req=urllib.request.Request(spec["url"],headers={"User-Agent":user_agent})
    with urllib.request.urlopen(req,timeout=240) as r:
        data=r.read()
    if len(data)!=int(spec["size_bytes"]):
        raise RuntimeError(f"size mismatch {len(data)} != {spec['size_bytes']}")
    observed=hashlib.md5(data).hexdigest()
    if observed!=spec["md5"]:
        raise RuntimeError(f"MD5 mismatch {observed} != {spec['md5']}")
    return data


def read_csv(data):
    reader=csv.DictReader(io.StringIO(data.decode("utf-8-sig",errors="replace"),newline=""))
    return [
      {canon(k):("" if v is None else str(v)) for k,v in row.items() if k is not None}
      for row in reader
    ], [canon(h) for h in reader.fieldnames or []]


def truthy(v):
    return str(v).strip().lower() in {"1","true","t","yes","y"}


def finite_float(v):
    try:
        x=float(v)
    except (TypeError,ValueError):
        return None
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


def source_outlier(row, explicit_present):
    if explicit_present:
        return any(truthy(row.get(f,"")) for f in OUTLIER_FIELDS if f in row)
    if "visible" in row and str(row.get("visible","")).strip():
        return not truthy(row.get("visible",""))
    return False


def reference_map(refs):
    grouped=defaultdict(list)
    for r in refs:
        animal=str(r.get("animal_id") or r.get("individual_local_identifier") or "").strip()
        if animal:
            grouped[animal].append(r)
    out={}
    for animal,rows in grouped.items():
        sites=sorted({str(r.get("study_site","")).strip() for r in rows if str(r.get("study_site","")).strip()})
        manip=[str(r.get("manipulation_type","")).strip().lower() for r in rows]
        out[animal]={
          "site":sites[0] if len(sites)==1 else None,
          "site_values":sites,
          "ambiguous_site":len(sites)>1,
          "manipulated":any(v not in {"","none"} for v in manip),
        }
    return out


def split_blocks(vals, gap_seconds):
    vals=sorted(vals,key=lambda x:x[1])
    blocks=[]
    current=[]
    prev=None
    for item in vals:
        if prev is not None and (item[1]-prev).total_seconds()>gap_seconds:
            if current:
                blocks.append(current)
            current=[]
        current.append(item)
        prev=item[1]
    if current:
        blocks.append(current)
    return blocks


def build_pre_numeric(rows,headers,refs,contract):
    refmap=reference_map(refs)
    height=contract["vertical"]["field"]
    explicit_present=any(f in headers for f in OUTLIER_FIELDS)
    min_session=int(contract["exclusions"]["session_minimum_events"])
    gap_seconds=4*3600

    candidates=defaultdict(list)
    excluded_outliers=0
    excluded_manipulated_rows=0
    missing_site_rows=0

    for idx,row in enumerate(rows):
        animal=iid(row)
        if not animal:
            continue
        ref=refmap.get(animal,{})
        if ref.get("manipulated"):
            excluded_manipulated_rows+=1
            continue
        if source_outlier(row,explicit_present):
            excluded_outliers+=1
            continue
        lon=finite_float(row.get("location_long"))
        lat=finite_float(row.get("location_lat"))
        if lon is None or lat is None:
            continue
        # Presence-only gate: numeric height remains unopened here.
        if not str(row.get(height,"")).strip():
            continue
        try:
            t=parse_time(row.get("timestamp",""))
        except Exception:
            continue
        site=ref.get("site")
        if not site:
            missing_site_rows+=1
            continue
        candidates[animal].append((idx,t,lon,lat,site))

    session_for_row={}
    session_meta={}
    eligible_sessions=[]
    for animal,vals in sorted(candidates.items()):
        blocks=split_blocks(vals,gap_seconds)
        for sidx,block in enumerate(blocks,1):
            sid=f"{animal}::S{sidx}"
            nights=Counter(shifted_night(x[1]) for x in block)
            night=nights.most_common(1)[0][0]
            site_values=sorted({x[4] for x in block})
            site=site_values[0] if len(site_values)==1 else None
            cohort=f"{site}::{night[:4]}" if site else None
            status="eligible" if len(block)>=min_session and cohort else (
              "too_few_rows" if len(block)<min_session else "ambiguous_or_missing_site"
            )
            session_meta[sid]={
              "individual":animal,"rows":len(block),"night_id":night,
              "study_site":site,"cohort":cohort,"status":status,
            }
            if status=="eligible":
                eligible_sessions.append(sid)
                for row_idx,*_ in block:
                    session_for_row[row_idx]=sid

    cohort_sessions=defaultdict(list)
    for sid in eligible_sessions:
        cohort_sessions[session_meta[sid]["cohort"]].append(sid)

    min_ind=int(contract["cohort"]["minimum_total_individuals"])
    min_repeat=int(contract["cohort"]["minimum_repeat_individuals"])
    admitted=[]
    cohort_meta={}
    for cohort,sids in sorted(cohort_sessions.items()):
        animals=sorted({session_meta[s]["individual"] for s in sids})
        counts=Counter(session_meta[s]["individual"] for s in sids)
        repeat=sorted(a for a,n in counts.items() if n>=2)
        ok=len(animals)>=min_ind and len(repeat)>=min_repeat
        cohort_meta[cohort]={
          "eligible_session_count":len(sids),
          "individual_count":len(animals),
          "repeat_individual_count":len(repeat),
          "repeat_individuals":repeat,
          "admitted":ok,
        }
        if ok:
            admitted.append(cohort)

    projections={}
    for cohort in admitted:
        allowed=set(cohort_sessions[cohort])
        coords=[]
        for animal,vals in candidates.items():
            for idx,t,lon,lat,site in vals:
                if session_for_row.get(idx) in allowed:
                    coords.append((lon,lat))
        if not coords:
            continue
        lon_med=float(np.median([x[0] for x in coords]))
        lat_med=float(np.median([x[1] for x in coords]))
        projections[cohort]={
          "median_lon":lon_med,"median_lat":lat_med,"epsg":utm_epsg(lon_med,lat_med)
        }

    return {
      "height_field":height,
      "numeric_height_values_parsed":False,
      "reference_ambiguous_site_individuals":sorted(a for a,v in refmap.items() if v.get("ambiguous_site")),
      "excluded_manipulated_rows":excluded_manipulated_rows,
      "excluded_source_outlier_rows":excluded_outliers,
      "missing_site_rows":missing_site_rows,
      "session_for_row":session_for_row,
      "session_meta":session_meta,
      "cohort_meta":cohort_meta,
      "admitted_cohorts":admitted,
      "projections":projections,
    }


def parse_edges(values):
    out=[]
    for x in values:
        if x=="-inf": out.append(-math.inf)
        elif x=="inf": out.append(math.inf)
        else: out.append(float(x))
    return tuple(out)


def build_events(rows,pre,contract,cell_size):
    height_field=contract["vertical"]["field"]
    edges=parse_edges(contract["vertical"]["primary_edges_m"])
    transformers={
      cohort:Transformer.from_crs("EPSG:4326",f"EPSG:{spec['epsg']}",always_xy=True)
      for cohort,spec in pre["projections"].items()
    }
    events=defaultdict(list)
    numeric_failures=0
    for idx,row in enumerate(rows):
        sid=pre["session_for_row"].get(idx)
        if sid is None:
            continue
        sm=pre["session_meta"][sid]
        cohort=sm["cohort"]
        if cohort not in pre["admitted_cohorts"]:
            continue
        h=finite_float(row.get(height_field))
        lon=finite_float(row.get("location_long"))
        lat=finite_float(row.get("location_lat"))
        if h is None or lon is None or lat is None:
            numeric_failures+=1
            continue
        try:
            t=parse_time(row.get("timestamp",""))
        except Exception:
            numeric_failures+=1
            continue
        x,y=transformers[cohort].transform(lon,lat)
        cell=(math.floor(x/cell_size),math.floor(y/cell_size))
        events[cohort].append(Event(sm["individual"],t,cell,z_bin(h,edges=edges),sid))
    return events,numeric_failures


def score_target(target,self_train,pop_train,k,alpha,min_scored):
    p_self=conditional_profile(self_train,unit="session",alpha=alpha,k=k)
    p_pop=conditional_profile(pop_train,unit="individual",alpha=alpha,k=k)
    m_self=marginal_profile(self_train,unit="session",alpha=alpha,k=k)
    m_pop=marginal_profile(pop_train,unit="individual",alpha=alpha,k=k)
    scored=[e for e in target if e.cell in p_self and e.cell in p_pop]
    if len(scored)<min_scored:
        return {"evaluable":False,"target_fixes":len(target),"scored_fixes":len(scored)}
    cond=[]; marg=[]
    for e in scored:
        cond.append(math.log(float(p_self[e.cell][e.zbin]))-math.log(float(p_pop[e.cell][e.zbin])))
        marg.append(math.log(float(m_self[e.zbin]))-math.log(float(m_pop[e.zbin])))
    cg=float(np.mean(cond)); mg=float(np.mean(marg))
    return {
      "evaluable":True,
      "target_fixes":len(target),"scored_fixes":len(scored),"coverage":len(scored)/len(target),
      "conditional_identity_gain":cg,
      "marginal_identity_gain":mg,
      "identity_x_location_increment":cg-mg,
    }


def analyze(rows,pre,contract,cell_size):
    events_by_cohort,numeric_failures=build_events(rows,pre,contract,cell_size)
    alpha=float(contract["probability_model"]["jeffreys_alpha"])
    min_scored=int(contract["probability_model"]["minimum_scored_target_fixes"])
    k=len(parse_edges(contract["vertical"]["primary_edges_m"]))-1
    session_results=[]

    for cohort,events in sorted(events_by_cohort.items()):
        by_session=defaultdict(list)
        by_ind=defaultdict(list)
        for e in events:
            by_session[e.session].append(e)
            by_ind[e.individual].append(e)

        for sid,target in sorted(by_session.items()):
            individual=target[0].individual
            self_train=[e for e in by_ind[individual] if e.session!=sid]
            if not self_train:
                session_results.append({"cohort":cohort,"session":sid,"individual":individual,"evaluable":False,"reason":"no_other_self_session_in_cohort"})
                continue
            pop_train=[e for e in events if e.individual!=individual]
            if not pop_train:
                session_results.append({"cohort":cohort,"session":sid,"individual":individual,"evaluable":False,"reason":"no_other_individual_in_cohort"})
                continue
            s=score_target(target,self_train,pop_train,k,alpha,min_scored)
            s.update({"cohort":cohort,"session":sid,"individual":individual})
            session_results.append(s)

    # First average sessions equally within each individual, across its admitted cohort sessions.
    per_individual={}
    for individual in sorted({r["individual"] for r in session_results}):
        vals=[r for r in session_results if r["individual"]==individual and r.get("evaluable")]
        cond=[r["conditional_identity_gain"] for r in vals]
        marg=[r["marginal_identity_gain"] for r in vals]
        inter=[r["identity_x_location_increment"] for r in vals]
        per_individual[individual]={
          "evaluable_sessions":len(vals),
          "cohorts":sorted({r["cohort"] for r in vals}),
          "mean_conditional_identity_gain":float(np.mean(cond)) if cond else None,
          "mean_marginal_identity_gain":float(np.mean(marg)) if marg else None,
          "mean_identity_x_location_increment":float(np.mean(inter)) if inter else None,
          "positive_conditional_session_fraction":float(np.mean(np.array(cond)>0)) if cond else None,
        }

    evaluable=[v for v in per_individual.values() if v["mean_conditional_identity_gain"] is not None]
    cond=[v["mean_conditional_identity_gain"] for v in evaluable]
    marg=[v["mean_marginal_identity_gain"] for v in evaluable]
    inter=[v["mean_identity_x_location_increment"] for v in evaluable]

    cohort_summary={}
    for cohort in pre["admitted_cohorts"]:
        vals=[r for r in session_results if r.get("cohort")==cohort and r.get("evaluable")]
        by_i=defaultdict(list)
        for r in vals:
            by_i[r["individual"]].append(r)
        civ=[]
        for individual,rs in by_i.items():
            civ.append({
              "individual":individual,
              "cond":float(np.mean([r["conditional_identity_gain"] for r in rs])),
              "marg":float(np.mean([r["marginal_identity_gain"] for r in rs])),
              "inter":float(np.mean([r["identity_x_location_increment"] for r in rs])),
            })
        cohort_summary[cohort]={
          "evaluable_individual_count":len(civ),
          "mean_conditional_identity_gain":float(np.mean([x["cond"] for x in civ])) if civ else None,
          "mean_marginal_identity_gain":float(np.mean([x["marg"] for x in civ])) if civ else None,
          "mean_identity_x_location_increment":float(np.mean([x["inter"] for x in civ])) if civ else None,
          "positive_conditional_individual_fraction":float(np.mean(np.array([x["cond"] for x in civ])>0)) if civ else None,
        }

    return {
      "cell_size_m":cell_size,
      "numeric_height_parse_failures":numeric_failures,
      "evaluable_individual_count":len(evaluable),
      "equal_individual_mean_conditional_identity_gain":float(np.mean(cond)) if cond else None,
      "equal_individual_mean_marginal_identity_gain":float(np.mean(marg)) if marg else None,
      "equal_individual_mean_identity_x_location_increment":float(np.mean(inter)) if inter else None,
      "positive_conditional_individual_fraction":float(np.mean(np.array(cond)>0)) if cond else None,
      "median_individual_conditional_identity_gain":float(np.median(cond)) if cond else None,
      "individual_results":per_individual,
      "cohort_summaries":cohort_summary,
      "session_results":session_results,
    }


def pass_rule(summary,contract):
    return {
      "minimum_evaluable_individuals":summary["evaluable_individual_count"]>=int(contract["replication_rule"]["minimum_evaluable_individuals"]),
      "mean_conditional_positive":(summary["equal_individual_mean_conditional_identity_gain"] or -math.inf)>0,
      "majority_individuals_positive":(summary["positive_conditional_individual_fraction"] or 0)>0.5,
      "mean_identity_x_location_positive":(summary["equal_individual_mean_identity_x_location_increment"] or -math.inf)>0,
      "conditional_exceeds_marginal":(
        summary["equal_individual_mean_conditional_identity_gain"] is not None and
        summary["equal_individual_mean_marginal_identity_gain"] is not None and
        summary["equal_individual_mean_conditional_identity_gain"]>summary["equal_individual_mean_marginal_identity_gain"]
      ),
    }


def compact_pre(pre):
    return {k:v for k,v in pre.items() if k!="session_for_row"}


def compact_summary(summary):
    return {k:summary[k] for k in [
      "cell_size_m","evaluable_individual_count",
      "equal_individual_mean_conditional_identity_gain",
      "equal_individual_mean_marginal_identity_gain",
      "equal_individual_mean_identity_x_location_increment",
      "positive_conditional_individual_fraction",
      "median_individual_conditional_identity_gain",
      "cohort_summaries"
    ]}


def run_contract(path):
    contract=json.loads(path.read_text(encoding="utf-8"))
    ua=contract["study_id"]+"/1.0"
    gps_data=get(contract["source"]["gps"],ua)
    ref_data=get(contract["source"]["reference"],ua)
    rows,headers=read_csv(gps_data)
    refs,_=read_csv(ref_data)

    # Entire structural/cohort/projection phase happens before numeric height parse.
    pre=build_pre_numeric(rows,headers,refs,contract)
    if not pre["admitted_cohorts"]:
        return {
          "study_id":contract["study_id"],"taxon":contract["taxon"],
          "status":"structurally_unavailable",
          "pre_numeric_structure":compact_pre(pre),
          "numeric_height_opened":False,
        }

    primary=analyze(rows,pre,contract,float(contract["horizontal"]["primary_cell_size_m"]))
    sensitivities={
      str(int(cs)):analyze(rows,pre,contract,float(cs))
      for cs in contract["horizontal"]["sensitivity_cell_sizes_m"]
    }
    checks=pass_rule(primary,contract)
    return {
      "study_id":contract["study_id"],
      "taxon":contract["taxon"],
      "role":contract["role"],
      "repository_doi":contract["repository_doi"],
      "vertical_field":contract["vertical"]["field"],
      "pre_numeric_structure":compact_pre(pre),
      "numeric_height_opened":True,
      "primary":primary,
      "sensitivities":sensitivities,
      "replication_rule_checks":checks,
      "replication_supported":all(checks.values()),
      "claim_boundary":contract["claim_boundary"],
    }


def main():
    results=[]
    for path in CONTRACTS:
        results.append(run_contract(path))
    payload={
      "program_id":"batter-new-species-replications-v1",
      "results":results,
    }
    out=Path("results/new_species_replications_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
      "results":[{
        "study_id":r["study_id"],"taxon":r["taxon"],"role":r.get("role"),
        "status":r.get("status","evaluated"),
        "admitted_cohorts":r.get("pre_numeric_structure",{}).get("admitted_cohorts"),
        "primary":compact_summary(r["primary"]) if r.get("primary") else None,
        "replication_rule_checks":r.get("replication_rule_checks"),
        "replication_supported":r.get("replication_supported"),
        "sensitivity_summaries":{
          k:compact_summary(v) for k,v in r.get("sensitivities",{}).items()
        },
      } for r in results]
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
