#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
import urllib.request

import numpy as np
from pyproj import Transformer

from batter.analysis import Event, leave_one_session_out, z_bin

URL="https://datarepository.movebank.org/server/api/core/bitstreams/a6a6db33-0aca-4902-a58d-f32980c1a3e1/content"
EXPECTED_SIZE=3630088
EXPECTED_MD5="e0f6faedfd1f21bac222d9da430ea5d8"
EXPECTED_ROWS=9873
EDGES=(-math.inf,0.0,50.0,100.0,200.0,400.0,800.0,1600.0,3200.0,math.inf)
K=len(EDGES)-1
ALPHA=0.5
MIN_SESSION=50
MIN_SCORED=50
CONTRACT=Path("contract/tadarida_residual_confounds_v1.json")

TESTS={
    "roost_1000":{"cell":5000.0,"radius":1000.0,"B":9999,"perm_seed":2026092902,"boot_B":20000,"boot_seed":2026093002},
    "roost_500":{"cell":5000.0,"radius":500.0,"B":4999,"perm_seed":2026092903,"boot_B":10000,"boot_seed":2026093002},
    "roost_2000":{"cell":5000.0,"radius":2000.0,"B":4999,"perm_seed":2026092904,"boot_B":10000,"boot_seed":2026093002},
    "grid_2500":{"cell":2500.0,"radius":None,"B":4999,"perm_seed":2026092905,"boot_B":10000,"boot_seed":2026093003},
    "grid_10000":{"cell":10000.0,"radius":None,"B":4999,"perm_seed":2026092906,"boot_B":10000,"boot_seed":2026093004},
}

GRID_TARGETS={
    "grid_2500":{"conditional":0.765597965810336,"marginal":0.09027353932570703,"advantage":0.6753244264846291,"eligible_individuals":5},
    "grid_10000":{"conditional":-0.04500055406329954,"marginal":-0.2198245415954591,"advantage":0.17482398753215955,"eligible_individuals":7},
}
TOL=1e-12
METRICS=("conditional","marginal","advantage","common_cell_marginal","common_cell_advantage")


def finite_float(x):
    try:
        y=float(x)
    except (TypeError,ValueError):
        return None
    return y if math.isfinite(y) else None


def parse_time(x):
    from datetime import datetime
    return datetime.fromisoformat(str(x).strip().replace("Z","+00:00"))


def load_rows():
    req=urllib.request.Request(URL,headers={"User-Agent":"batter-tadarida-residual-confounds-v1/1.0"})
    with urllib.request.urlopen(req,timeout=120) as response:
        data=response.read()
    if len(data)!=EXPECTED_SIZE:
        raise RuntimeError(f"source size mismatch {len(data)} != {EXPECTED_SIZE}")
    digest=hashlib.md5(data).hexdigest()
    if digest!=EXPECTED_MD5:
        raise RuntimeError(f"source md5 mismatch {digest}")
    rows=list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"),newline="")))
    if len(rows)!=EXPECTED_ROWS:
        raise RuntimeError(f"row count mismatch {len(rows)} != {EXPECTED_ROWS}")
    return rows,digest


def parsed_records(rows):
    tr=Transformer.from_crs("EPSG:4326","EPSG:3035",always_xy=True)
    rec=[]
    for row in rows:
        iid=str(row.get("animal-id","")).strip()
        day=str(row.get("BatDay","")).strip()
        lon=finite_float(row.get("location-long"))
        lat=finite_float(row.get("location-lat"))
        z=finite_float(row.get("height_true"))
        if not iid or not day or lon is None or lat is None or z is None:
            continue
        try:
            t=parse_time(row.get("timestamp",""))
        except Exception:
            continue
        x,y=tr.transform(lon,lat)
        rec.append({"iid":iid,"day":day,"session":f"{iid}::{day}","t":t,"x":x,"y":y,"z":z})
    return rec


def base_retained(records):
    counts=Counter(r["session"] for r in records)
    retained={s for s,n in counts.items() if n>=MIN_SESSION}
    return [r for r in records if r["session"] in retained],counts,retained


