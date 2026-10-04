#!/usr/bin/env python3
"""Focused fast calibration of the 1-D training-only identity subspace."""
from __future__ import annotations
import collections, importlib.util, json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("L",HERE/"latent_policy_dimensionality_v1.py")
L=importlib.util.module_from_spec(spec);spec.loader.exec_module(L)

NPERM=9999
SEED=202610042292

def prepare():
    rows,envs=L.standardized_rows()
    labelsets=L.env_label_sets(rows,envs)
    # 8D cluster means and target arrays.
    cmean={}
    cvals={}
    for e in envs:
        for b in labelsets[e]:
            vals=np.vstack([r["z8"] for r in rows if r["env"]==e and r["bat"]==b])
            cmean[(e,b)]=vals.mean(axis=0)
            cvals[(e,b)]=vals
    return rows,envs,labelsets,cmean,cvals

def stat(envs,labelsets,cmean,cvals,mapping):
    perbat=collections.defaultdict(list)
    for e0 in envs:
        train_env=[e for e in envs if e!=e0]
        # assigned-label cluster means
        assigned=collections.defaultdict(dict)
        for e in train_env:
            for old in labelsets[e]:
                assigned[mapping[(e,old)]][e]=cmean[(e,old)]
        # Require five stable labels with >=2 train environments.
        labs=sorted([b for b,d in assigned.items() if len(d)>=2])
        if len(labs)<5:return None,{}
        batcent=np.vstack([np.mean(np.vstack(list(assigned[b].values())),axis=0) for b in labs])
        grand=batcent.mean(axis=0)
        C=batcent-grand
        _,_,Vt=np.linalg.svd(C,full_matrices=False)
        v=Vt[0]
        cent1={b:float((batcent[i]-grand)@v) for i,b in enumerate(labs)}
        if len(cent1)<3:return None,{}
        for old in labelsets[e0]:
            new=mapping[(e0,old)]
            if new not in cent1:continue
            donors=[b for b in cent1 if b!=new]
            if len(donors)<2:continue
            zvals=(cvals[(e0,old)]-grand)@v
            for z in zvals:
                ds=abs(float(z)-cent1[new])
                do=float(np.mean([abs(float(z)-cent1[b]) for b in donors]))
                perbat[new].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in perbat.items() if v}
    if len(bm)<3:return None,bm
    return float(np.mean(list(bm.values()))),bm

def main():
    rows,envs,labelsets,cmean,cvals=prepare()
    obsmap=L.observed_mapping(rows,envs)
    obs,bm=stat(envs,labelsets,cmean,cvals,obsmap)
    rng=np.random.default_rng(SEED)
    null=[]
    for _ in range(NPERM):
        mp=L.perm_mapping(labelsets,rng)
        s,_=stat(envs,labelsets,cmean,cvals,mp)
        if s is not None:null.append(s)
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs))/(1+len(a)))
    pos=sum(v>0 for v in bm.values());frac=pos/len(bm)
    out={
      "parent_contract":"LATENT_POLICY_DIMENSIONALITY_CONTRACT_V1.md",
      "diagnostic":"D2_training_only_identity_subspace_d1",
      "implementation":"FAST_CLUSTER_EQUIVALENT",
      "K":float(obs),"bat_means":bm,"positive_bats":pos,
      "n_bats":len(bm),"positive_fraction":frac,
      "requested_permutations":NPERM,"valid_permutations":len(a),"seed":SEED,
      "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
      "null_q975":float(np.quantile(a,.975)),"p_one_sided":p,
      "sufficient":bool(len(a)>=9500 and obs>0 and p<=.05 and frac>=.70)
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
