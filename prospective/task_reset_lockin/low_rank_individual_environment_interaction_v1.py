#!/usr/bin/env python3
from __future__ import annotations
import importlib.util
import json
import math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("F",HERE/"flight_intensity_scalar_v1.py")
F=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(F)

B=9999
SEED=20261007941
MAXITER=1000
TOL=1e-12

def centroids():
    rows,envs=F.load_scalar_rows()
    cm={}
    for e in envs:
        for b in sorted(set(r["bat"] for r in rows if r["env"]==e)):
            vals=[r["flight_intensity"] for r in rows if r["env"]==e and r["bat"]==b]
            cm[(str(b),int(e))]=float(np.mean(vals))
    bats=sorted(set(b for b,e in cm))
    envs=sorted(set(e for b,e in cm))
    return cm,bats,envs

def design_fit(train,bats,envs):
    b0=bats[0]; e0=envs[0]
    p=1+(len(bats)-1)+(len(envs)-1)
    X=[]; y=[]
    for b,e,v in train:
        row=[1.0]
        row += [1.0 if b==bb else 0.0 for bb in bats[1:]]
        row += [1.0 if e==ee else 0.0 for ee in envs[1:]]
        X.append(row); y.append(v)
    X=np.asarray(X,float); y=np.asarray(y,float)
    beta=np.linalg.lstsq(X,y,rcond=None)[0]

    def pred(b,e):
        row=[1.0]
        row += [1.0 if b==bb else 0.0 for bb in bats[1:]]
        row += [1.0 if e==ee else 0.0 for ee in envs[1:]]
        return float(np.dot(np.asarray(row,float),beta))
    return pred

def interaction_fit(residuals,bats,envs,rank):
    bi={b:i for i,b in enumerate(bats)}
    ei={e:j for j,e in enumerate(envs)}
    R=np.zeros((len(bats),len(envs)),float)
    mask=np.zeros_like(R,dtype=bool)
    for b,e,r in residuals:
        R[bi[b],ei[e]]=r
        mask[bi[b],ei[e]]=True

    # Deterministic SVD initialization; missing cells are zero only for initialization.
    U,S,Vt=np.linalg.svd(R,full_matrices=False)
    rr=min(rank,len(S))
    L=U[:,:rr]*np.sqrt(S[:rr])[None,:]
    G=Vt[:rr,:].T*np.sqrt(S[:rr])[None,:]
    if rr<rank:
        L=np.pad(L,((0,0),(0,rank-rr)))
        G=np.pad(G,((0,0),(0,rank-rr)))

    prev=math.inf
    for _ in range(MAXITER):
        # bat factors
        for i in range(len(bats)):
            js=np.where(mask[i])[0]
            if len(js)==0: continue
            A=G[js,:]
            y=R[i,js]
            L[i,:]=np.linalg.lstsq(A,y,rcond=None)[0]
        # environment factors
        for j in range(len(envs)):
            ii=np.where(mask[:,j])[0]
            if len(ii)==0: continue
            A=L[ii,:]
            y=R[ii,j]
            G[j,:]=np.linalg.lstsq(A,y,rcond=None)[0]

        # Normalize for numerical stability; predictions are unchanged.
        for k in range(rank):
            norm=float(np.sqrt(np.mean(G[:,k]**2)))
            if math.isfinite(norm) and norm>0:
                G[:,k]/=norm
                L[:,k]*=norm

        err=0.0
        for i,j in zip(*np.where(mask)):
            d=R[i,j]-float(np.dot(L[i],G[j]))
            err+=d*d
        if math.isfinite(prev) and abs(prev-err)<=TOL*max(1.0,prev):
            break
        prev=err

    return L,G,bi,ei,float(prev)

def target_universe(cm,bats,envs):
    out=[]
    for (b,e),y in sorted(cm.items(),key=lambda x:(x[0][1],x[0][0])):
        nb=sum((b,ee) in cm for ee in envs)
        ne=sum((bb,e) in cm for bb in bats)
        if nb>=4 and ne>=3:
            out.append((b,e,y))
    return out

