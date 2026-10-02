#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_new_species_replications as core

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

geom=load_module("geom_v1",ROOT/"post_freeze_extensions/3d_niche_partition/run_v1.py")
CFG=ROOT/"post_freeze_extensions/3d_niche_partition/couse_vertical_separation_contract_v1.json"
OUTDIR=ROOT/"post_freeze_extensions/3d_niche_partition/couse_preflight"

CPATH={
    "hypsignathus":"contract/hypsignathus_replication_v1.json",
    "phyllostomus_2022":"contract/phyllostomus_replication_v1.json",
    "phyllostomus_2023":"contract/phyllostomus_2023_replication_v1.json",
    "phyllostomus_2016":"contract/phyllostomus_2016_dry_architecture_v1.json",
}

def source_contract(panel):
    base=json.loads((ROOT/CPATH[panel]).read_text(encoding="utf-8"))
    if panel=="phyllostomus_2016":
        c=copy.deepcopy(base)
        c["vertical"]={
            "field":base["vertical"]["primary_field"],
            "primary_edges_m":base["vertical"]["edges_m"],
        }
        return c
    return base

def frozen_target_sessions(panel):
    sessions,_=geom.build_session_distributions(panel)
    return {(cohort,s["session"]) for cohort,rows in sessions.items() for s in rows}

def load_xy_time(panel):
    contract=source_contract(panel)
    ua="batter-couse-preflight-v1/1.0"
    gps=core.get(contract["source"]["gps"],ua)
    ref=core.get(contract["source"]["reference"],ua)
    rows,headers=core.read_csv(gps)
    refs,_=core.read_csv(ref)
    pre=core.build_pre_numeric(rows,headers,refs,contract)
    targets=frozen_target_sessions(panel)

    transformers={
        cohort:Transformer.from_crs("EPSG:4326",f"EPSG:{meta['epsg']}",always_xy=True)
        for cohort,meta in pre["projections"].items()
    }

    rec=[]
    seen=set()
    for idx,row in enumerate(rows):
        sid=pre["session_for_row"].get(idx)
        if sid is None:
            continue
        sm=pre["session_meta"][sid]
        cohort=sm["cohort"]
        if cohort not in pre["admitted_cohorts"] or (cohort,sid) not in targets:
            continue
        lon=core.finite_float(row.get("location_long"))
        lat=core.finite_float(row.get("location_lat"))
        if lon is None or lat is None:
            continue
        try:
            t=core.parse_time(row.get("timestamp",""))
        except Exception:
            continue
        x,y=transformers[cohort].transform(lon,lat)
        rec.append({
            "cohort":str(cohort),
            "iid":str(sm["individual"]),
            "session":str(sid),
            "t":t,
            "x":float(x),
            "y":float(y),
        })
        seen.add((cohort,sid))
    if seen!=targets:
        missing=sorted(targets-seen)
        extra=sorted(seen-targets)
        raise RuntimeError(f"{panel}: xy-time target-session mismatch missing={missing[:5]} extra={extra[:5]}")
    return rec

def session_durations(records):
    by=defaultdict(list)
    for r in records:
        by[(r["cohort"],r["session"])].append(r["t"])
    return {k:(max(v)-min(v)).total_seconds() for k,v in by.items() if v}

def nearest_indices(times_a,times_b,max_dt):
    # Return nearest b index for each a, or -1 if outside tolerance.
    b=np.asarray(times_b,dtype=float)
    out=np.full(len(times_a),-1,dtype=int)
    if len(b)==0:
        return out
    for i,t in enumerate(times_a):
        j=int(np.searchsorted(b,t))
        cand=[]
        if j<len(b): cand.append(j)
        if j>0: cand.append(j-1)
        if not cand: continue
        best=min(cand,key=lambda q:abs(b[q]-t))
        if abs(b[best]-t)<=max_dt:
            out[i]=best
    return out

def mutual_matches(a_rows,b_rows,tol_s):
    # Group by shared 500-m cell, then mutual-nearest temporal matching.
    ca=defaultdict(list); cb=defaultdict(list)
    for idx,r in enumerate(a_rows):
        c=(math.floor(r["x"]/500.0),math.floor(r["y"]/500.0))
        ca[c].append((idx,r))
    for idx,r in enumerate(b_rows):
        c=(math.floor(r["x"]/500.0),math.floor(r["y"]/500.0))
        cb[c].append((idx,r))

    matches=[]
    for c in sorted(set(ca)&set(cb)):
        aa=sorted(ca[c],key=lambda z:z[1]["t"])
        bb=sorted(cb[c],key=lambda z:z[1]["t"])
        ta=np.array([z[1]["t"].timestamp() for z in aa],dtype=float)
        tb=np.array([z[1]["t"].timestamp() for z in bb],dtype=float)
        ab=nearest_indices(ta,tb,tol_s)
        ba=nearest_indices(tb,ta,tol_s)
        for ia,jb in enumerate(ab):
            if jb<0: continue
            if ba[jb]==ia:
                matches.append({
                    "cell":c,
                    "a_index":aa[ia][0],
                    "b_index":bb[jb][0],
                    "dt_s":float(abs(ta[ia]-tb[jb])),
                })
    return matches

