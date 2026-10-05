#!/usr/bin/env python3
"""Altitude-blind structural preflight for the wild policy -> vertical bridge.

No height value is used in any calculation.
"""
from __future__ import annotations
import collections, importlib.util, json, math, sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
for p in (ROOT, ROOT/"src"):
    if str(p) not in sys.path:
        sys.path.insert(0,str(p))

import scripts.run_tag_altitude_bias_shape as shape

PANELS=["hypsignathus","phyllostomus_2022","phyllostomus_2023","phyllostomus_2016"]
MAX_DT=1800.0
GRID=2000.0
MIN_SPEED_INTERVALS=30
MIN_TURNS=20
MIN_SESSIONS_TOTAL=4
MIN_SIDE_SESSIONS=2
MIN_POLICY_VALID_SIDE=2
MIN_EVENTS_STRATUM=10
MIN_SHARED_STRATA=3
MIN_INDIVIDUALS=6
MIN_PAIRS=15

def turn_angle(v1x,v1y,v2x,v2y):
    a=math.hypot(v1x,v1y);b=math.hypot(v2x,v2y)
    if a<=0 or b<=0:return None
    c=max(-1.0,min(1.0,(v1x*v2x+v1y*v2y)/(a*b)))
    return math.acos(c)

def session_horizontal_structure(vals):
    vals=sorted(vals,key=lambda r:r["t"])
    speeds=[];turns=[];endpoints=[]
    # Path support from all positive <=MAX_DT consecutive intervals.
    path=0.0; first_xy=None; last_xy=None
    for i in range(1,len(vals)):
        a,b=vals[i-1],vals[i]
        dt=(b["t"]-a["t"]).total_seconds()
        if math.isfinite(dt) and 0<dt<=MAX_DT:
            d=math.hypot(b["x"]-a["x"],b["y"]-a["y"])
            if math.isfinite(d):
                path+=d
                if first_xy is None:first_xy=(a["x"],a["y"])
                last_xy=(b["x"],b["y"])
    for i in range(2,len(vals)):
        a,b,d=vals[i-2],vals[i-1],vals[i]
        dt1=(b["t"]-a["t"]).total_seconds()
        dt2=(d["t"]-b["t"]).total_seconds()
        if not all(math.isfinite(x) and 0<x<=MAX_DT for x in (dt1,dt2)):
            continue
        v1x,v1y=b["x"]-a["x"],b["y"]-a["y"]
        v2x,v2y=d["x"]-b["x"],d["y"]-b["y"]
        ang=turn_angle(v1x,v1y,v2x,v2y)
        if ang is None:continue
        sp=math.hypot(v2x,v2y)/dt2
        rate=ang/((dt1+dt2)/2.0)
        if not (math.isfinite(sp) and math.isfinite(rate)):continue
        speeds.append(float(sp));turns.append(float(rate))
        endpoints.append({
            "x":d["x"],"y":d["y"],"speed":float(sp),
            "turn_angle":float(ang),"turn_rate":float(rate),
        })
    valid=(len(speeds)>=MIN_SPEED_INTERVALS and len(turns)>=MIN_TURNS and path>0 and first_xy is not None and last_xy is not None)
    return {
        "valid_policy":valid,
        "n_speed":len(speeds),"n_turn":len(turns),
        "endpoints":endpoints,
    }