def endpoint_proxy(records):
    by_session=defaultdict(list)
    for r in records:
        by_session[r["session"]].append(r)
    endpoints=defaultdict(list)
    for session,vals in by_session.items():
        vals=sorted(vals,key=lambda r:r["t"])
        for r in vals[:5]+vals[-5:]:
            endpoints[r["iid"]].append((r["x"],r["y"]))
    centers={}
    endpoint_spread={}
    for iid,pts in endpoints.items():
        arr=np.asarray(pts,dtype=float)
        # Medoid: choose an observed endpoint minimizing total Euclidean distance.
        d=np.sqrt(((arr[:,None,:]-arr[None,:,:])**2).sum(axis=2))
        idx=int(np.argmin(d.sum(axis=1)))
        center=arr[idx]
        centers[iid]=(float(center[0]),float(center[1]))
        dist=np.sqrt(((arr-center)**2).sum(axis=1))
        endpoint_spread[iid]={
            "endpoint_count":int(len(arr)),
            "median_distance_to_proxy_m":float(np.median(dist)),
            "q90_distance_to_proxy_m":float(np.quantile(dist,0.9)),
        }
    return centers,endpoint_spread


def build_events(records,cell_size,radius):
    base,base_counts,base_sessions=base_retained(records)
    centers,spread=endpoint_proxy(base)
    excluded=0
    if radius is not None:
        kept=[]
        for r in base:
            cx,cy=centers[r["iid"]]
            d=math.hypot(r["x"]-cx,r["y"]-cy)
            if d < radius:
                excluded+=1
            else:
                kept.append(r)
    else:
        kept=base

    post_counts=Counter(r["session"] for r in kept)
    retained={s for s,n in post_counts.items() if n>=MIN_SESSION}
    kept=[r for r in kept if r["session"] in retained]
    events=[
        Event(
            individual=r["iid"],timestamp=r["t"],
            cell=(math.floor(r["x"]/cell_size),math.floor(r["y"]/cell_size)),
            zbin=z_bin(r["z"],edges=EDGES),session=r["session"]
        )
        for r in kept
    ]
    qc={
        "base_retained_events":len(base),
        "base_retained_sessions":len(base_sessions),
        "events_excluded_by_proxy_radius":excluded,
        "post_exclusion_events":len(events),
        "post_exclusion_sessions":len(retained),
        "post_exclusion_session_counts":dict(sorted((s,post_counts[s]) for s in retained)),
        "proxy_endpoint_spread":spread,
        "proxy_coordinates_not_written":True,
    }
    return events,qc


def make_arrays(events):
    sessions=sorted({e.session for e in events})
    individuals=sorted({e.individual for e in events})
    cells=sorted({e.cell for e in events})
    sidx={s:i for i,s in enumerate(sessions)}
    iidx={iid:i for i,iid in enumerate(individuals)}
    cidx={c:i for i,c in enumerate(cells)}
    S,I,C=len(sessions),len(individuals),len(cells)
    counts=np.zeros((S,C,K),dtype=np.int32)
    labels=np.empty(S,dtype=np.int16)
    for e in events:
        si=sidx[e.session]; ci=cidx[e.cell]
        labels[si]=iidx[e.individual]
        counts[si,ci,e.zbin]+=1
    cell_tot=counts.sum(axis=2)
    sess_cond=np.full((S,C,K),np.nan,dtype=float)
    for s in range(S):
        pc=np.flatnonzero(cell_tot[s]>0)
        if len(pc):
            sess_cond[s,pc,:]=(counts[s,pc,:]+ALPHA)/(cell_tot[s,pc,None]+ALPHA*K)
    marg_counts=counts.sum(axis=1)
    sess_marg=(marg_counts+ALPHA)/(marg_counts.sum(axis=1,keepdims=True)+ALPHA*K)
    return {"sessions":sessions,"individuals":individuals,"counts":counts,"cell_tot":cell_tot,"sess_cond":sess_cond,"sess_marg":sess_marg,"orig_labels":labels}


def mean_nan_axis0(x):
    n=np.sum(~np.isnan(x[...,0]),axis=0)
    summed=np.nansum(x,axis=0)
    out=np.full(summed.shape,np.nan,dtype=float)
    ok=n>0
    out[ok]=summed[ok]/n[ok,None]
    return out


