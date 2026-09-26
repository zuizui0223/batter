#!/usr/bin/env python3
from __future__ import annotations

from collections import defaultdict
import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_new_species_replications as core
from batter.analysis import conditional_profile, marginal_profile

CONFIG=Path("contract/extended_pairwise_architecture_v1.json")
ALPHA=0.5
MIN_SCORED=50


def pairwise_score(target,self_train,alternative_train,k):
    p_self=conditional_profile(self_train,unit="session",alpha=ALPHA,k=k)
    p_alt=conditional_profile(alternative_train,unit="session",alpha=ALPHA,k=k)
    m_self=marginal_profile(self_train,unit="session",alpha=ALPHA,k=k)
    m_alt=marginal_profile(alternative_train,unit="session",alpha=ALPHA,k=k)
    scored=[e for e in target if e.cell in p_self and e.cell in p_alt]
    if len(scored)<MIN_SCORED:
        return None
    cond=np.array([
      math.log(float(p_self[e.cell][e.zbin]))-math.log(float(p_alt[e.cell][e.zbin]))
      for e in scored
    ],dtype=float)
    marg=np.array([
      math.log(float(m_self[e.zbin]))-math.log(float(m_alt[e.zbin]))
      for e in scored
    ],dtype=float)
    return {
      "scored_fixes":len(scored),
      "conditional_gain":float(cond.mean()),
      "marginal_gain":float(marg.mean()),
      "interaction_gain":float((cond-marg).mean()),
      "conditional_self_win":bool(cond.mean()>0),
      "marginal_self_win":bool(marg.mean()>0),
    }


def summarize(events_by_cohort,k):
    pair_rows=[]
    for cohort,events in sorted(events_by_cohort.items()):
        by_session=defaultdict(list)
        by_ind=defaultdict(list)
        for e in events:
            by_session[e.session].append(e)
            by_ind[e.individual].append(e)

        for session,target in sorted(by_session.items()):
            iid=target[0].individual
            self_train=[e for e in by_ind[iid] if e.session!=session]
            if not self_train:
                continue
            for alt,alt_events in sorted(by_ind.items()):
                if alt==iid:
                    continue
                scored=pairwise_score(target,self_train,alt_events,k)
                if scored is None:
                    continue
                pair_rows.append({
                  "cohort":cohort,
                  "target_session":session,
                  "target_individual":iid,
                  "alternative_individual":alt,
                  **scored,
                })

    session_rows=[]
    keys=sorted({(r["cohort"],r["target_session"],r["target_individual"]) for r in pair_rows})
    for cohort,session,iid in keys:
        vals=[r for r in pair_rows if r["cohort"]==cohort and r["target_session"]==session and r["target_individual"]==iid]
        if not vals:
            continue
        cond=np.array([r["conditional_gain"] for r in vals])
        marg=np.array([r["marginal_gain"] for r in vals])
        inter=np.array([r["interaction_gain"] for r in vals])
        session_rows.append({
          "cohort":cohort,
          "session":session,
          "individual":iid,
          "evaluable_alternatives":len(vals),
          "mean_conditional_pairwise_gain":float(cond.mean()),
          "conditional_self_win_fraction":float(np.mean(cond>0)),
          "mean_marginal_pairwise_gain":float(marg.mean()),
          "marginal_self_win_fraction":float(np.mean(marg>0)),
          "mean_interaction_pairwise_gain":float(inter.mean()),
        })

    individual={}
    for iid in sorted({r["individual"] for r in session_rows}):
        vals=[r for r in session_rows if r["individual"]==iid]
        individual[iid]={
          "evaluable_sessions":len(vals),
          "mean_conditional_pairwise_gain":float(np.mean([v["mean_conditional_pairwise_gain"] for v in vals])),
          "conditional_self_win_fraction":float(np.mean([v["conditional_self_win_fraction"] for v in vals])),
          "mean_marginal_pairwise_gain":float(np.mean([v["mean_marginal_pairwise_gain"] for v in vals])),
          "marginal_self_win_fraction":float(np.mean([v["marginal_self_win_fraction"] for v in vals])),
          "mean_interaction_pairwise_gain":float(np.mean([v["mean_interaction_pairwise_gain"] for v in vals])),
        }

    vals=list(individual.values())
    def mean(field):
        x=[v[field] for v in vals]
        return float(np.mean(x)) if x else None
    return {
      "evaluable_individual_count":len(vals),
      "equal_individual_mean_conditional_pairwise_gain":mean("mean_conditional_pairwise_gain"),
      "equal_individual_conditional_self_win_fraction":mean("conditional_self_win_fraction"),
      "equal_individual_mean_marginal_pairwise_gain":mean("mean_marginal_pairwise_gain"),
      "equal_individual_marginal_self_win_fraction":mean("marginal_self_win_fraction"),
      "equal_individual_mean_interaction_pairwise_gain":mean("mean_interaction_pairwise_gain"),
      "individual_results":individual,
      "session_results":session_rows,
      "pair_count":len(pair_rows),
    }


def run_panel(panel):
    path=Path(panel["contract"])
    contract=json.loads(path.read_text(encoding="utf-8"))
    ua="batter-extended-pairwise-architecture-v1/1.0"
    gps=core.get(contract["source"]["gps"],ua)
    ref=core.get(contract["source"]["reference"],ua)
    rows,headers=core.read_csv(gps)
    refs,_=core.read_csv(ref)
    pre=core.build_pre_numeric(rows,headers,refs,contract)
    if not pre["admitted_cohorts"]:
        return {
          "id":panel["id"],
          "taxon":contract["taxon"],
          "status":"structurally_unavailable",
          "admitted_cohorts":[],
        }
    events,_=core.build_events(rows,pre,contract,5000.0)
    edges=core.parse_edges(contract["vertical"]["primary_edges_m"])
    summary=summarize(events,len(edges)-1)
    return {
      "id":panel["id"],
      "taxon":contract["taxon"],
      "status":"evaluated",
      "admitted_cohorts":pre["admitted_cohorts"],
      "vertical_field":contract["vertical"]["field"],
      **summary,
    }


def main():
    cfg=json.loads(CONFIG.read_text(encoding="utf-8"))
    results=[run_panel(panel) for panel in cfg["panels"]]
    payload={
      "study_id":cfg["study_id"],
      "results":results,
      "claim_boundary":cfg["claim_boundary"],
    }
    out=Path("results/extended_pairwise_architecture_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
      "results":[{
        k:r.get(k) for k in [
          "id","taxon","status","evaluable_individual_count",
          "equal_individual_mean_conditional_pairwise_gain",
          "equal_individual_conditional_self_win_fraction",
          "equal_individual_mean_marginal_pairwise_gain",
          "equal_individual_marginal_self_win_fraction",
          "equal_individual_mean_interaction_pairwise_gain"
        ]
      } for r in results]
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
