#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

pre=load_module("couse_preflight_v1",ROOT/"post_freeze_extensions/3d_niche_partition/run_couse_preflight_v1.py")
ep=load_module("couse_endpoint_v1",ROOT/"post_freeze_extensions/3d_niche_partition/run_couse_endpoint_audit_v1.py")

CFG=ROOT/"post_freeze_extensions/3d_niche_partition/couse_vertical_separation_contract_v1.json"
PREF=ROOT/"post_freeze_extensions/3d_niche_partition/couse_preflight_summary_v1.json"
EPSUM=ROOT/"post_freeze_extensions/3d_niche_partition/couse_endpoint_audit_summary_v1.json"
OUTDIR=ROOT/"post_freeze_extensions/3d_niche_partition/couse_shiftability"


def primary_encounters(panel,records,tol_s,scope,cfg):
    durations=pre.session_durations(records)
    shiftable_sessions={k for k,span in durations.items() if span>=4.0*tol_s}
    rr=[r for r in records if (r["cohort"],r["session"]) in shiftable_sessions]

    centers,_=ep.endpoint_centers(records)
    radius=float(cfg["endpoint_exclusion"]["radius_m"])

    by_ind=defaultdict(list)
    for r in rr:
        by_ind[(r["cohort"],r["iid"])].append(r)

    cohort_ids=defaultdict(list)
    for c,i in by_ind:
        cohort_ids[c].append(i)

    matches_by_dyad=defaultdict(list)
    for cohort,ids0 in sorted(cohort_ids.items()):
        ids=sorted(set(ids0))
        for a_i in range(len(ids)):
            for b_i in range(a_i+1,len(ids)):
                a,b=ids[a_i],ids[b_i]
                ar=by_ind[(cohort,a)]; br=by_ind[(cohort,b)]
                for m in pre.mutual_matches(ar,br,tol_s):
                    ra=ar[m["a_index"]]; rb=br[m["b_index"]]
                    if scope=="endpoint_excluded":
                        if not (ep.is_away(ra,centers,radius) and ep.is_away(rb,centers,radius)):
                            continue
                    matches_by_dyad[(cohort,a,b)].append((ra,rb,m))

    g=cfg["structural_gate"]
    usable={k:v for k,v in matches_by_dyad.items() if len(v)>=int(g["dyad_min_encounters"])}
    ind_enc=defaultdict(int); partners=defaultdict(set)
    for (c,a,b),vals in usable.items():
        n=len(vals)
        ind_enc[(c,a)]+=n; ind_enc[(c,b)]+=n
        partners[(c,a)].add(b); partners[(c,b)].add(a)
    inds={
        k for k,n in ind_enc.items()
        if n>=int(g["individual_min_encounters"]) and len(partners[k])>=int(g["individual_min_partners"])
    }
    final={k:v for k,v in usable.items() if (k[0],k[1]) in inds and (k[0],k[2]) in inds}
    return rr,final


def run(panel):
    cfg=json.loads(CFG.read_text())
    pf=json.loads(PREF.read_text())
    es=json.loads(EPSUM.read_text())
    tol=int(pf["panels"][panel]["selected_tolerance_s"])
    scope=str(es["panels"][panel]["primary_scope"])

    records=pre.load_xy_time(panel)
    rr,dyads=primary_encounters(panel,records,tol,scope,cfg)

    group_n=defaultdict(int)
    for r in rr:
        cell=(math.floor(r["x"]/500.0),math.floor(r["y"]/500.0))
        group_n[(r["cohort"],r["iid"],r["session"],cell)]+=1

    total_ep=0; shift_ep=0; fixed_ep=0
    encounter_count=0
    dyad_counts={}
    group_sizes_used=defaultdict(int)
    for key,vals in sorted(dyads.items()):
        dyad_counts["|||".join(key)]=len(vals)
        encounter_count+=len(vals)
        for ra,rb,m in vals:
            for r in (ra,rb):
                cell=(math.floor(r["x"]/500.0),math.floor(r["y"]/500.0))
                gk=(r["cohort"],r["iid"],r["session"],cell)
                n=group_n[gk]
                total_ep+=1
                group_sizes_used[n]+=1
                if n>=2: shift_ep+=1
                else: fixed_ep+=1

    frac=shift_ep/total_ep if total_ep else 0.0
    gate=frac>=0.90
    payload={
        "schema_version":1,
        "study_id":"batter-couse-z-phase-shiftability-v1",
        "panel":panel,
        "tolerance_s":tol,
        "primary_scope":scope,
        "vertical_values_used":False,
        "usable_dyads":len(dyads),
        "encounters":encounter_count,
        "encounter_endpoints":total_ep,
        "shiftable_endpoints":shift_ep,
        "unshiftable_endpoints":fixed_ep,
        "shiftable_endpoint_fraction":frac,
        "gate_threshold":0.90,
        "shiftability_gate_met":bool(gate),
        "dyad_counts":dyad_counts,
        "used_group_size_distribution":{str(k):int(v) for k,v in sorted(group_sizes_used.items())},
        "null_rule_if_proceed":"groups with n>=2 receive random nonzero circular z rotation; n=1 endpoints remain fixed",
    }
    OUTDIR.mkdir(parents=True,exist_ok=True)
    out=OUTDIR/f"{panel}_shiftability_v1.json"
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "panel":panel,"tolerance_s":tol,"primary_scope":scope,
        "dyads":len(dyads),"encounters":encounter_count,
        "shiftable_fraction":frac,"gate":gate
    },sort_keys=True))


def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--panel",required=True,choices=["hypsignathus","phyllostomus_2022","phyllostomus_2023","phyllostomus_2016"])
    args=ap.parse_args()
    run(args.panel)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