def evaluate(A,labels):
    counts=A["counts"]; cell_tot=A["cell_tot"]; sess_cond=A["sess_cond"]; sess_marg=A["sess_marg"]
    S,C,K=counts.shape; I=len(A["individuals"])
    group_counts=np.zeros((I,C,K),dtype=np.int32)
    group_marg_counts=np.zeros((I,K),dtype=np.int32)
    for i in range(I):
        sel=np.flatnonzero(labels==i)
        if len(sel):
            group_counts[i]=counts[sel].sum(axis=0)
            group_marg_counts[i]=counts[sel].sum(axis=(0,1))
    group_cell_tot=group_counts.sum(axis=2)
    group_cond=np.full((I,C,K),np.nan,dtype=float)
    for i in range(I):
        pc=np.flatnonzero(group_cell_tot[i]>0)
        if len(pc):
            group_cond[i,pc,:]=(group_counts[i,pc,:]+ALPHA)/(group_cell_tot[i,pc,None]+ALPHA*K)
    group_marg=(group_marg_counts+ALPHA)/(group_marg_counts.sum(axis=1,keepdims=True)+ALPHA*K)

    rows=[]
    idx=np.arange(S)
    for t in range(S):
        lab=int(labels[t])
        self_sel=np.flatnonzero((labels==lab)&(idx!=t))
        if not len(self_sel):
            continue
        p_self=mean_nan_axis0(sess_cond[self_sel])
        other=np.array([i for i in range(I) if i!=lab],dtype=int)
        p_other=mean_nan_axis0(group_cond[other])
        m_self=sess_marg[self_sel].mean(axis=0)
        m_other=group_marg[other].mean(axis=0)
        supported=(cell_tot[t]>0)&(~np.isnan(p_self[:,0]))&(~np.isnan(p_other[:,0]))
        scored=int(cell_tot[t,supported].sum())
        if scored<MIN_SCORED:
            continue
        target=counts[t,supported,:].astype(float)
        tz=target.sum(axis=0)
        ps=p_self[supported,:]; po=p_other[supported,:]
        cond=float(np.sum(target*(np.log(ps)-np.log(po)))/scored)
        marg=float(np.sum(tz*(np.log(m_self)-np.log(m_other)))/scored)
        supported_idx=np.flatnonzero(supported)
        ws=[]
        for s in self_sel:
            w=cell_tot[s,supported_idx].astype(float)
            if w.sum()>0:
                ws.append(w/w.sum())
        if not ws:
            continue
        w=np.mean(np.stack(ws),axis=0); w=w/w.sum()
        sm=np.sum(ps*w[:,None],axis=0); om=np.sum(po*w[:,None],axis=0)
        cm=float(np.sum(tz*(np.log(sm)-np.log(om)))/scored)
        rows.append({
            "label":lab,"conditional":cond,"marginal":marg,"advantage":cond-marg,
            "common_cell_marginal":cm,"common_cell_advantage":cond-cm
        })
    per={}
    for lab in range(I):
        rs=[r for r in rows if r["label"]==lab]
        if rs:
            per[lab]={m:float(np.mean([r[m] for r in rs])) for m in METRICS}
            per[lab]["evaluable_sessions"]=len(rs)
    out={"eligible_individuals":len(per)}
    for m in METRICS:
        vals=[v[m] for v in per.values()]
        out[m]=float(np.mean(vals)) if vals else None
    return out,per


def null_summary(x,obs):
    a=np.asarray(x,dtype=float)
    return {
        "n":int(len(a)),"mean":float(a.mean()),"sd":float(a.std(ddof=1)),
        "q025":float(np.quantile(a,0.025)),"q50":float(np.quantile(a,0.5)),"q975":float(np.quantile(a,0.975)),
        "observed":float(obs),"observed_minus_null_mean":float(obs-a.mean()),
        "p_null_ge_observed":float((1+np.sum(a>=obs))/(len(a)+1)),
        "p_null_le_observed":float((1+np.sum(a<=obs))/(len(a)+1)),
    }


