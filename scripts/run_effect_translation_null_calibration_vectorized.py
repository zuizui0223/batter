#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
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
REF={
 "mean":0.5075058033959102,
 "sd":0.14055803554069368,
 "q025":0.23749007936507935,
 "q50":0.5071428571428571,
 "q975":0.779047619047619,
 "p_null_ge_observed":0.0189,
}
TOL=2e-12


def spec_for(panel):
    cfg=json.loads(CONTRACT.read_text(encoding="utf-8"))
    return cfg,next(x for x in cfg["pairwise_self_win_null"]["panels"] if x["id"]==panel)


def cohort_rows(A,labels,cohort):
    counts=A["counts"]
    cell_tot=A["cell_tot"].astype(float)
    sess_cond=A["sess_cond"]
    S,C,K=counts.shape
    L=len(A["label_names"])
    idx=np.arange(S)
    present=~np.isnan(sess_cond[:,:,0])
    sess0=np.nan_to_num(sess_cond,nan=0.0)

    gsum=np.zeros((L,C,K),dtype=float)
    gn=np.zeros((L,C),dtype=np.int32)
    for lab in range(L):
        sel=np.flatnonzero(labels==lab)
        if len(sel):
            gsum[lab]=sess0[sel].sum(axis=0)
            gn[lab]=present[sel].sum(axis=0)
    gp=np.full((L,C,K),np.nan,dtype=float)
    np.divide(gsum,gn[:,:,None],out=gp,where=gn[:,:,None]>0)

    rows=[]
    for t in range(S):
        lab=int(labels[t])
        self_sel=np.flatnonzero((labels==lab)&(idx!=t))
        if len(self_sel)==0:
            continue

        self_sum=gsum[lab]-sess0[t]
        self_n=gn[lab]-present[t].astype(np.int32)
        pself=np.full((C,K),np.nan,dtype=float)
        np.divide(self_sum,self_n[:,None],out=pself,where=self_n[:,None]>0)

        base=(cell_tot[t]>0)&(self_n>0)
        support=(gn>0)&base[None,:]  # L x C
        support[lab,:]=False

        self_counts=cell_tot[self_sel,:]  # M x C
        denom=self_counts @ support.T.astype(float)  # M x L
        valid=denom>0
        inv=np.zeros_like(denom,dtype=float)
        inv[valid]=1.0/denom[valid]

        # Sum normalized self-session cell distributions for each alternative.
        wsum=np.einsum("mc,ml,lc->lc",self_counts,inv,support.astype(float),optimize=True)
        nvalid=valid.sum(axis=0)
        W=np.zeros((L,C),dtype=float)
        ok=nvalid>0
        W[ok]=wsum[ok]/nvalid[ok,None]
        rowsum=W.sum(axis=1)
        ok2=rowsum>0
        W[ok2]=W[ok2]/rowsum[ok2,None]

        pself0=np.nan_to_num(pself,nan=0.0)
        gp0=np.nan_to_num(gp,nan=0.0)
        mself=W @ pself0                         # L x K
        malt=np.einsum("lc,lck->lk",W,gp0,optimize=True)
        target_counts=counts[t].astype(float)   # C x K
        tz=support.astype(float) @ target_counts
        scored=tz.sum(axis=1)

        good=(np.arange(L)!=lab)&(scored>=MIN_SCORED)&ok2
        good &= np.all(mself>0,axis=1)&np.all(malt>0,axis=1)
        if not np.any(good):
            continue
        gains=np.full(L,np.nan,dtype=float)
        gains[good]=(
            np.sum(tz[good]*(np.log(mself[good])-np.log(malt[good])),axis=1)
            / scored[good]
        )
        gv=gains[good]
        rows.append({
            "cohort":cohort,
            "individual":A["label_names"][lab],
            "session":A["sessions"][t],
            "alternatives":int(len(gv)),
            "win_fraction":float(np.mean(gv>0)),
            "mean_pairwise_gain":float(np.mean(gv)),
        })
    return rows


def aggregate(rows):
    by=defaultdict(list)
    for r in rows: by[r["individual"]].append(r)
    per={}
    for iid,rr in sorted(by.items()):
        per[iid]={
            "win_fraction":float(np.mean([x["win_fraction"] for x in rr])),
            "mean_pairwise_gain":float(np.mean([x["mean_pairwise_gain"] for x in rr])),
            "evaluable_sessions":len(rr),
            "cohorts":sorted({x["cohort"] for x in rr}),
        }
    vals=[x["win_fraction"] for x in per.values()]
    return {
        "equal_individual_self_win_fraction":float(np.mean(vals)) if vals else None,
        "evaluable_individuals":len(vals),
        "individual_results":per,
        "session_results":rows,
    }


def eval_panel(arrays,maps=None):
    rows=[]
    for cohort,A in sorted(arrays.items()):
        labels=A["orig_labels"] if maps is None else maps[cohort]
        rows.extend(cohort_rows(A,labels,cohort))
    return aggregate(rows)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--panel",required=True,choices=["tadarida","hypsignathus","phyllostomus_2022"])
    args=ap.parse_args()
    cfg,spec=spec_for(args.panel)
    events,k,source=eff.load_panel(args.panel)
    arrays=eff.make_arrays(events,k)
    obs=eval_panel(arrays)
    expected=float(spec["observed"])
    if abs(obs["equal_individual_self_win_fraction"]-expected)>TOL:
        raise RuntimeError(f"observed mismatch {obs['equal_individual_self_win_fraction']} != {expected}")

    rng=np.random.default_rng(int(spec["seed"]))
    null=[]; ns=[]
    for _ in range(int(spec["permutations"])):
        maps={co:rng.permutation(A["orig_labels"]) for co,A in sorted(arrays.items())}
        s=eval_panel(arrays,maps)
        if s["equal_individual_self_win_fraction"] is not None:
            null.append(s["equal_individual_self_win_fraction"]); ns.append(s["evaluable_individuals"])
    summary=cal.tail_summary(null,expected)

    if args.panel=="tadarida":
        for key,want in REF.items():
            if abs(float(summary[key])-want)>TOL:
                raise RuntimeError(f"vectorized equivalence mismatch {key}: {summary[key]} != {want}")

    payload={
      "study_id":cfg["study_id"],
      "contract":str(CONTRACT),
      "implementation":"vectorized alternative-profile evaluator",
      "panel_id":args.panel,
      "source":source,
      "observed":obs,
      "permutation":{"B":int(spec["permutations"]),"seed":int(spec["seed"]),"calibration":summary,
                     "eligible_individual_count":{"observed":obs["evaluable_individuals"],
                                                  "mean":float(np.mean(ns)) if ns else None}},
      "implementation_equivalence":{"tadarida_full_null_matches_original_slow_runner":True if args.panel=="tadarida" else None},
      "interpretation":{"may_use_as_calibrated_main_text_translation":
          bool(summary["observed_minus_null_mean"]>0 and summary["p_null_ge_observed"]<=0.05),
          "reference_0_5_is_intuitive_only":True}
    }
    out=Path(f"results/effect_null_pairwise_vectorized_{args.panel}_v1.json")
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"panel":args.panel,"observed":expected,"null":summary,
                      "main_text_translation":payload["interpretation"]["may_use_as_calibrated_main_text_translation"],
                      "tadarida_equivalence":payload["implementation_equivalence"]["tadarida_full_null_matches_original_slow_runner"]},sort_keys=True))
    return 0

if __name__=="__main__": raise SystemExit(main())
