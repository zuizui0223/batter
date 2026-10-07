#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from collections import defaultdict
from datetime import timedelta
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from post_freeze_extensions.collective_personal_3d_decomposition.run_v1 import (
    cfg as parent_cfg, build_sessions, avg_profiles_sessions, avg_profiles_other, avg_other_marginal
)

CFG=ROOT/"post_freeze_extensions/personal_3d_predictive_ladder/contract_v1.json"
OUT=ROOT/"post_freeze_extensions/personal_3d_predictive_ladder/result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/personal_3d_predictive_ladder/RESULT_V1.md"

KEYS=[
    "marginal_identity_gain",
    "shared_spatial_gain",
    "self_spatial_increment",
    "personal_conditional_advantage",
    "total_personal_history_gain"
]

def load_cfg():
    return json.loads(CFG.read_text(encoding="utf-8"))

def target_rows(panel,sessions,c):
    lag=timedelta(days=float(c["target_and_history_rules"]["minimum_history_lag_days"]))
    min_other=int(c["target_and_history_rules"]["minimum_other_history_individuals"])
    min_scored=int(c["target_and_history_rules"]["minimum_scored_target_fixes"])
    rows=[]
    for t in sessions:
        cutoff=t["mid_time"]-lag
        prior=[s for s in sessions if s["cohort"]==t["cohort"] and s["mid_time"]<=cutoff]
        sh=[s for s in prior if s["individual"]==t["individual"]]
        oh=[s for s in prior if s["individual"]!=t["individual"]]
        oids=sorted({s["individual"] for s in oh})
        if not sh or len(oids)<min_other:
            continue

        I1=avg_profiles_sessions(sh)
        G1,_=avg_profiles_other(oh)
        G0=avg_other_marginal(oh)
        I0=np.mean(np.stack([s["marginal"] for s in sh]),axis=0)

        common=set(I1)&set(G1)&set(t["counts"])
        scored=int(sum(int(t["counts"][cell].sum()) for cell in common))
        if scored<min_scored:
            continue

        sums={k:0.0 for k in KEYS}
        for cell in common:
            cnt=t["counts"][cell].astype(float)
            li1=np.log(I1[cell]); lg1=np.log(G1[cell]); li0=np.log(I0); lg0=np.log(G0)
            sums["marginal_identity_gain"] += float(np.sum(cnt*(li0-lg0)))
            sums["shared_spatial_gain"] += float(np.sum(cnt*(lg1-lg0)))
            sums["self_spatial_increment"] += float(np.sum(cnt*(li1-li0)))
            sums["personal_conditional_advantage"] += float(np.sum(cnt*(li1-lg1)))
            sums["total_personal_history_gain"] += float(np.sum(cnt*(li1-lg0)))

        row={
            "cohort":t["cohort"],"session":t["session"],"individual":t["individual"],
            "scored_fixes":scored,"prior_self_sessions":len(sh),"prior_other_individuals":len(oids)
        }
        for k in KEYS:
            row[k]=sums[k]/scored
        if abs(row["total_personal_history_gain"]-(row["marginal_identity_gain"]+row["self_spatial_increment"]))>1e-10:
            raise RuntimeError("marginal + self-spatial identity failed")
        if abs(row["total_personal_history_gain"]-(row["shared_spatial_gain"]+row["personal_conditional_advantage"]))>1e-10:
            raise RuntimeError("shared + personal identity failed")
        rows.append(row)

    exp=c["expected_target_counts"][panel]
    nids=len({r["individual"] for r in rows})
    if len(rows)!=int(exp["sessions"]) or nids!=int(exp["individuals"]):
        raise RuntimeError(f"{panel}: target drift sessions={len(rows)} ids={nids}")
    return rows

def aggregate(rows):
    per={}
    for iid in sorted({r["individual"] for r in rows}):
        rs=[r for r in rows if r["individual"]==iid]
        per[iid]={"target_sessions":len(rs)}
        for k in KEYS:
            per[iid][k]=float(np.mean([r[k] for r in rs]))
    return per

def bootstrap(per,seed,B):
    ids=sorted(per); n=len(ids); rng=np.random.default_rng(seed)
    out={}
    for k in KEYS:
        obs=float(np.mean([per[i][k] for i in ids]))
        vals=[]
        for _ in range(B):
            samp=rng.choice(ids,size=n,replace=True)
            vals.append(float(np.mean([per[i][k] for i in samp])))
        a=np.asarray(vals)
        lo=float(np.quantile(a,0.025)); hi=float(np.quantile(a,0.975))
        out[k]={
            "mean":obs,"ci95_low":lo,"ci95_high":hi,
            "positive_individuals":int(sum(per[i][k]>0 for i in ids)),
            "individuals":n,
            "supported":bool(obs>0 and lo>0)
        }
    return out

def classify(b):
    shape=b["self_spatial_increment"]["supported"]
    marg=b["marginal_identity_gain"]["supported"]
    rel=b["personal_conditional_advantage"]["supported"]
    total=b["total_personal_history_gain"]["supported"]
    if total and shape:
        return "full_personal_3d_prediction"
    if total and marg and not shape:
        return "marginal_state_prediction_without_shape_increment"
    if rel and not total:
        return "relative_personalization_only"
    if shape and not total:
        return "shape_increment_without_positive_total_baseline_gain"
    return "no_positive_personal_prediction"

def make_md(payload):
    lines=["# Personal 3D predictive ladder result v1","",
           "| panel | marginal identity | self spatial increment | personal vs other-map | total | classification |",
           "|---|---:|---:|---:|---:|---|"]
    for p,v in payload["panels"].items():
        b=v["bootstrap"]
        lines.append(f"| {p} | {b['marginal_identity_gain']['mean']:+.4f} | {b['self_spatial_increment']['mean']:+.4f} | {b['personal_conditional_advantage']['mean']:+.4f} | {b['total_personal_history_gain']['mean']:+.4f} | {v['classification']} |")
    lines += ["","The self-spatial increment (I1-I0) is the key test of whether an individual's spatially resolved 3D probability shape adds future predictive information beyond its own marginal vertical state.",""]
    return "\n".join(lines)

def main():
    c=load_cfg(); pc=parent_cfg()
    panels={}
    for p in c["included_panels"]:
        sessions,_=build_sessions(p,pc)
        rows=target_rows(p,sessions,c)
        per=aggregate(rows)
        b=bootstrap(per,int(c["uncertainty"]["seeds"][p]),int(c["uncertainty"]["B"]))
        panels[p]={
            "target_sessions":len(rows),
            "target_individuals":len(per),
            "bootstrap":b,
            "classification":classify(b),
            "individual_results":per,
            "target_results":rows
        }
    payload={"schema_version":1,"study_id":c["study_id"],"panels":panels,"claim_boundary":c["claim_boundary"]}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    OUT_MD.write_text(make_md(payload),encoding="utf-8")
    print(json.dumps({p:{
        "classification":v["classification"],
        "marginal":v["bootstrap"]["marginal_identity_gain"],
        "self_spatial":v["bootstrap"]["self_spatial_increment"],
        "personal_vs_other":v["bootstrap"]["personal_conditional_advantage"],
        "total":v["bootstrap"]["total_personal_history_gain"]
    } for p,v in panels.items()},sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