def bootstrap(per,B,seed):
    ids=sorted(per)
    mat=np.array([[per[i][m] for m in METRICS] for i in ids],dtype=float)
    rng=np.random.default_rng(seed); n=len(ids)
    draw=np.empty((B,len(METRICS)),dtype=float)
    for b in range(B):
        ix=rng.integers(0,n,size=n); draw[b]=mat[ix].mean(axis=0)
    return {m:{
        "observed":float(mat[:,j].mean()),
        "q025":float(np.quantile(draw[:,j],0.025)),
        "q50":float(np.quantile(draw[:,j],0.5)),
        "q975":float(np.quantile(draw[:,j],0.975))
    } for j,m in enumerate(METRICS)}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--test",required=True,choices=sorted(TESTS)); args=ap.parse_args()
    spec=TESTS[args.test]
    rows,digest=load_rows(); rec=parsed_records(rows)
    events,qc=build_events(rec,spec["cell"],spec["radius"])

    frozen=leave_one_session_out(events,alpha=ALPHA,minimum_scored_fixes=MIN_SCORED,n_z_bins=K)
    d=frozen["decomposition"]
    ordinary={
        "conditional":d["equal_individual_mean_conditional_identity_gain_nats_per_fix"],
        "marginal":d["equal_individual_mean_marginal_identity_gain_nats_per_fix"],
        "advantage":d["equal_individual_mean_identity_x_location_gain_nats_per_fix"],
        "eligible_individuals":frozen["eligible_individual_count"],
    }
    if args.test in GRID_TARGETS:
        exp=GRID_TARGETS[args.test]
        for m in ("conditional","marginal","advantage"):
            if abs(ordinary[m]-exp[m])>TOL:
                raise RuntimeError(f"frozen grid mismatch {m}: {ordinary[m]} != {exp[m]}")
        if ordinary["eligible_individuals"]!=exp["eligible_individuals"]:
            raise RuntimeError("frozen grid eligible-individual mismatch")

    A=make_arrays(events)
    observed,per=evaluate(A,A["orig_labels"])
    for m in ("conditional","marginal","advantage"):
        if abs(observed[m]-ordinary[m])>TOL:
            raise RuntimeError(f"optimized evaluator mismatch {m}: {observed[m]} != {ordinary[m]}")

    rng=np.random.default_rng(spec["perm_seed"]); slots=A["orig_labels"].copy()
    null={m:[] for m in METRICS}; eligible=[]
    for _ in range(spec["B"]):
        s,_=evaluate(A,rng.permutation(slots)); eligible.append(s["eligible_individuals"])
        for m in METRICS: null[m].append(s[m])
    cal={m:null_summary(null[m],observed[m]) for m in METRICS}
    boot=bootstrap(per,spec["boot_B"],spec["boot_seed"])
    primary=cal["common_cell_marginal"]
    passed=(observed["eligible_individuals"]>=5 and primary["observed_minus_null_mean"]>0 and primary["p_null_ge_observed"]<=0.05)

    payload={
        "study_id":"batter-tadarida-residual-confounds-v1",
        "test_id":args.test,
        "source_md5":digest,
        "spec":spec,
        "qc":qc,
        "ordinary":ordinary,
        "observed":observed,
        "permutation":{"calibration":cal,"eligible_individual_count": {
            "observed":observed["eligible_individuals"],"mean":float(np.mean(eligible)),
            "min":int(np.min(eligible)),"max":int(np.max(eligible)),
            "q025":float(np.quantile(eligible,0.025)),"q50":float(np.quantile(eligible,0.5)),"q975":float(np.quantile(eligible,0.975))
        }},
        "individual_bootstrap":{"percentile_95_interval":boot},
        "primary_pass_rule":{
            "minimum_evaluable_individuals_5":observed["eligible_individuals"]>=5,
            "calibrated_common_cell_marginal_positive":primary["observed_minus_null_mean"]>0,
            "upper_tail_le_0_05":primary["p_null_ge_observed"]<=0.05,
            "passes":passed
        },
        "claim_boundary":{
            "post_freeze_robustness":True,
            "decision_rules_frozen_in":"contract/tadarida_residual_confounds_v1.json",
            "proxy_is_not_verified_roost":spec["radius"] is not None,
        }
    }
    out=Path(f"results/tadarida_residual_confounds_{args.test}_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "test":args.test,"qc":qc,"ordinary":ordinary,"observed":observed,
        "common_cell_marginal_calibration":cal["common_cell_marginal"],
        "common_cell_advantage_calibration":cal["common_cell_advantage"],
        "bootstrap_common_cell_marginal":boot["common_cell_marginal"],
        "pass_rule":payload["primary_pass_rule"]
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
