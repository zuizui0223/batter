#!/usr/bin/env python3
from __future__ import annotations

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
CELL_SIZE=5000.0
MIN_SESSION=50
MIN_SCORED=50
N_PERM=9999
PERM_SEED=20260927
N_BOOT=20000
BOOT_SEED=20260928
OBS_TARGET={
    "conditional":0.42804057006673096,
    "marginal":0.052484319998149565,
    "advantage":0.37555625006858145,
    "eligible_individuals":6,
}
TOL=1e-12


def finite_float(x):
    try:
        y=float(x)
    except (TypeError,ValueError):
        return None
    return y if math.isfinite(y) else None


def parse_events(rows):
    tr=Transformer.from_crs("EPSG:4326","EPSG:3035",always_xy=True)
    counts=Counter()
    parsed=[]
    for row in rows:
        iid=str(row.get("animal-id","")).strip()
        batday=str(row.get("BatDay","")).strip()
        lon=finite_float(row.get("location-long"))
        lat=finite_float(row.get("location-lat"))
        z=finite_float(row.get("height-above-msl"))
        if not iid or not batday or lon is None or lat is None or z is None:
            continue
        x,y=tr.transform(lon,lat)
        session=f"{iid}::{batday}"
        counts[session]+=1
        parsed.append((iid,session,(math.floor(x/CELL_SIZE),math.floor(y/CELL_SIZE)),z_bin(z,edges=EDGES)))
    retained={s for s,n in counts.items() if n>=MIN_SESSION}
    events=[
        Event(individual=iid,timestamp=None,cell=cell,zbin=zb,session=session)
        for iid,session,cell,zb in parsed if session in retained
    ]
    return events,counts,retained


def frozen_observed(events):
    return leave_one_session_out(
        events,
        alpha=ALPHA,
        minimum_scored_fixes=MIN_SCORED,
        n_z_bins=K,
    )


def make_arrays(events):
    sessions=sorted({e.session for e in events})
    individuals=sorted({e.individual for e in events})
    sidx={s:i for i,s in enumerate(sessions)}
    iidx={iid:i for i,iid in enumerate(individuals)}
    cells=sorted({e.cell for e in events})
    cidx={c:i for i,c in enumerate(cells)}
    S,I,C=len(sessions),len(individuals),len(cells)
    counts=np.zeros((S,C,K),dtype=np.int32)
    orig_labels=np.empty(S,dtype=np.int16)
    for s in sessions:
        ev=[e for e in events if e.session==s]
        orig_labels[sidx[s]]=iidx[ev[0].individual]
        for e in ev:
            counts[sidx[s],cidx[e.cell],e.zbin]+=1

    cell_tot=counts.sum(axis=2)
    sess_cond=np.full((S,C,K),np.nan,dtype=np.float64)
    present=cell_tot>0
    for s in range(S):
        pc=np.where(present[s])[0]
        if len(pc):
            sess_cond[s,pc,:]=(counts[s,pc,:]+ALPHA)/(cell_tot[s,pc,None]+ALPHA*K)

    marg_counts=counts.sum(axis=1)
    sess_marg=(marg_counts+ALPHA)/(marg_counts.sum(axis=1,keepdims=True)+ALPHA*K)
    return {
        "sessions":sessions,
        "individuals":individuals,
        "cells":cells,
        "counts":counts,
        "cell_tot":cell_tot,
        "sess_cond":sess_cond,
        "sess_marg":sess_marg,
        "orig_labels":orig_labels,
    }


def mean_nan_axis0(x):
    n=np.sum(~np.isnan(x[...,0]),axis=0)
    summed=np.nansum(x,axis=0)
    out=np.full(summed.shape,np.nan,dtype=float)
    ok=n>0
    out[ok]=summed[ok]/n[ok,None]
    return out


