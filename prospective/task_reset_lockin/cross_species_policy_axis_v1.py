#!/usr/bin/env python3
"""Post-primary cross-species transfer of the Rhino policy axis to Miniopterus."""
from __future__ import annotations
import collections, hashlib, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"rhino_configuration_identity_primary_v1.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)

MINI_MIN=55033796
MINI_MAX=55033850
NPERM=9999
MIN_VALID=9500

def load_mini():
    article=P.get_article()
    out=[]
    for f in article.get("files") or []:
        fid=int(f["id"]); name=f.get("name") or ""; m=P.PAT.match(name)
        if not m or not (MINI_MIN<=fid<=MINI_MAX):
            continue
        size=int(f["size"]); b=P.get_bytes(f["download_url"],size+4096)
        if len(b)!=size: raise RuntimeError(f"size mismatch {name}")
        exp=f.get("computed_md5") or f.get("supplied_md5")
        if exp and hashlib.md5(b).hexdigest()!=exp: raise RuntimeError(f"md5 mismatch {name}")
        arr=P.parse_xyz(b)
        rf=P.route_and_features(arr)
        out.append({
          "id":fid,"name":name,"env":int(m.group("env")),
          "bat":m.group("bat"),"trial":m.group("trial"),**rf
        })
    if len(out)!=19: raise RuntimeError(f"expected 19 Mini trajectories, got {len(out)}")
    return out

def mini_standardized():
    t=[r for r in load_mini() if r["feature_valid"]]
    if len(t)!=19: raise RuntimeError(f"expected all 19 feature-valid, got {len(t)}")
    X=np.vstack([r["features"] for r in t]).astype(float)
    env=np.asarray([r["env"] for r in t])
    resid=np.empty_like(X)
    for e in sorted(set(env.tolist())):
        ix=np.where(env==e)[0]
        resid[ix]=X[ix]-X[ix].mean(axis=0,keepdims=True)
    sd=resid.std(axis=0,ddof=1)
    if np.any(~np.isfinite(sd)) or np.any(sd<=0):
        raise RuntimeError(f"bad pooled residual SD {sd}")
    Z=resid/sd
    rows=[]
    for i,r in enumerate(t):
        q=dict(r);q["z8"]=Z[i];rows.append(q)
    return rows

def rhino_pc1():
    t=[r for r in P.load_rhino() if r["feature_valid"]]
    rows=[]
    for e in sorted(set(r["env"] for r in t)):
        rr=[r for r in t if r["env"]==e]
        M=np.vstack([r["features"] for r in rr]).astype(float)
        mu=M.mean(axis=0);sd=M.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0): raise RuntimeError(f"bad Rhino sd env {e}")
        rows.append((M-mu)/sd)
    X=np.vstack(rows)
    X=X-X.mean(axis=0,keepdims=True)
    _,_,Vt=np.linalg.svd(X,full_matrices=False)
    v=Vt[0].copy()
    if np.sum(v[:4])<0:v=-v
    return v

def labelsets(rows):
    envs=sorted(set(r["env"] for r in rows))
    return envs,{e:sorted(set(r["bat"] for r in rows if r["env"]==e)) for e in envs}

def observed_mapping(ls):
    return {(e,b):b for e,labs in ls.items() for b in labs}

def perm_mapping(ls,rng):
    mp={}
    for e,labs in ls.items():
        perm=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,perm):mp[(e,old)]=str(new)
    return mp

def scalar_stat(rows,scalar_key,mapping):
    envs,ls=labelsets(rows)
    # Centroid for every currently assigned bat×environment cluster.
    cm={}
    presence=collections.defaultdict(set)
    for e,labs in ls.items():
        for old in labs:
            new=mapping[(e,old)]
            vals=[r[scalar_key] for r in rows if r["env"]==e and r["bat"]==old]
            cm[(e,new)]=float(np.mean(vals))
            presence[new].add(e)
    candidate=sorted([b for b,es in presence.items() if len(es)>=3])
    perbat=collections.defaultdict(list)
    for r in rows:
        e=r["env"]; new=mapping[(e,r["bat"])]
        if new not in candidate:continue
        own_envs=[ee for ee in sorted(presence[new]) if ee!=e and (ee,new) in cm]
        if len(own_envs)<2:continue
        own=float(np.mean([cm[(ee,new)] for ee in own_envs]))
        donors=[]
        for b in candidate:
            if b==new:continue
            bes=[ee for ee in sorted(presence[b]) if ee!=e and (ee,b) in cm]
            if len(bes)>=2:
                donors.append(float(np.mean([cm[(ee,b)] for ee in bes])))
        if len(donors)<2:continue
        z=float(r[scalar_key])
        ds=abs(z-own); do=float(np.mean([abs(z-d) for d in donors]))
        perbat[new].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in perbat.items() if v}
    if len(bm)<3:return None,bm
    return float(np.mean(list(bm.values()))),bm

def run(rows,key,seed):
    envs,ls=labelsets(rows)
    obsmap=observed_mapping(ls)
    obs,bm=scalar_stat(rows,key,obsmap)
    if obs is None:return {"status":"STOP_OBSERVED_SUPPORT"}
    rng=np.random.default_rng(seed);null=[]
    for _ in range(NPERM):
        mp=perm_mapping(ls,rng)
        s,_=scalar_stat(rows,key,mp)
        if s is not None:null.append(s)
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs))/(1+len(a))) if len(a) else math.nan
    pos=sum(v>0 for v in bm.values());frac=pos/len(bm)
    support=bool(len(a)>=MIN_VALID and obs>0 and p<=.05 and pos>=3)
    return {
      "status":"DONE","K":float(obs),"bat_means":bm,
      "positive_bats":pos,"n_bats":len(bm),"positive_fraction":frac,
      "requested_permutations":NPERM,"valid_permutations":int(len(a)),"seed":seed,
      "null_mean":float(a.mean()) if len(a) else None,
      "null_q025":float(np.quantile(a,.025)) if len(a) else None,
      "null_q975":float(np.quantile(a,.975)) if len(a) else None,
      "p_one_sided":p,
      "diagnostic_verdict":"SUPPORTED_CROSS_SPECIES_AXIS" if support else "UNSUPPORTED_CROSS_SPECIES_AXIS"
    }

def main():
    rows=mini_standardized()
    v=rhino_pc1()
    for r in rows:
        r["flight_intensity"]=float(np.mean(r["z8"][:4]))
        r["rhino_pc1_score"]=float(r["z8"]@v)
    out={
      "contract":"CROSS_SPECIES_POLICY_AXIS_CONTRACT_V1.md",
      "standardization":"CROSS_SPECIES_STANDARDIZATION_AMENDMENT_V1.md",
      "status":"POST_PRIMARY_CROSS_SPECIES_GENERALITY_DIAGNOSTIC",
      "target_species":"Miniopterus fuliginosus",
      "n_trajectories":len(rows),
      "rhino_pc1_oriented_loadings":v.tolist(),
      "G1_transparent_flight_intensity":run(rows,"flight_intensity",202610042311),
      "G2_fixed_rhino_PC1":run(rows,"rhino_pc1_score",202610042312),
      "reference_failed_full8_primary":{
        "K":-0.013597525318187484,
        "p_one_sided":0.1687,
        "positive_bats":2,
        "n_bats":4
      }
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
