#!/usr/bin/env python3
"""Rhinolophus-only coordinate support gate for configuration-conditioned identity tests.

Reads Time/X/Y/Z but computes no individual-identity outcome.
"""
from __future__ import annotations
import collections, csv, hashlib, io, json, math, re, urllib.request
import numpy as np

API="https://api.figshare.com/v2/articles/29209493"
UA="batter-rhino-coordinate-support/1.0"
PAT=re.compile(r"^Env(?P<env>\d+)_Bat(?P<bat>[A-Za-z]+)_no(?P<trial>.+)\.csv$")
RHINO_MIN=55033853
RHINO_MAX=55033985
FEATURES=[
    "median_speed",
    "p90_speed",
    "median_abs_vertical_speed",
    "p90_abs_vertical_speed",
    "median_abs_horizontal_turn_rate",
    "p90_abs_horizontal_turn_rate",
    "path_efficiency",
    "vertical_range",
]

def get_article():
    req=urllib.request.Request(API,headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:return json.load(r)

def get_bytes(url,maxn):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"text/csv,*/*"})
    with urllib.request.urlopen(req,timeout=90) as r:
        b=r.read(maxn+1)
    if len(b)>maxn:
        raise RuntimeError("download budget exceeded")
    return b

def parse_xyz(b):
    txt=io.StringIO(b.decode("utf-8-sig",errors="strict"))
    reader=csv.DictReader(txt)
    expect=["Time (Seconds)","X","Y","Z","pulse"]
    if reader.fieldnames!=expect:
        raise RuntimeError(f"header drift: {reader.fieldnames}")
    vals=[]
    for row in reader:
        try:
            t=float(row["Time (Seconds)"])
            x=float(row["X"]); y=float(row["Y"]); z=float(row["Z"])
        except Exception:
            vals.append((math.nan,math.nan,math.nan,math.nan))
            continue
        vals.append((t,x,y,z))
    if not vals:
        return np.empty((0,4),dtype=float)
    arr=np.asarray(vals,dtype=float)
    arr=arr[np.all(np.isfinite(arr),axis=1)]
    if len(arr)==0:
        return arr
    order=np.argsort(arr[:,0],kind="mergesort")
    arr=arr[order]
    # retain first row per timestamp after stable time sort
    _, first_idx=np.unique(arr[:,0],return_index=True)
    arr=arr[np.sort(first_idx)]
    return arr

def trajectory_summary(arr):
    out={
        "n_finite_dedup_rows":int(len(arr)),
        "duration":None,
        "path_length":None,
        "positive_dt_intervals":0,
        "route_valid":False,
        "feature_valid":False,
        "features":None,
    }
    if len(arr)<2:
        return out
    t=arr[:,0]; xyz=arr[:,1:4]
    duration=float(t[-1]-t[0])
    dxyz=np.diff(xyz,axis=0)
    seglen=np.linalg.norm(dxyz,axis=1)
    path=float(np.sum(seglen[np.isfinite(seglen)]))
    dt=np.diff(t)
    pos=dt>0
    npos=int(np.sum(pos))
    out["duration"]=duration
    out["path_length"]=path
    out["positive_dt_intervals"]=npos
    route_valid=(len(arr)>=100 and duration>0 and path>0 and np.isfinite(path))
    out["route_valid"]=bool(route_valid)
    if not route_valid or npos<50:
        return out

    dxyzp=dxyz[pos]
    dtp=dt[pos]
    speed=np.linalg.norm(dxyzp,axis=1)/dtp
    vz=np.abs(dxyzp[:,2]/dtp)

    dx=dxyz[:,0]; dy=dxyz[:,1]
    hmag=np.hypot(dx,dy)
    heading=np.full(len(dt),np.nan,dtype=float)
    good_head=(dt>0)&(hmag>0)&np.isfinite(hmag)
    heading[good_head]=np.arctan2(dy[good_head],dx[good_head])
    turns=[]
    for k in range(len(heading)-1):
        if not (np.isfinite(heading[k]) and np.isfinite(heading[k+1])):
            continue
        dt_turn=0.5*(dt[k]+dt[k+1])
        if not (np.isfinite(dt_turn) and dt_turn>0):
            continue
        dtheta=math.atan2(math.sin(heading[k+1]-heading[k]),math.cos(heading[k+1]-heading[k]))
        turns.append(abs(dtheta)/dt_turn)
    turns=np.asarray(turns,dtype=float)

    net=float(np.linalg.norm(xyz[-1]-xyz[0]))
    eff=net/path if path>0 else math.nan
    vrange=float(np.max(xyz[:,2])-np.min(xyz[:,2]))
    feats=np.array([
        np.median(speed),
        np.percentile(speed,90),
        np.median(vz),
        np.percentile(vz,90),
        np.median(turns) if len(turns) else np.nan,
        np.percentile(turns,90) if len(turns) else np.nan,
        eff,
        vrange,
    ],dtype=float)
    valid=bool(np.all(np.isfinite(feats)))
    out["feature_valid"]=valid
    out["features"]={k:(float(v) if np.isfinite(v) else None) for k,v in zip(FEATURES,feats)}
    return out

