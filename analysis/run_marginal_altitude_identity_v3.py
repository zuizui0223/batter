#!/usr/bin/env python3
from __future__ import annotations

import itertools, json, hashlib
from pathlib import Path

import numpy as np
import run_individual_vertical_strategy_v1 as v1

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"analysis/marginal_altitude_identity_contract_v3.json"
BASE=ROOT/"analysis/individual_vertical_strategy_contract_v1.json"
OUT=ROOT/"results/marginal_altitude_identity_result_v3.json"

def build(halves,k,alpha,lam):
    ids=sorted(halves)
    marg={}
    for iid in ids:
        counts=np.zeros(k,dtype=float)
        for _,_,_,z in halves[iid]["early"]:
            counts[z]+=1
        marg[iid]=counts
    species=np.mean(np.stack([v1.smooth(marg[i],alpha) for i in ids]),axis=0)
    individual={}
    for iid in ids:
        counts=marg[iid]
        n=float(counts.sum())
        individual[iid]=(counts+float(lam)*species)/(n+float(lam))
    return ids,species,individual

def score(halves,ids,species,individual):
    matrix=np.zeros((len(ids),len(ids)),dtype=float)
    counts={}
    for j,target in enumerate(ids):
        events=halves[target]["late"]
        counts[target]=len(events)
        for i,source in enumerate(ids):
            vals=[
                v1.safe_log(individual[source][z])-v1.safe_log(species[z])
                for _,_,_,z in events
            ]
            matrix[i,j]=float(np.mean(vals))
    return matrix,counts

def exact(matrix):
    n=matrix.shape[0]
    observed=float(np.mean([matrix[i,i] for i in range(n)]))
    stats=[]; ge=0
    for perm in itertools.permutations(range(n)):
        x=float(np.mean([matrix[perm[j],j] for j in range(n)]))
        stats.append(x)
        ge+=int(x>=observed-1e-15)
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
    ids,species,individual=build(
        halves,k,float(c["inherited"]["jeffreys_alpha"]),float(lam)
    )
    matrix,event_counts=score(halves,ids,species,individual)
    diag=np.asarray([matrix[i,i] for i in range(len(ids))])
    test=exact(matrix)
    positive=int(np.sum(diag>0))
    top1=sum(int(matrix[j,j]>np.max(np.delete(matrix[:,j],j))) for j in range(len(ids)))
    passed=bool(test["one_sided_p"]<=0.05 and positive>=6)
    return {
        "lambda":lam,
        "individual_ids":ids,
        "late_event_counts":event_counts,
        "source_by_target_marginal_gain_matrix":matrix.tolist(),
        "individual_diagonal_marginal_gain":{iid:float(diag[i]) for i,iid in enumerate(ids)},
        "positive_diagonal_count":positive,
        "self_distribution_strict_top1_count":top1,
        "identity_permutation_test":test,
        "primary_pass":passed,
        "category":(
            "individual_specific_marginal_altitude_distribution_supported"
            if passed else
            "individual_specific_marginal_altitude_distribution_not_supported"
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
        "schema":"batter.marginal_altitude_identity.result.v3",
        "source_md5":hashlib.md5(raw).hexdigest(),
        "individual_count":len(halves),
        "role":c["role"],
        "primary":primary,
        "sensitivities":sens,
        "sensitivities_cannot_replace_primary":True,
        "v1_and_v2_results_unchanged":True,
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
