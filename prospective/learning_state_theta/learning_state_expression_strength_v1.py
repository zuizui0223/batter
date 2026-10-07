#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, itertools, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("S",HERE/"personal_speed_state_v1.py")
S=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(S)

B=9999
SEEDS={"1":20261007701,"2":20261007702}
DELTA_B=99999
DELTA_SEED=20261007703

def condition_arrays(rows,cond):
    rr=[r for r in rows if r["condition"]==cond]
    bats=sorted(set(r["bat"] for r in rr),key=int)
    x=np.asarray([next(r["speed"] for r in rr if r["bat"]==b and r["trial"]=="1") for b in bats],float)
    y=np.asarray([next(r["speed"] for r in rr if r["bat"]==b and r["trial"]=="12") for b in bats],float)
    return bats,x,y

def alpha_stat(x,y):
    xc=x-x.mean(); yc=y-y.mean()
    den=float(np.sum(xc*xc))
    if den<=0: return math.nan
    alpha=float(np.sum(xc*yc)/den)
    r=float(np.corrcoef(xc,yc)[0,1])
    sd_ratio=float(np.std(yc,ddof=1)/np.std(xc,ddof=1))
    rmse=float(np.sqrt(np.mean((yc-alpha*xc)**2)))
    return alpha,r,sd_ratio,rmse,xc,yc

def exact_null(x,y):
    _,_,_,_,xc,yc=alpha_stat(x,y)
    vals=[]
    for perm in itertools.permutations(range(len(xc))):
        xp=xc[list(perm)]
        vals.append(float(np.sum(xp*yc)/np.sum(xp*xp)))
    return np.asarray(vals,float)

def boot_alpha(x,y,seed):
    rng=np.random.default_rng(seed); n=len(x); vals=[]
    for _ in range(B):
        idx=rng.integers(0,n,n)
        xb=x[idx]; yb=y[idx]
        den=float(np.sum((xb-xb.mean())**2))
        if den<=0: continue
        vals.append(float(np.sum((xb-xb.mean())*(yb-yb.mean()))/den))
    a=np.asarray(vals,float)
    return {"valid":len(a),"ci95_low":float(np.quantile(a,.025)),"ci95_high":float(np.quantile(a,.975))}

def main():
    rows=S.read_rows()
    if len(rows)!=28: raise RuntimeError(f"row drift {len(rows)}")
    out={"contract":"LEARNING_STATE_EXPRESSION_STRENGTH_CONTRACT_V1.md","conditions":{}}
    nulls={}
    alphas={}
    for cond in ["1","2"]:
        bats,x,y=condition_arrays(rows,cond)
        if len(bats)!=7: raise RuntimeError(f"{cond}: bat count")
        alpha,r,q,rmse,xc,yc=alpha_stat(x,y)
        null=exact_null(x,y); nulls[cond]=null; alphas[cond]=alpha
        p=float(np.mean(null>=alpha-1e-15))
        boot=boot_alpha(x,y,SEEDS[cond])
        out["conditions"][cond]={
            "bats":bats,
            "trial1_mean":float(x.mean()),"trial12_mean":float(y.mean()),
            "mean_shift":float(y.mean()-x.mean()),
            "trial1_sd":float(np.std(x,ddof=1)),"trial12_sd":float(np.std(y,ddof=1)),
            "alpha":alpha,"pearson_r":r,"sd_ratio":q,"residual_rmse":rmse,
            "exact_permutations":len(null),
            "null_mean":float(null.mean()),"null_q025":float(np.quantile(null,.025)),
            "null_q975":float(np.quantile(null,.975)),"p_alpha_one_sided":p,
            "bootstrap":boot,
            "individual_pairs":[{"bat":b,"trial1":float(a),"trial12":float(z),"x_centered":float(xx),"y_centered":float(yy)}
                                for b,a,z,xx,yy in zip(bats,x,y,xc,yc)]
        }
    delta=float(alphas["2"]-alphas["1"])
    rng=np.random.default_rng(DELTA_SEED)
    i1=rng.integers(0,len(nulls["1"]),DELTA_B)
    i2=rng.integers(0,len(nulls["2"]),DELTA_B)
    dn=nulls["2"][i2]-nulls["1"][i1]
    pdelta=float((1+np.sum(np.abs(dn)>=abs(delta)-1e-15))/(DELTA_B+1))
    out["between_condition"]={
        "delta_alpha_reflective_minus_permeable":delta,
        "null_mean":float(dn.mean()),"null_q025":float(np.quantile(dn,.025)),
        "null_q975":float(np.quantile(dn,.975)),"draws":DELTA_B,
        "seed":DELTA_SEED,"p_two_sided":pdelta
    }
    c1=out["conditions"]["1"]; c2=out["conditions"]["2"]
    out["interpretation_category"]=(
        "CONTEXT_DEPENDENT_EXPRESSION_SUPPORTED"
        if c2["p_alpha_one_sided"]<=.05 and c1["p_alpha_one_sided"]>.05 and pdelta<=.05
        else "CONTEXT_DEPENDENT_EXPRESSION_SUGGESTIVE"
        if c2["p_alpha_one_sided"]<=.05 and c1["p_alpha_one_sided"]>.05
        else "PERSONAL_EXPRESSION_PERSISTS_BOTH"
        if c1["p_alpha_one_sided"]<=.05 and c2["p_alpha_one_sided"]<=.05
        else "NO_CLEAR_ALPHA_ARCHITECTURE"
    )
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
