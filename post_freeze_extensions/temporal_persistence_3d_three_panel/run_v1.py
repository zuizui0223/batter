#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, math, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from batter.analysis import Event, z_bin
import scripts.run_cross_panel_estimator_calibration as cal
import scripts.run_tag_altitude_bias_shape as shape

CONTRACT=ROOT/"post_freeze_extensions/temporal_persistence_3d_three_panel/contract_v1.json"
OUT=ROOT/"post_freeze_extensions/temporal_persistence_3d_three_panel/result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/temporal_persistence_3d_three_panel/RESULT_V1.md"
EDGES=(-math.inf,-400.0,-200.0,-100.0,-50.0,0.0,50.0,100.0,200.0,400.0,math.inf)
K=len(EDGES)-1
ALPHA=0.5

def turn_angle(a,b,c):
    v1x,v1y=b["x"]-a["x"],b["y"]-a["y"]
    v2x,v2y=c["x"]-b["x"],c["y"]-b["y"]
    n1=math.hypot(v1x,v1y);n2=math.hypot(v2x,v2y)
    if n1<=0 or n2<=0:
        return None
    z=max(-1.0,min(1.0,(v1x*v2x+v1y*v2y)/(n1*n2)))
    return math.acos(z)

def median_timestamp(vals):
    ts=sorted(vals)
    n=len(ts)
    if n%2:
        return ts[n//2]
    return ts[n//2-1]+(ts[n//2]-ts[n//2-1])/2

def build_events(panel,c):
    records,source=shape.panel_raw(panel)
    by_session=defaultdict(list)
    for r in records:
        by_session[(r["cohort"],r["session"])].append(r)

    height_medians={}
    raw=[]
    max_dt=int(c["state_definition"]["maximum_step_interval_seconds"])
    for key,vals in sorted(by_session.items()):
        vals=sorted(vals,key=lambda x:x["t"])
        height_medians[key]=float(np.median([r["h"] for r in vals]))
        for i in range(2,len(vals)):
            a,b,d=vals[i-2],vals[i-1],vals[i]
            dt1=(b["t"]-a["t"]).total_seconds()
            dt2=(d["t"]-b["t"]).total_seconds()
            if not all(math.isfinite(x) and x>0 and x<=max_dt for x in (dt1,dt2)):
                continue
            tr=turn_angle(a,b,d)
            if tr is None:
                continue
            sp=math.hypot(d["x"]-b["x"],d["y"]-b["y"])/dt2
            raw.append({
                "cohort":d["cohort"],"session":d["session"],"iid":d["iid"],
                "t":d["t"],"x":d["x"],"y":d["y"],"h":d["h"],
                "speed":float(sp),"turn":float(tr)
            })

    speeds=defaultdict(list);turns=defaultdict(list)
    for r in raw:
        speeds[r["cohort"]].append(r["speed"])
        turns[r["cohort"]].append(r["turn"])
    thresholds={cohort:{
        "speed":float(np.median(np.asarray(speeds[cohort],dtype=float))),
        "turn":float(np.median(np.asarray(turns[cohort],dtype=float)))
    } for cohort in speeds}

    events=defaultdict(list)
    times=defaultdict(lambda:defaultdict(list))
    grid=float(c["state_definition"]["horizontal_cell_m"])
    for r in raw:
        th=thresholds[r["cohort"]]
        state=int(r["speed"]>th["speed"])*2+int(r["turn"]>th["turn"])
        cell=(math.floor(r["x"]/grid),math.floor(r["y"]/grid),state)
        med=height_medians[(r["cohort"],r["session"])]
        zb=z_bin(float(r["h"]-med),edges=EDGES)
        events[r["cohort"]].append(Event(
            individual=r["iid"],timestamp=r["t"],cell=cell,zbin=zb,session=r["session"]
        ))
        times[r["cohort"]][r["session"]].append(r["t"])

    session_mid={
        cohort:{sid:median_timestamp(ts) for sid,ts in smap.items()}
        for cohort,smap in times.items()
    }
    return dict(events),session_mid,{
        "source":source,
        "cohort_thresholds":thresholds,
        "valid_kinematic_endpoints":len(raw),
        "session_count":len(by_session)
    }

def mean_nan_axis0(x):
    present=~np.isnan(x[...,0])
    n=present.sum(axis=0)
    summed=np.nansum(x,axis=0)
    out=np.full(summed.shape,np.nan,dtype=float)
    ok=n>0
    out[ok]=summed[ok]/n[ok,None]
    return out

def eval_cohort_lag(A,labels,times_s,cohort_name,lag_seconds,min_scored):
    counts=A["counts"];cell_tot=A["cell_tot"];sess_cond=A["sess_cond"]
    S,C,K2=counts.shape
    L=len(A["label_names"])

    group_counts=np.zeros((L,C,K2),dtype=np.int32)
    for lab in range(L):
        sel=np.flatnonzero(labels==lab)
        if len(sel):
            group_counts[lab]=counts[sel].sum(axis=0)
    group_tot=group_counts.sum(axis=2)
    group_cond=np.full((L,C,K2),np.nan,dtype=float)
    for lab in range(L):
        pc=np.flatnonzero(group_tot[lab]>0)
        if len(pc):
            group_cond[lab,pc,:]=(group_counts[lab,pc,:]+ALPHA)/(group_tot[lab,pc,None]+ALPHA*K2)

    rows=[]
    idx=np.arange(S)
    for t in range(S):
        lab=int(labels[t])
        lag_ok=np.abs(times_s-times_s[t])>=lag_seconds
        self_sel=np.flatnonzero((labels==lab)&(idx!=t)&lag_ok)
        if len(self_sel)==0:
            continue
        other_idx=np.array([x for x in range(L) if x!=lab],dtype=int)
        if len(other_idx)==0:
            continue

        p_self=mean_nan_axis0(sess_cond[self_sel])
        p_other=mean_nan_axis0(group_cond[other_idx])
        target_tot=cell_tot[t]
        supported=(target_tot>0)&(~np.isnan(p_self[:,0]))&(~np.isnan(p_other[:,0]))
        scored=int(target_tot[supported].sum())
        if scored<min_scored:
            continue

        target_counts=counts[t,supported,:].astype(float)
        target_z=target_counts.sum(axis=0)
        ps=p_self[supported,:];po=p_other[supported,:]
        supported_idx=np.flatnonzero(supported)

        ws=[]
        for s in self_sel:
            w=cell_tot[s,supported_idx].astype(float)
            tot=w.sum()
            if tot>0:
                ws.append(w/tot)
        if not ws:
            continue
        w=np.mean(np.stack(ws),axis=0)
        w=w/w.sum()
        m_self=np.sum(ps*w[:,None],axis=0)
        m_other=np.sum(po*w[:,None],axis=0)
        score=float(np.sum(target_z*(np.log(m_self)-np.log(m_other)))/scored)

        rows.append({
            "cohort":cohort_name,
            "session":A["sessions"][t],
            "individual":A["label_names"][lab],
            "scored_fixes":scored,
            "lag_qualified_self_sessions":len(self_sel),
            "minimum_qualified_lag_days":float(np.min(np.abs(times_s[self_sel]-times_s[t]))/86400.0),
            "common_cell_marginal":score
        })
    return rows

def aggregate(rows):
    per={}
    for iid in sorted({r["individual"] for r in rows}):
        rs=[r for r in rows if r["individual"]==iid]
        if rs:
            per[iid]={
                "evaluable_sessions":len(rs),
                "mean_common_cell_marginal":float(np.mean([r["common_cell_marginal"] for r in rs])),
                "minimum_qualified_lag_days":float(min(r["minimum_qualified_lag_days"] for r in rs))
            }
    vals=[v["mean_common_cell_marginal"] for v in per.values()]
    return {
        "eligible_individuals":len(vals),
        "common_cell_marginal":float(np.mean(vals)) if vals else None
    },per

def eval_panel(arrays,time_arrays,labels_by_cohort,lag_seconds,min_scored):
    rows=[]
    for cohort,A in arrays.items():
        rows.extend(eval_cohort_lag(A,labels_by_cohort[cohort],time_arrays[cohort],cohort,lag_seconds,min_scored))
    out,per=aggregate(rows)
    return out,per,rows

def run_panel(panel,c):
    events_by_cohort,session_mid,diag=build_events(panel,c)
    arrays={cohort:cal.make_cohort_arrays(events,K) for cohort,events in sorted(events_by_cohort.items())}
    time_arrays={}
    for cohort,A in arrays.items():
        epoch=A["sessions"]
        mids=session_mid[cohort]
        time_arrays[cohort]=np.asarray([mids[s].timestamp() for s in epoch],dtype=float)

    labels_obs={cohort:A["orig_labels"] for cohort,A in arrays.items()}
    lag_seconds=float(c["subset"]["minimum_self_lag_days"])*86400.0
    min_scored=int(c["estimator"]["minimum_scored_target_events"])
    observed,per_ind,session_rows=eval_panel(arrays,time_arrays,labels_obs,lag_seconds,min_scored)
    expected=int(c["subset"]["expected_evaluable_individuals"][panel])
    if observed["eligible_individuals"]!=expected:
        raise RuntimeError(f"{panel}: observed n {observed['eligible_individuals']} != expected {expected}")

    setting={x["panel"]:x for x in c["calibration"]["settings"]}[panel]
    rng=np.random.default_rng(int(setting["seed"]))
    null=[];eligible=[];invalid=0
    for _ in range(int(setting["B"])):
        labels_perm={cohort:rng.permutation(A["orig_labels"]) for cohort,A in arrays.items()}
        p,_,_=eval_panel(arrays,time_arrays,labels_perm,lag_seconds,min_scored)
        if p["eligible_individuals"]<1 or p["common_cell_marginal"] is None:
            invalid+=1;continue
        null.append(float(p["common_cell_marginal"]))
        eligible.append(int(p["eligible_individuals"]))
    cali=cal.tail_summary(null,float(observed["common_cell_marginal"]))
    passed=(cali["observed_minus_null_mean"]>0 and cali["p_null_ge_observed"]<=0.05)

    return {
        "schema_version":1,"study_id":c["study_id"],"panel":panel,
        "diagnostics":diag,
        "observed":{**observed,"individual_results":per_ind,"session_results":session_rows},
        "permutation":{
            "B":int(setting["B"]),"seed":int(setting["seed"]),
            "valid_replicates":len(null),"invalid_replicates":invalid,
            "eligible_individual_count_min":int(min(eligible)),
            "eligible_individual_count_max":int(max(eligible)),
            "lagged_identity":cali
        },
        "primary_verdict":{
            "expected_evaluable_individuals":expected,
            "exact_n_met":True,
            "calibrated_identity_positive":cali["observed_minus_null_mean"]>0,
            "upper_tail_le_0_05":cali["p_null_ge_observed"]<=0.05,
            "pass":bool(passed)
        },
        "claim_boundary":c["claim_boundary"]
    }

def aggregate_panels(c,panel_dir):
    panels={}
    for p in c["subset"]["included_panels"]:
        path=panel_dir/f"panel_{p}_v1.json"
        if not path.exists():
            raise RuntimeError(f"missing {path}")
        panels[p]=json.loads(path.read_text())
    n=sum(int(v["primary_verdict"]["pass"]) for v in panels.values())
    cat="3_pass" if n==3 else ("1_or_2_pass" if n>=1 else "0_pass")
    return {
        "schema_version":1,"study_id":c["study_id"],"submission_claims_unchanged":True,
        "panels":panels,
        "synthesis":{"pass_count":n,"panel_count":len(panels),"category":cat,"interpretation":c["synthesis"]["decision_matrix"][cat]},
        "claim_boundary":c["claim_boundary"],"stop_rule":c["stop_rule"]
    }

def markdown(payload):
    s=payload["synthesis"]
    lines=["# Three-panel >=3-day temporal persistence stress test v1","",
           "**POST-FREEZE STRUCTURALLY-EVALUABLE SUBSET TEST. No inference to Eidolon.**","",
           f"- passing panels: **{s['pass_count']}/{s['panel_count']}**",
           f"- synthesis: **{s['category']}**","",
           "| panel | n | calibrated excess | p(null >= observed) | pass |",
           "|---|---:|---:|---:|---:|"]
    for p,v in payload["panels"].items():
        x=v["permutation"]["lagged_identity"]
        lines.append(f"| {p} | {v['observed']['eligible_individuals']} | {x['observed_minus_null_mean']:+.3f} | {x['p_null_ge_observed']:.4f} | {'PASS' if v['primary_verdict']['pass'] else 'FAIL'} |")
    lines += ["","## Interpretation","",s["interpretation"],""]
    return "\n".join(lines)

def main():
    ap=argparse.ArgumentParser()
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--panel")
    g.add_argument("--aggregate",action="store_true")
    ap.add_argument("--panel-dir",default="post_freeze_extensions/temporal_persistence_3d_three_panel/panel_results")
    args=ap.parse_args()
    c=json.loads(CONTRACT.read_text())
    panel_dir=ROOT/args.panel_dir
    if args.panel:
        if args.panel not in c["subset"]["included_panels"]:
            raise SystemExit("unknown panel")
        payload=run_panel(args.panel,c)
        panel_dir.mkdir(parents=True,exist_ok=True)
        (panel_dir/f"panel_{args.panel}_v1.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
        x=payload["permutation"]["lagged_identity"]
        print(json.dumps({
            "panel":args.panel,"n":payload["observed"]["eligible_individuals"],
            "calibrated_excess":x["observed_minus_null_mean"],
            "p_upper":x["p_null_ge_observed"],"pass":payload["primary_verdict"]["pass"]
        },sort_keys=True))
        return 0
    payload=aggregate_panels(c,panel_dir)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    OUT_MD.write_text(markdown(payload))
    print(json.dumps({
        "pass_count":payload["synthesis"]["pass_count"],
        "category":payload["synthesis"]["category"],
        "panels":{p:{
            "calibrated_excess":v["permutation"]["lagged_identity"]["observed_minus_null_mean"],
            "p_upper":v["permutation"]["lagged_identity"]["p_null_ge_observed"],
            "pass":v["primary_verdict"]["pass"]
        } for p,v in payload["panels"].items()}
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
