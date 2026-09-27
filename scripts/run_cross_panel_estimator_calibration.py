#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import math
from collections import defaultdict
from pathlib import Path
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_new_species_replications as core
import scripts.run_eidolon_independent_replication as eid

CFG_PATH=Path("contract/cross_panel_estimator_calibration_v1.json")
ALPHA=0.5
MIN_SCORED=50
CELL_SIZE=5000.0
N_PERM=4999
N_BOOT=10000


def load_cfg():
    cfg=json.loads(CFG_PATH.read_text(encoding="utf-8"))
    return cfg,{p["id"]:p for p in cfg["panels"]}


def load_panel(panel_id):
    cfg,panels=load_cfg()
    spec=panels[panel_id]

    if panel_id=="eidolon":
        gps=eid.get(eid.GPS_URL,eid.GPS_MD5,eid.GPS_SIZE)
        ref=eid.get(eid.REF_URL,eid.REF_MD5)
        rows=eid.read_csv(gps)
        refs=eid.read_csv(ref)
        pre=eid.build_pre_numeric(rows,refs)
        events_by_cohort,numeric_failures=eid.build_events(rows,pre,CELL_SIZE)
        edges=eid.EDGES
        source={
            "gps_md5":eid.GPS_MD5,
            "reference_md5":eid.REF_MD5,
            "gps_rows":len(rows),
        }
        return spec,events_by_cohort,len(edges)-1,source,pre,numeric_failures

    path=Path(spec["contract"])
    contract=json.loads(path.read_text(encoding="utf-8"))
    if panel_id=="phyllostomus_2016":
        c=copy.deepcopy(contract)
        c["vertical"]={
            "field":contract["vertical"]["primary_field"],
            "primary_edges_m":contract["vertical"]["edges_m"],
        }
        contract=c

    ua="batter-cross-panel-estimator-calibration-v1/1.0"
    gps=core.get(contract["source"]["gps"],ua)
    ref=core.get(contract["source"]["reference"],ua)
    rows,headers=core.read_csv(gps)
    refs,_=core.read_csv(ref)
    pre=core.build_pre_numeric(rows,headers,refs,contract)
    events_by_cohort,numeric_failures=core.build_events(rows,pre,contract,CELL_SIZE)
    edges=core.parse_edges(contract["vertical"]["primary_edges_m"])
    source={
        "gps_md5":contract["source"]["gps"]["md5"],
        "reference_md5":contract["source"]["reference"]["md5"],
        "gps_rows":len(rows),
    }
    return spec,events_by_cohort,len(edges)-1,source,pre,numeric_failures


def make_cohort_arrays(events,k):
    sessions=sorted({e.session for e in events})
    labels=sorted({e.individual for e in events})
    cells=sorted({e.cell for e in events})
    sidx={s:i for i,s in enumerate(sessions)}
    lidx={x:i for i,x in enumerate(labels)}
    cidx={c:i for i,c in enumerate(cells)}
    S,L,C=len(sessions),len(labels),len(cells)
    counts=np.zeros((S,C,k),dtype=np.int32)
    orig=np.empty(S,dtype=np.int16)
    for e in events:
        si=sidx[e.session]
        orig[si]=lidx[e.individual]
        counts[si,cidx[e.cell],e.zbin]+=1

    cell_tot=counts.sum(axis=2)
    sess_cond=np.full((S,C,k),np.nan,dtype=float)
    for s in range(S):
        pc=np.flatnonzero(cell_tot[s]>0)
        if len(pc):
            sess_cond[s,pc,:]=(counts[s,pc,:]+ALPHA)/(cell_tot[s,pc,None]+ALPHA*k)
    marg_counts=counts.sum(axis=1)
    sess_marg=(marg_counts+ALPHA)/(marg_counts.sum(axis=1,keepdims=True)+ALPHA*k)
    return {
        "sessions":sessions,"label_names":labels,"cells":cells,
        "counts":counts,"cell_tot":cell_tot,
        "sess_cond":sess_cond,"sess_marg":sess_marg,
        "orig_labels":orig,"k":k,
    }


def mean_nan_axis0(x):
    # x: units x cells x k
    present=~np.isnan(x[...,0])
    n=present.sum(axis=0)
    summed=np.nansum(x,axis=0)
    out=np.full(summed.shape,np.nan,dtype=float)
    ok=n>0
    out[ok]=summed[ok]/n[ok,None]
    return out


