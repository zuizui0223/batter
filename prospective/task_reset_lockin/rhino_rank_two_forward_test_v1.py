#!/usr/bin/env python3
"""Same-endpoint, training-only rank-2 vs rank-1 8D bat policy forecasts."""
from __future__ import annotations
import importlib.util
import json
from collections import defaultdict
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("L",HERE/"latent_policy_dimensionality_v1.py")
L=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(L)

N_PERM=9999
PERM_SEED=20261008161
N_BOOT=9999
BOOT_SEED=20261008162
DIMS=(0,1,2,3,4)

def assemble():
    rows, envs=L.standardized_rows()
    if len(rows)!=45 or len(envs)!=7 or sorted({str(r["bat"]) for r in rows})!=["A","B","C","D","E"]:
        raise RuntimeError("source structural gate failed")
    bat_env=defaultdict(list)
    for r in rows:
        bat_env[(int(r["env"]),str(r["bat"]))].append(np.asarray(r["z8"],float))
    clusters={k:np.mean(np.stack(v),axis=0) for k,v in bat_env.items()}
    trials={k:np.stack(v) for k,v in bat_env.items()}
    labels={e:sorted(b for ee,b in clusters if ee==e) for e in envs}
    if len(clusters)!=25:
        raise RuntimeError(f"expected 25 biological bat x environment clusters, got {len(clusters)}")
    if any(len({e for e,b in clusters if b==bat})<4 for bat in ("A","B","C","D","E")):
        raise RuntimeError("insufficient per-bat training configurations")
    return envs,labels,clusters,trials

def perm_mapping(labels,rng=None):
    out={}
    for env,bs in sorted(labels.items()):
        targets=bs if rng is None else list(rng.permutation(np.asarray(bs,dtype=object)))
        for orig,assigned in zip(bs,targets):
            out[(env,orig)]=str(assigned)
    return out

def calculate(envs,labels,clusters,trials,mapping):
    per_bat_env=defaultdict(list)
    for target_env in envs:
        train=defaultdict(list)
        for (e,old),val in clusters.items():
            if e==target_env:continue
            train[mapping[(e,old)]].append((e,val))
        eligible=sorted(b for b,v in train.items() if len(v)>=2)
        if eligible!=["A","B","C","D","E"]:
            return None
        centers=np.stack([np.mean(np.stack([v for e,v in train[b]]),axis=0) for b in eligible])
        grand=np.mean(centers,axis=0)
        _,_,Vt=np.linalg.svd(centers-grand,full_matrices=False)
        for (e,old),features in trials.items():
            if e!=target_env:continue
            b=mapping[(e,old)]
            idx=eligible.index(b)
            v=centers[idx]-grand
            errs=[]
            for d in DIMS:
                pred=grand if d==0 else grand+(v@Vt[:d].T)@Vt[:d]
                errors=np.mean((features-pred)**2,axis=1)
                errs.append(float(np.mean(errors)))
            per_bat_env[b].append(errs)
    if sorted(per_bat_env)!=["A","B","C","D","E"]:
        return None
    per_bat={b:np.mean(np.asarray(per_bat_env[b],float),axis=0) for b in sorted(per_bat_env)}
    program=np.mean(np.stack(list(per_bat.values())),axis=0)
    if not np.all(np.isfinite(program)):
        return None
    return program,per_bat

def summarize(loss):
    return {
      "rank_losses":{str(d):float(loss[d]) for d in DIMS},
      "gain_1_given_0":float(loss[0]-loss[1]),
      "gain_2_given_1":float(loss[1]-loss[2]),
      "gain_2_given_0":float(loss[0]-loss[2]),
      "relative_change_2_vs_1":float((loss[2]-loss[1])/loss[1])
    }

def main():
    envs,labels,clusters,trials=assemble()
    obs=calculate(envs,labels,clusters,trials,perm_mapping(labels))
    if obs is None:raise RuntimeError("observed target gate failed")
    losses,per_bat=obs
    observed=summarize(losses)
    individual={b:summarize(v) for b,v in per_bat.items()}
    primary=observed["gain_2_given_1"]

    rng=np.random.default_rng(PERM_SEED)
    nul=np.empty(N_PERM,float)
    for k in range(N_PERM):
        q=calculate(envs,labels,clusters,trials,perm_mapping(labels,rng))
        if q is None:raise RuntimeError(f"invalid permutation {k}")
        nul[k]=float(q[0][1]-q[0][2])
    p=float((1+np.sum(nul>=primary-1e-12))/(N_PERM+1))

    bats=sorted(per_bat)
    matrix=np.stack([per_bat[b] for b in bats])
    bootrng=np.random.default_rng(BOOT_SEED)
    sampled=bootrng.integers(0,len(bats),size=(N_BOOT,len(bats)))
    boots=np.mean(matrix[sampled,:,],axis=1)
    gains=boots[:,1]-boots[:,2]
    lo,hi=np.quantile(gains,[.025,.975])
    positive=int(sum(individual[b]["gain_2_given_1"]>0 for b in bats))
    supported=bool(primary>0 and p<=.05 and positive>=4 and lo>0)
    output={
      "study_id":"rhino-rank-two-forward-test-v1",
      "evidence_status":"POST_OUTCOME_DIAGNOSTIC_NOT_INDEPENDENT_CONFIRMATION",
      "source":"45 Rhinolophus trajectories, 7 obstacle environments",
      "transductive_normalization":True,
      "target_trajectories":sum(len(t) for t in trials.values()),
      "bat_env_clusters":len(clusters),
      "observed":observed,
      "individual_results":individual,
      "primary_null":{"B":N_PERM,"seed":PERM_SEED,"mean":float(nul.mean()),
          "ci95":[float(np.quantile(nul,.025)),float(np.quantile(nul,.975))],
          "p_one_sided":p},
      "bat_cluster_bootstrap":{"B":N_BOOT,"seed":BOOT_SEED,
          "primary_ci95":[float(lo),float(hi)]},
      "positive_bats":positive,
      "supported_under_frozen_rule":supported,
      "claim_boundary":[
          "Rank1 identity sufficiency does not equal full trajectory sufficiency.",
          "Rank2 forecast improvement is scored on the same original eight-feature endpoint.",
          "Source normalization includes target environment unlabeled distribution.",
          "No unique dynamical law, biological stationarity or intrinsic dimensionality inferred."
      ]
    }
    out=HERE/"RHINO_RANK_TWO_FORWARD_TEST_RESULT_V1.json"
    out.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
      "observed":observed,"positive_bats":positive,
      "individual_gains":{b:individual[b]["gain_2_given_1"] for b in bats},
      "null":output["primary_null"],"bootstrap_ci95":[float(lo),float(hi)],
      "supported":supported
    },sort_keys=True))
if __name__=="__main__": main()
