#!/usr/bin/env python3
"""Early-to-late persistence of individual policy breadth."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("RN",HERE/"individual_peer_context_reaction_norm_v1.py")
RN=importlib.util.module_from_spec(spec);spec.loader.exec_module(RN)

NPERM=9999
SEEDS={"2022":202610052201,"2023":202610052202}
EPS=1e-12

def breadth(vals):
    X=np.vstack(vals).astype(float)
    if X.shape[0]<3:return None
    cen=X.mean(axis=0)
    w=float(np.sum((X-cen)**2)/(X.shape[0]-1))
    if not math.isfinite(w) or w<0:return None
    return w

def prepared(panel):
    rows,audit=RN.day_records(panel)
    if rows is None:return None,audit
    by=collections.defaultdict(list)
    for r in rows:
        ik=f"{r['cohort']}::{r['iid']}"
        by[ik].append({
          "cohort":r["cohort"],"iid":r["iid"],"day":r["day"],
          "resid":np.asarray(r["y"]-r["c"],float)
        })
    indiv=[]
    for ik,vals in sorted(by.items()):
        vals=sorted(vals,key=lambda z:z["day"])
        n=len(vals)
        if n<6:continue
        cut=n//2
        early=vals[:cut];late=vals[cut:]
        if len(early)<3 or len(late)<3:continue
        we=breadth([z["resid"] for z in early])
        wl=breadth([z["resid"] for z in late])
        if we is None or wl is None:continue
        indiv.append({
          "indkey":ik,"cohort":vals[0]["cohort"],"iid":vals[0]["iid"],
          "n_days":n,"n_early":len(early),"n_late":len(late),
          "W_early":we,"W_late":wl,
          "L_early":float(math.log(max(we,EPS))),
          "L_late":float(math.log(max(wl,EPS))),
        })
    return indiv,audit

def stat(indiv,late_map=None):
    byco=collections.defaultdict(list)
    for z in indiv:byco[z["cohort"]].append(z)
    ki={}
    valid=[]
    for co,vals in byco.items():
        if len(vals)<3:continue
        late={z["indkey"]:(late_map[z["indkey"]] if late_map is not None else z["L_late"]) for z in vals}
        for z in vals:
            own=late[z["indkey"]]
            others=[v for k,v in late.items() if k!=z["indkey"]]
            if len(others)<2:continue
            ds=abs(z["L_early"]-own)
            do=float(np.mean([abs(z["L_early"]-v) for v in others]))
            ki[z["indkey"]]=do-ds
            valid.append(z)
    if len(ki)<5:return None,{},valid
    return float(np.mean(list(ki.values()))),ki,valid

def perm_late(indiv,rng):
    out={}
    byco=collections.defaultdict(list)
    for z in indiv:byco[z["cohort"]].append(z)
    for vals in byco.values():
        ids=[z["indkey"] for z in vals]
        lv=np.asarray([z["L_late"] for z in vals],float)
        p=rng.permutation(lv)
        for k,v in zip(ids,p):out[k]=float(v)
    return out

def run(year,panel):
    indiv,audit=prepared(panel)
    if indiv is None:return {"status":"STOP_SOURCE_SUPPORT","audit":audit}
    obs,ki,valid=stat(indiv)
    if obs is None:
        return {"status":"STOP_STRUCTURAL_SUPPORT","n_candidate_individuals":len(indiv),
                "individual_support":indiv,"audit":audit}
    rng=np.random.default_rng(SEEDS[year]);null=[]
    for _ in range(NPERM):
        q,_,_=stat(indiv,perm_late(indiv,rng))
        if q is not None and math.isfinite(q):null.append(q)
    a=np.asarray(null,float)
    if len(a)<9500:
        return {"status":"STOP_RANDOMIZATION_SUPPORT","K_W":obs,
                "valid_permutations":len(a),"individual_support":indiv}
    p=float((1+np.sum(a>=obs))/(1+len(a)))
    pos=sum(v>0 for v in ki.values())
    valid_ids=set(ki)
    ev=[z for z in indiv if z["indkey"] in valid_ids]
    rho,p_rho=spearmanr([z["L_early"] for z in ev],[z["L_late"] for z in ev])
    supported=bool(obs>0 and p<=.05 and pos/len(ki)>=.70)
    return {
      "status":"DONE","K_W":obs,"individual_K":ki,
      "positive_individuals":pos,"n_individuals":len(ki),
      "positive_fraction":pos/len(ki),
      "requested_permutations":NPERM,"valid_permutations":len(a),
      "seed":SEEDS[year],"null_mean":float(a.mean()),
      "null_q025":float(np.quantile(a,.025)),"null_q975":float(np.quantile(a,.975)),
      "p_one_sided":p,
      "secondary":{
        "spearman_log_breadth":float(rho),"spearman_p_two_sided":float(p_rho),
        "median_W_early":float(np.median([z["W_early"] for z in ev])),
        "median_W_late":float(np.median([z["W_late"] for z in ev])),
      },
      "individual_support":ev,
      "diagnostic_verdict":"SUPPORTED_POLICY_BREADTH_PERSISTENCE" if supported else "UNSUPPORTED_POLICY_BREADTH_PERSISTENCE"
    }

def main():
    print(json.dumps({
      "contract":"FIELD_POLICY_BREADTH_PERSISTENCE_CONTRACT_V1.md",
      "status":"POST_JAE_POST_OUTCOME_PREDICTABILITY_DIAGNOSTIC",
      "years":{y:run(y,p) for y,p in RN.BV.PANELS.items()}
    },indent=2))

if __name__=="__main__":main()
