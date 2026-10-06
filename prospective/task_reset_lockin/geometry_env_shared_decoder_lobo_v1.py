#!/usr/bin/env python3
"""LOBO environment-specific shared I/M -> geometry decoder diagnostic."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("X",HERE/"geometry_crossfit_im_expression_v1.py")
X=importlib.util.module_from_spec(spec);spec.loader.exec_module(X)

NPERM=9999
MIN_VALID=9500
SEED=202610061701
ELIGIBLE_ENVS=[1,2,3,4]
EVAL_BATS=["B","C","D","E"]

def build_lobo_residuals(rows):
    out=[]; sse=0.0; sse0=0.0; fits=[]
    for e in ELIGIBLE_ENVS:
        bats=sorted(set(r["bat"] for r in rows if r["env"]==e))
        if len(bats)<4:
            raise RuntimeError(f"env {e} has <4 bats: {bats}")
        for focal in bats:
            donors=[r for r in rows if r["env"]==e and r["bat"]!=focal]
            targets=[r for r in rows if r["env"]==e and r["bat"]==focal]
            donor_bats=sorted(set(r["bat"] for r in donors))
            if len(donor_bats)<3 or not targets:
                continue
            M=np.vstack([r["mfeat"] for r in donors])
            Gm=np.vstack([r["gfeat"] for r in donors])
            mm=M.mean(0); ms=M.std(0,ddof=1)
            gm=Gm.mean(0); gs=Gm.std(0,ddof=1)
            if np.any(~np.isfinite(ms)) or np.any(ms<=0) or np.any(~np.isfinite(gs)) or np.any(gs<=0):
                raise RuntimeError(f"bad donor scale env={e} focal={focal}")
            def trans(r):
                mz=(r["mfeat"]-mm)/ms
                gz=(r["gfeat"]-gm)/gs
                I=float(np.mean(mz[:4]))
                Man=float(np.mean(np.array([-mz[0],mz[4],mz[5],mz[6],mz[7]],float)))
                return I,Man,gz
            XX=[]; YY=[]
            for r in donors:
                I,Man,gz=trans(r)
                XX.append([1.0,I,Man]); YY.append(gz)
            XX=np.asarray(XX,float); YY=np.vstack(YY)
            B=np.linalg.lstsq(XX,YY,rcond=None)[0]
            for r in targets:
                I,Man,gz=trans(r)
                pred=np.array([1.0,I,Man])@B
                resid=gz-pred
                q=dict(r); q["resid"]=np.asarray(resid,float)
                out.append(q)
                sse += float(np.sum(resid*resid))
                sse0 += float(np.sum(gz*gz))
            fits.append({"env":e,"focal_bat":focal,"n_donor_bats":len(donor_bats),
                         "n_donor_trajectories":len(donors),"n_target_trajectories":len(targets)})
    return out,{"SSE_decoder":sse,"SSE_zero":sse0,
                "R2_heldout_bat":float(1-sse/sse0) if sse0>0 else None,
                "fits":fits}

def idmap(rows):
    return {(e,b):b for e,b in sorted(set((r["env"],r["bat"]) for r in rows))}

def permmap(rows,rng):
    mp={}
    for e in sorted(set(r["env"] for r in rows)):
        labs=sorted(set(r["bat"] for r in rows if r["env"]==e))
        p=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,p):
            mp[(e,old)]=str(new)
    return mp

def stat(rows,mapping):
    vals=collections.defaultdict(list)
    envs=sorted(set(r["env"] for r in rows))
    for e0 in envs:
        cent=collections.defaultdict(lambda:collections.defaultdict(list))
        for r in rows:
            if r["env"]==e0:continue
            lab=mapping[(r["env"],r["bat"])]
            cent[lab][r["env"]].append(r["resid"])
        train={}
        for b,d in cent.items():
            envc=[np.mean(np.vstack(v),0) for _,v in sorted(d.items()) if v]
            if len(envc)>=2:
                train[b]=np.mean(np.vstack(envc),0)
        if len(train)<3:continue
        for r in [x for x in rows if x["env"]==e0]:
            lab=mapping[(e0,r["bat"])]
            if lab not in train:continue
            donors=[b for b in train if b!=lab]
            if len(donors)<2:continue
            x=r["resid"]
            ds=float(np.linalg.norm(x-train[lab]))
            do=float(np.mean([np.linalg.norm(x-train[b]) for b in donors]))
            vals[lab].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in vals.items() if v}
    if len(bm)<3:return None,bm
    return float(np.mean(list(bm.values()))),bm

def main():
    rows,all_envs=X.rows_raw()
    if all_envs!=list(range(1,8)):
        raise RuntimeError(f"environment drift {all_envs}")
    rr,pred=build_lobo_residuals(rows)
    identity_rows=[r for r in rr if r["bat"] in EVAL_BATS]
    obs,bm=stat(identity_rows,idmap(identity_rows))
    if obs is None:raise RuntimeError("observed identity support failed")
    rng=np.random.default_rng(SEED);null=[]
    for _ in range(NPERM):
        s,_=stat(identity_rows,permmap(identity_rows,rng))
        if s is not None and math.isfinite(s):null.append(float(s))
    a=np.asarray(null,float)
    if len(a)<MIN_VALID:raise RuntimeError(f"randomization support {len(a)}")
    p=float((1+np.sum(a>=obs))/(1+len(a)))
    pos=sum(v>0 for v in bm.values())
    support=bool(obs>0 and p<=.05 and pos>=3)
    print(json.dumps({
      "contract":"GEOMETRY_ENV_SHARED_DECODER_LOBO_CONTRACT_V1.md",
      "status":"POST_PRIMARY_EXPLORATORY_FALSIFICATION_DIAGNOSTIC",
      "eligible_environments":ELIGIBLE_ENVS,
      "identity_population":EVAL_BATS,
      "n_residual_trajectories_all_focals":len(rr),
      "n_identity_trajectories":len(identity_rows),
      "decoder_prediction":pred,
      "residual_geometry_identity":{
        "K":float(obs),"bat_means":bm,
        "positive_bats":int(pos),"n_bats":len(bm),
        "positive_fraction":float(pos/len(bm)),
        "requested_permutations":NPERM,"valid_permutations":len(a),"seed":SEED,
        "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
        "null_q975":float(np.quantile(a,.975)),"p_one_sided":p,
        "verdict":"SUPPORTED_IDENTITY_BEYOND_SHARED_ENV_DECODER" if support
                  else "UNSUPPORTED_IDENTITY_BEYOND_SHARED_ENV_DECODER"
      }
    },indent=2))

if __name__=="__main__":main()
