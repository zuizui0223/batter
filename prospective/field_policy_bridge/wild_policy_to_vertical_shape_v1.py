#!/usr/bin/env python3
"""Conditional wild FlightIntensity -> centered vertical-shape bridge.

Runs only when the frozen carrier JSON passes its >=3/4 panel gate.
Scientific contract:
- WILD_POLICY_TO_VERTICAL_SHAPE_CONTRACT_V1.md
- WILD_POLICY_TO_VERTICAL_SHAPE_ESTIMATOR_APPENDIX_V1.md
"""
from __future__ import annotations

import argparse
import collections
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_cross_panel_estimator_calibration as cal
import scripts.run_tag_altitude_bias_shape as shape

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("W",HERE/"wild_flight_intensity_persistence_v1.py")
W=importlib.util.module_from_spec(spec); spec.loader.exec_module(W)

PANELS={
 "hypsignathus":("contract/hypsignathus_replication_v1.json",202610051321),
 "phyllostomus_2022":("contract/phyllostomus_replication_v1.json",202610051322),
 "phyllostomus_2023":("contract/phyllostomus_2023_replication_v1.json",202610051323),
 "phyllostomus_2016":("contract/phyllostomus_2016_dry_architecture_v1.json",202610051324),
}
NPERM=9999
MIN_SCORED=50
ALPHA=0.5

def policy_histories(panel,path):
    sessions,audit=W.prepare(panel,path)
    by=collections.defaultdict(list)
    for s in sessions:
        by[(s["cohort"],s["iid"])].append((s["session"],float(s["I"])))
    # persistence prepare() already applies >=2 policy-valid sessions per individual
    return {k:sorted(v) for k,v in by.items()},audit

def donor_gain(A,t,donor_lab):
    counts=A["counts"]; cell_tot=A["cell_tot"]; sess_cond=A["sess_cond"]
    labels=A["orig_labels"]; S,C,K=counts.shape
    focal=int(labels[t])
    idx_all=np.arange(S)
    self_sel=np.flatnonzero((labels==focal)&(idx_all!=t))
    donor_sel=np.flatnonzero(labels==donor_lab)
    if len(self_sel)==0 or len(donor_sel)==0:
        return None
    p_self=cal.mean_nan_axis0(sess_cond[self_sel])
    p_donor=cal.mean_nan_axis0(sess_cond[donor_sel])
    target_cell_tot=cell_tot[t]
    supported=(target_cell_tot>0)&(~np.isnan(p_self[:,0]))&(~np.isnan(p_donor[:,0]))
    scored=int(target_cell_tot[supported].sum())
    if scored<MIN_SCORED:
        return None
    supported_idx=np.flatnonzero(supported)
    target_counts=counts[t,supported,:].astype(float)
    target_z=target_counts.sum(axis=0)
    ps=p_self[supported,:]; pd=p_donor[supported,:]
    ws=[]
    for s in self_sel:
        w=cell_tot[s,supported_idx].astype(float)
        tot=w.sum()
        if tot>0:
            ws.append(w/tot)
    if not ws:
        return None
    w=np.mean(np.stack(ws),axis=0)
    w=w/w.sum()
    m_self=np.sum(ps*w[:,None],axis=0)
    m_donor=np.sum(pd*w[:,None],axis=0)
    g=float(np.sum(target_z*(np.log(m_self)-np.log(m_donor)))/scored)
    return {"G":g,"scored_fixes":scored}

def build_vertical_targets(panel):
    records,_=shape.panel_raw(panel)
    events_by_cohort,_=shape.centered_events(records)
    arrays={c:cal.make_cohort_arrays(e,len(shape.EDGES)-1) for c,e in sorted(events_by_cohort.items())}
    targets=[]
    for cohort,A in arrays.items():
        labels=A["orig_labels"]
        for t,session in enumerate(A["sessions"]):
            focal_lab=int(labels[t])
            focal=A["label_names"][focal_lab]
            # Must have vertical self history.
            if int(np.sum(labels==focal_lab))<2:
                continue
            gains={}
            support={}
            for dl,donor in enumerate(A["label_names"]):
                if dl==focal_lab: continue
                q=donor_gain(A,t,dl)
                if q is not None:
                    gains[donor]=q["G"]
                    support[donor]=q["scored_fixes"]
            if len(gains)>=2:
                targets.append({
                    "cohort":cohort,"session":session,"focal":focal,
                    "gains":gains,"scored_fixes_by_donor":support,
                })
    return targets