def fit_predict_target(cm,bats,envs,target):
    tb,te,ty=target
    train=[(b,e,y) for (b,e),y in cm.items() if not (b==tb and e==te)]

    # all target categories must remain observed
    if not any(b==tb for b,e,y in train): return None
    if not any(e==te for b,e,y in train): return None

    pred0=design_fit(train,bats,envs)
    p0=pred0(tb,te)
    residuals=[(b,e,y-pred0(b,e)) for b,e,y in train]

    out={"bat":tb,"env":te,"target":ty,"pred0":p0,"se0":(ty-p0)**2}
    for r in (1,2):
        L,G,bi,ei,sse=interaction_fit(residuals,bats,envs,r)
        pr=p0+float(np.dot(L[bi[tb]],G[ei[te]]))
        out[f"pred{r}"]=pr
        out[f"se{r}"]=(ty-pr)**2
        out[f"training_interaction_sse_r{r}"]=sse
    return out

def aggregate(rows,sampled_bats=None):
    bats=sorted(set(r["bat"] for r in rows))
    if sampled_bats is None: sampled_bats=bats
    inst=[]
    for b in sampled_bats:
        rr=[r for r in rows if r["bat"]==b]
        if not rr: continue
        q={
            "mse0":float(np.mean([r["se0"] for r in rr])),
            "mse1":float(np.mean([r["se1"] for r in rr])),
            "mse2":float(np.mean([r["se2"] for r in rr])),
        }
        q["delta1"]=q["mse0"]-q["mse1"]
        q["delta2"]=q["mse0"]-q["mse2"]
        q["delta21"]=q["mse1"]-q["mse2"]
        inst.append(q)
    keys=inst[0].keys()
    return {k:float(np.mean([q[k] for q in inst])) for k in keys}

def per_bat(rows):
    out={}
    for b in sorted(set(r["bat"] for r in rows)):
        out[b]=aggregate(rows,[b])
    return out

def bootstrap(rows,bats):
    obs=aggregate(rows,bats)
    rng=np.random.default_rng(SEED)
    vals={k:[] for k in ("delta1","delta2","delta21")}
    for _ in range(B):
        samp=list(rng.choice(np.asarray(bats,dtype=object),size=len(bats),replace=True))
        q=aggregate(rows,samp)
        for k in vals: vals[k].append(q[k])
    cis={}
    for k,a0 in vals.items():
        a=np.asarray(a0,float)
        cis[k]={
            "observed":obs[k],
            "ci95_low":float(np.quantile(a,.025)),
            "ci95_high":float(np.quantile(a,.975))
        }
    return obs,cis

def main():
    cm,bats,envs=centroids()
    targets=target_universe(cm,bats,envs)
    if len(targets)!=23:
        raise RuntimeError(f"target universe drift: {len(targets)}")
    rows=[]
    for t in targets:
        q=fit_predict_target(cm,bats,envs,t)
        if q is None: raise RuntimeError(f"target support failed {t}")
        rows.append(q)

    pb=per_bat(rows)
    obs,cis=bootstrap(rows,bats)
    pos1=sum(pb[b]["delta1"]>0 for b in bats)
    pos2=sum(pb[b]["delta2"]>0 for b in bats)
    s1=bool(obs["delta1"]>0 and cis["delta1"]["ci95_low"]>0 and pos1>=3)
    s2=bool(obs["delta2"]>0 and cis["delta2"]["ci95_low"]>0 and pos2>=3)
    mind=1 if s1 else (2 if s2 else None)

    out={
        "status":"POST_PRIMARY_MATHEMATICAL_STRUCTURE_DIAGNOSTIC",
        "contract":"LOW_RANK_INDIVIDUAL_ENVIRONMENT_INTERACTION_CONTRACT_V1.md",
        "species":"Rhinolophus nippon",
        "n_targets":len(rows),
        "n_bats":len(bats),
        "observed":obs,
        "bootstrap":cis,
        "per_bat":pb,
        "positive_bats":{"rank1":pos1,"rank2":pos2},
        "supported":{"rank1":s1,"rank2_vs_additive":s2},
        "minimal_sufficient_interaction_rank":mind,
        "target_rows":rows,
        "interpretation":(
            "RANK1_INTERACTION_SUFFICIENT" if mind==1
            else "RANK2_INTERACTION_SUFFICIENT" if mind==2
            else "NO_LOW_RANK_INTERACTION_GAIN"
        )
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
