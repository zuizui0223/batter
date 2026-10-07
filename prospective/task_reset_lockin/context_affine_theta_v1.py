#!/usr/bin/env python3
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("F",HERE/"flight_intensity_scalar_v1.py")
F=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(F)

B=9999
SEED=20261007961

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

def theta_excluding(cm,b,exclude,envs):
    vals=[cm[(b,e)] for e in envs if e!=exclude and (b,e) in cm]
    if len(vals)<2:return None
    return float(np.mean(vals)),len(vals)

def targets(cm,bats,envs):
    out=[]
    for (b,e),y in sorted(cm.items(),key=lambda x:(x[0][1],x[0][0])):
        ne=sum((bb,e) in cm for bb in bats)
        nb=sum((b,ee) in cm for ee in envs)
        if ne>=4 and nb>=4:
            out.append((b,e,y))
    return out

def predict_one(cm,bats,envs,t):
    tb,te,ty=t
    th=theta_excluding(cm,tb,te,envs)
    if th is None:return None
    theta_t,ntrain=th
    peers=[]
    for b in bats:
        if b==tb or (b,te) not in cm:continue
        q=theta_excluding(cm,b,te,envs)
        if q is None:continue
        peers.append((b,float(q[0]),float(cm[(b,te)])))
    if len(peers)<3:return None

    x=np.asarray([p[1] for p in peers],float)
    y=np.asarray([p[2] for p in peers],float)

    pred_env=float(np.mean(y))
    pred_theta=theta_t

    X=np.column_stack([np.ones(len(x)),x])
    beta=np.linalg.lstsq(X,y,rcond=None)[0]
    gamma=float(beta[0]); alpha=float(beta[1])
    pred_affine=gamma+alpha*theta_t

    return {
        "bat":tb,"env":te,"target":ty,
        "theta_hat":theta_t,"theta_training_envs":ntrain,
        "peer_count":len(peers),
        "gamma_hat":gamma,"alpha_hat":alpha,
        "pred_env":pred_env,"pred_theta":pred_theta,"pred_affine":pred_affine,
        "se_env":(ty-pred_env)**2,
        "se_theta":(ty-pred_theta)**2,
        "se_affine":(ty-pred_affine)**2,
    }

def aggregate(rows,sample=None):
    bats=sorted(set(r["bat"] for r in rows))
    if sample is None: sample=bats
    per_inst=[]
    for b in sample:
        rr=[r for r in rows if r["bat"]==b]
        if not rr:continue
        q={
            "mse_env":float(np.mean([r["se_env"] for r in rr])),
            "mse_theta":float(np.mean([r["se_theta"] for r in rr])),
            "mse_affine":float(np.mean([r["se_affine"] for r in rr])),
        }
        q["gain_vs_env"]=q["mse_env"]-q["mse_affine"]
        q["gain_vs_theta"]=q["mse_theta"]-q["mse_affine"]
        per_inst.append(q)
    keys=per_inst[0].keys()
    return {k:float(np.mean([q[k] for q in per_inst])) for k in keys}

def per_bat(rows):
    return {b:aggregate(rows,[b]) for b in sorted(set(r["bat"] for r in rows))}

def bootstrap(rows,bats):
    obs=aggregate(rows,bats)
    rng=np.random.default_rng(SEED)
    vals={k:[] for k in ("gain_vs_env","gain_vs_theta")}
    for _ in range(B):
        s=list(rng.choice(np.asarray(bats,dtype=object),size=len(bats),replace=True))
        q=aggregate(rows,s)
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
    tt=targets(cm,bats,envs)
    if len(tt)!=17:
        raise RuntimeError(f"target universe drift {len(tt)}")
    rows=[]
    for t in tt:
        q=predict_one(cm,bats,envs,t)
        if q is None:raise RuntimeError(f"target support {t}")
        rows.append(q)

    pb=per_bat(rows)
    obs,cis=bootstrap(rows,bats)
    pos_env=sum(pb[b]["gain_vs_env"]>0 for b in bats)
    pos_theta=sum(pb[b]["gain_vs_theta"]>0 for b in bats)
    supported=bool(
        obs["gain_vs_env"]>0 and cis["gain_vs_env"]["ci95_low"]>0 and pos_env>=3
        and obs["gain_vs_theta"]>0 and cis["gain_vs_theta"]["ci95_low"]>0 and pos_theta>=3
    )
    out={
        "status":"POST_PRIMARY_MATHEMATICAL_STRUCTURE_DIAGNOSTIC",
        "contract":"CONTEXT_AFFINE_THETA_CONTRACT_V1.md",
        "species":"Rhinolophus nippon",
        "n_targets":len(rows),
        "n_bats":len(bats),
        "observed":obs,
        "bootstrap":cis,
        "per_bat":pb,
        "positive_bats":{"vs_env":pos_env,"vs_theta":pos_theta},
        "supported":supported,
        "target_rows":rows,
        "interpretation":"SUPPORTED_CONTEXT_AFFINE_THETA" if supported else "UNSUPPORTED_CONTEXT_AFFINE_THETA"
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
