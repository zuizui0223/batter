#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, importlib.util, json, math, sys
from collections import defaultdict, Counter
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

shift=load_module("couse_shift_v1",ROOT/"post_freeze_extensions/3d_niche_partition/run_couse_shiftability_v1.py")
ep=load_module("couse_endpoint_v1",ROOT/"post_freeze_extensions/3d_niche_partition/run_couse_endpoint_audit_v1.py")

CFG=ROOT/"post_freeze_extensions/3d_niche_partition/couse_vertical_separation_contract_v1.json"
RECEIPT=ROOT/"post_freeze_extensions/3d_niche_partition/couse_primary_encounter_receipt_v1.json"
OUTDIR=ROOT/"post_freeze_extensions/3d_niche_partition/couse_context_results"

MAX_GAP_S=1200.0
STATIONARY_SPEED=0.5


def record_key(r):
    cell=(math.floor(r["x"]/500.0),math.floor(r["y"]/500.0))
    return (r["cohort"],r["iid"],r["session"],r["t"].isoformat(),cell)


def movement_context(records):
    by_session=defaultdict(list)
    for r in records:
        by_session[(r["cohort"],r["session"])].append(r)

    ctx={}
    session_bounds={}
    for key,vals in sorted(by_session.items()):
        vals=sorted(vals,key=lambda r:r["t"])
        t0=vals[0]["t"]; t1=vals[-1]["t"]
        span=(t1-t0).total_seconds()
        session_bounds[key]=(t0,t1)
        for i,r in enumerate(vals):
            rk=record_key(r)
            phase=((r["t"]-t0).total_seconds()/span) if span>0 else None
            if phase is None:
                phase_class="unknown"
            elif phase<0.2:
                phase_class="early"
            elif phase>0.8:
                phase_class="late"
            else:
                phase_class="middle"

            stationary=False
            local_speed=None
            adjacent_valid=False
            if 0<i<len(vals)-1:
                a=vals[i-1]; c=vals[i+1]
                dt1=(r["t"]-a["t"]).total_seconds()
                dt2=(c["t"]-r["t"]).total_seconds()
                if 0<dt1<=MAX_GAP_S and 0<dt2<=MAX_GAP_S:
                    s1=math.hypot(r["x"]-a["x"],r["y"]-a["y"])/dt1
                    s2=math.hypot(c["x"]-r["x"],c["y"]-r["y"])/dt2
                    adjacent_valid=True
                    local_speed=(s1+s2)/2.0
                    stationary=(s1<=STATIONARY_SPEED and s2<=STATIONARY_SPEED)

            ctx[rk]={
                "stationary_like":bool(stationary),
                "adjacent_speed_valid":bool(adjacent_valid),
                "local_speed_m_s":float(local_speed) if local_speed is not None else None,
                "phase":float(phase) if phase is not None else None,
                "phase_class":phase_class,
            }
    return ctx


def reconstruct(panel,records,cfg,receipt):
    p=receipt["panels"][panel]
    tol=int(p["tolerance_s"])
    scope=str(p["primary_scope"])
    centers,_=ep.endpoint_centers(records)
    radius=float(cfg["endpoint_exclusion"]["radius_m"])

    rr_full,_,_=shift.shiftable_records(records,tol)
    encounters,dyads,inds=shift.build_primary_encounters(rr_full,tol,cfg,scope,centers,radius)
    desc=sorted(shift.canonical_encounter(m) for m in encounters)
    sha=hashlib.sha256(("\n".join(desc)+"\n").encode()).hexdigest()
    if sha!=p["primary_encounter_set_sha256"]:
        raise RuntimeError(f"{panel}: encounter SHA {sha} != receipt {p['primary_encounter_set_sha256']}")
    if len(encounters)!=int(p["encounters"]):
        raise RuntimeError(f"{panel}: encounter count mismatch")
    return encounters,dyads,inds,sha


def endpoint_key(m,side):
    if side=="a":
        return (m["cohort"],m["a"],m["a_session"],m["a_t"].isoformat(),tuple(m["cell"]))
    return (m["cohort"],m["b"],m["b_session"],m["b_t"].isoformat(),tuple(m["cell"]))


