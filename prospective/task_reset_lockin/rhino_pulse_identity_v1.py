#!/usr/bin/env python3
"""Post-primary cross-configuration echolocation-policy identity diagnostic."""
from __future__ import annotations
import collections,csv,hashlib,importlib.util,io,json,math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"rhino_configuration_identity_primary_v1.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)

NPERM=9999
SEED=202610042231
MIN_VALID=9500
FEATURES=[
 "log_pulse_rate",
 "median_log_ipi",
 "p10_log_ipi",
 "p90_log_ipi",
 "iqr_log_ipi",
 "sd_log_ipi",
]

def parse_feature(b):
    rdr=csv.DictReader(io.StringIO(b.decode("utf-8-sig",errors="strict")))
    if rdr.fieldnames!=["Time (Seconds)","X","Y","Z","pulse"]:
        raise RuntimeError(f"header drift {rdr.fieldnames}")
    vals=[]
    for row in rdr:
        try:
            t=float(row["Time (Seconds)"])
            pulse=float(row["pulse"])
        except Exception:
            continue
        if not (math.isfinite(t) and pulse in (0.0,1.0)):
            continue
        vals.append((t,int(pulse)))
    if not vals:return None
    vals.sort(key=lambda x:x[0])
    # duplicate timestamps: logical max
    bytime={}
    for t,p in vals:
        if t not in bytime:bytime[t]=p
        else:bytime[t]=max(bytime[t],p)
    times=np.asarray(sorted(bytime),float)
    if len(times)<2:return None
    duration=float(times[-1]-times[0])
    if not (math.isfinite(duration) and duration>0):return None
    event=np.asarray([t for t in times if bytime[t]==1],float)
    if len(event)<30:return None
    ipi=np.diff(event)
    ipi=ipi[np.isfinite(ipi)&(ipi>0)]
    if len(ipi)<29:return None
    lipi=np.log(ipi)
    rate=len(event)/duration
    if not (math.isfinite(rate) and rate>0):return None
    f=np.asarray([
      math.log(rate),
      np.median(lipi),
      np.percentile(lipi,10),
      np.percentile(lipi,90),
      np.percentile(lipi,75)-np.percentile(lipi,25),
      np.std(lipi,ddof=1),
    ],float)
    return f if np.all(np.isfinite(f)) else None

def load_rows():
    article=P.get_article();out=[]
    for f in article.get("files") or []:
        fid=int(f["id"]);name=f.get("name") or "";m=P.PAT.match(name)
        if not m or not (P.RHINO_MIN<=fid<=P.RHINO_MAX):continue
        size=int(f["size"]);b=P.get_bytes(f["download_url"],size+4096)
        if len(b)!=size:raise RuntimeError(f"size mismatch {name}")
        exp=f.get("computed_md5") or f.get("supplied_md5")
        if exp and hashlib.md5(b).hexdigest()!=exp:raise RuntimeError(f"md5 mismatch {name}")
        feat=parse_feature(b)
        out.append({"name":name,"env":int(m.group("env")),"bat":m.group("bat"),"features":feat,"valid":feat is not None})
    if len(out)!=45:raise RuntimeError(f"expected 45, got {len(out)}")
    return out

def build(rows):
    valid=[r for r in rows if r["valid"]]
    envs=sorted(set(r["env"] for r in valid))
    usable=[]
    keep=np.ones(len(FEATURES),dtype=bool)
    estats={}
    for e in envs:
        rr=[r for r in valid if r["env"]==e]
        if len(rr)<2 or len(set(r["bat"] for r in rr))<2:continue
        mat=np.vstack([r["features"] for r in rr])
        mu=mat.mean(axis=0);sd=mat.std(axis=0,ddof=1)
        usable.append(e);estats[e]=(mu,sd)
        keep &= np.isfinite(sd)&(sd>0)
    idx=np.where(keep)[0]
    if len(idx)<4:return None,{"status":"STOP_FEATURE_SUPPORT","retained_features":[FEATURES[i] for i in idx],"usable_envs":usable}
    zr=[]
    for r in valid:
        if r["env"] not in usable:continue
        mu,sd=estats[r["env"]]
        q=dict(r);q["z"]=(r["features"][idx]-mu[idx])/sd[idx];zr.append(q)
    bats=sorted(set(r["bat"] for r in zr))
    presence={b:sorted(set(r["env"] for r in zr if r["bat"]==b)) for b in bats}
    candidates=sorted([b for b,es in presence.items() if len(es)>=3])
    targets=[]
    support=collections.Counter()
    for i,r in enumerate(zr):
        b,e=r["bat"],r["env"]
        if b not in candidates:continue
        own=[ee for ee in presence[b] if ee!=e]
        donors=[]
        for j in bats:
            if j==b:continue
            jes=[ee for ee in presence[j] if ee!=e]
            if len(jes)>=2:donors.append(j)
        if len(own)>=2 and len(donors)>=2:
            targets.append(i);support[b]+=1
    if len(candidates)<3 or not targets:
        return None,{"status":"STOP_TARGET_SUPPORT","candidate_bats":candidates,"support":dict(support)}
    return (zr,bats,targets,usable,candidates),{
      "status":"PASS_SUPPORT","usable_envs":usable,"candidate_bats":candidates,
      "support_by_bat":dict(support),"n_targets":len(targets),
      "retained_feature_indices":idx.tolist(),"retained_features":[FEATURES[i] for i in idx],
      "valid_trajectories":len(valid),
    }

def main():
    raw=load_rows()
    obj,support=build(raw)
    if obj is None:
        print(json.dumps({"contract":"RHINO_PULSE_IDENTITY_CONTRACT_V1.md",**support},indent=2));return
    rows,bats,targets,usable,candidates=obj
    obs=P.b_stat(rows,bats,targets,None)
    if obs is None:raise RuntimeError("observed support failed")
    Pobs,batmeans,tvals=obs
    envclusters={e:sorted(set(r["bat"] for r in rows if r["env"]==e)) for e in usable}
    rng=np.random.default_rng(SEED);null=[]
    for _ in range(NPERM):
        mapping={}
        for e,labs in envclusters.items():
            perm=list(rng.permutation(np.asarray(labs,dtype=object)))
            for old,new in zip(labs,perm):mapping[(e,old)]=str(new)
        s=P.b_stat(rows,bats,targets,mapping)
        if s is not None:null.append(float(s[0]))
    out={
      "contract":"RHINO_PULSE_IDENTITY_CONTRACT_V1.md","status":"POST_PRIMARY_SENSING_DIAGNOSTIC",
      **support,"P_obs":float(Pobs),"bat_means":{k:float(v) for k,v in batmeans.items()},
      "positive_bats":sum(v>0 for v in batmeans.values()),"n_bats":len(batmeans),
      "positive_fraction":sum(v>0 for v in batmeans.values())/len(batmeans),
      "requested_permutations":NPERM,"valid_permutations":len(null),"seed":SEED,
    }
    if len(null)<MIN_VALID:
        out["verdict"]="STOP_RANDOMIZATION_SUPPORT"
    else:
        a=np.asarray(null,float);p=float((1+np.sum(a>=Pobs))/(1+len(a)))
        supported=Pobs>0 and p<=.05 and out["positive_fraction"]>=.70
        out.update({
          "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),"null_q975":float(np.quantile(a,.975)),
          "p_one_sided":p,"verdict":"SUPPORTED_PULSE_IDENTITY" if supported else "UNSUPPORTED_PULSE_IDENTITY"
        })
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
