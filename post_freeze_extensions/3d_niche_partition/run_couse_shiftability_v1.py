#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, importlib.util, json, math, sys
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
EPSUM=ROOT/"post_freeze_extensions/3d_niche_partition/couse_endpoint_audit_summary_v1.json"
OUTDIR=ROOT/"post_freeze_extensions/3d_niche_partition/couse_shiftability"


def primary_records(records,scope,centers,radius,tol_s):
    durations=pre.session_durations(records)
    shiftable={k for k,span in durations.items() if span>=4.0*tol_s}
    rr=[r for r in records if (r["cohort"],r["session"]) in shiftable]
    if scope=="endpoint_excluded":
        rr=[r for r in rr if ep.is_away(r,centers,radius)]
    return rr,shiftable,len(durations)-len(shiftable)


def build_primary_encounters(records,tol_s,cfg):
    by_ind=defaultdict(list)
    for r in records:
        by_ind[(r["cohort"],r["iid"])].append(r)

    all_matches=[]
    ids_by_cohort=defaultdict(set)
    for cohort,iid in by_ind:
        ids_by_cohort[cohort].add(iid)

    for cohort,ids0 in sorted(ids_by_cohort.items()):
        ids=sorted(ids0)
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
                        "cell":tuple(m["cell"]),
                        "dt_s":float(m["dt_s"]),
                        "a_session":ra["session"],"b_session":rb["session"],
                        "a_t":ra["t"],"b_t":rb["t"],
                    })

    g=cfg["structural_gate"]
    counts=defaultdict(int)
    for m in all_matches:
        counts[(m["cohort"],m["a"],m["b"])]+=1
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
    final_dyads={k:n for k,n in usable.items() if (k[0],k[1]) in inds and (k[0],k[2]) in inds}
    final=[m for m in all_matches if (m["cohort"],m["a"],m["b"]) in final_dyads]
    return final,final_dyads,inds


def canonical_encounter(m):
    return "|".join([
        str(m["cohort"]),str(m["a"]),str(m["b"]),
        f"{int(m['cell'][0])},{int(m['cell'][1])}",
        str(m["a_session"]),m["a_t"].isoformat(),
        str(m["b_session"]),m["b_t"].isoformat(),
    ])


def run(panel):
    cfg=json.loads(CFG.read_text())
    es=json.loads(EPSUM.read_text())
    info=es["panels"][panel]
    tol=int(info["tolerance_s"])
    scope=str(info["primary_scope"])

    records=pre.load_xy_time(panel)
    centers,_=ep.endpoint_centers(records)
    radius=float(cfg["endpoint_exclusion"]["radius_m"])
    rr,shiftable,excluded_short=primary_records(records,scope,centers,radius,tol)

    encounters,dyads,inds=build_primary_encounters(rr,tol,cfg)
    expected=int(info["endpoint_excluded"]["encounters"] if scope=="endpoint_excluded" else info["all_space"]["encounters"])
    if len(encounters)!=expected:
        raise RuntimeError(f"{panel}: reconstructed primary encounter count {len(encounters)} != frozen {expected}")

    # Count fixes in the exact primary-scope phase groups.
    group_n=defaultdict(int)
    for r in rr:
        cell=(math.floor(r["x"]/500.0),math.floor(r["y"]/500.0))
        group_n[(r["cohort"],r["iid"],r["session"],cell)]+=1

    endpoint_total=0
    endpoint_shiftable=0
    unshiftable_groups=defaultdict(int)
    for m in encounters:
        for iid,sid,cell in [(m["a"],m["a_session"],m["cell"]),(m["b"],m["b_session"],m["cell"])]:
            endpoint_total+=1
            key=(m["cohort"],iid,sid,tuple(cell))
            if group_n[key]>=2:
                endpoint_shiftable+=1
            else:
                unshiftable_groups[key]+=1

    frac=endpoint_shiftable/endpoint_total if endpoint_total else 0.0
    gate=frac>=float(cfg["null"]["pre_vertical_shiftability_fraction_min"])

    desc=sorted(canonical_encounter(m) for m in encounters)
    encounter_sha=hashlib.sha256(("\n".join(desc)+"\n").encode()).hexdigest()

    payload={
        "schema_version":1,
        "study_id":"batter-couse-phase-shiftability-v1",
        "panel":panel,
        "vertical_values_used":False,
        "primary_scope":scope,
        "tolerance_s":tol,
        "primary_encounters":len(encounters),
        "usable_dyads":len(dyads),
        "usable_individuals":len(inds),
        "shiftable_sessions":len(shiftable),
        "excluded_short_sessions":excluded_short,
        "encounter_endpoint_count":endpoint_total,
        "shiftable_endpoint_count":endpoint_shiftable,
        "shiftable_endpoint_fraction":frac,
        "required_fraction":float(cfg["null"]["pre_vertical_shiftability_fraction_min"]),
        "phase_shiftability_gate_met":bool(gate),
        "unshiftable_endpoint_group_count":len(unshiftable_groups),
        "primary_encounter_set_sha256":encounter_sha,
        "primary_dyads":{
            f"{c}|||{a}|||{b}":int(n)
            for (c,a,b),n in sorted(dyads.items())
        }
    }
    OUTDIR.mkdir(parents=True,exist_ok=True)
    out=OUTDIR/f"{panel}_shiftability_v1.json"
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "panel":panel,"primary_scope":scope,"tolerance_s":tol,
        "encounters":len(encounters),"dyads":len(dyads),"individuals":len(inds),
        "shiftable_endpoint_fraction":frac,
        "gate":gate,"encounter_sha256":encounter_sha
    },sort_keys=True))
    return 0


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--panel",required=True,choices=["hypsignathus","phyllostomus_2022","phyllostomus_2023","phyllostomus_2016"])
    args=ap.parse_args()
    return run(args.panel)

if __name__=="__main__":
    raise SystemExit(main())
