#!/usr/bin/env python3
"""Post-outcome bivariate HxV policy-to-vertical-shape localization in P. hastatus."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent

spec=importlib.util.spec_from_file_location("BV",HERE/"phyllostomus_fixed_bin_bivariate_carrier_v1.py")
BV=importlib.util.module_from_spec(spec);spec.loader.exec_module(BV)

spec2=importlib.util.spec_from_file_location("W",HERE/"wild_policy_to_vertical_shape_v1.py")
W=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(W)

PANELS={
 "2022":("phyllostomus_2022",202610051471),
 "2023":("phyllostomus_2023",202610051472),
}
NPERM=9999

def policy_histories(panel):
    rows,audit=BV.B.prepare(panel)
    if not rows or not audit["colony_retention_pass"]:
        return None,audit
    rr=BV.standardize_2d(rows)
    if rr is None:return None,audit
    by=collections.defaultdict(list)
    for r in rr:
        by[(r["cohort"],r["iid"])].append((r["session"],np.asarray(r["policy2"],float)))
    return {k:sorted(v,key=lambda x:x[0]) for k,v in by.items()},audit

def theta(histories,key,target_session):
    vals=[v for s,v in histories.get(key,[]) if s!=target_session]
    if not vals:return None
    return np.mean(np.vstack(vals),axis=0)

def keys_for_cohort(histories,c):
    return sorted(i for co,i in histories if co==c)

def build_targets(panel,histories):
    targets=W.build_vertical_targets(panel)
    out=[]
    for q in targets:
        c=q["cohort"];i=q["focal"]
        if (c,i) not in histories:continue
        dg={j:g for j,g in q["gains"].items() if (c,j) in histories}
        if len(dg)>=2:
            qq=dict(q);qq["gains"]=dg;out.append(qq)
    return out

def obsmap(histories,targets):
    out={}
    for c in sorted({q["cohort"] for q in targets}):
        for i in keys_for_cohort(histories,c):out[(c,i)]=i
    return out

def permmap(histories,targets,rng):
    out={}
    for c in sorted({q["cohort"] for q in targets}):
        ids=keys_for_cohort(histories,c)
        p=list(rng.permutation(np.asarray(ids,dtype=object)))
        for i,src in zip(ids,p):out[(c,i)]=str(src)
    return out

def stat(targets,histories,assignment,detail=False):
    per=collections.defaultdict(list);details=[]
    for q in targets:
        c=q["cohort"];i=q["focal"];ts=q["session"]
        si=assignment.get((c,i))
        if si is None:continue
        ti=theta(histories,(c,si),ts)
        if ti is None:continue
        donors=[]
        for j,g in q["gains"].items():
            sj=assignment.get((c,j))
            if sj is None:continue
            tj=theta(histories,(c,sj),ts)
            if tj is None:continue
            donors.append((j,float(g),float(np.linalg.norm(ti-tj))))
        if len(donors)<2:continue
        md=min(x[2] for x in donors)
        nearest=[x for x in donors if abs(x[2]-md)<=1e-15]
        non=[x for x in donors if abs(x[2]-md)>1e-15]
        if not nearest or not non:continue
        gn=float(np.mean([x[1] for x in nearest]))
        go=float(np.mean([x[1] for x in non]))
        C=go-gn
        per[(c,i)].append(C)
        if detail:
            details.append({"cohort":c,"session":ts,"focal":i,
              "theta_focal":ti.tolist(),"nearest_donors":[x[0] for x in nearest],
              "nearest_policy_distance":md,"nearest_mean_G":gn,
              "nonnearest_mean_G":go,"C_target":C,"n_evaluable_donors":len(donors)})
    ind={f"{c}:{i}":float(np.mean(v)) for (c,i),v in per.items() if v}
    if not ind:return None,{},details
    return float(np.mean(list(ind.values()))),ind,details

def run(year,panel,seed):
    histories,audit=policy_histories(panel)
    if histories is None:return {"status":"STOP_POLICY_SUPPORT"}
    targets=build_targets(panel,histories)
    om=obsmap(histories,targets)
    obs,ind,detail=stat(targets,histories,om,True)
    if obs is None:return {"status":"STOP_OBSERVED_SUPPORT","n_targets":len(targets)}
    rng=np.random.default_rng(seed);null=[]
    for _ in range(NPERM):
        q,_,_=stat(targets,histories,permmap(histories,targets,rng),False)
        if q is not None and math.isfinite(q):null.append(q)
    a=np.asarray(null,float)
    pos=sum(v>0 for v in ind.values());frac=pos/len(ind)
    p=float((1+np.sum(a>=obs))/(1+len(a)))
    return {
      "status":"DONE","C_panel":float(obs),"individual_C":ind,
      "positive_individuals":pos,"n_individuals":len(ind),"positive_fraction":frac,
      "n_vertical_targets":len(detail),"policy_history_count":len(histories),
      "valid_permutations":int(len(a)),"seed":seed,
      "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
      "null_q975":float(np.quantile(a,.975)),"p_one_sided":p,
      "diagnostic_verdict":"SUPPORTED_BIVARIATE_POLICY_TO_SHAPE"
        if obs>0 and p<=.05 and frac>=.70 else "UNSUPPORTED_BIVARIATE_POLICY_TO_SHAPE",
      "policy_audit":{"colony_retention_pass":audit["colony_retention_pass"]},
      "target_details":detail,
    }

def main():
    print(json.dumps({
      "contract":"BIVARIATE_POLICY_TO_VERTICAL_SHAPE_CONTRACT_V1.md",
      "status":"POST_OUTCOME_MECHANISM_DIAGNOSTIC",
      "frozen_global_field_bridge_reopened":False,
      "years":{y:run(y,p,s) for y,(p,s) in PANELS.items()},
    },ensure_ascii=False,indent=2))
if __name__=="__main__":main()
