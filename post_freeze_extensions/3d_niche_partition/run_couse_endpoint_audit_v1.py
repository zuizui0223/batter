#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

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
CFG=ROOT/"post_freeze_extensions/3d_niche_partition/couse_vertical_separation_contract_v1.json"
PREF=ROOT/"post_freeze_extensions/3d_niche_partition/couse_preflight_summary_v1.json"
OUTDIR=ROOT/"post_freeze_extensions/3d_niche_partition/couse_endpoint_audit"


def endpoint_centers(records):
    by_session=defaultdict(list)
    for r in records:
        by_session[(r["cohort"],r["session"])].append(r)

    pts=defaultdict(list)
    for (cohort,_sid),vals in by_session.items():
        vals=sorted(vals,key=lambda r:r["t"])
        for r in vals[:5]+vals[-5:]:
            pts[(cohort,r["iid"])].append((r["x"],r["y"]))

    centers={}
    spread={}
    for key,p in sorted(pts.items()):
        arr=np.asarray(p,dtype=float)
        d=np.sqrt(((arr[:,None,:]-arr[None,:,:])**2).sum(axis=2))
        idx=int(np.argmin(d.sum(axis=1)))
        center=arr[idx]
        centers[key]=(float(center[0]),float(center[1]))
        dist=np.sqrt(((arr-center)**2).sum(axis=1))
        spread[f"{key[0]}|||{key[1]}"]={
            "endpoint_count":int(len(arr)),
            "median_distance_to_proxy_m":float(np.median(dist)),
            "q90_distance_to_proxy_m":float(np.quantile(dist,0.9)),
        }
    return centers,spread


def is_away(r,centers,radius):
    c=centers.get((r["cohort"],r["iid"]))
    if c is None:
        return False
    return math.hypot(r["x"]-c[0],r["y"]-c[1])>=radius


def structural_summary(records,tol_s,centers,radius,cfg):
    durations=pre.session_durations(records)
    shiftable={k for k,span in durations.items() if span>=4.0*tol_s}
    rr=[r for r in records if (r["cohort"],r["session"]) in shiftable]

    by_ind=defaultdict(list)
    for r in rr:
        by_ind[(r["cohort"],r["iid"])].append(r)

    all_matches=[]
    cohort_ids=defaultdict(list)
    for cohort,iid in by_ind:
        cohort_ids[cohort].append(iid)

    for cohort,ids0 in sorted(cohort_ids.items()):
        ids=sorted(set(ids0))
        for i in range(len(ids)):
            for j in range(i+1,len(ids)):
                a,b=ids[i],ids[j]
                ar=by_ind[(cohort,a)]
                br=by_ind[(cohort,b)]
                for m in pre.mutual_matches(ar,br,tol_s):
                    ra=ar[m["a_index"]]
                    rb=br[m["b_index"]]
                    all_matches.append({
                        "cohort":cohort,"a":a,"b":b,
                        "cell":m["cell"],"dt_s":m["dt_s"],
                        "away_a":is_away(ra,centers,radius),
                        "away_b":is_away(rb,centers,radius),
                    })

    endpoint_matches=[m for m in all_matches if m["away_a"] and m["away_b"]]

    def gate(matches):
        counts=defaultdict(int)
        cell_counts=defaultdict(int)
        for m in matches:
            counts[(m["cohort"],m["a"],m["b"])]+=1
            cell_counts[(m["cohort"],m["cell"])]+=1

        g=cfg["structural_gate"]
        usable={k:n for k,n in counts.items() if n>=int(g["dyad_min_encounters"])}
        ind_enc=defaultdict(int); partners=defaultdict(set)
        for (c,a,b),n in usable.items():
            ind_enc[(c,a)]+=n; ind_enc[(c,b)]+=n
            partners[(c,a)].add(b); partners[(c,b)].add(a)
        inds={
            k for k,n in ind_enc.items()
            if n>=int(g["individual_min_encounters"]) and
               len(partners[k])>=int(g["individual_min_partners"])
        }
        final={k:n for k,n in usable.items() if (k[0],k[1]) in inds and (k[0],k[2]) in inds}
        final_inds={(c,i) for c,a,b in final for i in (a,b)}
        nenc=sum(final.values())
        passed=(
            len(final_inds)>=int(g["panel_min_individuals"]) and
            len(final)>=int(g["panel_min_dyads"]) and
            nenc>=int(g["panel_min_encounters"])
        )
        used_cells=defaultdict(int)
        for m in matches:
            key=(m["cohort"],m["a"],m["b"])
            if key in final:
                used_cells[(m["cohort"],m["cell"])]+=1
        vals=sorted(used_cells.values(),reverse=True)
        return {
            "passed":bool(passed),
            "usable_individuals":len(final_inds),
            "usable_dyads":len(final),
            "encounters":int(nenc),
            "dyad_counts":{f"{c}|||{a}|||{b}":int(n) for (c,a,b),n in sorted(final.items())},
            "distinct_cells":len(used_cells),
            "top_cell_fraction":float(vals[0]/sum(vals)) if vals and sum(vals)>0 else None,
            "top5_cell_fraction":float(sum(vals[:5])/sum(vals)) if vals and sum(vals)>0 else None,
        }

    return {
        "all_match_count":len(all_matches),
        "endpoint_excluded_raw_match_count":len(endpoint_matches),
        "fraction_raw_matches_endpoint_excluded":float(len(endpoint_matches)/len(all_matches)) if all_matches else None,
        "all_space_gate":gate(all_matches),
        "endpoint_excluded_gate":gate(endpoint_matches),
        "shiftable_session_count":len(shiftable),
        "excluded_short_session_count":len(durations)-len(shiftable),
    }


def run(panel):
    cfg=json.loads(CFG.read_text())
    pf=json.loads(PREF.read_text())
    tol=int(pf["panels"][panel]["selected_tolerance_s"])
    records=pre.load_xy_time(panel)
    centers,spread=endpoint_centers(records)
    radius=float(cfg["endpoint_exclusion"]["radius_m"])
    s=structural_summary(records,tol,centers,radius,cfg)
    primary_scope="endpoint_excluded" if s["endpoint_excluded_gate"]["passed"] else "all_space"

    payload={
        "schema_version":1,
        "study_id":"batter-couse-endpoint-audit-v1",
        "panel":panel,
        "selected_tolerance_s":tol,
        "radius_m":radius,
        "vertical_values_used":False,
        "proxy_is_verified_roost":False,
        "endpoint_proxy_spread":spread,
        "support":s,
        "primary_scope":primary_scope,
        "interpretation_limit":(
            "away-from-endpoint synchronous co-use"
            if primary_scope=="endpoint_excluded"
            else "generic synchronous co-presence; endpoint-excluded support insufficient"
        )
    }
    OUTDIR.mkdir(parents=True,exist_ok=True)
    out=OUTDIR/f"{panel}_endpoint_audit_v1.json"
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "panel":panel,
        "tolerance_s":tol,
        "raw_matches":s["all_match_count"],
        "endpoint_excluded_raw_matches":s["endpoint_excluded_raw_match_count"],
        "fraction_endpoint_excluded":s["fraction_raw_matches_endpoint_excluded"],
        "all_space":s["all_space_gate"],
        "endpoint_excluded":s["endpoint_excluded_gate"],
        "primary_scope":primary_scope
    },sort_keys=True))
    return 0


def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--panel",required=True,choices=["hypsignathus","phyllostomus_2022","phyllostomus_2023","phyllostomus_2016"])
    args=ap.parse_args()
    return run(args.panel)

if __name__=="__main__":
    raise SystemExit(main())
