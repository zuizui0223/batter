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
import sys
import urllib.request

import numpy as np
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from batter.analysis import Event, z_bin
import scripts.run_cross_panel_estimator_calibration as cal

INPUT=Path("results/calibrated_vertical_identity_effect_input_v1.csv")
TAD_URL="https://datarepository.movebank.org/server/api/core/bitstreams/a6a6db33-0aca-4902-a58d-f32980c1a3e1/content"
TAD_MD5="e0f6faedfd1f21bac222d9da430ea5d8"
TAD_SIZE=3630088
TAD_ROWS=9873
EDGES=(-math.inf,0.0,50.0,100.0,200.0,400.0,800.0,1600.0,3200.0,math.inf)
ALPHA=0.5
MIN_SCORED=50
BOOT_B=20000
PANEL_ORDER=["tadarida","eidolon","hypsignathus","phyllostomus_2022","phyllostomus_2023","phyllostomus_2016"]


def effect_inputs():
    with INPUT.open(newline="",encoding="utf-8") as fh:
        return {r["panel_id"]:r for r in csv.DictReader(fh)}


def get_tad_rows():
    req=urllib.request.Request(TAD_URL,headers={"User-Agent":"batter-biological-effect-translation-v1/1.0"})
    with urllib.request.urlopen(req,timeout=120) as r:
        data=r.read()
    if len(data)!=TAD_SIZE:
        raise RuntimeError("Tadarida source size mismatch")
    if hashlib.md5(data).hexdigest()!=TAD_MD5:
        raise RuntimeError("Tadarida source checksum mismatch")
    rows=list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"),newline="")))
    if len(rows)!=TAD_ROWS:
        raise RuntimeError("Tadarida row mismatch")
    return rows


def finite_float(v):
    try:
        x=float(v)
    except (TypeError,ValueError):
        return None
    return x if math.isfinite(x) else None


def load_tadarida_events():
    rows=get_tad_rows()
    tr=Transformer.from_crs("EPSG:4326","EPSG:3035",always_xy=True)
    parsed=[]; counts=Counter()
    for row in rows:
        iid=str(row.get("animal-id","")).strip()
        day=str(row.get("BatDay","")).strip()
        lon=finite_float(row.get("location-long")); lat=finite_float(row.get("location-lat"))
        h=finite_float(row.get("height-above-msl"))
        if not iid or not day or lon is None or lat is None or h is None:
            continue
        x,y=tr.transform(lon,lat); sid=f"{iid}::{day}"; counts[sid]+=1
        parsed.append((iid,sid,(math.floor(x/5000.0),math.floor(y/5000.0)),z_bin(h,edges=EDGES)))
    retained={s for s,n in counts.items() if n>=50}
    events=[Event(iid,None,cell,zb,sid) for iid,sid,cell,zb in parsed if sid in retained]
    return {"focal":events},len(EDGES)-1,{"gps_md5":TAD_MD5,"gps_rows":len(rows)}


def load_panel(panel):
    if panel=="tadarida":
        return load_tadarida_events()
    spec,events_by_cohort,k,source,pre,numeric_failures=cal.load_panel(panel)
    return events_by_cohort,k,source


def make_arrays(events_by_cohort,k):
    return {cohort:cal.make_cohort_arrays(events,k) for cohort,events in sorted(events_by_cohort.items())}