def evaluate_tolerance(records,tol_s,cfg):
    durations=session_durations(records)
    shiftable={
        k for k,span in durations.items()
        if span>=4.0*tol_s
    }
    rr=[r for r in records if (r["cohort"],r["session"]) in shiftable]

    by_ind=defaultdict(list)
    for r in rr:
        by_ind[(r["cohort"],r["iid"])].append(r)

    dyad_counts={}
    cohort_ids=defaultdict(list)
    for cohort,iid in by_ind:
        cohort_ids[cohort].append(iid)

    for cohort,ids0 in sorted(cohort_ids.items()):
        ids=sorted(set(ids0))
        for i in range(len(ids)):
            for j in range(i+1,len(ids)):
                a,b=ids[i],ids[j]
                m=mutual_matches(by_ind[(cohort,a)],by_ind[(cohort,b)],tol_s)
                if m:
                    dyad_counts[(cohort,a,b)]=len(m)

    g=cfg["structural_gate"]
    usable_dyads={k:n for k,n in dyad_counts.items() if n>=int(g["dyad_min_encounters"])}

    ind_enc=defaultdict(int)
    ind_partners=defaultdict(set)
    for (cohort,a,b),n in usable_dyads.items():
        ind_enc[(cohort,a)]+=n
        ind_enc[(cohort,b)]+=n
        ind_partners[(cohort,a)].add(b)
        ind_partners[(cohort,b)].add(a)

    usable_inds={
        k for k,n in ind_enc.items()
        if n>=int(g["individual_min_encounters"]) and
           len(ind_partners[k])>=int(g["individual_min_partners"])
    }

    # Retain only dyads connecting two usable individuals for the panel gate.
    final_dyads={
        k:n for k,n in usable_dyads.items()
        if (k[0],k[1]) in usable_inds and (k[0],k[2]) in usable_inds
    }
    final_encounters=sum(final_dyads.values())
    final_inds={
        (cohort,iid)
        for cohort,a,b in final_dyads
        for iid in (a,b)
    }

    passed=(
        len(final_inds)>=int(g["panel_min_individuals"]) and
        len(final_dyads)>=int(g["panel_min_dyads"]) and
        final_encounters>=int(g["panel_min_encounters"])
    )

    return {
        "tolerance_s":int(tol_s),
        "shiftable_session_count":len(shiftable),
        "excluded_short_session_count":len(durations)-len(shiftable),
        "all_mutual_match_dyads":len(dyad_counts),
        "all_mutual_matches":int(sum(dyad_counts.values())),
        "usable_dyads_before_individual_gate":len(usable_dyads),
        "usable_individuals_before_final_dyad_filter":len(usable_inds),
        "final_usable_dyads":len(final_dyads),
        "final_usable_individuals":len(final_inds),
        "final_encounters":int(final_encounters),
        "passed":bool(passed),
        "dyad_counts":{
            f"{c}|||{a}|||{b}":int(n)
            for (c,a,b),n in sorted(final_dyads.items())
        },
        "individual_support":{
            f"{c}|||{i}":{
                "encounters":int(ind_enc[(c,i)]),
                "partners":sorted(ind_partners[(c,i)]),
            }
            for c,i in sorted(usable_inds)
        }
    }

def run(panel):
    cfg=json.loads(CFG.read_text(encoding="utf-8"))
    if panel not in cfg["panels"]:
        raise RuntimeError(panel)
    records=load_xy_time(panel)
    results=[evaluate_tolerance(records,int(t),cfg) for t in cfg["candidate_tolerances_s"]]
    selected=next((x for x in results if x["passed"]),None)

    payload={
        "schema_version":1,
        "study_id":cfg["study_id"],
        "panel":panel,
        "vertical_values_used_for_preflight":False,
        "selection_basis":"x-y-time only",
        "target_session_count":len({(r["cohort"],r["session"]) for r in records}),
        "target_individual_count":len({(r["cohort"],r["iid"]) for r in records}),
        "candidate_results":results,
        "selected_tolerance_s":selected["tolerance_s"] if selected else None,
        "structural_gate_met":selected is not None,
        "selected_support":selected,
    }
    OUTDIR.mkdir(parents=True,exist_ok=True)
    out=OUTDIR/f"{panel}_preflight_v1.json"
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "panel":panel,
        "selected_tolerance_s":payload["selected_tolerance_s"],
        "structural_gate_met":payload["structural_gate_met"],
        "candidate_summary":[{
            "tolerance_s":x["tolerance_s"],
            "individuals":x["final_usable_individuals"],
            "dyads":x["final_usable_dyads"],
            "encounters":x["final_encounters"],
            "passed":x["passed"],
        } for x in results]
    },sort_keys=True))
    return 0

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--panel",required=True,choices=["hypsignathus","phyllostomus_2022","phyllostomus_2023","phyllostomus_2016"])
    args=ap.parse_args()
    return run(args.panel)

if __name__=="__main__":
    raise SystemExit(main())
