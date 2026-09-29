#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, math, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_cross_panel_estimator_calibration as cal
from post_freeze_extensions.fine_place_same_night_four_panel.run_v1 import (
    prepare_panel, observed_labels, permuted_labels, ALPHA, EDGES
)

CONTRACT=ROOT/"post_freeze_extensions/fine_place_same_night_four_panel/contract_v1.json"
OUTDIR=ROOT/"post_freeze_extensions/fine_place_same_night_four_panel_fast"
K=len(EDGES)-1


def session_counts(cohorts):
    out={}
    for cohort,sessions in cohorts.items():
        crec={}
        for sid,rec in sessions.items():
            cells={}
            for e in rec["events"]:
                cell=e["cell"]
                if cell not in cells:
                    cells[cell]=np.zeros(K,dtype=float)
                cells[cell][e["zbin"]]+=1.0
            crec[sid]={
                "session":sid,
                "night":rec["night"],
                "original_label":rec["original_label"],
                "cell_counts":cells,
                "target_n":int(sum(v.sum() for v in cells.values()))
            }
        out[cohort]=crec
    return out


def smooth(v):
    x=np.asarray(v,dtype=float)+ALPHA
    return x/x.sum()


def self_profile(sessions,self_sids):
    per_cell=defaultdict(list)
    for sid in self_sids:
        for cell,counts in sessions[sid]["cell_counts"].items():
            per_cell[cell].append(smooth(counts))
    return {cell:np.mean(np.stack(v),axis=0) for cell,v in per_cell.items()}


def night_other_profile(sessions,night_sids,labels):
    by_label_cell={}
    for sid in night_sids:
        lab=labels[sid]
        for cell,counts in sessions[sid]["cell_counts"].items():
            key=(lab,cell)
            if key not in by_label_cell:
                by_label_cell[key]=np.zeros(K,dtype=float)
            by_label_cell[key]+=counts
    per_cell=defaultdict(list)
    for (lab,cell),counts in by_label_cell.items():
        per_cell[cell].append(smooth(counts))
    return {cell:np.mean(np.stack(v),axis=0) for cell,v in per_cell.items()}


def fast_score_panel(counts_by_cohort,labels_by_cohort,min_scored):
    rows=[]
    for cohort,sessions in sorted(counts_by_cohort.items()):
        labels=labels_by_cohort[cohort]
        ids=sorted(sessions)
        for sid in ids:
            target=sessions[sid]
            lab=labels[sid]
            self_sids=[x for x in ids if x!=sid and labels[x]==lab]
            night_sids=[
                x for x in ids
                if sessions[x]["night"]==target["night"] and labels[x]!=lab
            ]
            if not self_sids:
                rows.append({"cohort":cohort,"session":sid,"label":lab,"evaluable":False,"reason":"no_self_history"})
                continue
            if not night_sids:
                rows.append({"cohort":cohort,"session":sid,"label":lab,"evaluable":False,"reason":"no_same_night_other"})
                continue

            ps=self_profile(sessions,self_sids)
            pn=night_other_profile(sessions,night_sids,labels)
            common=set(ps)&set(pn)&set(target["cell_counts"])
            scored=int(sum(target["cell_counts"][cell].sum() for cell in common))
            if scored<min_scored:
                rows.append({"cohort":cohort,"session":sid,"label":lab,"evaluable":False,"reason":"insufficient_common_support","scored_events":scored})
                continue

            total=0.0
            for cell in common:
                cnt=target["cell_counts"][cell]
                mask=cnt>0
                if np.any(mask):
                    total += float(np.dot(cnt[mask],np.log(ps[cell][mask])-np.log(pn[cell][mask])))
            gain=total/scored
            rows.append({
                "cohort":cohort,"session":sid,"label":lab,"night":target["night"],
                "evaluable":True,"scored_events":scored,"gain":float(gain)
            })

    per_ind={}
    labs=sorted({r["label"] for r in rows if r.get("evaluable")})
    for lab in labs:
        vals=[r["gain"] for r in rows if r.get("evaluable") and r["label"]==lab]
        if vals:
            per_ind[lab]={"evaluable_sessions":len(vals),"mean_gain":float(np.mean(vals))}
    vals=[v["mean_gain"] for v in per_ind.values()]
    return {
        "eligible_individuals":len(vals),
        "equal_individual_mean_gain":float(np.mean(vals)) if vals else None,
        "individual_results":per_ind
    }


def run(panel):
    c=json.loads(CONTRACT.read_text())
    cohorts,diag=prepare_panel(panel,c)
    counts=session_counts(cohorts)
    labels=observed_labels(cohorts)
    min_scored=int(c["predictors"]["minimum_supported_target_events"])
    obs=fast_score_panel(counts,labels,min_scored)
    expected=int(c["preflight"]["exact_evaluable_individuals"][panel])
    if obs["eligible_individuals"]!=expected:
        raise RuntimeError(f"{panel}: fast observed n {obs['eligible_individuals']} != {expected}")

    setting={x["panel"]:x for x in c["calibration"]["settings"]}[panel]
    rng=np.random.default_rng(int(setting["seed"]))
    null=[];invalid=0
    for _ in range(int(setting["B"])):
        labs=permuted_labels(cohorts,rng)
        p=fast_score_panel(counts,labs,min_scored)
        if p["eligible_individuals"]<1 or p["equal_individual_mean_gain"] is None:
            invalid+=1
            continue
        null.append(float(p["equal_individual_mean_gain"]))
    calibration=cal.tail_summary(null,float(obs["equal_individual_mean_gain"]))
    passed=(calibration["observed_minus_null_mean"]>0 and calibration["p_null_ge_observed"]<=0.05)
    return {
        "panel":panel,"diagnostics":diag,"observed":obs,
        "permutation":{"B":int(setting["B"]),"seed":int(setting["seed"]),"valid_replicates":len(null),"invalid_replicates":invalid,"calibration":calibration},
        "pass":bool(passed)
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--panel",required=True)
    ap.add_argument("--validate-2023",action="store_true")
    args=ap.parse_args()
    out=run(args.panel)
    x=out["permutation"]["calibration"]
    if args.validate_2023:
        if args.panel!="phyllostomus_2023":
            raise SystemExit("--validate-2023 requires phyllostomus_2023")
        checks=[
            (out["observed"]["equal_individual_mean_gain"],0.030475762902606115,"observed_gain"),
            (x["observed_minus_null_mean"],0.08217380087970408,"calibrated_excess"),
            (x["p_null_ge_observed"],0.0286,"p_upper")
        ]
        for got,want,name in checks:
            if abs(got-want)>1e-12:
                raise RuntimeError(f"validation mismatch {name}: {got} != {want}")
    OUTDIR.mkdir(parents=True,exist_ok=True)
    (OUTDIR/f"panel_{args.panel}_fast_v1.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "panel":args.panel,
        "n":out["observed"]["eligible_individuals"],
        "observed_gain":out["observed"]["equal_individual_mean_gain"],
        "calibrated_excess":x["observed_minus_null_mean"],
        "p_upper":x["p_null_ge_observed"],
        "pass":out["pass"],
        "validated_2023":bool(args.validate_2023)
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