def pooled_support_entropy(A):
    counts=A["counts"]; cell_tot=A["cell_tot"]; sess_cond=A["sess_cond"]; labels=A["orig_labels"]
    S,C,K=counts.shape; L=len(A["label_names"]); idx=np.arange(S)

    group_counts=np.zeros((L,C,K),dtype=np.int32)
    for lab in range(L):
        sel=np.flatnonzero(labels==lab)
        if len(sel):
            group_counts[lab]=counts[sel].sum(axis=0)
    group_cell_tot=group_counts.sum(axis=2)
    group_cond=np.full((L,C,K),np.nan,dtype=float)
    for lab in range(L):
        pc=np.flatnonzero(group_cell_tot[lab]>0)
        if len(pc):
            group_cond[lab,pc,:]=(group_counts[lab,pc,:]+ALPHA)/(group_cell_tot[lab,pc,None]+ALPHA*K)

    rows=[]
    for t in range(S):
        lab=int(labels[t])
        self_sel=np.flatnonzero((labels==lab)&(idx!=t))
        if len(self_sel)==0:
            continue
        p_self=cal.mean_nan_axis0(sess_cond[self_sel])
        other_idx=np.array([x for x in range(L) if x!=lab],dtype=int)
        p_other=cal.mean_nan_axis0(group_cond[other_idx])
        supported=(cell_tot[t]>0)&(~np.isnan(p_self[:,0]))&(~np.isnan(p_other[:,0]))
        scored=int(cell_tot[t,supported].sum())
        if scored<MIN_SCORED:
            continue
        tz=counts[t,supported,:].sum(axis=0).astype(float)
        p=tz/tz.sum()
        nz=p>0
        entropy=float(-np.sum(p[nz]*np.log(p[nz])))
        rows.append({
            "individual":A["label_names"][lab],
            "session":A["sessions"][t],
            "scored_fixes":scored,
            "entropy_nats":entropy,
        })
    return rows


def aggregate_equal_individual(rows,value_key):
    per={}
    for iid in sorted({r["individual"] for r in rows}):
        vals=[r[value_key] for r in rows if r["individual"]==iid]
        if vals:
            per[iid]=float(np.mean(vals))
    vals=list(per.values())
    return (float(np.mean(vals)) if vals else None),per


def self_weights(cell_tot,self_sel,supported_idx):
    ws=[]
    for s in self_sel:
        w=cell_tot[s,supported_idx].astype(float)
        if w.sum()>0:
            ws.append(w/w.sum())
    if not ws:
        return None
    w=np.mean(np.stack(ws),axis=0)
    return w/w.sum()


def pairwise_identification(A):
    counts=A["counts"]; cell_tot=A["cell_tot"]; sess_cond=A["sess_cond"]; labels=A["orig_labels"]
    S,C,K=counts.shape; L=len(A["label_names"]); idx=np.arange(S)
    rows=[]
    for t in range(S):
        lab=int(labels[t])
        self_sel=np.flatnonzero((labels==lab)&(idx!=t))
        if len(self_sel)==0:
            continue
        p_self=cal.mean_nan_axis0(sess_cond[self_sel])
        for alt in range(L):
            if alt==lab:
                continue
            alt_sel=np.flatnonzero(labels==alt)
            if len(alt_sel)==0:
                continue
            p_alt=cal.mean_nan_axis0(sess_cond[alt_sel])
            supported=(cell_tot[t]>0)&(~np.isnan(p_self[:,0]))&(~np.isnan(p_alt[:,0]))
            scored=int(cell_tot[t,supported].sum())
            if scored<MIN_SCORED:
                continue
            sidx=np.flatnonzero(supported)
            w=self_weights(cell_tot,self_sel,sidx)
            if w is None:
                continue
            m_self=np.sum(p_self[sidx,:]*w[:,None],axis=0)
            m_alt=np.sum(p_alt[sidx,:]*w[:,None],axis=0)
            tz=counts[t,supported,:].sum(axis=0).astype(float)
            gain=float(np.sum(tz*(np.log(m_self)-np.log(m_alt)))/scored)
            rows.append({
                "individual":A["label_names"][lab],
                "session":A["sessions"][t],
                "alternative":A["label_names"][alt],
                "gain":gain,
                "win":float(gain>0),
            })
    # Alternatives -> target session -> individual -> panel.
    session_rows=[]
    keys=sorted({(r["individual"],r["session"]) for r in rows})
    for iid,sid in keys:
        rs=[r for r in rows if r["individual"]==iid and r["session"]==sid]
        session_rows.append({
            "individual":iid,"session":sid,
            "alternatives":len(rs),
            "win_fraction":float(np.mean([r["win"] for r in rs])),
            "mean_pairwise_gain":float(np.mean([r["gain"] for r in rs])),
        })
    per_ind={}
    for iid in sorted({r["individual"] for r in session_rows}):
        rs=[r for r in session_rows if r["individual"]==iid]
        per_ind[iid]={
            "win_fraction":float(np.mean([r["win_fraction"] for r in rs])),
            "mean_pairwise_gain":float(np.mean([r["mean_pairwise_gain"] for r in rs])),
            "evaluable_sessions":len(rs),
        }
    vals=[v["win_fraction"] for v in per_ind.values()]
    return {
        "equal_individual_self_win_fraction":float(np.mean(vals)) if vals else None,
        "pair_count":len(rows),
        "individual_results":per_ind,
    }


