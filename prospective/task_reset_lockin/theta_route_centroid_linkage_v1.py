#!/usr/bin/env python3
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent

spec=importlib.util.spec_from_file_location("P",HERE/"rhino_configuration_identity_primary_v1.py")
P=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(P)

spec=importlib.util.spec_from_file_location("F",HERE/"flight_intensity_scalar_v1.py")
F=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(F)

ROUTE_ENVS=[1,2,3]
NPERM=9999
SEED=20261007901
MIN_VALID=9500

def route_centroids():
    traj=P.load_rhino()
    vals=collections.defaultdict(list)
    for r in traj:
        if not r["route_valid"] or r["env"] not in ROUTE_ENVS:
            continue
        c=np.mean(np.asarray(r["route101"],float),axis=0)
        vals[(int(r["env"]),str(r["bat"]))].append(c)
    out={k:np.mean(np.vstack(v),axis=0) for k,v in vals.items()}
    return out

def scalar_cluster_means():
    rows,envs=F.load_scalar_rows()
    cm={}
    ls={}
    for e in envs:
        labs=sorted(set(r["bat"] for r in rows if r["env"]==e))
        ls[e]=labs
        for b in labs:
            vv=[r["flight_intensity"] for r in rows if r["env"]==e and r["bat"]==b]
            cm[(e,b)]=float(np.mean(vv))
    return cm,envs,ls

def identity_mapping(ls):
    return {(e,b):b for e,labs in ls.items() for b in labs}

def perm_mapping(ls,rng):
    mp={}
    for e,labs in ls.items():
        q=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,q):
            mp[(e,old)]=str(new)
    return mp

def assigned_scalar(cm,envs,ls,mapping):
    out={}
    for e in envs:
        for old in ls[e]:
            new=mapping[(e,old)]
            out[(e,new)]=cm[(e,old)]
    return out

def theta_for(route_env,bat,scalars,envs):
    vv=[scalars[(e,bat)] for e in envs if e!=route_env and (e,bat) in scalars]
    if len(vv)<2:
        return None
    return float(np.mean(vv))

def build_env_tables(routes,scalars,envs):
    tables={}
    for e in ROUTE_ENVS:
        bats=sorted(b for (ee,b) in routes if ee==e)
        rows=[]
        for b in bats:
            th=theta_for(e,b,scalars,envs)
            if th is None:
                continue
            rows.append((b,th,np.asarray(routes[(e,b)],float)))
        if len(rows)<3:
            return None
        thmean=float(np.mean([x[1] for x in rows]))
        cmean=np.mean(np.vstack([x[2] for x in rows]),axis=0)
        tables[e]=[
            {
                "bat":b,
                "x":float(th-thmean),
                "y":c-cmean,
                "theta":float(th),
                "centroid":c,
            }
            for b,th,c in rows
        ]
    return tables

def fit_beta(tables,target):
    xs=[]; ys=[]
    for e in ROUTE_ENVS:
        if e==target: continue
        for r in tables[e]:
            xs.append(r["x"]); ys.append(r["y"])
    x=np.asarray(xs,float); Y=np.vstack(ys)
    den=float(np.sum(x*x))
    if den<=0:
        return None
    return np.sum(x[:,None]*Y,axis=0)/den

def stat(routes,cm,envs,ls,mapping,details=False):
    scalars=assigned_scalar(cm,envs,ls,mapping)
    tables=build_env_tables(routes,scalars,envs)
    if tables is None:
        return None,None
    envout={}
    for e0 in ROUTE_ENVS:
        beta=fit_beta(tables,e0)
        if beta is None:
            return None,None
        gains=[]; zero=[]; pred=[]; targets=[]
        for r in tables[e0]:
            y=r["y"]; yh=r["x"]*beta
            z=float(np.sum(y*y))
            p=float(np.sum((y-yh)**2))
            g=z-p
            gains.append(g);zero.append(z);pred.append(p)
            if details:
                targets.append({
                    "bat":r["bat"],
                    "theta_non_target":r["theta"],
                    "theta_centered":r["x"],
                    "route_centroid":r["centroid"].tolist(),
                    "route_centroid_centered":y.tolist(),
                    "predicted_centered":yh.tolist(),
                    "gain_sq_m":g
                })
        mg=float(np.mean(gains))
        mz=float(np.mean(zero)); mp=float(np.mean(pred))
        envout[e0]={
            "mean_gain":mg,
            "R2":float(1-mp/mz) if mz>0 else None,
            "beta":beta.tolist(),
            "n_bats":len(gains),
        }
        if details:
            envout[e0]["targets"]=targets
    G=float(np.mean([envout[e]["mean_gain"] for e in ROUTE_ENVS]))
    R2=float(np.mean([envout[e]["R2"] for e in ROUTE_ENVS]))
    return G,{"G":G,"R2_equal_environment":R2,"environments":envout}

def cosine(a,b):
    a=np.asarray(a,float);b=np.asarray(b,float)
    d=float(np.linalg.norm(a)*np.linalg.norm(b))
    return float(np.dot(a,b)/d) if d>0 else None

def main():
    routes=route_centroids()
    cm,envs,ls=scalar_cluster_means()
    obs,detail=stat(routes,cm,envs,ls,identity_mapping(ls),details=True)
    if obs is None:
        raise RuntimeError("observed structural support failed")
    betas={e:detail["environments"][e]["beta"] for e in ROUTE_ENVS}
    detail["beta_cosines"]={
        "1_2":cosine(betas[1],betas[2]),
        "1_3":cosine(betas[1],betas[3]),
        "2_3":cosine(betas[2],betas[3])
    }
    rng=np.random.default_rng(SEED)
    null=[]
    for _ in range(NPERM):
        q,_=stat(routes,cm,envs,ls,perm_mapping(ls,rng),details=False)
        if q is not None and math.isfinite(q):
            null.append(q)
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs))/(1+len(a)))
    positive_envs=sum(detail["environments"][e]["mean_gain"]>0 for e in ROUTE_ENVS)
    supported=bool(len(a)>=MIN_VALID and obs>0 and p<=.05 and positive_envs>=2)
    out={
        "contract":"THETA_ROUTE_CENTROID_LINKAGE_CONTRACT_V1.md",
        "status":"POST_PRIMARY_MECHANISM_LINKAGE_DIAGNOSTIC",
        "species":"Rhinolophus nippon",
        "route_environments":ROUTE_ENVS,
        "observed":detail,
        "positive_target_environments":positive_envs,
        "null":{
            "requested":NPERM,
            "valid":int(len(a)),
            "seed":SEED,
            "mean":float(a.mean()),
            "q025":float(np.quantile(a,.025)),
            "q975":float(np.quantile(a,.975)),
            "p_one_sided":p
        },
        "supported":supported,
        "verdict":"SUPPORTED_THETA_TO_ROUTE_CENTROID_LINKAGE" if supported else "UNSUPPORTED_THETA_TO_ROUTE_CENTROID_LINKAGE"
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
