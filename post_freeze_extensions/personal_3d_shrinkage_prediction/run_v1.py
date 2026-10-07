#!/usr/bin/env python3
from __future__ import annotations
import json, math, sys
from collections import defaultdict
from datetime import timedelta
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from post_freeze_extensions.collective_personal_3d_decomposition.run_v1 import (
    cfg as parent_cfg, build_sessions, avg_profiles_sessions, avg_profiles_other
)

CFG=ROOT/"post_freeze_extensions/personal_3d_shrinkage_prediction/contract_v1.json"
OUT=ROOT/"post_freeze_extensions/personal_3d_shrinkage_prediction/result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/personal_3d_shrinkage_prediction/RESULT_V1.md"

def load_cfg():
    return json.loads(CFG.read_text())

def marginal(ss):
    return np.mean(np.stack([s["marginal"] for s in ss]),axis=0)

def raw_conditional(ss):
    return avg_profiles_sessions(ss)

def cell_n(ss):
    out=defaultdict(int)
    for s in ss:
        for cell,v in s["counts"].items():
            out[cell]+=int(v.sum())
    return dict(out)

def shrink_model(ss,lam):
    i0=marginal(ss)
    i1=raw_conditional(ss)
    n=cell_n(ss)
    out={}
    for cell,p in i1.items():
        nn=float(n.get(cell,0))
        w=nn/(nn+float(lam)) if lam>0 else 1.0
        out[cell]=w*p+(1.0-w)*i0
    return i0,out

def score_session(validation,train,lam):
    i0,pm=shrink_model(train,lam)
    num=0.0; den=0
    for cell,cnt in validation["counts"].items():
        p=pm.get(cell,i0)
        num+=float(np.sum(cnt.astype(float)*np.log(p)))
        den+=int(cnt.sum())
    return num/den if den else -math.inf

def choose_lambda(sh,grid):
    scores={}
    for lam in grid:
        vals=[]
        for j,val in enumerate(sh):
            tr=[s for k,s in enumerate(sh) if k!=j]
            vals.append(score_session(val,tr,float(lam)))
        scores[str(lam)]=float(np.mean(vals))
    best=max(scores.values())
    tied=[int(l) for l,v in scores.items() if abs(v-best)<=1e-12]
    chosen=max(tied)
    return chosen,scores

def target_rows(panel,sessions,c):
    pc=parent_cfg()
    lag=timedelta(days=float(c["history"]["minimum_lag_days"]))
    min_other=int(c["history"]["minimum_other_individuals"])
    min_scored=int(c["history"]["minimum_scored_target_fixes"])
    grid=[int(x) for x in c["model"]["lambda_grid"]]
    rows=[]
    for t in sessions:
        cutoff=t["mid_time"]-lag
        prior=[s for s in sessions if s["cohort"]==t["cohort"] and s["mid_time"]<=cutoff]
        sh=[s for s in prior if s["individual"]==t["individual"]]
        oh=[s for s in prior if s["individual"]!=t["individual"]]
        if len(sh)<int(c["target_gate"]["minimum_self_history_sessions_for_internal_cv"]):
            continue
        if len({s["individual"] for s in oh})<min_other:
            continue

        # Rebuild exact Lane-B support: both self and group conditional models must support the target cell.
        self_raw=raw_conditional(sh)
        group_raw,_=avg_profiles_other(oh)
        common=set(self_raw)&set(group_raw)&set(t["counts"])
        scored=int(sum(int(t["counts"][cell].sum()) for cell in common))
        if scored<min_scored: continue

        lam,cv=choose_lambda(sh,grid)
        i0,pm=shrink_model(sh,lam)
        gain=0.0
        raw_gain=0.0
        for cell in common:
            cnt=t["counts"][cell].astype(float)
            gain+=float(np.sum(cnt*(np.log(pm[cell])-np.log(i0))))
            raw_gain+=float(np.sum(cnt*(np.log(self_raw[cell])-np.log(i0))))
        gain/=scored; raw_gain/=scored

        rows.append({
            "cohort":t["cohort"],"session":t["session"],"individual":t["individual"],
            "prior_self_sessions":len(sh),"scored_fixes":scored,
            "selected_lambda":lam,"cv_log_scores":cv,
            "regularized_shape_gain":gain,"raw_shape_gain":raw_gain
        })

    exp=c["target_gate"]["expected_after_gate"][panel]
    nids=len({r["individual"] for r in rows})
    if len(rows)!=int(exp["target_sessions"]) or nids!=int(exp["target_individuals"]):
        raise RuntimeError(f"{panel}: structural drift sessions={len(rows)} ids={nids}")
    return rows