def history_assignment_keys(histories,cohort):
    return sorted(i for c,i in histories if c==cohort)

def theta_from_assigned(histories,cohort,source_iid,target_session):
    vals=[v for s,v in histories.get((cohort,source_iid),[]) if s!=target_session]
    if not vals:
        return None
    return float(np.mean(vals))

def panel_stat(targets,histories,assignment):
    # assignment[(cohort, biological_label)] = source history iid
    per_ind=collections.defaultdict(list)
    target_detail=[]
    for q in targets:
        c=q["cohort"]; i=q["focal"]; ts=q["session"]
        src_i=assignment.get((c,i))
        if src_i is None:
            continue
        theta_i=theta_from_assigned(histories,c,src_i,ts)
        if theta_i is None:
            continue
        donor_rows=[]
        for j,g in q["gains"].items():
            src_j=assignment.get((c,j))
            if src_j is None:
                continue
            theta_j=theta_from_assigned(histories,c,src_j,ts)
            if theta_j is None:
                continue
            donor_rows.append((j,float(g),abs(theta_i-theta_j),theta_j))
        if len(donor_rows)<2:
            continue
        mind=min(x[2] for x in donor_rows)
        nearest=[x for x in donor_rows if x[2]==mind]
        non=[x for x in donor_rows if x[2]!=mind]
        if not nearest or not non:
            continue
        gnear=float(np.mean([x[1] for x in nearest]))
        gother=float(np.mean([x[1] for x in non]))
        C=gother-gnear
        key=(c,i)
        per_ind[key].append(C)
        target_detail.append({
            "cohort":c,"session":ts,"focal":i,
            "theta_focal":theta_i,
            "nearest_donors":[x[0] for x in nearest],
            "nearest_policy_distance":mind,
            "nearest_mean_G":gnear,
            "nonnearest_mean_G":gother,
            "C_target":C,
            "n_evaluable_donors":len(donor_rows),
        })
    indiv={f"{c}:{i}":float(np.mean(v)) for (c,i),v in per_ind.items() if v}
    if not indiv:
        return None,{},target_detail
    return float(np.mean(list(indiv.values()))),indiv,target_detail

def observed_assignment(histories,vertical_targets):
    cohorts=sorted(set(q["cohort"] for q in vertical_targets))
    mp={}
    for c in cohorts:
        ids=history_assignment_keys(histories,c)
        for i in ids: mp[(c,i)]=i
    return mp

def permutation_assignment(histories,vertical_targets,rng):
    cohorts=sorted(set(q["cohort"] for q in vertical_targets))
    mp={}
    for c in cohorts:
        ids=history_assignment_keys(histories,c)
        p=list(rng.permutation(np.asarray(ids,dtype=object)))
        for i,src in zip(ids,p): mp[(c,i)]=str(src)
    return mp

