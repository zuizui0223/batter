#!/usr/bin/env python3
"""Sparse-support stress test: downsample Rhino to four bats / 19 trajectories."""
from __future__ import annotations
import collections, importlib.util, json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"rhino_configuration_identity_primary_v1.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)

N=9999
MAX_ATTEMPTS=1_000_000
SEED=202610051401
MINI_K=-0.013597525318187484
RHINO_K=0.9435600964999665

def standardized_rows():
    t=[r for r in P.load_rhino() if r["feature_valid"]]
    rows=[]
    for e in sorted(set(r["env"] for r in t)):
        rr=[r for r in t if r["env"]==e]
        M=np.vstack([r["features"] for r in rr]).astype(float)
        mu=M.mean(axis=0);sd=M.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):raise RuntimeError(f"bad sd env {e}")
        for r in rr:
            q=dict(r);q["zfeat"]=(r["features"]-mu)/sd;rows.append(q)
    if len(rows)!=45:raise RuntimeError(len(rows))
    return rows

def K_stat(rows):
    labels=[r["bat"] for r in rows]
    env_idx=collections.defaultdict(list)
    for i,r in enumerate(rows):env_idx[r["env"]].append(i)
    presence=collections.defaultdict(set)
    for i,r in enumerate(rows):presence[labels[i]].add(r["env"])
    cand=sorted([b for b,es in presence.items() if len(es)>=3])
    if len(cand)<3:return None
    # environment × bat centroids
    cm={}
    for e,idxs in env_idx.items():
        for b in cand:
            ii=[i for i in idxs if labels[i]==b]
            if ii:cm[(e,b)]=np.mean(np.vstack([rows[i]["zfeat"] for i in ii]),axis=0)
    vals=collections.defaultdict(list)
    for i,r in enumerate(rows):
        b=labels[i];e=r["env"]
        if b not in cand:continue
        own=[cm[(ee,b)] for ee in sorted(presence[b]) if ee!=e and (ee,b) in cm]
        if len(own)<2:continue
        ownc=np.mean(np.vstack(own),axis=0)
        donors=[]
        for d in cand:
            if d==b:continue
            z=[cm[(ee,d)] for ee in sorted(presence[d]) if ee!=e and (ee,d) in cm]
            if len(z)>=2:donors.append(np.mean(np.vstack(z),axis=0))
        if len(donors)<2:continue
        ds=float(np.linalg.norm(r["zfeat"]-ownc))
        do=float(np.mean([np.linalg.norm(r["zfeat"]-x) for x in donors]))
        vals[b].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in vals.items() if v}
    return float(np.mean(list(bm.values()))) if len(bm)>=3 else None

def main():
    rows=standardized_rows()
    bats=sorted(set(r["bat"] for r in rows))
    bybat={b:[i for i,r in enumerate(rows) if r["bat"]==b] for b in bats}
    rng=np.random.default_rng(SEED)
    outK=[];sets=collections.Counter();attempts=0
    while len(outK)<N and attempts<MAX_ATTEMPTS:
        attempts+=1
        chosen=tuple(sorted(rng.choice(np.asarray(bats,dtype=object),size=4,replace=False).tolist()))
        pool=np.asarray([i for b in chosen for i in bybat[b]],dtype=int)
        if len(pool)<19:continue
        ix=rng.choice(pool,size=19,replace=False)
        sub=[rows[int(i)] for i in ix]
        ok=True
        for b in chosen:
            rr=[r for r in sub if r["bat"]==b]
            if len(rr)<3 or len(set(r["env"] for r in rr))<3:
                ok=False;break
        if not ok:continue
        k=K_stat(sub)
        if k is None or not np.isfinite(k):continue
        outK.append(float(k));sets["".join(chosen)]+=1
    a=np.asarray(outK,float)
    status="DONE" if len(a)>=9500 else "STOP_ACCEPTED_SUPPORT"
    out={
      "contract":"SPARSE_SUPPORT_SPECIES_BOUNDARY_CONTRACT_V1.md",
      "status":status,
      "accepted":int(len(a)),"attempts":attempts,
      "seed":SEED,
      "K_median":float(np.median(a)) if len(a) else None,
      "K_q025":float(np.quantile(a,.025)) if len(a) else None,
      "K_q975":float(np.quantile(a,.975)) if len(a) else None,
      "fraction_K_positive":float(np.mean(a>0)) if len(a) else None,
      "fraction_K_le_Mini_observed":float(np.mean(a<=MINI_K)) if len(a) else None,
      "fraction_K_ge_full_Rhino":float(np.mean(a>=RHINO_K)) if len(a) else None,
      "selected_bat_sets":dict(sorted(sets.items())),
      "reference":{"Miniopterus_K":MINI_K,"full_Rhinolophus_K":RHINO_K},
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
