#!/usr/bin/env python3
from __future__ import annotations

import json, math, sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_cross_panel_estimator_calibration as cal
from post_freeze_extensions.phyllostomus_2023_phase_attribution.run_v1 import (
    CONTRACT, OUT, OUT_MD, K, ALPHA, prepare
)

FAST_DIR=ROOT/"post_freeze_extensions/phyllostomus_2023_phase_attribution_fast"
FAST_OUT=FAST_DIR/"result_v1.json"
FAST_MD=FAST_DIR/"RESULT_V1.md"
EXPECTED_PHASE_CONDITIONAL=-0.07041361832377967


def dense_cohort(sessions):
    sids=sorted(sessions)
    labels=sorted({sessions[s]["original_label"] for s in sids})
    lmap={x:i for i,x in enumerate(labels)}
    orig=np.asarray([lmap[sessions[s]["original_label"]] for s in sids],dtype=int)

    pcells=sorted({c for s in sids for c in sessions[s]["phase_counts"]})
    bcells=sorted({c for s in sids for c in sessions[s]["base_counts"]})
    pmap={c:i for i,c in enumerate(pcells)}
    bmap={c:i for i,c in enumerate(bcells)}
    p_to_b=np.asarray([bmap[c[:-1]] for c in pcells],dtype=int)

    P=np.zeros((len(sids),len(pcells),K),dtype=float)
    B=np.zeros((len(sids),len(bcells),K),dtype=float)
    for i,sid in enumerate(sids):
        for c,v in sessions[sid]["phase_counts"].items():
            P[i,pmap[c],:]=v
        for c,v in sessions[sid]["base_counts"].items():
            B[i,bmap[c],:]=v

    def sess_cond(X):
        totals=X.sum(axis=2)
        out=np.full(X.shape,np.nan,dtype=float)
        for i in range(X.shape[0]):
            idx=np.flatnonzero(totals[i]>0)
            if len(idx):
                out[i,idx,:]=(X[i,idx,:]+ALPHA)/(totals[i,idx,None]+ALPHA*K)
        return out,totals

    Pc,Pt=sess_cond(P)
    Bc,Bt=sess_cond(B)
    return {
        "sids":sids,"label_names":labels,"orig_labels":orig,
        "phase_counts":P,"base_counts":B,
        "phase_cond":Pc,"base_cond":Bc,
        "phase_totals":Pt,"base_totals":Bt,
        "phase_to_base":p_to_b
    }


def group_cond(counts,labels,L):
    S,C,K_=counts.shape
    gc=np.zeros((L,C,K_),dtype=float)
    for lab in range(L):
        sel=np.flatnonzero(labels==lab)
        if len(sel):
            gc[lab]=counts[sel].sum(axis=0)
    totals=gc.sum(axis=2)
    out=np.full(gc.shape,np.nan,dtype=float)
    for lab in range(L):
        idx=np.flatnonzero(totals[lab]>0)
        if len(idx):
            out[lab,idx,:]=(gc[lab,idx,:]+ALPHA)/(totals[lab,idx,None]+ALPHA*K_)
    return out


def mean_nan(a,axis=0):
    with np.errstate(invalid="ignore"):
        valid=np.sum(~np.isnan(a),axis=axis)
        sums=np.nansum(a,axis=axis)
        return np.divide(sums,valid,out=np.full_like(sums,np.nan,dtype=float),where=valid>0)


def eval_cohort(A,labels,cohort):
    S=A["phase_counts"].shape[0]
    L=len(A["label_names"])
    gP=group_cond(A["phase_counts"],labels,L)
    gB=group_cond(A["base_counts"],labels,L)
    idx_all=np.arange(S)
    rows=[]

    for t in range(S):
        lab=int(labels[t])
        self_sel=np.flatnonzero((labels==lab)&(idx_all!=t))
        if len(self_sel)==0:
            continue
        other=np.asarray([x for x in range(L) if x!=lab],dtype=int)
        if len(other)==0:
            continue

        psP=mean_nan(A["phase_cond"][self_sel],axis=0)
        poP=mean_nan(gP[other],axis=0)
        psB=mean_nan(A["base_cond"][self_sel],axis=0)
        poB=mean_nan(gB[other],axis=0)

        target_tot=A["phase_totals"][t]
        support=(target_tot>0)&(~np.isnan(psP[:,0]))&(~np.isnan(poP[:,0]))
        # base availability on the exact same phase-supported targets
        pb=A["phase_to_base"]
        support=support&(~np.isnan(psB[pb,0]))&(~np.isnan(poB[pb,0]))
        scored=int(target_tot[support].sum())
        if scored<50:
            continue

        ix=np.flatnonzero(support)
        tc=A["phase_counts"][t,ix,:]
        phase=float(np.sum(tc*(np.log(psP[ix,:])-np.log(poP[ix,:])))/scored)
        bix=pb[ix]
        base=float(np.sum(tc*(np.log(psB[bix,:])-np.log(poB[bix,:])))/scored)
        rows.append({
            "cohort":cohort,
            "session":A["sids"][t],
            "individual":A["label_names"][lab],
            "scored_events":scored,
            "phase_gain":phase,
            "collapsed_gain":base,
            "phase_increment":phase-base
        })
    return rows


