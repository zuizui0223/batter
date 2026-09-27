#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_cross_panel_estimator_calibration as cal
import scripts.run_biological_effect_translation as eff

CONTRACT=Path("contract/effect_translation_null_calibration_v1.json")
MIN_SCORED=50

# Frozen old-run reference for implementation equivalence.
TADARIDA_REFERENCE={
    "null_mean":0.5075058033959102,
    "null_sd":0.14055803554069368,
    "p_upper":0.0189,
    "q025":0.23749007936507935,
    "q50":0.5071428571428571,
    "q975":0.779047619047619,
}
REF_TOL=1e-12


def load_spec(panel):
    cfg=json.loads(CONTRACT.read_text(encoding="utf-8"))
    return cfg,next(x for x in cfg["pairwise_self_win_null"]["panels"] if x["id"]==panel)


def label_profiles(A,labels):
    """Equal-session conditional profile per pseudo-label, computed once/assignment."""
    sess=A["sess_cond"]
    L=len(A["label_names"])
    out=[]
    for lab in range(L):
        sel=np.flatnonzero(labels==lab)
        out.append(cal.mean_nan_axis0(sess[sel]) if len(sel) else None)
    return out


def self_weights(cell_tot,self_sel,supported_idx):
    ws=[]
    for s in self_sel:
        w=cell_tot[s,supported_idx].astype(float)
        tot=w.sum()
        if tot>0:
            ws.append(w/tot)
    if not ws:
        return None
    w=np.mean(np.stack(ws),axis=0)
    return w/w.sum()


def eval_cohort_fast(A,labels,cohort):
    counts=A["counts"]; cell_tot=A["cell_tot"]; sess_cond=A["sess_cond"]
    S,C,K=counts.shape
    L=len(A["label_names"])
    idx=np.arange(S)
    alt_profiles=label_profiles(A,labels)
    rows=[]

    for t in range(S):
        lab=int(labels[t])
        self_sel=np.flatnonzero((labels==lab)&(idx!=t))
        if len(self_sel)==0:
            continue
        p_self=cal.mean_nan_axis0(sess_cond[self_sel])
        target_cell_tot=cell_tot[t]

        wins=[]
        gains=[]
        for alt in range(L):
            if alt==lab:
                continue
            p_alt=alt_profiles[alt]
            if p_alt is None:
                continue
            supported=(
                (target_cell_tot>0)
                & (~np.isnan(p_self[:,0]))
                & (~np.isnan(p_alt[:,0]))
            )
            scored=int(target_cell_tot[supported].sum())
            if scored<MIN_SCORED:
                continue
            sidx=np.flatnonzero(supported)
            w=self_weights(cell_tot,self_sel,sidx)
            if w is None:
                continue
            m_self=np.sum(p_self[sidx,:]*w[:,None],axis=0)
            m_alt=np.sum(p_alt[sidx,:]*w[:,None],axis=0)
            target_z=counts[t,supported,:].sum(axis=0).astype(float)
            gain=float(np.sum(target_z*(np.log(m_self)-np.log(m_alt)))/scored)
            gains.append(gain)
            wins.append(float(gain>0))

        if wins:
            rows.append({
                "cohort":cohort,
                "individual":A["label_names"][lab],
                "session":A["sessions"][t],
                "win_fraction":float(np.mean(wins)),
                "mean_pairwise_gain":float(np.mean(gains)),
                "alternatives":len(wins),
            })
    return rows


def aggregate(rows):
    per={}
    for iid in sorted({r["individual"] for r in rows}):
        rr=[r for r in rows if r["individual"]==iid]
        per[iid]={
            "win_fraction":float(np.mean([r["win_fraction"] for r in rr])),
            "mean_pairwise_gain":float(np.mean([r["mean_pairwise_gain"] for r in rr])),
            "evaluable_sessions":len(rr),
            "cohorts":sorted({r["cohort"] for r in rr}),
        }
    vals=[v["win_fraction"] for v in per.values()]
    return {
        "equal_individual_self_win_fraction":float(np.mean(vals)) if vals else None,
        "evaluable_individuals":len(vals),
        "individual_results":per,
        "session_results":rows,
    }


