#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, itertools, json, math
from collections import defaultdict
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,HERE/path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

P=loadmod("P","rhino_configuration_identity_primary_v1.py")
F=loadmod("F","flight_intensity_scalar_v1.py")

ENVS=(1,2,3)
MIN_ROUTES=2
MIN_THETA_ENVS=2
SEED=20261007901

def route_centroids():
    traj=P.load_rhino()
    cells=defaultdict(list)
    for r in traj:
        if not r["route_valid"] or r["env"] not in ENVS:
            continue
        c=np.mean(np.asarray(r["route101"],float),axis=0)
        cells[(int(r["env"]),str(r["bat"]))].append(c)
    out={}
    counts={}
    for key,vals in cells.items():
        counts[key]=len(vals)
        if len(vals)>=MIN_ROUTES:
            out[key]=np.mean(np.vstack(vals),axis=0)
    return out,counts

def theta_by_target_env():
    rows,envs=F.load_scalar_rows()
    cell=defaultdict(list)
    for r in rows:
        cell[(int(r["env"]),str(r["bat"]))].append(float(r["flight_intensity"]))
    means={k:float(np.mean(v)) for k,v in cell.items()}
    bats=sorted(set(b for _,b in means))
    out={}
    support={}
    for e0 in ENVS:
        for b in bats:
            vals=[means[(e,b)] for e in envs if e!=e0 and (e,b) in means]
            support[(e0,b)]=len(vals)
            if len(vals)>=MIN_THETA_ENVS:
                out[(e0,b)]=float(np.mean(vals))
    return out,support

def eligible():
    cent,route_counts=route_centroids()
    theta,theta_support=theta_by_target_env()
    by_env={}
    for e in ENVS:
        bats=sorted(b for (ee,b) in cent if ee==e and (e,b) in theta)
        if len(bats)>=3:
            by_env[e]=bats
    if len(by_env)!=3:
        raise RuntimeError(f"expected all Env1-3 evaluable, got {by_env}")
    return cent,theta,by_env,route_counts,theta_support

def affine_predict(train_theta,train_C,target_theta):
    x=np.asarray(train_theta,float)
    C=np.vstack(train_C).astype(float)
    X=np.column_stack([np.ones(len(x)),x])
    coef=np.linalg.pinv(X)@C
    return np.asarray([1.0,target_theta])@coef

def l1(cent,theta,by_env,mapping=None):
    rows=[]
    env_stats={}
    for e,bats in by_env.items():
        gs=[]
        for target in bats:
            train=[b for b in bats if b!=target]
            def th(b):
                lab=mapping[e][b] if mapping is not None else b
                return theta[(e,lab)]
            pred=affine_predict([th(b) for b in train],[cent[(e,b)] for b in train],th(target))
            base=np.mean(np.vstack([cent[(e,b)] for b in train]),axis=0)
            truth=cent[(e,target)]
            et=float(np.sum((truth-pred)**2))
            eb=float(np.sum((truth-base)**2))
            g=eb-et
            rows.append({"env":e,"bat":target,"gain":g,"theta_error":et,"baseline_error":eb})
            gs.append(g)
        env_stats[str(e)]=float(np.mean(gs))
    return float(np.mean(list(env_stats.values()))),rows,env_stats

def rankdata(a):
    a=np.asarray(a,float)
    order=np.argsort(a,kind="mergesort")
    ranks=np.empty(len(a),float)
    i=0
    while i<len(a):
        j=i+1
        while j<len(a) and a[order[j]]==a[order[i]]:
            j+=1
        ranks[order[i:j]]=(i+j-1)/2+1
        i=j
    return ranks

def spearman(x,y):
    if len(x)<3:return math.nan
    rx=rankdata(x); ry=rankdata(y)
    if np.std(rx)<=0 or np.std(ry)<=0:return math.nan
    return float(np.corrcoef(rx,ry)[0,1])

def l2(cent,theta,by_env,mapping=None):
    out={}
    vals=[]
    for e,bats in by_env.items():
        dx=[];dc=[]
        for a,b in itertools.combinations(bats,2):
            la=mapping[e][a] if mapping is not None else a
            lb=mapping[e][b] if mapping is not None else b
            dx.append(abs(theta[(e,la)]-theta[(e,lb)]))
            dc.append(float(np.linalg.norm(cent[(e,a)]-cent[(e,b)])))
        rho=spearman(dx,dc)
        out[str(e)]={"rho":rho,"n_pairs":len(dx)}
        if math.isfinite(rho):vals.append(rho)
    return float(np.mean(vals)),out

def all_mappings(by_env):
    envs=sorted(by_env)
    per=[list(itertools.permutations(by_env[e])) for e in envs]
    total=math.prod(len(x) for x in per)
    if total<=100000:
        for combo in itertools.product(*per):
            yield {e:{b:new for b,new in zip(by_env[e],perm)} for e,perm in zip(envs,combo)}
    else:
        rng=np.random.default_rng(SEED)
        for _ in range(99999):
            yield {e:{b:new for b,new in zip(by_env[e],rng.permutation(by_env[e]))} for e in envs}

def main():
    cent,theta,by_env,route_counts,theta_support=eligible()
    G,rows,envstats=l1(cent,theta,by_env)
    rho,rhos=l2(cent,theta,by_env)
    nullG=[];nullR=[]
    for mp in all_mappings(by_env):
        g,_,_=l1(cent,theta,by_env,mp)
        r,_=l2(cent,theta,by_env,mp)
        nullG.append(g);nullR.append(r)
    a=np.asarray(nullG,float); b=np.asarray(nullR,float)
    p=float((1+np.sum(a>=G-1e-15))/(1+len(a)))
    pos=sum(r["gain"]>0 for r in rows)
    support=bool(G>0 and p<=.05 and pos/len(rows)>=.70)
    payload={
      "contract":"THETA_TO_LANE_LINKAGE_CONTRACT_V1.md",
      "status":"POST_PRIMARY_MECHANISM_DIAGNOSTIC",
      "eligible_bats_by_environment":{str(e):bs for e,bs in by_env.items()},
      "route_counts":{f"{e}:{b}":n for (e,b),n in sorted(route_counts.items()) if e in ENVS},
      "theta_training_environment_counts":{f"{e}:{b}":n for (e,b),n in sorted(theta_support.items()) if e in ENVS and b in by_env.get(e,[])},
      "L1":{
        "G":G,"environment_G":envstats,"target_rows":rows,
        "positive_targets":pos,"n_targets":len(rows),"positive_fraction":pos/len(rows),
        "null_n":len(a),"null_mean":float(a.mean()),
        "null_q025":float(np.quantile(a,.025)),"null_q975":float(np.quantile(a,.975)),
        "p_one_sided":p,"supported":support
      },
      "L2":{
        "mean_environment_spearman":rho,"environment_results":rhos,
        "null_mean":float(np.nanmean(b)),"null_q025":float(np.nanquantile(b,.025)),
        "null_q975":float(np.nanquantile(b,.975)),
        "p_one_sided":float((1+np.sum(b>=rho-1e-15))/(1+len(b)))
      },
      "interpretation":"THETA_PREDICTS_LANE" if support else "SEPARATE_TASK_SPECIFIC_LANE_STATE_REQUIRED"
    }
    print(json.dumps(payload,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
