#!/usr/bin/env python3
from __future__ import annotations
import collections
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
SEED=20261007921

def log_t_pdf(x,mu,scale,df):
    if not (math.isfinite(scale) and scale>0 and df>0):
        return math.nan
    z=(x-mu)/scale
    return (
        math.lgamma((df+1)/2)-math.lgamma(df/2)
        -0.5*math.log(df*math.pi)-math.log(scale)
        -0.5*(df+1)*math.log1p((z*z)/df)
    )

def rankdata(x):
    a=np.asarray(x,float)
    order=np.argsort(a,kind="mergesort")
    r=np.empty(len(a),float)
    i=0
    while i<len(a):
        j=i+1
        while j<len(a) and a[order[j]]==a[order[i]]:
            j+=1
        rr=0.5*((i+1)+j)
        r[order[i:j]]=rr
        i=j
    return r

def spearman(x,y):
    if len(x)<3:return math.nan
    rx=rankdata(x); ry=rankdata(y)
    if np.std(rx,ddof=1)<=0 or np.std(ry,ddof=1)<=0:return math.nan
    return float(np.corrcoef(rx,ry)[0,1])

def centroids():
    rows,envs=F.load_scalar_rows()
    cm={}
    for e in envs:
        for b in sorted(set(r["bat"] for r in rows if r["env"]==e)):
            vals=[r["flight_intensity"] for r in rows if r["env"]==e and r["bat"]==b]
            cm[(e,b)]=float(np.mean(vals))
    bats=sorted(set(b for _,b in cm))
    return cm,envs,bats

def folds(cm,envs,bats):
    rows=[]
    for e0 in envs:
        train_envs=[e for e in envs if e!=e0]

        # training bat means and pooled residual variance
        train_by_bat={}
        residual_ss=0.0
        residual_df=0
        for b in bats:
            vals=[cm[(e,b)] for e in train_envs if (e,b) in cm]
            if len(vals)>=2:
                a=np.asarray(vals,float)
                mu=float(a.mean())
                train_by_bat[b]=(a,mu)
                residual_ss+=float(np.sum((a-mu)**2))
                residual_df+=len(a)-1
        if residual_df<=0:
            raise RuntimeError(f"no pooled variance target env {e0}")
        spool=math.sqrt(residual_ss/residual_df)

        for b in bats:
            if (e0,b) not in cm or b not in train_by_bat:
                continue
            a,mu=train_by_bat[b]
            n=len(a)
            if n<3:
                continue
            si=float(np.std(a,ddof=1))
            if not (math.isfinite(si) and si>0):
                continue
            y=float(cm[(e0,b)])
            scale_common=spool*math.sqrt(1+1/n)
            scale_personal=si*math.sqrt(1+1/n)
            l1=log_t_pdf(y,mu,scale_common,residual_df)
            l2=log_t_pdf(y,mu,scale_personal,n-1)
            if not (math.isfinite(l1) and math.isfinite(l2)):
                continue
            rows.append({
                "target_env":e0,
                "bat":b,
                "n_training_envs":n,
                "target":y,
                "theta_hat":mu,
                "personal_sd":si,
                "pooled_sd":spool,
                "abs_deviation":abs(y-mu),
                "log_M1":l1,
                "log_M2":l2,
                "gain_M2_minus_M1":l2-l1,
            })
    return rows

def aggregate(rows,bats_sample=None):
    bats=sorted(set(r["bat"] for r in rows))
    if bats_sample is None:bats_sample=bats
    vals=[]
    per={}
    for b in bats_sample:
        rr=[r for r in rows if r["bat"]==b]
        if not rr:continue
        g=float(np.mean([r["gain_M2_minus_M1"] for r in rr]))
        vals.append(g)
        per.setdefault(b,g)
    if not vals:raise RuntimeError("no aggregate")
    return float(np.mean(vals)),per

def bootstrap(rows,bats):
    rng=np.random.default_rng(SEED)
    obs,per=aggregate(rows,bats)
    vals=[]
    for _ in range(B):
        samp=list(rng.choice(np.asarray(bats,dtype=object),size=len(bats),replace=True))
        q,_=aggregate(rows,samp)
        vals.append(q)
    a=np.asarray(vals,float)
    return obs,per,{
        "B":B,"seed":SEED,
        "ci95_low":float(np.quantile(a,.025)),
        "ci95_high":float(np.quantile(a,.975))
    }

def main():
    cm,envs,bats=centroids()
    rows=folds(cm,envs,bats)
    ebats=sorted(set(r["bat"] for r in rows))
    obs,per,boot=bootstrap(rows,ebats)
    rho=spearman(
        [r["personal_sd"] for r in rows],
        [r["abs_deviation"] for r in rows]
    )
    pos=sum(v>0 for v in per.values())
    supported=bool(obs>0 and boot["ci95_low"]>0 and pos>=3)
    out={
        "status":"POST_PRIMARY_MATHEMATICAL_STRUCTURE_DIAGNOSTIC",
        "contract":"THETA_SIGMA_PREDICTIVE_MODEL_CONTRACT_V1.md",
        "species":"Rhinolophus nippon",
        "n_targets":len(rows),
        "n_bats":len(ebats),
        "primary":{
            "mean_log_score_gain_M2_minus_M1":obs,
            "bat_means":per,
            "positive_bats":pos,
            "bootstrap":boot,
            "supported":supported
        },
        "secondary":{
            "spearman_training_sigma_vs_heldout_abs_deviation":rho
        },
        "target_rows":rows,
        "interpretation":"SUPPORTED_PERSONAL_THETA_SIGMA" if supported else "THETA_ONLY_NO_PERSONAL_SIGMA_GAIN"
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