def eval_cohort(A,labels,cohort_name):
    counts=A["counts"]; cell_tot=A["cell_tot"]
    sess_cond=A["sess_cond"]; sess_marg=A["sess_marg"]
    S,C,K=counts.shape
    L=len(A["label_names"])

    group_counts=np.zeros((L,C,K),dtype=np.int32)
    group_marg_counts=np.zeros((L,K),dtype=np.int32)
    for lab in range(L):
        sel=np.flatnonzero(labels==lab)
        if len(sel):
            group_counts[lab]=counts[sel].sum(axis=0)
            group_marg_counts[lab]=counts[sel].sum(axis=(0,1))

    group_cell_tot=group_counts.sum(axis=2)
    group_cond=np.full((L,C,K),np.nan,dtype=float)
    for lab in range(L):
        pc=np.flatnonzero(group_cell_tot[lab]>0)
        if len(pc):
            group_cond[lab,pc,:]=(group_counts[lab,pc,:]+ALPHA)/(group_cell_tot[lab,pc,None]+ALPHA*K)
    group_marg=(group_marg_counts+ALPHA)/(group_marg_counts.sum(axis=1,keepdims=True)+ALPHA*K)

    rows=[]
    idx_all=np.arange(S)
    for t in range(S):
        lab=int(labels[t])
        self_sel=np.flatnonzero((labels==lab)&(idx_all!=t))
        if len(self_sel)==0:
            continue

        p_self=mean_nan_axis0(sess_cond[self_sel])
        other_idx=np.array([x for x in range(L) if x!=lab],dtype=int)
        if len(other_idx)==0:
            continue
        p_other=mean_nan_axis0(group_cond[other_idx])
        p_self_marg=sess_marg[self_sel].mean(axis=0)
        p_other_marg=group_marg[other_idx].mean(axis=0)

        target_cell_tot=cell_tot[t]
        supported=(target_cell_tot>0)&(~np.isnan(p_self[:,0]))&(~np.isnan(p_other[:,0]))
        scored=int(target_cell_tot[supported].sum())
        if scored<MIN_SCORED:
            continue

        target_counts=counts[t,supported,:].astype(float)
        target_z=target_counts.sum(axis=0)
        ps=p_self[supported,:]; po=p_other[supported,:]

        g_cond=float(np.sum(target_counts*(np.log(ps)-np.log(po)))/scored)
        g_marg=float(np.sum(target_z*(np.log(p_self_marg)-np.log(p_other_marg)))/scored)
        g_adv=g_cond-g_marg

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
        m_self_w=np.sum(ps*w[:,None],axis=0)
        m_other_w=np.sum(po*w[:,None],axis=0)
        g_marg_w=float(np.sum(target_z*(np.log(m_self_w)-np.log(m_other_w)))/scored)
        g_adv_w=g_cond-g_marg_w

        rows.append({
            "cohort":cohort_name,
            "session":A["sessions"][t],
            "individual":A["label_names"][lab],
            "scored_fixes":scored,
            "conditional":g_cond,
            "marginal":g_marg,
            "advantage":g_adv,
            "common_cell_marginal":g_marg_w,
            "common_cell_advantage":g_adv_w,
        })
    return rows


METRICS=("conditional","marginal","advantage","common_cell_marginal","common_cell_advantage")


def aggregate_panel(rows):
    per_ind={}
    for iid in sorted({r["individual"] for r in rows}):
        rs=[r for r in rows if r["individual"]==iid]
        if not rs:
            continue
        per_ind[iid]={m:float(np.mean([r[m] for r in rs])) for m in METRICS}
        per_ind[iid]["evaluable_sessions"]=len(rs)
        per_ind[iid]["cohorts"]=sorted({r["cohort"] for r in rs})

    vals=list(per_ind.values())
    out={"eligible_individuals":len(vals)}
    for m in METRICS:
        x=[v[m] for v in vals]
        out[m]=float(np.mean(x)) if x else None
    out["positive_common_cell_advantage_fraction"]=(
        float(np.mean(np.array([v["common_cell_advantage"] for v in vals])>0))
        if vals else None
    )
    return out,per_ind


def observed_eval(arrays):
    rows=[]
    for cohort,A in arrays.items():
        rows.extend(eval_cohort(A,A["orig_labels"],cohort))
    return aggregate_panel(rows)+(rows,)


def perm_eval(arrays,rng):
    rows=[]
    for cohort,A in arrays.items():
        labels=rng.permutation(A["orig_labels"])
        rows.extend(eval_cohort(A,labels,cohort))
    return aggregate_panel(rows)[0]


def tail_summary(values,obs):
    x=np.asarray(values,dtype=float)
    sd=float(x.std(ddof=1))
    return {
        "n":int(x.size),
        "mean":float(x.mean()),
        "sd":sd,
        "q025":float(np.quantile(x,0.025)),
        "q50":float(np.quantile(x,0.5)),
        "q975":float(np.quantile(x,0.975)),
        "observed":float(obs),
        "observed_minus_null_mean":float(obs-x.mean()),
        "null_standardized_deviation":float((obs-x.mean())/sd) if sd>0 else None,
        "p_null_ge_observed":float((1+np.sum(x>=obs))/(x.size+1)),
        "p_null_le_observed":float((1+np.sum(x<=obs))/(x.size+1)),
    }


