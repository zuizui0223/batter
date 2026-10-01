#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
EXT_PATH=ROOT/"post_freeze_extensions/3d_niche_partition/run_external_geometry_v1.py"
spec=importlib.util.spec_from_file_location("external_geom_v1",EXT_PATH)
mod=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

CFG=ROOT/"post_freeze_extensions/3d_niche_partition/external_geometry_prediction_contract_v1.json"
OUTDIR=ROOT/"post_freeze_extensions/3d_niche_partition/external_results_fast_equivalence"


def encode_labels(labels):
    names=sorted(set(labels.tolist()))
    idx={x:i for i,x in enumerate(names)}
    return np.array([idx[x] for x in labels],dtype=np.int16),names


def fast_primary(M, labels_int, min_other=2):
    S=M.shape[0]
    labs=np.unique(labels_int)
    L=int(labs.max())+1
    finite=np.isfinite(M)
    M0=np.nan_to_num(M,nan=0.0)

    # session x assigned-label mean overlap
    means=np.full((S,L),np.nan,dtype=float)
    for lab in range(L):
        mask=(labels_int==lab).astype(float)
        counts=finite @ mask
        sums=M0 @ mask
        ok=counts>0
        means[ok,lab]=sums[ok]/counts[ok]

    per=[]
    for lab in labs:
        tids=np.flatnonzero(labels_int==lab)
        if len(tids)==0:
            continue
        selfv=means[tids,lab]
        others=[x for x in labs if x!=lab]
        if len(others)<min_other:
            continue
        A=means[np.ix_(tids,others)]
        nfinite=np.isfinite(A).sum(axis=1)
        ok=np.isfinite(selfv)&(nfinite>=min_other)
        if not np.any(ok):
            continue
        om=np.nanmean(A[ok],axis=1)
        d=selfv[ok]-om
        per.append(float(np.mean(d)))
    return (float(np.mean(per)) if per else None, len(per))


def run(source):
    cfg=json.loads(CFG.read_text())
    scfg=cfg["sources"][source]
    df,prov=mod.standardized_source(source)
    sessions=mod.build_sessions(df,float(cfg["primary_grid_m"]),float(cfg["alpha"]))
    if len(sessions)!=1:
        raise RuntimeError(f"fast equivalence runner expects one cohort, got {list(sessions)}")
    cohort=next(iter(sessions))
    ss=sessions[cohort]
    mats,pairs=mod.metric_matrices(ss,int(cfg["pair_shared_fix_min_each"]))

    labels_raw=np.array([s["individual"] for s in ss],dtype=object)
    labels_int,names=encode_labels(labels_raw)

    # Full slow observed calculation for secondary quantities; this is only once.
    obs,per_ind,rows=mod.evaluate_generic(sessions,{cohort:mats},{cohort:labels_raw})
    fast_obs,fast_n=fast_primary(mats["ozxy"],labels_int)
    if fast_n!=obs["eligible_individuals"] or not np.isclose(fast_obs,obs["d_panel"],rtol=0,atol=1e-15):
        raise RuntimeError(f"fast observed mismatch fast={fast_obs}/{fast_n} slow={obs['d_panel']}/{obs['eligible_individuals']}")

    B=int(cfg["B"])
    seed=int(scfg["seed"])
    gate=int(scfg["primary_gate_n"])
    rng=np.random.default_rng(seed)
    null=[]
    null_n=[]
    invalid=0
    for _ in range(B):
        lp=rng.permutation(labels_int)
        d,n=fast_primary(mats["ozxy"],lp)
        if d is None or n<gate:
            invalid+=1
            continue
        null.append(float(d));null_n.append(int(n))

    cal=mod.cal.tail_summary(null,float(fast_obs)) if null else None
    supported=bool(cal and cal["observed_minus_null_mean"]>0 and cal["p_null_ge_observed"]<=0.05)
    payload={
      "study_id":"batter-external-3d-geometry-fast-equivalence-v1",
      "source":source,
      "provenance":prov,
      "session_count":len(ss),
      "pair_count":pairs,
      "observed":{**obs,"individual_results":per_ind,"session_results":rows},
      "fast_observed_exact_match":True,
      "permutation":{
        "B_requested":B,"seed":seed,
        "valid_replicates":len(null),"invalid_replicates":invalid,
        "eligible_individuals_null":{
          "mean":float(np.mean(null_n)) if null_n else None,
          "min":int(np.min(null_n)) if null_n else None,
          "max":int(np.max(null_n)) if null_n else None,
        },
        "primary_d_panel":cal,
      },
      "decision":{"structural_gate_met":obs["eligible_individuals"]>=gate,"supported":supported},
    }
    OUTDIR.mkdir(parents=True,exist_ok=True)
    out=OUTDIR/f"{source}_fast_result_v1.json"
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    print(json.dumps({
      "source":source,
      "sessions":len(ss),
      "pairs":pairs,
      "eligible_individuals":obs["eligible_individuals"],
      "d_panel":obs["d_panel"],
      "calibrated_excess":cal["observed_minus_null_mean"] if cal else None,
      "p_upper":cal["p_null_ge_observed"] if cal else None,
      "valid_permutations":len(null),
      "supported":supported,
      "fast_observed_exact_match":True,
    },sort_keys=True))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",required=True,choices=["myotis_vivesi","pteropus_poliocephalus"])
    args=ap.parse_args()
    run(args.source)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