def evaluate_assignment(A, labels):
    counts=A["counts"]
    cell_tot=A["cell_tot"]
    sess_cond=A["sess_cond"]
    sess_marg=A["sess_marg"]
    S,C,K=counts.shape
    I=len(A["individuals"])

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

    session_rows=[]
    for t in range(S):
        lab=int(labels[t])
        self_sel=np.flatnonzero((labels==lab) & (np.arange(S)!=t))
        if len(self_sel)==0:
            continue

        p_self=mean_nan_axis0(sess_cond[self_sel])
        other_idx=np.array([i for i in range(I) if i!=lab],dtype=int)
        p_other=mean_nan_axis0(group_cond[other_idx])
        p_self_marg=sess_marg[self_sel].mean(axis=0)
        p_other_marg=group_marg[other_idx].mean(axis=0)

        target_cell_tot=cell_tot[t]
        supported=(target_cell_tot>0) & (~np.isnan(p_self[:,0])) & (~np.isnan(p_other[:,0]))
        scored=int(target_cell_tot[supported].sum())
        if scored<MIN_SCORED:
            continue

        target_counts=counts[t,supported,:].astype(float)
        ps=p_self[supported,:]
        po=p_other[supported,:]
        cond_sum=float(np.sum(target_counts*(np.log(ps)-np.log(po))))

        target_z=target_counts.sum(axis=0)
        marg_sum=float(np.sum(target_z*(np.log(p_self_marg)-np.log(p_other_marg))))
        g_cond=cond_sum/scored
        g_marg=marg_sum/scored
        g_adv=g_cond-g_marg

        # Equal-session self cell-use weights over cells supported by both predictors.
        per_session_weights=[]
        supported_idx=np.flatnonzero(supported)
        for s in self_sel:
            w=cell_tot[s,supported_idx].astype(float)
            tot=w.sum()
            if tot>0:
                per_session_weights.append(w/tot)
        if not per_session_weights:
            continue
        w=np.mean(np.stack(per_session_weights),axis=0)
        w=w/w.sum()
        m_self_w=np.sum(ps*w[:,None],axis=0)
        m_other_w=np.sum(po*w[:,None],axis=0)
        rw_sum=float(np.sum(target_z*(np.log(m_self_w)-np.log(m_other_w))))
        g_marg_w=rw_sum/scored
        g_adv_w=g_cond-g_marg_w

        session_rows.append({
            "session_index":t,
            "label":lab,
            "scored_fixes":scored,
            "conditional":g_cond,
            "marginal":g_marg,
            "advantage":g_adv,
            "common_cell_marginal":g_marg_w,
            "common_cell_advantage":g_adv_w,
        })

    metric_names=["conditional","marginal","advantage","common_cell_marginal","common_cell_advantage"]
    per_label={}
    for lab in range(I):
        rows=[r for r in session_rows if r["label"]==lab]
        if not rows:
            continue
        per_label[lab]={
            m:float(np.mean([r[m] for r in rows]))
            for m in metric_names
        }
        per_label[lab]["evaluable_sessions"]=len(rows)

    summary={"eligible_individuals":len(per_label)}
    for m in metric_names:
        vals=[v[m] for v in per_label.values()]
        summary[m]=float(np.mean(vals)) if vals else None

    return summary,per_label,session_rows


def null_summary(values, observed):
    x=np.asarray(values,dtype=float)
    return {
        "n":int(x.size),
        "mean":float(x.mean()),
        "sd":float(x.std(ddof=1)),
        "q025":float(np.quantile(x,0.025)),
        "q50":float(np.quantile(x,0.5)),
        "q975":float(np.quantile(x,0.975)),
        "observed":float(observed),
        "observed_minus_null_mean":float(observed-x.mean()),
        "p_null_ge_observed":float((1+np.sum(x>=observed))/(x.size+1)),
    }


def bootstrap_ci(per_label):
    ids=sorted(per_label)
    metrics=["conditional","marginal","advantage","common_cell_marginal","common_cell_advantage"]
    mat=np.array([[per_label[i][m] for m in metrics] for i in ids],dtype=float)
    rng=np.random.default_rng(BOOT_SEED)
    draws=np.empty((N_BOOT,len(metrics)),dtype=float)
    n=len(ids)
    for b in range(N_BOOT):
        ix=rng.integers(0,n,size=n)
        draws[b]=mat[ix].mean(axis=0)
    return {
        m:{
            "observed":float(mat[:,j].mean()),
            "q025":float(np.quantile(draws[:,j],0.025)),
            "q50":float(np.quantile(draws[:,j],0.5)),
            "q975":float(np.quantile(draws[:,j],0.975)),
        }
        for j,m in enumerate(metrics)
    }