def aggregate(rows):
    per={}
    for iid in sorted({r["individual"] for r in rows}):
        rs=[r for r in rows if r["individual"]==iid]
        per[iid]={
            "target_sessions":len(rs),
            "regularized_shape_gain":float(np.mean([r["regularized_shape_gain"] for r in rs])),
            "raw_shape_gain":float(np.mean([r["raw_shape_gain"] for r in rs])),
            "selected_lambda_median":float(np.median([r["selected_lambda"] for r in rs]))
        }
    return per

def bootstrap(per,seed,B,key):
    ids=sorted(per); n=len(ids); rng=np.random.default_rng(seed)
    obs=float(np.mean([per[i][key] for i in ids]))
    vals=[]
    for _ in range(B):
        ss=rng.choice(ids,size=n,replace=True)
        vals.append(float(np.mean([per[i][key] for i in ss])))
    a=np.asarray(vals)
    lo=float(np.quantile(a,.025)); hi=float(np.quantile(a,.975))
    return {
        "mean":obs,"ci95_low":lo,"ci95_high":hi,
        "positive_individuals":int(sum(per[i][key]>0 for i in ids)),
        "individuals":n,
        "supported":bool(obs>0 and lo>0)
    }

def main():
    c=load_cfg(); pc=parent_cfg(); panels={}
    for p in c["included_panels"]:
        sessions,_=build_sessions(p,pc)
        rows=target_rows(p,sessions,c)
        per=aggregate(rows)
        seed=int(c["uncertainty"]["seeds"][p]); B=int(c["uncertainty"]["B"])
        reg=bootstrap(per,seed,B,"regularized_shape_gain")
        raw=bootstrap(per,seed+100,B,"raw_shape_gain")
        lams=[r["selected_lambda"] for r in rows]
        panels[p]={
            "target_sessions":len(rows),"target_individuals":len(per),
            "regularized":reg,"raw_restricted_subset":raw,
            "selected_lambda_counts":{str(x):int(sum(v==x for v in lams)) for x in c["model"]["lambda_grid"]},
            "individual_results":per,"target_results":rows
        }

    payload={"schema_version":1,"study_id":c["study_id"],"panels":panels,"claim_boundary":c["claim_boundary"]}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    lines=["# Personal 3D shrinkage prediction result v1","",
           "| panel | regularized shape gain [95% CI] | raw gain on same subset | support | median selected lambda |",
           "|---|---:|---:|---|---:|"]
    for p,v in panels.items():
        a=v["regularized"]; b=v["raw_restricted_subset"]
        all_l=[]
        for r in v["target_results"]: all_l.append(r["selected_lambda"])
        lines.append(f"| {p} | {a['mean']:+.4f} [{a['ci95_low']:+.4f},{a['ci95_high']:+.4f}] | {b['mean']:+.4f} [{b['ci95_low']:+.4f},{b['ci95_high']:+.4f}] | {'PASS' if a['supported'] else 'FAIL'} | {np.median(all_l):.0f} |")
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(json.dumps({p:{
        "regularized":v["regularized"],
        "raw":v["raw_restricted_subset"],
        "lambda_counts":v["selected_lambda_counts"]
    } for p,v in panels.items()},sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