def main():
    a=get_article()
    traj=[]
    for f in a.get("files") or []:
        fid=int(f.get("id"))
        name=f.get("name") or ""
        m=PAT.match(name)
        if not m or not (RHINO_MIN<=fid<=RHINO_MAX):
            continue
        size=int(f["size"])
        b=get_bytes(f["download_url"],size+4096)
        if len(b)!=size:
            raise RuntimeError(f"size mismatch {name}")
        md5=hashlib.md5(b).hexdigest()
        expected=f.get("computed_md5") or f.get("supplied_md5")
        if expected and md5!=expected:
            raise RuntimeError(f"md5 mismatch {name}")
        arr=parse_xyz(b)
        summ=trajectory_summary(arr)
        traj.append({
            "file_id":fid,"name":name,"env":int(m.group("env")),
            "bat":m.group("bat"),"trial_token":m.group("trial"),
            **summ,
        })

    if len(traj)!=45:
        raise RuntimeError(f"expected 45 Rhino CSVs, got {len(traj)}")

    # Primary A coordinate support
    route_counts=collections.Counter()
    for r in traj:
        if r["route_valid"]:
            route_counts[(r["env"],r["bat"])]+=1
    envs=sorted(set(r["env"] for r in traj))
    bats=sorted(set(r["bat"] for r in traj))
    a_env=[]
    eligible_A=[]
    for e in envs:
        counts={b:route_counts[(e,b)] for b in bats}
        repeated=[b for b,n in counts.items() if n>=2]
        ok=len(repeated)>=3
        if ok:eligible_A.append(e)
        a_env.append({"env":e,"route_valid_counts_by_bat":counts,
                      "repeated_target_bats":repeated,"pass_A_environment":ok})
    pass_A=len(eligible_A)>=2

    # Raw Primary B feature-valid support
    feature_valid=[r for r in traj if r["feature_valid"]]
    feature_counts=collections.Counter()
    for r in feature_valid:
        feature_counts[(r["env"],r["bat"])]+=1
    usable_env=[]
    env_feature_stats={}
    for e in envs:
        rr=[r for r in feature_valid if r["env"]==e]
        distinct=sorted(set(r["bat"] for r in rr))
        if len(rr)>=2 and len(distinct)>=2:
            usable_env.append(e)
            mat=np.array([[r["features"][k] for k in FEATURES] for r in rr],dtype=float)
            means=np.mean(mat,axis=0)
            sds=np.std(mat,axis=0,ddof=1)
            env_feature_stats[str(e)]={
                "n_trajectories":len(rr),"bats":distinct,
                "means":{k:float(v) for k,v in zip(FEATURES,means)},
                "sample_sds":{k:float(v) if np.isfinite(v) else None for k,v in zip(FEATURES,sds)},
            }

    retained=[]
    dropped=[]
    for kidx,k in enumerate(FEATURES):
        bad=[]
        for e in usable_env:
            sd=env_feature_stats[str(e)]["sample_sds"][k]
            if sd is None or not np.isfinite(sd) or sd<=0:
                bad.append(e)
        if bad:dropped.append({"feature":k,"bad_envs":bad})
        else:retained.append(k)

    bat_envs={}
    candidates=[]
    for b in bats:
        es=sorted(set(r["env"] for r in feature_valid if r["bat"]==b and r["env"] in usable_env))
        bat_envs[b]=es
        if len(es)>=3:candidates.append(b)

    target_support=[]
    supported_by_bat=collections.Counter()
    for r in feature_valid:
        if r["env"] not in usable_env or r["bat"] not in candidates:
            continue
        e=r["env"]; b=r["bat"]
        own_other=[ee for ee in bat_envs[b] if ee!=e]
        donors=[]
        for j in bats:
            if j==b:continue
            jes=sorted(set(x["env"] for x in feature_valid if x["bat"]==j and x["env"] in usable_env and x["env"]!=e))
            if len(jes)>=2:
                donors.append(j)
        ok=(len(own_other)>=2 and len(donors)>=2)
        target_support.append({"name":r["name"],"bat":b,"env":e,
                               "n_own_other_envs":len(own_other),
                               "donor_bats":donors,"pass_target_support":ok})
        if ok:supported_by_bat[b]+=1

    pass_B=(len(retained)>=6 and len(candidates)>=3 and
            all(supported_by_bat[b]>=1 for b in candidates) and
            all(x["pass_target_support"] for x in target_support))

    out={
        "contract":"RHINO_COORDINATE_SUPPORT_OPENING_V1.md",
        "identity_outcomes_calculated":False,
        "pulse_values_used":False,
        "n_trajectories":len(traj),
        "trajectory_support":traj,
        "primary_A":{
            "eligible_environments":eligible_A,
            "environment_support":a_env,
            "verdict":"PASS_A_OPEN_OUTCOME" if pass_A else "STOP_A_COORDINATE_SUPPORT",
        },
        "primary_B":{
            "usable_environments":usable_env,
            "feature_environment_stats":env_feature_stats,
            "retained_features":retained,
            "dropped_features":dropped,
            "candidate_bats":candidates,
            "usable_envs_by_bat":bat_envs,
            "supported_targets_by_bat":dict(supported_by_bat),
            "target_support":target_support,
            "verdict":"PASS_B_OPEN_OUTCOME" if pass_B else "STOP_B_COORDINATE_SUPPORT",
        },
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