def eval_panel(arrays,label_maps=None):
    rows=[]
    for cohort,A in sorted(arrays.items()):
        labels=A["orig_labels"] if label_maps is None else label_maps[cohort]
        rows.extend(eval_cohort_fast(A,labels,cohort))
    return aggregate(rows)


def tail(values,obs):
    return cal.tail_summary(values,obs)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--panel",required=True,choices=[
        "tadarida","eidolon","hypsignathus",
        "phyllostomus_2022","phyllostomus_2023","phyllostomus_2016"
    ])
    args=ap.parse_args()

    cfg,spec=load_spec(args.panel)
    events_by_cohort,k,source=eff.load_panel(args.panel)
    arrays=eff.make_arrays(events_by_cohort,k)
    observed=eval_panel(arrays)
    expected=float(spec["observed"])
    if abs(float(observed["equal_individual_self_win_fraction"])-expected)>REF_TOL:
        raise RuntimeError(
            f"fast observed mismatch {args.panel}: "
            f"{observed['equal_individual_self_win_fraction']} != {expected}"
        )

    rng=np.random.default_rng(int(spec["seed"]))
    null=[]; eligible=[]; invalid=0
    for _ in range(int(spec["permutations"])):
        maps={
            cohort:rng.permutation(A["orig_labels"])
            for cohort,A in sorted(arrays.items())
        }
        s=eval_panel(arrays,maps)
        v=s["equal_individual_self_win_fraction"]
        if v is None:
            invalid+=1
            continue
        null.append(v)
        eligible.append(s["evaluable_individuals"])

    summary=tail(null,expected)

    # Tadarida is the equivalence gate because the original slow run completed.
    if args.panel=="tadarida":
        checks={
            "mean":TADARIDA_REFERENCE["null_mean"],
            "sd":TADARIDA_REFERENCE["null_sd"],
            "q025":TADARIDA_REFERENCE["q025"],
            "q50":TADARIDA_REFERENCE["q50"],
            "q975":TADARIDA_REFERENCE["q975"],
        }
        for key,want in checks.items():
            if abs(float(summary[key])-want)>REF_TOL:
                raise RuntimeError(
                    f"fast/slow Tadarida null mismatch {key}: {summary[key]} != {want}"
                )
        if abs(float(summary["p_null_ge_observed"])-TADARIDA_REFERENCE["p_upper"])>REF_TOL:
            raise RuntimeError("fast/slow Tadarida p-value mismatch")

    payload={
        "study_id":cfg["study_id"],
        "contract":str(CONTRACT),
        "implementation":"optimized pairwise evaluator; label profiles cached once per assignment",
        "panel_id":args.panel,
        "source":source,
        "observed":observed,
        "permutation":{
            "B":int(spec["permutations"]),
            "seed":int(spec["seed"]),
            "calibration":summary,
            "invalid_replicates":invalid,
            "eligible_individual_count":{
                "observed":observed["evaluable_individuals"],
                "mean":float(np.mean(eligible)) if eligible else None,
                "min":int(np.min(eligible)) if eligible else None,
                "max":int(np.max(eligible)) if eligible else None,
            },
        },
        "implementation_equivalence":{
            "observed_matches_frozen_effect_translation":True,
            "tadarida_full_null_matches_original_slow_runner":(
                True if args.panel=="tadarida" else None
            ),
        },
        "interpretation":{
            "calibrated_excess_positive":summary["observed_minus_null_mean"]>0,
            "upper_tail_le_0_05":summary["p_null_ge_observed"]<=0.05,
            "may_use_as_calibrated_main_text_translation":(
                summary["observed_minus_null_mean"]>0
                and summary["p_null_ge_observed"]<=0.05
            ),
            "reference_0_5_is_intuitive_only":True,
        },
    }
    out=Path(f"results/effect_null_pairwise_fast_{args.panel}_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "panel":args.panel,
        "observed":expected,
        "null":summary,
        "main_text_translation":payload["interpretation"]["may_use_as_calibrated_main_text_translation"],
        "tadarida_equivalence":payload["implementation_equivalence"]["tadarida_full_null_matches_original_slow_runner"],
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
