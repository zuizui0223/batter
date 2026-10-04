#!/usr/bin/env python3
"""Post-primary pulse-component decomposition for Rhinolophus nippon."""
from __future__ import annotations
import collections, importlib.util, json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("Q",HERE/"rhino_pulse_identity_v1.py")
Q=importlib.util.module_from_spec(spec);spec.loader.exec_module(Q)
spec2=importlib.util.spec_from_file_location("P",HERE/"rhino_configuration_identity_primary_v1.py")
P=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(P)

NPERM=9999
MIN_VALID=9500
SETS={
 "D1_rate_only":{"idx":[0],"seed":202610042261},
 "D2_ipi_structure_no_rate":{"idx":[1,2,3,4,5],"seed":202610042262},
 "D3_ipi_variability_only":{"idx":[4,5],"seed":202610042263},
 "D4_ipi_central_quantile":{"idx":[1,2,3],"seed":202610042264},
}

def build_selected(raw,idx):
    valid=[r for r in raw if r["valid"]]
    envs=sorted(set(r["env"] for r in valid))
    usable=[];stats={}
    for e in envs:
        rr=[r for r in valid if r["env"]==e]
        if len(rr)<2 or len(set(r["bat"] for r in rr))<2:continue
        M=np.vstack([r["features"][idx] for r in rr])
        mu=M.mean(axis=0);sd=M.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):
            continue
        usable.append(e);stats[e]=(mu,sd)
    rows=[]
    for r in valid:
        if r["env"] not in usable:continue
        mu,sd=stats[r["env"]]
        q=dict(r);q["z"]=(r["features"][idx]-mu)/sd;rows.append(q)
    bats=sorted(set(r["bat"] for r in rows))
    presence={b:sorted(set(r["env"] for r in rows if r["bat"]==b)) for b in bats}
    candidates=sorted([b for b,es in presence.items() if len(es)>=3])
    targets=[];support=collections.Counter()
    for i,r in enumerate(rows):
        b,e=r["bat"],r["env"]
        if b not in candidates:continue
        own=[ee for ee in presence[b] if ee!=e]
        donors=[]
        for j in bats:
            if j==b:continue
            jes=[ee for ee in presence[j] if ee!=e]
            if len(jes)>=2:donors.append(j)
        if len(own)>=2 and len(donors)>=2:
            targets.append(i);support[b]+=1
    if len(candidates)<3 or not targets:
        return None,{"status":"STOP_SUPPORT","usable_envs":usable,"candidate_bats":candidates}
    return (rows,bats,targets,usable,candidates),{
        "status":"PASS_SUPPORT","usable_envs":usable,
        "candidate_bats":candidates,"support_by_bat":dict(support),"n_targets":len(targets)
    }

def run_one(raw,idx,seed):
    obj,sup=build_selected(raw,idx)
    if obj is None:return sup
    rows,bats,targets,usable,candidates=obj
    obs=P.b_stat(rows,bats,targets,None)
    if obs is None:return {**sup,"status":"STOP_OBSERVED"}
    Pobs,bm,_=obs
    envclusters={e:sorted(set(r["bat"] for r in rows if r["env"]==e)) for e in usable}
    rng=np.random.default_rng(seed);null=[]
    for _ in range(NPERM):
        mp={}
        for e,labs in envclusters.items():
            perm=list(rng.permutation(np.asarray(labs,dtype=object)))
            for old,new in zip(labs,perm):mp[(e,old)]=str(new)
        s=P.b_stat(rows,bats,targets,mp)
        if s is not None:null.append(float(s[0]))
    if len(null)<MIN_VALID:
        return {**sup,"status":"STOP_RANDOMIZATION","P_obs":float(Pobs),"valid_permutations":len(null)}
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=Pobs))/(1+len(a)))
    pos=sum(v>0 for v in bm.values());frac=pos/len(bm)
    return {
      **sup,"status":"DONE","P_obs":float(Pobs),
      "bat_means":{k:float(v) for k,v in bm.items()},
      "positive_bats":pos,"n_bats":len(bm),"positive_fraction":frac,
      "requested_permutations":NPERM,"valid_permutations":len(a),"seed":seed,
      "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
      "null_q975":float(np.quantile(a,.975)),"p_one_sided":p,
      "diagnostic_verdict":"SUPPORTED" if (Pobs>0 and p<=.05 and frac>=.70) else "UNSUPPORTED"
    }

def main():
    raw=Q.load_rows()
    out={"contract":"PULSE_COMPONENT_DECOMPOSITION_CONTRACT_V1.md",
         "status":"POST_PRIMARY_MECHANISM_DIAGNOSTIC","components":{}}
    for name,spec in SETS.items():
        out["components"][name]=run_one(raw,spec["idx"],spec["seed"])
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
