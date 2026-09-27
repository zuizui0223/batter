#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import run_individual_vertical_strategy_v1 as v1

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"analysis/shared_template_individual_reweighting_contract_v4.json"
BASE=ROOT/"analysis/individual_vertical_strategy_contract_v1.json"
OUT=ROOT/"results/shared_template_individual_reweighting_result_v4.json"

def normalize(x):
    a=np.asarray(x,dtype=float)
    s=float(a.sum())
    if s<=0:
        raise RuntimeError("zero probability mass")
    return a/s

def build(halves,k,alpha,lam):
    ids=sorted(halves)
    counts={iid:{} for iid in ids}
    marg={iid:np.zeros(k,dtype=float) for iid in ids}
    cells=sorted({x[2] for h in halves.values() for x in h["early"]})
    for iid in ids:
        for _,_,cell,z in halves[iid]["early"]:
            counts[iid].setdefault(cell,np.zeros(k,dtype=float))[z]+=1
            marg[iid][z]+=1

    species_cond={}
    for cell in cells:
        ps=[]
        for iid in ids:
            if cell in counts[iid]:
                ps.append(v1.smooth(counts[iid][cell],alpha))
        if ps:
            species_cond[cell]=np.mean(np.stack(ps),axis=0)

    species_marg=np.mean(
        np.stack([v1.smooth(marg[i],alpha) for i in ids]),
        axis=0
    )

    ind_marg={}
    reweighted={}
    for iid in ids:
        raw=marg[iid]
        n=float(raw.sum())
        p_i=(raw+float(lam)*species_marg)/(n+float(lam))
        ind_marg[iid]=p_i
        ratio=p_i/species_marg
        reweighted[iid]={
            cell:normalize(p_cell*ratio)
            for cell,p_cell in species_cond.items()
        }
    return ids,species_cond,species_marg,ind_marg,reweighted

def score(halves,ids,species_cond,reweighted):
    matrix=np.zeros((len(ids),len(ids)),dtype=float)
    event_counts={}
    for j,target in enumerate(ids):
        events=[x for x in halves[target]["late"] if x[2] in species_cond]
        event_counts[target]=len(events)
        for i,source in enumerate(ids):
            vals=[
                v1.safe_log(reweighted[source][cell][z]) -
                v1.safe_log(species_cond[cell][z])
                for _,_,cell,z in events
            ]
            matrix[i,j]=float(np.mean(vals))
    return matrix,event_counts

def exact(matrix):
    n=matrix.shape[0]
    observed=float(np.mean([matrix[i,i] for i in range(n)]))
    stats=[]; ge=0
    for perm in itertools.permutations(range(n)):
        x=float(np.mean([matrix[perm[j],j] for j in range(n)]))
        stats.append(x)
        ge += int(x>=observed-1e-15)
    a=np.asarray(stats)
    return {
        "observed_diagonal_mean_gain":observed,
        "permutation_count":len(stats),
        "one_sided_p":ge/len(stats),
        "null_mean":float(a.mean()),
        "null_q05":float(np.quantile(a,0.05)),
        "null_q95":float(np.quantile(a,0.95))
    }

def run_one(halves,k,c,lam):
    ids,species_cond,_,_,reweighted=build(
        halves,k,float(c["inherited"]["jeffreys_alpha"]),float(lam)
    )
    matrix,event_counts=score(halves,ids,species_cond,reweighted)
    diag=np.asarray([matrix[i,i] for i in range(len(ids))])
    test=exact(matrix)
    positive=int(np.sum(diag>0))
    top1=sum(int(matrix[j,j]>np.max(np.delete(matrix[:,j],j))) for j in range(len(ids)))
    passed=bool(test["one_sided_p"]<=0.05 and positive>=6)
    return {
        "lambda":lam,
        "individual_ids":ids,
        "late_event_counts":event_counts,
        "source_by_target_reweighting_gain_matrix":matrix.tolist(),
        "individual_diagonal_reweighting_gain":{iid:float(diag[i]) for i,iid in enumerate(ids)},
        "positive_diagonal_count":positive,
        "self_reweighting_strict_top1_count":top1,
        "identity_permutation_test":test,
        "primary_pass":passed,
        "category":(
            "shared_spatial_template_individual_reweighting_supported"
            if passed else
            "shared_spatial_template_individual_reweighting_not_supported"
        )
    }

def main():
    c=json.loads(CONTRACT.read_text())
    base=json.loads(BASE.read_text())
    raw,rows,k,_=v1.load_events(base)
    halves=v1.split_events(rows,base)
    primary=run_one(halves,k,c,int(c["inherited"]["primary_lambda"]))
    sens={str(x):run_one(halves,k,c,int(x)) for x in c["inherited"]["sensitivity_lambdas"]}
    result={
        "schema":"batter.shared_template_individual_reweighting.result.v4",
        "source_md5":hashlib.md5(raw).hexdigest(),
        "individual_count":len(halves),
        "role":c["role"],
        "primary":primary,
        "sensitivities":sens,
        "sensitivities_cannot_replace_primary":True,
        "v1_v2_v3_unchanged":True,
        "prohibited_interpretations":c["prohibited"]
    }
    result["fingerprint"]=hashlib.sha256(
        json.dumps(result,sort_keys=True,separators=(",",":")).encode()
    ).hexdigest()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
