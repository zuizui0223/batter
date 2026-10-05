#!/usr/bin/env python3
"""Vectorized exact-equivalent bivariate policy-to-vertical-shape localization.

Implements BIVARIATE_POLICY_TO_VERTICAL_SHAPE_CONTRACT_V1.md with the same
policy histories, vertical-shape gains, assignment null, seeds and aggregation.
"""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent

spec=importlib.util.spec_from_file_location("BV",HERE/"phyllostomus_fixed_bin_bivariate_carrier_v1.py")
BV=importlib.util.module_from_spec(spec);spec.loader.exec_module(BV)

spec2=importlib.util.spec_from_file_location("W",HERE/"wild_policy_to_vertical_shape_v1.py")
W=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(W)

NPERM=9999
PANELS={
 "2022":("phyllostomus_2022",202610051471),
 "2023":("phyllostomus_2023",202610051472),
}

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

def theta_for(histories,c,src,target_session):
    vals=[v for s,v in histories[(c,src)] if s!=target_session]
    if not vals:return None
    return np.mean(np.vstack(vals),axis=0)

def build(panel,histories):
    targets=[]
    for q in W.build_vertical_targets(panel):
        c=q["cohort"];i=q["focal"]
        ids=sorted(src for cc,src in histories if cc==c)
        if i not in ids:continue
        gains={j:float(g) for j,g in q["gains"].items() if j in ids}
        if len(gains)<2:continue
        targets.append({"cohort":c,"session":q["session"],"focal":i,"gains":gains})
    return targets

def cohort_struct(histories,targets):
    out={}
    for c in sorted({q["cohort"] for q in targets}):
        ids=sorted(src for cc,src in histories if cc==c)
        idx={x:i for i,x in enumerate(ids)}
        out[c]={"ids":ids,"idx":idx}
    return out

def make_permutations(struct,seed):
    """Same RNG call order as original permutation_assignment()."""
    rng=np.random.default_rng(seed)
    P={c:np.empty((NPERM,len(d["ids"])),dtype=np.int16) for c,d in struct.items()}
    cohorts=sorted(struct)
    for z in range(NPERM):
        for c in cohorts:
            L=len(struct[c]["ids"])
            P[c][z]=rng.permutation(np.arange(L,dtype=np.int16))
    return P

def target_C_all(q,histories,struct,P):
    c=q["cohort"];ts=q["session"];focal=q["focal"]
    ids=struct[c]["ids"];idx=struct[c]["idx"];L=len(ids)
    fi=idx[focal]
    donors=sorted(q["gains"])
    di=np.asarray([idx[j] for j in donors],int)
    g=np.asarray([q["gains"][j] for j in donors],float)

    # Target-specific theta for every possible source history.
    T=np.empty((L,2),float)
    valid=np.ones(L,bool)
    for k,src in enumerate(ids):
        t=theta_for(histories,c,src,ts)
        if t is None:
            valid[k]=False;T[k]=np.nan
        else:T[k]=t

    # Observed assignment is identity.
    tf=T[fi]
    td=T[di]
    dist=np.linalg.norm(td-tf[None,:],axis=1)
    if not np.all(np.isfinite(dist)): return None,None
    md=float(np.min(dist))
    near=np.isclose(dist,md,rtol=0,atol=1e-15)
    if near.all():return None,None
    Cobs=float(np.mean(g[~near])-np.mean(g[near]))

    # Permuted assignment: bio label b receives source index P[:, b].
    PP=P[c]
    sf=PP[:,fi]                         # [perm]
    sd=PP[:,di]                         # [perm,donor]
    good=valid[sf] & np.all(valid[sd],axis=1)
    C=np.full(NPERM,np.nan,float)
    if np.any(good):
        tfp=T[sf[good]]                 # [n,2]
        tdp=T[sd[good]]                 # [n,D,2]
        dd=np.linalg.norm(tdp-tfp[:,None,:],axis=2)
        mins=np.min(dd,axis=1,keepdims=True)
        nearp=np.isclose(dd,mins,rtol=0,atol=1e-15)
        nnear=np.sum(nearp,axis=1)
        # exact mean near and mean non-near
        sumnear=nearp@g
        total=float(np.sum(g))
        meannear=sumnear/nnear
        nnon=len(g)-nnear
        ok=nnon>0
        vals=np.full(len(meannear),np.nan,float)
        vals[ok]=(total-sumnear[ok])/nnon[ok]-meannear[ok]
        C[np.flatnonzero(good)]=vals
    return Cobs,C

def aggregate(targets,histories,struct,P):
    obs_by_ind=collections.defaultdict(list)
    null_by_ind=collections.defaultdict(list)
    details=[]
    for q in targets:
        co=q["cohort"];f=q["focal"]
        cobs,cnull=target_C_all(q,histories,struct,P)
        if cobs is None:continue
        key=(co,f)
        obs_by_ind[key].append(cobs)
        null_by_ind[key].append(cnull)
        details.append((key,cobs))
    if not obs_by_ind:return None

    keys=sorted(obs_by_ind)
    obs_ind={f"{c}:{i}":float(np.mean(obs_by_ind[(c,i)])) for c,i in keys}
    obs=float(np.mean(list(obs_ind.values())))

    # Equal targets within biological individual, then equal individuals.
    M=[]
    for k in keys:
        A=np.vstack(null_by_ind[k])
        M.append(np.nanmean(A,axis=0))
    N=np.vstack(M)
    null=np.nanmean(N,axis=0)
    valid=np.all(np.isfinite(N),axis=0)
    null=null[valid]
    return obs,obs_ind,null,len(details)

def run(year,panel,seed):
    histories,audit=policy_histories(panel)
    if histories is None:return {"status":"STOP_POLICY_SUPPORT"}
    targets=build(panel,histories)
    struct=cohort_struct(histories,targets)
    P=make_permutations(struct,seed)
    q=aggregate(targets,histories,struct,P)
    if q is None:return {"status":"STOP_OBSERVED_SUPPORT"}
    obs,ind,null,nt=q
    if len(null)<9500:
        return {"status":"STOP_RANDOMIZATION_SUPPORT","valid_permutations":int(len(null))}
    pos=sum(v>0 for v in ind.values());frac=pos/len(ind)
    p=float((1+np.sum(null>=obs))/(1+len(null)))
    return {
      "status":"DONE","C_panel":obs,"individual_C":ind,
      "positive_individuals":pos,"n_individuals":len(ind),"positive_fraction":frac,
      "n_vertical_targets":nt,"policy_history_count":len(histories),
      "valid_permutations":int(len(null)),"seed":seed,
      "null_mean":float(np.mean(null)),"null_q025":float(np.quantile(null,.025)),
      "null_q975":float(np.quantile(null,.975)),"p_one_sided":p,
      "diagnostic_verdict":"SUPPORTED_BIVARIATE_POLICY_TO_SHAPE"
        if obs>0 and p<=.05 and frac>=.70 else "UNSUPPORTED_BIVARIATE_POLICY_TO_SHAPE",
      "policy_audit":{"colony_retention_pass":audit["colony_retention_pass"]},
    }

def main():
    out={
      "contract":"BIVARIATE_POLICY_TO_VERTICAL_SHAPE_CONTRACT_V1.md",
      "implementation":"vectorized_exact_equivalent_v1",
      "status":"POST_OUTCOME_MECHANISM_DIAGNOSTIC",
      "frozen_global_field_bridge_reopened":False,
      "years":{y:run(y,p,s) for y,(p,s) in PANELS.items()}
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