def summarize(panel):
    cfg=json.loads(CFG.read_text())
    receipt=json.loads(RECEIPT.read_text())
    records=shift.pre.load_xy_time(panel)
    encounters,dyads,inds,esha=reconstruct(panel,records,cfg,receipt)
    ctx=movement_context(records)

    categories=Counter()
    phase_pairs=Counter()
    both_middle=0
    endpoint_rows=[]
    valid_speeds=[]
    stat_speeds=[]
    nonstat_speeds=[]

    for m in encounters:
        ca=ctx.get(endpoint_key(m,"a"))
        cb=ctx.get(endpoint_key(m,"b"))
        if ca is None or cb is None:
            raise RuntimeError("encounter endpoint missing movement context")

        sa=ca["stationary_like"]; sb=cb["stationary_like"]
        if sa and sb:
            cat="both_stationary_like"
        elif sa or sb:
            cat="one_stationary_like"
        else:
            cat="neither_stationary_like"
        categories[cat]+=1

        pp="|".join(sorted([ca["phase_class"],cb["phase_class"]]))
        phase_pairs[pp]+=1
        if ca["phase_class"]=="middle" and cb["phase_class"]=="middle":
            both_middle+=1

        for c in (ca,cb):
            if c["local_speed_m_s"] is not None:
                valid_speeds.append(c["local_speed_m_s"])
                if c["stationary_like"]:
                    stat_speeds.append(c["local_speed_m_s"])
                else:
                    nonstat_speeds.append(c["local_speed_m_s"])

    n=len(encounters)
    def speed_summary(x):
        if not x:
            return {"n":0,"median":None,"q25":None,"q75":None}
        a=np.asarray(x,dtype=float)
        return {
            "n":int(len(a)),
            "median":float(np.median(a)),
            "q25":float(np.quantile(a,0.25)),
            "q75":float(np.quantile(a,0.75)),
        }

    payload={
        "schema_version":1,
        "study_id":"batter-couse-behavioural-context-audit-v1",
        "panel":panel,
        "inferential_role":"descriptive_only_post_outcome",
        "vertical_values_used":False,
        "encounter_set_sha256":esha,
        "primary_scope":receipt["panels"][panel]["primary_scope"],
        "tolerance_s":int(receipt["panels"][panel]["tolerance_s"]),
        "encounters":n,
        "usable_dyads":len(dyads),
        "usable_individuals":len(inds),
        "stationary_definition":{
            "max_adjacent_gap_s":MAX_GAP_S,
            "max_both_adjacent_segment_speed_m_s":STATIONARY_SPEED,
            "inherited_from":"tag-altitude-bias stationary-candidate audit"
        },
        "encounter_context":{
            "counts":dict(categories),
            "fractions":{k:float(v/n) for k,v in categories.items()},
            "both_middle_session_fraction":float(both_middle/n) if n else None,
            "phase_pair_counts":dict(phase_pairs),
        },
        "endpoint_speed_summary":{
            "all_valid":speed_summary(valid_speeds),
            "stationary_like":speed_summary(stat_speeds),
            "not_stationary_candidate":speed_summary(nonstat_speeds),
        },
        "claim_boundary":[
            "descriptive only; result was defined after co-use vertical outcome",
            "stationary-like is not a verified roost/rest behavioural state",
            "not-stationary-candidate is not equivalent to foraging or commuting"
        ]
    }
    OUTDIR.mkdir(parents=True,exist_ok=True)
    out=OUTDIR/f"{panel}_context_v1.json"
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "panel":panel,
        "scope":payload["primary_scope"],
        "tolerance_s":payload["tolerance_s"],
        "encounters":n,
        "both_stationary_like_fraction":payload["encounter_context"]["fractions"].get("both_stationary_like",0.0),
        "one_stationary_like_fraction":payload["encounter_context"]["fractions"].get("one_stationary_like",0.0),
        "neither_stationary_like_fraction":payload["encounter_context"]["fractions"].get("neither_stationary_like",0.0),
        "both_middle_session_fraction":payload["encounter_context"]["both_middle_session_fraction"],
        "valid_endpoint_speed_median":payload["endpoint_speed_summary"]["all_valid"]["median"],
        "encounter_sha256":esha
    },sort_keys=True))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--panel",required=True,choices=["hypsignathus","phyllostomus_2022","phyllostomus_2023","phyllostomus_2016"])
    args=ap.parse_args()
    summarize(args.panel)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