def bootstrap_values(per_ind,key,seed):
    ids=sorted(per_ind); vals=np.array([per_ind[i][key] for i in ids],dtype=float)
    rng=np.random.default_rng(seed); n=len(vals)
    draws=np.empty(BOOT_B,dtype=float)
    for b in range(BOOT_B):
        draws[b]=vals[rng.integers(0,n,size=n)].mean()
    return {
        "observed":float(vals.mean()),
        "q025":float(np.quantile(draws,0.025)),
        "q50":float(np.quantile(draws,0.5)),
        "q975":float(np.quantile(draws,0.975)),
    }


def tadarida_agl_height_separation():
    rows=get_tad_rows()
    tr=Transformer.from_crs("EPSG:4326","EPSG:3035",always_xy=True)
    rec=[]; counts=Counter()
    for row in rows:
        iid=str(row.get("animal-id","")).strip(); day=str(row.get("BatDay","")).strip()
        lon=finite_float(row.get("location-long")); lat=finite_float(row.get("location-lat"))
        h=finite_float(row.get("height_true"))
        if not iid or not day or lon is None or lat is None or h is None:
            continue
        x,y=tr.transform(lon,lat); sid=f"{iid}::{day}"; cell=(math.floor(x/5000.0),math.floor(y/5000.0))
        counts[sid]+=1; rec.append({"iid":iid,"session":sid,"cell":cell,"h":h})
    retained={s for s,n in counts.items() if n>=50}
    rec=[r for r in rec if r["session"] in retained]
    by_session=defaultdict(list); by_ind=defaultdict(list)
    for r in rec:
        by_session[r["session"]].append(r); by_ind[r["iid"]].append(r)

    rows_out=[]
    for sid,target in sorted(by_session.items()):
        iid=target[0]["iid"]
        self_sessions=sorted({r["session"] for r in by_ind[iid] if r["session"]!=sid})
        if not self_sessions:
            continue

        # Self per-session cell means and counts.
        self_means=defaultdict(list); self_counts=defaultdict(dict)
        for ss in self_sessions:
            sr=[r for r in by_session[ss]]
            cells=defaultdict(list)
            for r in sr: cells[r["cell"]].append(r["h"])
            for cell,hs in cells.items():
                self_means[cell].append(float(np.mean(hs)))
                self_counts[ss][cell]=len(hs)

        # Other-individual cell means, equal individual weighting.
        other_means=defaultdict(list)
        for alt,ars in by_ind.items():
            if alt==iid: continue
            cells=defaultdict(list)
            for r in ars: cells[r["cell"]].append(r["h"])
            for cell,hs in cells.items(): other_means[cell].append(float(np.mean(hs)))

        target_counts=Counter(r["cell"] for r in target)
        support=sorted(set(target_counts)&set(self_means)&set(other_means))
        scored=sum(target_counts[c] for c in support)
        if scored<MIN_SCORED:
            continue
        ws=[]
        for ss in self_sessions:
            arr=np.array([self_counts[ss].get(c,0) for c in support],dtype=float)
            if arr.sum()>0: ws.append(arr/arr.sum())
        if not ws: continue
        w=np.mean(np.stack(ws),axis=0); w=w/w.sum()
        self_cell=np.array([np.mean(self_means[c]) for c in support],dtype=float)
        other_cell=np.array([np.mean(other_means[c]) for c in support],dtype=float)
        self_exp=float(np.sum(w*self_cell)); other_exp=float(np.sum(w*other_cell))
        rows_out.append({"individual":iid,"session":sid,"absolute_separation_m":abs(self_exp-other_exp)})
    mean_sep,per=aggregate_equal_individual(rows_out,"absolute_separation_m")
    seed=2026100100+1
    per_struct={iid:{"absolute_separation_m":v} for iid,v in per.items()}
    ci=bootstrap_values(per_struct,"absolute_separation_m",seed)
    return {
        "equal_individual_mean_absolute_separation_m":mean_sep,
        "median_individual_separation_m":float(np.median(list(per.values()))) if per else None,
        "bootstrap_95":ci,
        "individual_results":per,
        "evaluable_sessions":len(rows_out),
    }


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--panel",required=True,choices=PANEL_ORDER); args=ap.parse_args()
    inp=effect_inputs()[args.panel]
    events_by_cohort,k,source=load_panel(args.panel)
    arrays=make_arrays(events_by_cohort,k)

    observed,_,_=cal.observed_eval(arrays)
    expected=float(inp["common_cell_marginal"])
    if abs(observed["common_cell_marginal"]-expected)>1e-12:
        raise RuntimeError(f"common-cell marginal mismatch {observed['common_cell_marginal']} != {expected}")

    entropy_rows=[]
    pair_rows=[]
    pair_ind={}
    # Entropy pooled over cohorts.
    for cohort,A in arrays.items():
        for r in pooled_support_entropy(A):
            r["cohort"]=cohort; entropy_rows.append(r)
        p=pairwise_identification(A)
        # Same individual can appear in multiple cohorts; retain cohort namespace for aggregation.
        for iid,v in p["individual_results"].items():
            pair_ind[f"{cohort}::{iid}"]=v
        pair_rows.append(p["pair_count"])

    mean_entropy,entropy_per=aggregate_equal_individual(entropy_rows,"entropy_nats")
    observed_cc=float(inp["common_cell_marginal"])
    null_cc=float(inp["null_common_cell_marginal"])
    calibrated=float(inp["calibrated_common_cell_marginal"])
    idx=PANEL_ORDER.index(args.panel)+1
    pair_ci=bootstrap_values(pair_ind,"win_fraction",2026100100+idx) if pair_ind else None
    pair_win=float(np.mean([v["win_fraction"] for v in pair_ind.values()])) if pair_ind else None

    payload={
        "study_id":"batter-biological-effect-translation-v1",
        "panel_id":args.panel,
        "source":source,
        "calibrated_identity_input":{
            "common_cell_marginal":observed_cc,
            "null_mean":null_cc,
            "calibrated":calibrated,
        },
        "likelihood_multipliers":{
            "observed":float(math.exp(observed_cc)),
            "calibrated_excess_scale":float(math.exp(calibrated)),
        },
        "target_vertical_entropy":{
            "equal_individual_mean_entropy_nats":mean_entropy,
            "equal_individual_mean_entropy_bits":float(mean_entropy/math.log(2)) if mean_entropy is not None else None,
            "individual_results_nats":entropy_per,
            "entropy_equivalent_fraction":float(calibrated/mean_entropy) if mean_entropy and mean_entropy>0 else None,
            "interpretation_boundary":"calibrated log-score gain / empirical target entropy; not mutual information or variance explained"
        },
        "pairwise_self_identification":{
            "equal_individual_self_win_fraction":pair_win,
            "chance_reference":0.5,
            "pair_count":int(sum(pair_rows)),
            "individual_bootstrap_95":pair_ci,
            "individual_results":pair_ind,
            "inferential_role":"descriptive only"
        },
        "focal_agl_height_separation_m":tadarida_agl_height_separation() if args.panel=="tadarida" else None,
        "claim_boundary":{
            "no_new_significance_gate":True,
            "no_cross_datum_meter_comparison":True,
            "no_panel_ranking":True,
        }
    }
    out=Path(f"results/biological_effect_translation_{args.panel}_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "panel":args.panel,
        "likelihood_multipliers":payload["likelihood_multipliers"],
        "entropy":payload["target_vertical_entropy"],
        "pairwise":{k:payload["pairwise_self_identification"][k] for k in ["equal_individual_self_win_fraction","pair_count","individual_bootstrap_95"]},
        "focal_agl_height_separation_m":payload["focal_agl_height_separation_m"],
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