def panel_preflight(panel):
    records,_=shape.panel_raw(panel)
    # Deliberately strip altitude field immediately. No h access below.
    slim=[{k:r[k] for k in ("cohort","iid","session","t","x","y")} for r in records]
    by_session=collections.defaultdict(list)
    for r in slim:
        by_session[(r["cohort"],r["iid"],r["session"])].append(r)

    session_meta={}
    all_endpoint=collections.defaultdict(list)
    for key,vals in sorted(by_session.items()):
        cohort,iid,sid=key
        st=session_horizontal_structure(vals)
        start=min(r["t"] for r in vals)
        session_meta[key]={**st,"start":start}
        for ep in st["endpoints"]:
            all_endpoint[cohort].append(ep)

    # Frozen broad-state thresholds = cohort medians from all horizontal endpoints.
    thresholds={}
    for cohort,eps in sorted(all_endpoint.items()):
        thresholds[cohort]={
          "speed_median":float(np.median([x["speed"] for x in eps])),
          "turn_angle_median":float(np.median([x["turn_angle"] for x in eps])),
        }

    # Build per-individual chronological sessions and odd/even sides.
    indiv=collections.defaultdict(list)
    for key,m in session_meta.items():
        cohort,iid,sid=key
        indiv[(cohort,iid)].append((sid,m))
    split={}
    for key,ss in indiv.items():
        ss=sorted(ss,key=lambda x:(x[1]["start"],str(x[0])))
        odd=[];even=[]
        for idx,(sid,m) in enumerate(ss,1):
            side="odd" if idx%2==1 else "even"
            (odd if side=="odd" else even).append((sid,m))
        split[key]={"odd":odd,"even":even,"total":len(ss)}

    eligible=[]
    summaries=[]
    for key,d in sorted(split.items()):
        cohort,iid=key
        nv_odd=sum(m["valid_policy"] for _,m in d["odd"])
        nv_even=sum(m["valid_policy"] for _,m in d["even"])
        ok=(d["total"]>=MIN_SESSIONS_TOTAL and len(d["odd"])>=MIN_SIDE_SESSIONS and len(d["even"])>=MIN_SIDE_SESSIONS
            and nv_odd>=MIN_POLICY_VALID_SIDE and nv_even>=MIN_POLICY_VALID_SIDE)
        if ok:eligible.append(key)
        summaries.append({
          "cohort":cohort,"iid":iid,"n_sessions":d["total"],
          "n_odd":len(d["odd"]),"n_even":len(d["even"]),
          "policy_valid_odd":nv_odd,"policy_valid_even":nv_even,
          "eligible":ok
        })

    eligible_set=set(eligible)

    # Count held-out endpoints by individual x side x frozen 2-km cell/state.
    counts=collections.defaultdict(collections.Counter)
    for key,d in split.items():
        if key not in eligible_set:continue
        cohort,iid=key;th=thresholds[cohort]
        for side in ("odd","even"):
            for sid,m in d[side]:
                for ep in m["endpoints"]:
                    sb=int(ep["speed"]>th["speed_median"])
                    tb=int(ep["turn_angle"]>th["turn_angle_median"])
                    state=sb*2+tb
                    cell=(math.floor(ep["x"]/GRID),math.floor(ep["y"]/GRID),state)
                    counts[(cohort,iid,side)][cell]+=1

    def pair_support(target_side):
        pairs=[]
        by_cohort=collections.defaultdict(list)
        for c,i in eligible:
            by_cohort[c].append(i)
        for cohort,ids in sorted(by_cohort.items()):
            ids=sorted(ids)
            for a in range(len(ids)):
                for b in range(a+1,len(ids)):
                    i,j=ids[a],ids[b]
                    ci=counts[(cohort,i,target_side)]
                    cj=counts[(cohort,j,target_side)]
                    shared=[s for s in (ci.keys()&cj.keys()) if ci[s]>=MIN_EVENTS_STRATUM and cj[s]>=MIN_EVENTS_STRATUM]
                    if len(shared)>=MIN_SHARED_STRATA:
                        pairs.append({"cohort":cohort,"i":i,"j":j,"n_shared_strata":len(shared)})
        return pairs

    pairs_odd=pair_support("odd")
    pairs_even=pair_support("even")
    cohorts=collections.Counter(c for c,i in eligible)
    passed=(len(eligible)>=MIN_INDIVIDUALS and len(pairs_odd)>=MIN_PAIRS and len(pairs_even)>=MIN_PAIRS)
    return {
      "panel":panel,
      "height_values_used":False,
      "n_source_records":len(slim),
      "n_sessions":len(session_meta),
      "thresholds":thresholds,
      "eligible_individuals":len(eligible),
      "eligible_by_cohort":dict(cohorts),
      "individual_summary":summaries,
      "eligible_pairs_target_odd":len(pairs_odd),
      "eligible_pairs_target_even":len(pairs_even),
      "pair_support_odd":pairs_odd,
      "pair_support_even":pairs_even,
      "verdict":"PASS_TO_VERTICAL_BRIDGE" if passed else "STOP_STRUCTURAL_SUPPORT",
    }

def main():
    out={
      "contract":"STRUCTURAL_PREFLIGHT_CONTRACT_V1.md",
      "cohort_amendment":"COHORT_STRATIFICATION_AMENDMENT_V1.md",
      "vertical_distribution_outcome_opened":False,
      "thresholds":{
        "max_dt_s":MAX_DT,"grid_m":GRID,
        "min_speed_intervals":MIN_SPEED_INTERVALS,"min_turns":MIN_TURNS,
        "min_sessions_total":MIN_SESSIONS_TOTAL,"min_side_sessions":MIN_SIDE_SESSIONS,
        "min_policy_valid_side":MIN_POLICY_VALID_SIDE,
        "min_events_stratum_each":MIN_EVENTS_STRATUM,
        "min_shared_strata_pair":MIN_SHARED_STRATA,
        "min_individuals_panel":MIN_INDIVIDUALS,"min_pairs_fold":MIN_PAIRS,
      },
      "panels":{}
    }
    for panel in PANELS:
        out["panels"][panel]=panel_preflight(panel)
    print(json.dumps(out,ensure_ascii=False,indent=2,default=str))

if __name__=="__main__":
    main()
