#!/usr/bin/env python3
"""Decompose the transparent Rhino flight-intensity scalar into interpretable components."""
from __future__ import annotations
import collections, importlib.util, json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"rhino_configuration_identity_primary_v1.py")
P=importlib.util.module_from_spec(spec); spec.loader.exec_module(P)

NPERM=9999
SCALARS={
 "S1_speed":{"idx":[0,1],"weights":[0.5,0.5],"seed":202610042321},
 "S2_vertical_speed":{"idx":[2,3],"weights":[0.5,0.5],"seed":202610042322},
 "S4_verticality_contrast":{"seed":202610042324},
}

def load_rows():
    traj=P.load_rhino()
    ft=[r for r in traj if r["feature_valid"]]
    envs=sorted(set(r["env"] for r in ft))
    rows=[]
    for e in envs:
        rr=[r for r in ft if r["env"]==e]
        M=np.vstack([r["features"] for r in rr]).astype(float)
        mu=M.mean(axis=0); sd=M.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):
            raise RuntimeError(f"bad SD env={e}")
        for r in rr:
            z=(r["features"]-mu)/sd
            q=dict(r); q["z8"]=z
            q["speed"]=float(np.mean(z[[0,1]]))
            q["vertical_speed"]=float(np.mean(z[[2,3]]))
            q["verticality"]=q["vertical_speed"]-q["speed"]
            rows.append(q)
    return rows,envs

def labelsets(rows,envs):
    return {e:sorted(set(r["bat"] for r in rows if r["env"]==e)) for e in envs}

def mapping_identity(rows,envs):
    return {(e,b):b for e in envs for b in sorted(set(r["bat"] for r in rows if r["env"]==e))}

def perm_mapping(ls,rng):
    mp={}
    for e,labs in ls.items():
        perm=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,perm): mp[(e,old)]=str(new)
    return mp

def stat(rows,envs,mapping,key):
    perbat=collections.defaultdict(list)
    for target_e in envs:
        cent={}
        labels=sorted(set(mapping[(e,r["bat"])] for e in envs if e!=target_e for r in rows if r["env"]==e))
        for lab in labels:
            per_env=[]
            for e in envs:
                if e==target_e: continue
                vals=[r[key] for r in rows if r["env"]==e and mapping[(e,r["bat"])]==lab]
                if vals: per_env.append(float(np.mean(vals)))
            if len(per_env)>=2: cent[lab]=float(np.mean(per_env))
        if len(cent)<3: return None,{}
        for old in sorted(set(r["bat"] for r in rows if r["env"]==target_e)):
            lab=mapping[(target_e,old)]
            if lab not in cent: continue
            donors=[b for b in cent if b!=lab]
            if len(donors)<2: continue
            for r in [q for q in rows if q["env"]==target_e and q["bat"]==old]:
                x=r[key]; ds=abs(x-cent[lab]); do=float(np.mean([abs(x-cent[b]) for b in donors]))
                perbat[lab].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in perbat.items() if v}
    return (float(np.mean(list(bm.values()))),bm) if len(bm)>=3 else (None,bm)

def run(rows,envs,key,seed):
    obs,bm=stat(rows,envs,mapping_identity(rows,envs),key)
    if obs is None: return {"status":"STOP_OBSERVED_SUPPORT"}
    ls=labelsets(rows,envs); rng=np.random.default_rng(seed); null=np.empty(NPERM,float)
    for i in range(NPERM):
        q,_=stat(rows,envs,perm_mapping(ls,rng),key)
        if q is None: raise RuntimeError("invalid permutation")
        null[i]=q
    p=float((1+np.sum(null>=obs))/(NPERM+1))
    pos=sum(v>0 for v in bm.values()); frac=pos/len(bm)
    return {
      "status":"DONE","K":float(obs),"bat_means":bm,"positive_bats":pos,"n_bats":len(bm),
      "positive_fraction":frac,"p_one_sided":p,"null_mean":float(null.mean()),
      "null_q025":float(np.quantile(null,.025)),"null_q975":float(np.quantile(null,.975)),
      "seed":seed,"diagnostic_verdict":"SUPPORTED" if (obs>0 and p<=.05 and frac>=.70) else "UNSUPPORTED"
    }

def main():
    rows,envs=load_rows()
    out={"contract":"FLIGHT_INTENSITY_COMPONENT_CONTRACT_V1.md","species":"Rhinolophus nippon","components":{}}
    out["components"]["S1_speed"]=run(rows,envs,"speed",202610042321)
    out["components"]["S2_vertical_speed"]=run(rows,envs,"vertical_speed",202610042322)
    out["components"]["S4_verticality_contrast"]=run(rows,envs,"verticality",202610042324)
    out["reference_flight_intensity"]={"K":0.49655621310116754,"p":0.0003}
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
