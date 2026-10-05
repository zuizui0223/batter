#!/usr/bin/env python3
"""Pulse/call-sampled observation-process bridge for the frozen Rhino two-axis policy."""
from __future__ import annotations
import csv, hashlib, importlib.util, io, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"rhino_configuration_identity_primary_v1.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
spec2=importlib.util.spec_from_file_location("T",HERE/"transparent_two_axis_policy_v1.py")
T=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(T)

SEED=202610051101

def call_features(b):
    rdr=csv.DictReader(io.StringIO(b.decode("utf-8-sig",errors="strict")))
    if rdr.fieldnames!=["Time (Seconds)","X","Y","Z","pulse"]:
        raise RuntimeError(f"header drift {rdr.fieldnames}")
    vals=[]
    for row in rdr:
        try:
            t=float(row["Time (Seconds)"]);x=float(row["X"]);y=float(row["Y"]);z=float(row["Z"]);p=float(row["pulse"])
        except Exception:
            continue
        if p==0 or not all(math.isfinite(v) for v in (t,x,y,z,p)):
            continue
        vals.append((t,x,y,z))
    if len(vals)<20:return None
    a=np.asarray(vals,float)
    order=np.argsort(a[:,0],kind="mergesort");a=a[order]
    _,idx=np.unique(a[:,0],return_index=True);a=a[np.sort(idx)]
    if len(a)<20:return None
    t=a[:,0];xyz=a[:,1:4]
    dt=np.diff(t);dxyz=np.diff(xyz,axis=0)
    good=(dt>0)&np.all(np.isfinite(dxyz),axis=1)
    if int(np.sum(good))<19:return None
    dtg=dt[good];dg=dxyz[good]
    speed=np.linalg.norm(dg,axis=1)/dtg
    vz=np.abs(dg[:,2])/dtg
    h=np.hypot(dg[:,0],dg[:,1]);hg=h>0
    headings=np.arctan2(dg[hg,1],dg[hg,0]);hdt=dtg[hg]
    turns=[]
    for k in range(len(headings)-1):
        dtt=.5*(hdt[k]+hdt[k+1])
        if not (math.isfinite(dtt) and dtt>0):continue
        dtheta=math.atan2(math.sin(headings[k+1]-headings[k]),math.cos(headings[k+1]-headings[k]))
        turns.append(abs(dtheta)/dtt)
    turns=np.asarray(turns,float)
    if len(turns)<10:return None
    steps=np.linalg.norm(np.diff(xyz,axis=0),axis=1)
    path=float(np.sum(steps[np.isfinite(steps)]))
    duration=float(t[-1]-t[0])
    if not (duration>0 and path>0 and math.isfinite(path)):return None
    eff=float(np.linalg.norm(xyz[-1]-xyz[0])/path)
    vr=float(np.max(xyz[:,2])-np.min(xyz[:,2]))
    feat=np.asarray([
      np.median(speed),np.percentile(speed,90),
      np.median(vz),np.percentile(vz,90),
      np.median(turns),np.percentile(turns,90),
      eff,vr
    ],float)
    if not np.all(np.isfinite(feat)):return None
    return feat

def load_rows():
    article=P.get_article();raw=[]
    for f in article.get("files") or []:
        fid=int(f["id"]);name=f.get("name") or "";m=P.PAT.match(name)
        if not m or not (P.RHINO_MIN<=fid<=P.RHINO_MAX):continue
        size=int(f["size"]);b=P.get_bytes(f["download_url"],size+4096)
        if len(b)!=size:raise RuntimeError(f"size mismatch {name}")
        exp=f.get("computed_md5") or f.get("supplied_md5")
        if exp and hashlib.md5(b).hexdigest()!=exp:raise RuntimeError(f"md5 mismatch {name}")
        feat=call_features(b)
        raw.append({"name":name,"env":int(m.group("env")),"bat":m.group("bat"),"features":feat})
    if len(raw)!=45:raise RuntimeError(f"expected 45, got {len(raw)}")
    return raw

def build():
    raw=load_rows();valid=[r for r in raw if r["features"] is not None]
    envs=[]
    rows=[]
    for e in sorted(set(r["env"] for r in valid)):
        rr=[r for r in valid if r["env"]==e]
        if len(rr)<2 or len(set(r["bat"] for r in rr))<2:continue
        M=np.vstack([r["features"] for r in rr])
        mu=M.mean(axis=0);sd=M.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):continue
        envs.append(e)
        for r in rr:
            z=(r["features"]-mu)/sd
            q=dict(r);q["I"]=float(np.mean(z[:4]));q["M"]=float(np.mean([-z[0],z[4],z[5],z[6],z[7]]));rows.append(q)
    return raw,rows,envs

def main():
    raw,rows,envs=build()
    ls=T.labelsets(rows,envs);obsmap=T.observed_mapping(rows,envs)
    obs2=T.identity_stat(rows,envs,obsmap,lambda r:np.array([r["I"],r["M"]],float))
    obsi=T.identity_stat(rows,envs,obsmap,lambda r:np.array([r["I"]],float))
    obsm=T.identity_stat(rows,envs,obsmap,lambda r:np.array([r["M"]],float))
    if obs2 is None:
        print(json.dumps({"contract":"CALL_SAMPLED_BRIDGE_CONTRACT_V1.md","verdict":"STOP_OBSERVED_SUPPORT",
                          "n_valid_trajectories":len(rows),"usable_envs":envs},indent=2));return
    cal=T.calibrate(rows,envs,lambda r:np.array([r["I"],r["M"]],float),SEED)
    out={
      "contract":"CALL_SAMPLED_BRIDGE_CONTRACT_V1.md",
      "status":"PROSPECTIVE_OBSERVATION_PROCESS_GATE",
      "species":"Rhinolophus nippon",
      "n_source_trajectories":len(raw),
      "n_call_sampled_valid_trajectories":len(rows),
      "usable_envs":envs,
      "I_observed_K":None if obsi is None else float(obsi[0]),
      "M_observed_K":None if obsm is None else float(obsm[0]),
      "twoD":cal,
      "verdict":"PASS_CALL_SAMPLED_BRIDGE" if cal.get("supported",False) else "STOP_OBSERVATION_PROCESS_MISMATCH"
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