def main():
    req=urllib.request.Request(URL,headers={"User-Agent":"batter-tadarida-estimator-calibration-v1/1.0"})
    with urllib.request.urlopen(req,timeout=120) as response:
        data=response.read()
    if len(data)!=EXPECTED_SIZE:
        raise RuntimeError(f"source size mismatch: {len(data)} != {EXPECTED_SIZE}")
    digest=hashlib.md5(data).hexdigest()
    if digest!=EXPECTED_MD5:
        raise RuntimeError(f"source md5 mismatch: {digest}")
    rows=list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"),newline="")))
    if len(rows)!=EXPECTED_ROWS:
        raise RuntimeError(f"row count mismatch: {len(rows)} != {EXPECTED_ROWS}")

    events,raw_counts,retained=parse_events(rows)
    frozen=frozen_observed(events)
    d=frozen["decomposition"]
    legacy={
        "conditional":d["equal_individual_mean_conditional_identity_gain_nats_per_fix"],
        "marginal":d["equal_individual_mean_marginal_identity_gain_nats_per_fix"],
        "advantage":d["equal_individual_mean_identity_x_location_gain_nats_per_fix"],
        "eligible_individuals":frozen["eligible_individual_count"],
    }
    for key in ("conditional","marginal","advantage"):
        if abs(legacy[key]-OBS_TARGET[key])>TOL:
            raise RuntimeError(f"frozen observed mismatch {key}: {legacy[key]} vs {OBS_TARGET[key]}")
    if legacy["eligible_individuals"]!=OBS_TARGET["eligible_individuals"]:
        raise RuntimeError("frozen observed eligible-individual mismatch")

    A=make_arrays(events)
    observed,per_label,session_rows=evaluate_assignment(A,A["orig_labels"])
    for key in ("conditional","marginal","advantage"):
        if abs(observed[key]-OBS_TARGET[key])>TOL:
            raise RuntimeError(f"optimized evaluator mismatch {key}: {observed[key]} vs {OBS_TARGET[key]}")
    if observed["eligible_individuals"]!=OBS_TARGET["eligible_individuals"]:
        raise RuntimeError("optimized evaluator eligible-individual mismatch")

    rng=np.random.default_rng(PERM_SEED)
    slots=A["orig_labels"].copy()
    null={m:[] for m in ["conditional","marginal","advantage","common_cell_marginal","common_cell_advantage"]}
    eligible=[]
    invalid=0
    for _ in range(N_PERM):
        labels=rng.permutation(slots)
        summ,_,_=evaluate_assignment(A,labels)
        if summ["eligible_individuals"]<1:
            invalid+=1
            continue
        eligible.append(summ["eligible_individuals"])
        for m in null:
            null[m].append(summ[m])

    calibration={
        m:null_summary(null[m],observed[m])
        for m in null
    }
    elig=np.asarray(eligible,dtype=int)
    eligible_summary={
        "valid_permutations":int(len(eligible)),
        "invalid_permutations":int(invalid),
        "mean":float(elig.mean()),
        "min":int(elig.min()),
        "max":int(elig.max()),
        "q025":float(np.quantile(elig,0.025)),
        "q50":float(np.quantile(elig,0.5)),
        "q975":float(np.quantile(elig,0.975)),
    }

    label_names=A["individuals"]
    observed_individuals={
        label_names[i]:v for i,v in sorted(per_label.items())
    }
    payload={
        "study_id":"batter-tadarida-estimator-calibration-v1",
        "status":"post-freeze diagnostic calibration; frozen before calibration output",
        "source":{
            "bytes":len(data),
            "md5":digest,
            "rows":len(rows),
            "retained_events":len(events),
            "retained_sessions":len(retained),
            "session_count_by_original_individual":{
                iid:int(np.sum(A["orig_labels"]==i))
                for i,iid in enumerate(A["individuals"])
            },
        },
        "frozen_observed_consistency":legacy,
        "observed":{
            **observed,
            "individual_results":observed_individuals,
            "session_results":session_rows,
        },
        "permutation":{
            "B":N_PERM,
            "seed":PERM_SEED,
            "unit":"whole session block",
            "calibration":calibration,
            "eligible_individual_count_distribution":eligible_summary,
        },
        "individual_bootstrap":{
            "B":N_BOOT,
            "seed":BOOT_SEED,
            "percentile_95_interval":bootstrap_ci(per_label),
        },
        "diagnostic_decomposition":{
            "ordinary_marginal_minus_common_cell_marginal":
                observed["marginal"]-observed["common_cell_marginal"],
            "ordinary_advantage_minus_common_cell_advantage":
                observed["advantage"]-observed["common_cell_advantage"],
        },
        "claim_boundary":{
            "primary_endpoint_unchanged":True,
            "post_hoc_diagnostic_not_original_preregistration":True,
            "cannot_rescue_frozen_primary":True,
            "may_weaken_or_qualify_manuscript":True,
            "roost_exclusion_not_part_of_v1":True,
        },
    }

    out=Path("results/tadarida_estimator_calibration_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    summary={
        "observed":{k:observed[k] for k in [
            "eligible_individuals","conditional","marginal","advantage",
            "common_cell_marginal","common_cell_advantage"
        ]},
        "calibration":calibration,
        "eligible_null":eligible_summary,
        "bootstrap":payload["individual_bootstrap"],
        "diagnostic_decomposition":payload["diagnostic_decomposition"],
    }
    print(json.dumps(summary,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
