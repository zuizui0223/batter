#!/usr/bin/env python3
"""Peer-defined environment-specific I/M -> geometry expression map."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("C",HERE/"geometry_crossfit_im_expression_v1.py")
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)

NPERM=9999
MIN_VALID=9500
SEED=202610061701
MIN_PEER_BATS=3

def build_peer_residuals(rows):
    out=[]
    support={}
    sse=0.0
    sst=0.0
    n_pred=0
    for e in sorted(set(r["env"] for r in rows)):
        rr=[r for r in rows if r["env"]==e]
        M=np.vstack([r["mfeat"] for r in rr])
        Gm=np.vstack([r["gfeat"] for r in rr])
        mm=M.mean(0);ms=M.std(0,ddof=1)
        gm=Gm.mean(0);gs=Gm.std(0,ddof=1)
        if np.any(~np.isfinite(ms)) or np.any(ms<=0) or np.any(~np.isfinite(gs)) or np.any(gs<=0):
            support[str(e)]={"status":"STOP_SCALING"}
            continue

        def trans(r):
            mz=(r["mfeat"]-mm)/ms
            gz=(r["gfeat"]-gm)/gs
            I=float(np.mean(mz[:4]))
            Man=float(np.mean(np.array([-mz[0],mz[4],mz[5],mz[6],mz[7]],float)))
            return I,Man,gz

        bats=sorted(set(r["bat"] for r in rr))
        es={"status":"DONE","bats":bats,"focal":{}}
        for focal in bats:
            peers=[r for r in rr if r["bat"]!=focal]
            peer_bats=sorted(set(r["bat"] for r in peers))
            rec={"n_peer_bats":len(peer_bats),"peer_bats":peer_bats,"n_peer_trajectories":len(peers)}
            if len(peer_bats)<MIN_PEER_BATS:
                rec["status"]="STOP_PEER_BATS";es["focal"][focal]=rec;continue
            X=[];Y=[]
            for r in peers:
                I,Man,gz=trans(r);X.append([1.0,I,Man]);Y.append(gz)
            X=np.asarray(X,float);Y=np.vstack(Y)
            rank=int(np.linalg.matrix_rank(X))
            rec["design_rank"]=rank
            if rank<3:
                rec["status"]="STOP_DESIGN_RANK";es["focal"][focal]=rec;continue
            B=np.linalg.lstsq(X,Y,rcond=None)[0]
            targets=[r for r in rr if r["bat"]==focal]
            for r in targets:
                I,Man,gz=trans(r)
                pred=np.array([1.0,I,Man])@B
                resid=gz-pred
                q=dict(r);q["resid"]=np.asarray(resid,float)
                out.append(q)
                sse += float(np.sum(resid*resid))
                sst += float(np.sum(gz*gz))
                n_pred += 1
            rec["status"]="PASS"
            rec["n_target_trajectories"]=len(targets)
            es["focal"][focal]=rec
        support[str(e)]=es
    r2=float(1-sse/sst) if sst>0 else None
    return out,support,{"n_predicted_trajectories":n_pred,"multivariate_R2_vs_env_zero":r2}

def mapping_identity(rows):
    return {(e,b):b for e,b in sorted(set((r["env"],r["bat"]) for r in rows))}

def mapping_perm(rows,rng):
    mp={}
    for e in sorted(set(r["env"] for r in rows)):
        labs=sorted(set(r["bat"] for r in rows if r["env"]==e))
        p=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,p):mp[(e,old)]=str(new)
    return mp

def stat(rows,mapping):
    cent=collections.defaultdict(list)
    for r in rows:
        lab=mapping[(r["env"],r["bat"])]
        cent[(r["env"],lab)].append(r["resid"])
    cent={k:np.mean(np.vstack(v),axis=0) for k,v in cent.items()}
    presence=collections.defaultdict(set)
    for e,b in cent:presence[b].add(e)
    candidate=sorted([b for b,es in presence.items() if len(es)>=3])
    vals=collections.defaultdict(list)
    for r in rows:
        e=r["env"];lab=mapping[(e,r["bat"])]
        if lab not in candidate:continue
        own_envs=[ee for ee in sorted(presence[lab]) if ee!=e and (ee,lab) in cent]
        if len(own_envs)<2:continue
        own=np.mean(np.vstack([cent[(ee,lab)] for ee in own_envs]),axis=0)
        donors=[]
        for b in candidate:
            if b==lab:continue
            ees=[ee for ee in sorted(presence[b]) if ee!=e and (ee,b) in cent]
            if len(ees)>=2:
                donors.append(np.mean(np.vstack([cent[(ee,b)] for ee in ees]),axis=0))
        if len(donors)<2:continue
        ds=float(np.linalg.norm(r["resid"]-own))
        do=float(np.mean([np.linalg.norm(r["resid"]-d) for d in donors]))
        vals[lab].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in vals.items() if v}
    if len(bm)<3:return None,bm,candidate
    return float(np.mean(list(bm.values()))),bm,candidate

def main():
    rows,envs=C.rows_raw()
    resid,support,pred=build_peer_residuals(rows)
    if not resid:
        raise RuntimeError("no peer-defined residuals")
    obs,bm,candidate=stat(resid,mapping_identity(resid))
    if obs is None:raise RuntimeError("observed residual identity support failed")

    rng=np.random.default_rng(SEED);null=[]
    for _ in range(NPERM):
        s,_,_=stat(resid,mapping_perm(resid,rng))
        if s is not None and math.isfinite(s):null.append(float(s))
    a=np.asarray(null,float)
    if len(a)<MIN_VALID:raise RuntimeError(f"randomization support {len(a)}")
    p=float((1+np.sum(a>=obs))/(1+len(a)))
    pos=sum(v>0 for v in bm.values())
    need=int(math.ceil(.75*len(bm)))
    supported=bool(obs>0 and p<=.05 and pos>=need)

    print(json.dumps({
      "contract":"PEER_DEFINED_ENVIRONMENT_EXPRESSION_MAP_CONTRACT_V1.md",
      "status":"POST_PRIMARY_FALSIFICATION_DIAGNOSTIC",
      "n_input_trajectories":len(rows),
      "n_residual_trajectories":len(resid),
      "environment_support":support,
      "peer_map_prediction":pred,
      "residual_identity":{
        "K":float(obs),"bat_means":bm,
        "candidate_bats":candidate,
        "positive_bats":int(pos),"required_positive":need,
        "positive_fraction":float(pos/len(bm)),
        "requested_permutations":NPERM,"valid_permutations":int(len(a)),
        "seed":SEED,
        "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
        "null_q975":float(np.quantile(a,.975)),
        "p_one_sided":p,
        "verdict":"SUPPORTED_IDENTITY_BEYOND_PEER_ENV_MAP" if supported else "UNSUPPORTED_IDENTITY_BEYOND_PEER_ENV_MAP"
      }
    },indent=2))

if __name__=="__main__":main()
