#!/usr/bin/env python3
from __future__ import annotations

import itertools, json, math
from pathlib import Path

import numpy as np

import run_individual_vertical_strategy_v1 as v1

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"analysis/spatial_interaction_refinement_contract_v2.json"
V1_CONTRACT=ROOT/"analysis/individual_vertical_strategy_contract_v1.json"
OUT=ROOT/"results/spatial_interaction_refinement_result_v2.json"

def _normalize(x):
    a=np.asarray(x,dtype=float)
    total=float(a.sum())
    if total<=0: raise RuntimeError("zero probability mass")
    return a/total

def build(halves,k,c,lam):
    alpha=float(c["inherited_without_change"]["jeffreys_alpha"])
    ids=sorted(halves)
    cells=sorted({x[2] for h in halves.values() for x in h["early"]})
    counts={iid:{} for iid in ids}
    marg={iid:np.zeros(k,dtype=float) for iid in ids}
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
    species_marg=np.mean(np.stack([v1.smooth(marg[i],alpha) for i in ids]),axis=0)

    ind_marg={}
    additive={}; full={}
    for iid in ids:
        n=float(marg[iid].sum())
        ind_marg[iid]=(marg[iid]+float(lam)*species_marg)/(n+float(lam))
        additive[iid]={}; full[iid]={}
        ratio=ind_marg[iid]/species_marg
        for cell,p_species in species_cond.items():
            p_add=_normalize(p_species*ratio)
            additive[iid][cell]=p_add
            cc=counts[iid].get(cell,np.zeros(k,dtype=float))
            nc=float(cc.sum())
            full[iid][cell]=(cc+float(lam)*p_add)/(nc+float(lam))
    return ids,species_cond,additive,full

def score(halves,ids,species_cond,additive,full):
    n=len(ids)
    matrix=np.zeros((n,n),dtype=float)
    event_counts={}
    for j,target in enumerate(ids):
        events=[x for x in halves[target]["late"] if x[2] in species_cond]
        event_counts[target]=len(events)
        for i,source in enumerate(ids):
            vals=[
                v1.safe_log(full[source][cell][z])-v1.safe_log(additive[source][cell][z])
                for _,_,cell,z in events
            ]
            matrix[i,j]=float(np.mean(vals))
    return matrix,event_counts

def exact(matrix):
    n=matrix.shape[0]
    obs=float(np.mean([matrix[i,i] for i in range(n)]))
    ge=0; stats=[]
    for perm in itertools.permutations(range(n)):
        x=float(np.mean([matrix[perm[j],j] for j in range(n)]))
        stats.append(x); ge+=int(x>=obs-1e-15)
    a=np.asarray(stats)
    return {
        "observed_diagonal_mean_residual_gain":obs,
        "permutation_count":len(stats),
        "one_sided_p":ge/len(stats),
        "null_mean":float(a.mean()),
        "null_q05":float(np.quantile(a,0.05)),
        "null_q95":float(np.quantile(a,0.95))
    }

def run_one(halves,k,c,lam):
    ids,sc,add,full=build(halves,k,c,lam)
    matrix,event_counts=score(halves,ids,sc,add,full)
    test=exact(matrix)
    diag=np.asarray([matrix[i,i] for i in range(len(ids))])
    positive=int(np.sum(diag>0))
    top1=sum(int(matrix[j,j]>np.max(np.delete(matrix[:,j],j))) for j in range(len(ids)))
    passed=bool(test["one_sided_p"]<=0.05 and positive>=6)
    return {
        "lambda":lam,
        "individual_ids":ids,
        "late_event_counts":event_counts,
        "source_by_target_spatial_residual_gain_matrix":matrix.tolist(),
        "individual_diagonal_spatial_residual_gain":{iid:float(diag[i]) for i,iid in enumerate(ids)},
        "positive_diagonal_count":positive,
        "self_map_strict_top1_count":top1,
        "identity_permutation_test":test,
        "primary_pass":passed,
        "category":(
            "individual_by_location_vertical_strategy_supported"
            if passed else
            "individual_by_location_vertical_strategy_not_supported"
        )
    }

def main():
    c=json.loads(CONTRACT.read_text())
    base=json.loads(V1_CONTRACT.read_text())
    raw,rows,k,_=v1.load_events(base)
    halves=v1.split_events(rows,base)
    primary=run_one(halves,k,c,int(c["inherited_without_change"]["primary_lambda"]))
    sens={str(x):run_one(halves,k,c,int(x)) for x in c["inherited_without_change"]["sensitivity_lambdas"]}
    result={
        "schema":"batter.spatial_interaction_refinement.result.v2",
        "source_md5":base["source"]["md5"],
        "individual_count":len(halves),
        "primary":primary,
        "sensitivities":sens,
        "sensitivities_cannot_replace_primary":True,
        "v1_result_reclassified":False,
        "claim_boundary":{"prohibited":c["prohibited"]}
    }
    import hashlib
    result["fingerprint"]=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