def bootstrap(per_ind,seed):
    ids=sorted(per_ind)
    mat=np.array([[per_ind[i][m] for m in METRICS] for i in ids],dtype=float)
    n=len(ids)
    rng=np.random.default_rng(seed)
    draws=np.empty((N_BOOT,len(METRICS)),dtype=float)
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
        for j,m in enumerate(METRICS)
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--panel",required=True)
    args=ap.parse_args()

    cfg,panels=load_cfg()
    if args.panel not in panels:
        raise SystemExit(f"unknown panel {args.panel}")
    spec,events_by_cohort,k,source,pre,numeric_failures=load_panel(args.panel)
    arrays={cohort:make_cohort_arrays(events,k) for cohort,events in sorted(events_by_cohort.items())}

    observed,per_ind,session_rows=observed_eval(arrays)
    exp=spec["observed"]
    tol=1e-12
    for key in ("conditional","marginal","advantage"):
        if abs(observed[key]-float(exp[key]))>tol:
            raise RuntimeError(f"observed mismatch {args.panel} {key}: {observed[key]} != {exp[key]}")
    if observed["eligible_individuals"]!=int(exp["n"]):
        raise RuntimeError(f"observed n mismatch {observed['eligible_individuals']} != {exp['n']}")

    rng=np.random.default_rng(int(spec["perm_seed"]))
    null={m:[] for m in METRICS}
    eligible=[]
    invalid=0
    for _ in range(N_PERM):
        s=perm_eval(arrays,rng)
        if s["eligible_individuals"]<1:
            invalid+=1
            continue
        eligible.append(s["eligible_individuals"])
        for m in METRICS:
            null[m].append(s[m])

    cal={m:tail_summary(null[m],observed[m]) for m in METRICS}
    elig=np.asarray(eligible,dtype=float)
    eligible_summary={
        "valid_permutations":int(len(eligible)),
        "invalid_permutations":int(invalid),
        "observed":int(observed["eligible_individuals"]),
        "mean":float(elig.mean()),
        "q025":float(np.quantile(elig,0.025)),
        "q50":float(np.quantile(elig,0.5)),
        "q975":float(np.quantile(elig,0.975)),
        "min":int(elig.min()),
        "max":int(elig.max()),
    }

    payload={
        "study_id":"batter-cross-panel-estimator-calibration-v1",
        "panel_id":args.panel,
        "taxon":spec["taxon"],
        "source":source,
        "admitted_cohorts":sorted(arrays),
        "numeric_height_parse_failures":numeric_failures,
        "frozen_observed_target":exp,
        "observed":{
            **observed,
            "individual_results":per_ind,
            "session_results":session_rows,
        },
        "permutation":{
            "B":N_PERM,
            "seed":int(spec["perm_seed"]),
            "scope":"within admitted cohort; whole-session labels; exact per-cohort label session counts preserved",
            "calibration":cal,
            "eligible_individual_count_distribution":eligible_summary,
        },
        "individual_bootstrap":{
            "B":N_BOOT,
            "seed":int(spec["boot_seed"]),
            "percentile_95_interval":bootstrap(per_ind,int(spec["boot_seed"])),
        },
        "diagnostic":{
            "ordinary_marginal_minus_common_cell_marginal":observed["marginal"]-observed["common_cell_marginal"],
            "ordinary_advantage_minus_common_cell_advantage":observed["advantage"]-observed["common_cell_advantage"],
            "calibrated_common_cell_advantage":cal["common_cell_advantage"]["observed_minus_null_mean"],
            "conditional_evidence_rule":{
                "calibrated_common_cell_advantage_positive":cal["common_cell_advantage"]["observed_minus_null_mean"]>0,
                "upper_tail_le_0_05":cal["common_cell_advantage"]["p_null_ge_observed"]<=0.05,
                "passes":(
                    cal["common_cell_advantage"]["observed_minus_null_mean"]>0
                    and cal["common_cell_advantage"]["p_null_ge_observed"]<=0.05
                ),
            }
        },
        "claim_boundary":{
            "post_freeze_diagnostic":True,
            "raw_sign_not_cross_panel_classifier":True,
            "absolute_nats_not_ranked_across_vertical_reference_systems":True,
            "source_search_closed":True,
        }
    }

    out=Path(f"results/cross_panel_calibration_{args.panel}_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    print(json.dumps({
        "panel":args.panel,
        "observed":{m:observed[m] for m in ("eligible_individuals",)+METRICS},
        "calibration":cal,
        "bootstrap":payload["individual_bootstrap"],
        "diagnostic":payload["diagnostic"],
        "eligible_null":eligible_summary,
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
