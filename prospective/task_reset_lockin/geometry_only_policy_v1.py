#!/usr/bin/env python3
"""Post-primary geometry-only cross-configuration identity diagnostic."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"rhino_configuration_identity_primary_v1.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)

NPERM=9999
SEED=202610042215
FEATURES=[
 "path_efficiency_3d","horizontal_displacement_ratio","abs_vertical_displacement_ratio",
 "vertical_range_ratio","median_abs_horizontal_turn_angle","p90_abs_horizontal_turn_angle",
 "median_abs_vertical_slope","p90_abs_vertical_slope"
]

def geometry_features(r):
    if not r["route_valid"]:
        return None
    x=np.asarray(r["route101"],dtype=float)
    L=float(r["path_length"])
    if not (np.isfinite(L) and L>0 and x.shape==(101,3)):
        return None
    q=(x-x[0])/L
    d=np.diff(q,axis=0)
    seg=np.linalg.norm(d,axis=1)
    good=seg>0
    if int(np.sum(good))<20:
        return None
    net=q[-1]-q[0]
    eff=float(np.linalg.norm(net))
    horiz_disp=float(np.hypot(net[0],net[1]))
    vert_disp=float(abs(net[2]))
    vert_range=float(np.max(q[:,2])-np.min(q[:,2]))

    h=np.hypot(d[:,0],d[:,1])
    head=np.full(len(d),np.nan)
    hg=h>0
    head[hg]=np.arctan2(d[hg,1],d[hg,0])
    turns=[]
    for k in range(len(head)-1):
        if not (np.isfinite(head[k]) and np.isfinite(head[k+1])):
            continue
        dd=math.atan2(math.sin(head[k+1]-head[k]),math.cos(head[k+1]-head[k]))
        turns.append(abs(dd))
    turns=np.asarray(turns,dtype=float)
    if len(turns)<20:
        return None
    slopes=np.abs(d[good,2])/seg[good]
    if len(slopes)<20:
        return None
    feat=np.array([
      eff,horiz_disp,vert_disp,vert_range,
      np.median(turns),np.percentile(turns,90),
      np.median(slopes),np.percentile(slopes,90)
    ],dtype=float)
    return feat if np.all(np.isfinite(feat)) else None

def build_rows(traj):
    raw=[]
    for r in traj:
        f=geometry_features(r)
        if f is not None:
            raw.append({**r,"gfeat":f})
    envs=sorted(set(r["env"] for r in raw))
    usable=[]
    stats={}
    for e in envs:
        rr=[r for r in raw if r["env"]==e]
        if len(rr)<2 or len(set(r["bat"] for r in rr))<2:
            continue
        M=np.vstack([r["gfeat"] for r in rr])
        mu=np.mean(M,axis=0); sd=np.std(M,axis=0,ddof=1)
        stats[e]=(mu,sd)
        usable.append(e)
    retained=[]
    dropped=[]
    for k,name in enumerate(FEATURES):
        bad=[e for e in usable if not (np.isfinite(stats[e][1][k]) and stats[e][1][k]>0)]
        if bad:dropped.append({"feature":name,"bad_envs":bad})
        else:retained.append(k)
    if len(retained)<6:
        return None,{"status":"STOP_FEATURE_SUPPORT","usable_envs":usable,
                     "retained_features":[FEATURES[k] for k in retained],"dropped_features":dropped}
    rows=[]
    for r in raw:
        e=r["env"]
        if e not in usable:continue
        mu,sd=stats[e]
        z=(r["gfeat"][retained]-mu[retained])/sd[retained]
        rows.append({**r,"z":z})
    return rows,{"status":"PASS_FEATURE_SUPPORT","usable_envs":usable,
                 "retained_features":[FEATURES[k] for k in retained],"dropped_features":dropped}

def cluster_centroids(rows,mapping=None):
    tmp=collections.defaultdict(list)
    for r in rows:
        e,old=r["env"],r["bat"]
        lab=mapping[(e,old)] if mapping is not None else old
        tmp[(e,lab)].append(r["z"])
    return {k:np.mean(np.vstack(v),axis=0) for k,v in tmp.items()}

def stat(rows,mapping=None):
    cent=cluster_centroids(rows,mapping)
    bats=sorted(set(lab for _,lab in cent))
    presence=collections.defaultdict(set)
    for e,b in cent:presence[b].add(e)
    candidate=[b for b in bats if len(presence[b])>=3]
    vals=collections.defaultdict(list)
    for r in rows:
        e,old=r["env"],r["bat"]
        lab=mapping[(e,old)] if mapping is not None else old
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
        ds=float(np.linalg.norm(r["z"]-own))
        do=float(np.mean([np.linalg.norm(r["z"]-d) for d in donors]))
        vals[lab].append(do-ds)
    indiv={b:float(np.mean(v)) for b,v in vals.items() if v}
    if len(indiv)<3:return None,indiv
    return float(np.mean(list(indiv.values()))),indiv

def main():
    traj=P.load_rhino()
    rows,support=build_rows(traj)
    if rows is None:
        print(json.dumps({"contract":"GEOMETRY_ONLY_POLICY_DIAGNOSTIC_CONTRACT_V1.md",**support},indent=2));return
    obs,indiv=stat(rows)
    if obs is None:
        print(json.dumps({"contract":"GEOMETRY_ONLY_POLICY_DIAGNOSTIC_CONTRACT_V1.md",
                          "status":"STOP_OBSERVED_SUPPORT",**support},indent=2));return
    env_labels={}
    for e in support["usable_envs"]:
        env_labels[e]=sorted(set(r["bat"] for r in rows if r["env"]==e))
    rng=np.random.default_rng(SEED)
    null=[]
    for _ in range(NPERM):
        mp={}
        for e,labs in env_labels.items():
            perm=list(rng.permutation(np.array(labs,dtype=object)))
            for old,new in zip(labs,perm):mp[(e,old)]=str(new)
        s,_=stat(rows,mp)
        if s is not None:null.append(s)
    null=np.asarray(null,float)
    p=float((1+np.sum(null>=obs))/(1+len(null)))
    npos=sum(v>0 for v in indiv.values())
    out={
      "contract":"GEOMETRY_ONLY_POLICY_DIAGNOSTIC_CONTRACT_V1.md",
      "status":"POST_PRIMARY_EXPLORATORY_ROBUSTNESS",
      **support,
      "n_trajectories":len(rows),
      "K_geometry":obs,
      "bat_means":indiv,
      "positive_bats":npos,
      "n_evaluable_bats":len(indiv),
      "positive_fraction":npos/len(indiv) if indiv else None,
      "requested_permutations":NPERM,
      "valid_permutations":int(len(null)),
      "seed":SEED,
      "null_mean":float(np.mean(null)),
      "null_q025":float(np.quantile(null,.025)),
      "null_q975":float(np.quantile(null,.975)),
      "p_one_sided":p,
      "diagnostic_verdict":"SUPPORTED_GEOMETRY_IDENTITY" if (obs>0 and p<=.05 and npos/len(indiv)>=.70) else "UNSUPPORTED_GEOMETRY_IDENTITY"
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
