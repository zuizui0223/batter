#!/usr/bin/env python3
"""Cross-environment rank stability of transparent FlightIntensity."""
from __future__ import annotations
import collections, importlib.util, json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("S",HERE/"flight_intensity_scalar_v1.py")
S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)

NPERM=9999
SEED=202610042302

def cluster_means(rows,envs,mapping):
    cm={}
    labels_by_env={}
    for e in envs:
        olds=sorted(set(r["bat"] for r in rows if r["env"]==e))
        labels_by_env[e]=[]
        tmp=collections.defaultdict(list)
        for old in olds:
            lab=mapping[(e,old)]
            vals=[r["flight_intensity"] for r in rows if r["env"]==e and r["bat"]==old]
            tmp[lab].extend(vals)
        for lab,vals in tmp.items():
            cm[(e,lab)]=float(np.mean(vals))
            labels_by_env[e].append(lab)
    return cm,labels_by_env

def stat(rows,envs,mapping):
    cm,leb=cluster_means(rows,envs,mapping)
    all_labels=sorted(set(l for labs in leb.values() for l in labs))
    pair_acc=collections.defaultdict(list)
    pair_counts=collections.Counter()
    for ii in range(len(all_labels)):
        for jj in range(ii+1,len(all_labels)):
            a,b=all_labels[ii],all_labels[jj]
            for e0 in envs:
                if (e0,a) not in cm or (e0,b) not in cm:
                    continue
                a_train=[cm[(e,a)] for e in envs if e!=e0 and (e,a) in cm]
                b_train=[cm[(e,b)] for e in envs if e!=e0 and (e,b) in cm]
                if len(a_train)<2 or len(b_train)<2:
                    continue
                pred=float(np.mean(a_train)-np.mean(b_train))
                targ=float(cm[(e0,a)]-cm[(e0,b)])
                if pred==0 or targ==0:
                    acc=0.5
                else:
                    acc=1.0 if np.sign(pred)==np.sign(targ) else 0.0
                pair_acc[(a,b)].append(acc)
                pair_counts[(a,b)]+=1
    pmeans={f"{a}-{b}":float(np.mean(v)) for (a,b),v in pair_acc.items() if v}
    counts={f"{a}-{b}":int(pair_counts[(a,b)]) for (a,b) in pair_acc if pair_acc[(a,b)]}
    if not pmeans:
        return None,{},{}
    R=float(np.mean(list(pmeans.values())))
    return R,pmeans,counts

def main():
    rows,envs=S.load_scalar_rows()
    obsmap=S.observed_mapping(rows,envs)
    obs,pmeans,counts=stat(rows,envs,obsmap)
    ls=S.labelsets(rows,envs)
    rng=np.random.default_rng(SEED)
    null=np.empty(NPERM,float)
    for i in range(NPERM):
        mp=S.perm_mapping(ls,rng)
        r,_,_=stat(rows,envs,mp)
        if r is None:
            raise RuntimeError("unexpected invalid permutation")
        null[i]=r
    p=float((1+np.sum(null>=obs))/(NPERM+1))
    above=sum(v>0.5 for v in pmeans.values())
    frac=above/len(pmeans)
    out={
      "contract":"FLIGHT_INTENSITY_RANK_STABILITY_CONTRACT_V1.md",
      "status":"POST_PRIMARY_INTERPRETABILITY_DIAGNOSTIC",
      "R_obs":obs,
      "pair_accuracy":pmeans,
      "target_environment_count_by_pair":counts,
      "pairs_above_chance":above,
      "n_pairs":len(pmeans),
      "fraction_pairs_above_chance":frac,
      "requested_permutations":NPERM,
      "valid_permutations":NPERM,
      "seed":SEED,
      "null_mean":float(null.mean()),
      "null_q025":float(np.quantile(null,.025)),
      "null_q975":float(np.quantile(null,.975)),
      "p_one_sided":p,
      "diagnostic_verdict":"SUPPORTED_STABLE_ORDERING" if (obs>0.5 and p<=.05 and frac>=.70) else "UNSUPPORTED_STABLE_ORDERING"
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