def run_panel(panel,path,seed):
    histories,paudit=policy_histories(panel,path)
    targets=build_vertical_targets(panel)
    # Keep only targets whose focal and at least two donors have eligible policy histories.
    filtered=[]
    for q in targets:
        c=q["cohort"]; i=q["focal"]
        if (c,i) not in histories: continue
        dg={j:g for j,g in q["gains"].items() if (c,j) in histories}
        ds={j:n for j,n in q["scored_fixes_by_donor"].items() if j in dg}
        if len(dg)>=2:
            qq=dict(q);qq["gains"]=dg;qq["scored_fixes_by_donor"]=ds;filtered.append(qq)
    targets=filtered
    om=observed_assignment(histories,targets)
    obs,indiv,detail=panel_stat(targets,histories,om)
    if obs is None or len(indiv)<1:
        return {"status":"STOP_VERTICAL_POLICY_SUPPORT",
                "n_policy_histories":len(histories),"n_vertical_targets":len(targets)}

    rng=np.random.default_rng(seed)
    null=[]
    for _ in range(NPERM):
        mp=permutation_assignment(histories,targets,rng)
        s,_,_=panel_stat(targets,histories,mp)
        if s is not None and math.isfinite(s): null.append(s)
    a=np.asarray(null,float)
    if len(a)<9500:
        return {"status":"STOP_RANDOMIZATION_SUPPORT","C_panel":obs,
                "valid_permutations":len(a),"n_vertical_targets":len(targets)}

    p=float((1+np.sum(a>=obs))/(1+len(a)))
    pos=sum(v>0 for v in indiv.values())
    return {
        "status":"DONE",
        "C_panel":float(obs),
        "individual_C":indiv,
        "positive_individuals":pos,
        "n_individuals":len(indiv),
        "positive_fraction":pos/len(indiv),
        "individual_pass":bool(obs>0 and p<=.05),
        "n_vertical_targets":len(detail),
        "target_details":detail,
        "policy_history_count":len(histories),
        "policy_audit":paudit,
        "requested_permutations":NPERM,
        "valid_permutations":len(a),
        "seed":seed,
        "null_mean":float(a.mean()),
        "null_q025":float(np.quantile(a,.025)),
        "null_q975":float(np.quantile(a,.975)),
        "p_one_sided":p,
        "_null":a,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--carrier-json",required=True)
    args=ap.parse_args()
    carrier=json.loads(Path(args.carrier_json).read_text(encoding="utf-8"))
    if not carrier.get("field_FlightIntensity_carrier_supported",False):
        out={
          "contract":"WILD_POLICY_TO_VERTICAL_SHAPE_ESTIMATOR_APPENDIX_V1.md",
          "status":"STOP_CARRIER_GATE",
          "carrier_panels_passed":carrier.get("n_panels_passed"),
          "bridge_opened":False,
        }
        print(json.dumps(out,indent=2));return

    open_panels=[p for p in PANELS if carrier.get("panels",{}).get(p,{}).get("status")=="PASS_PANEL"]
    results={}
    nulls=[]
    obsvals=[]
    for p in PANELS:
        if p not in open_panels:
            results[p]={"status":"STOP_PANEL_CARRIER_FAIL"}
            continue
        path,seed=PANELS[p]
        q=run_panel(p,path,seed)
        if "_null" in q:
            nulls.append(q["_null"]);obsvals.append(q["C_panel"])
            q={k:v for k,v in q.items() if k!="_null"}
        results[p]=q

    if len(nulls)>=3:
        n=min(len(x) for x in nulls)
        comb=np.mean(np.vstack([x[:n] for x in nulls]),axis=0)
        obscomb=float(np.mean(obsvals))
        pcomb=float((1+np.sum(comb>=obscomb))/(1+len(comb)))
    else:
        obscomb=None;pcomb=None;n=0

    n_pos=sum(results[p].get("C_panel",0)>0 for p in PANELS)
    n_indpass=sum(bool(results[p].get("individual_pass",False)) for p in PANELS)
    success=bool(len(open_panels)>=3 and n_pos>=3 and n_indpass>=2 and pcomb is not None and pcomb<=.05)

    out={
      "contract":"WILD_POLICY_TO_VERTICAL_SHAPE_ESTIMATOR_APPENDIX_V1.md",
      "status":"POST_JAE_CONDITIONAL_POLICY_TO_SHAPE_BRIDGE",
      "bridge_opened":True,
      "carrier_open_panels":open_panels,
      "panels":results,
      "n_original_panels_positive":n_pos,
      "n_original_panels_individually_passing":n_indpass,
      "combined_equal_open_panel_C":obscomb,
      "combined_valid_permutations":n,
      "combined_p_one_sided":pcomb,
      "bridge_supported":success,
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