def aggregate(rows):
    per={}
    for iid in sorted({r["individual"] for r in rows}):
        rs=[r for r in rows if r["individual"]==iid]
        if rs:
            per[iid]={
                "evaluable_sessions":len(rs),
                "phase_gain":float(np.mean([r["phase_gain"] for r in rs])),
                "collapsed_gain":float(np.mean([r["collapsed_gain"] for r in rs])),
                "phase_increment":float(np.mean([r["phase_increment"] for r in rs]))
            }
    vals=list(per.values())
    return {
        "eligible_individuals":len(vals),
        "phase_gain":float(np.mean([v["phase_gain"] for v in vals])) if vals else None,
        "collapsed_gain":float(np.mean([v["collapsed_gain"] for v in vals])) if vals else None,
        "phase_increment":float(np.mean([v["phase_increment"] for v in vals])) if vals else None,
        "individual_results":per
    }


def evaluate(arrays,labels_by):
    rows=[]
    for cohort,A in arrays.items():
        rows.extend(eval_cohort(A,labels_by[cohort],cohort))
    return aggregate(rows)


def main():
    c=json.loads(CONTRACT.read_text())
    sparse,diag=prepare()
    arrays={cohort:dense_cohort(sessions) for cohort,sessions in sparse.items()}
    observed_labels={cohort:A["orig_labels"] for cohort,A in arrays.items()}
    obs=evaluate(arrays,observed_labels)

    expected=int(c["fixed_context"]["expected_evaluable_individuals"])
    if obs["eligible_individuals"]!=expected:
        raise RuntimeError(f"observed n {obs['eligible_individuals']} != {expected}")
    if abs(obs["phase_gain"]-EXPECTED_PHASE_CONDITIONAL)>1e-12:
        raise RuntimeError(f"phase conditional mismatch {obs['phase_gain']} != {EXPECTED_PHASE_CONDITIONAL}")

    B=int(c["calibration"]["B"]);seed=int(c["calibration"]["seed"])
    rng=np.random.default_rng(seed)
    ni=[];npv=[];nb=[];invalid=0
    for _ in range(B):
        labels={cohort:rng.permutation(A["orig_labels"]) for cohort,A in arrays.items()}
        x=evaluate(arrays,labels)
        if x["eligible_individuals"]<1:
            invalid+=1;continue
        ni.append(x["phase_increment"]);npv.append(x["phase_gain"]);nb.append(x["collapsed_gain"])

    inc=cal.tail_summary(ni,obs["phase_increment"])
    ph=cal.tail_summary(npv,obs["phase_gain"])
    ba=cal.tail_summary(nb,obs["collapsed_gain"])
    supported=inc["observed_minus_null_mean"]<0 and inc["p_null_le_observed"]<=0.05

    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "implementation":"dense-array cached equivalent",
        "validation":{"phase_gain_matches_frozen_phase3_conditional":True,"expected":EXPECTED_PHASE_CONDITIONAL},
        "diagnostics":diag,
        "observed":obs,
        "permutation":{"B":B,"seed":seed,"invalid_replicates":invalid,"phase_increment":inc,"phase_gain":ph,"collapsed_gain":ba},
        "primary_supported":bool(supported),
        "interpretation":(
            "Support-matched phase conditioning removes more same-individual predictive advantage than expected under whole-session label exchangeability."
            if supported else
            "The support-matched phase increment does not exceed the permutation expectation in the predicted negative direction; phase-related sparsity/finite-sample effects remain sufficient to explain the panel-level attenuation."
        ),
        "claim_boundary":c["claim_boundary"],
        "submission_claims_unchanged":True
    }
    FAST_DIR.mkdir(parents=True,exist_ok=True)
    FAST_OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    FAST_MD.write_text(
        "# P. hastatus 2023 support-matched phase attribution — fast validated implementation\n\n"
        f"- n: **{obs['eligible_individuals']}**\n"
        f"- collapsed gain: **{obs['collapsed_gain']:+.5f}**\n"
        f"- phase gain: **{obs['phase_gain']:+.5f}**\n"
        f"- phase increment: **{obs['phase_increment']:+.5f}**\n"
        f"- null-centered phase increment: **{inc['observed_minus_null_mean']:+.5f}**\n"
        f"- p(null <= observed): **{inc['p_null_le_observed']:.4f}**\n"
        f"- verdict: **{'PASS' if supported else 'FAIL'}**\n"
    )
    print(json.dumps({
        "n":obs["eligible_individuals"],
        "collapsed_gain":obs["collapsed_gain"],
        "phase_gain":obs["phase_gain"],
        "phase_increment":obs["phase_increment"],
        "calibrated_phase_increment":inc["observed_minus_null_mean"],
        "p_lower":inc["p_null_le_observed"],
        "supported":supported,
        "validated_phase_gain":True
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
