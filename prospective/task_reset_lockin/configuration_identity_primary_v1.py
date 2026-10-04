#!/usr/bin/env python3
"""Run the frozen configuration-conditioned individual flight tests.

Scientific contract:
- CONFIGURATION_CONDITIONED_IDENTITY_CONTRACT_V1.md
- PRIMARY_B_NULL_AMENDMENT_V1.md
- PRIMARY_B_STANDARDIZATION_AMENDMENT_V1.md
- ESTIMATOR_IMPLEMENTATION_APPENDIX_V1.md
"""
from __future__ import annotations
import collections, csv, hashlib, io, json, math, re, urllib.request
import numpy as np

API="https://api.figshare.com/v2/articles/29209493"
UA="batter-task-reset-primary/1.0"
PAT=re.compile(r"^Env(?P<env>\d+)_Bat(?P<bat>[A-Za-z]+)_no(?P<trial>.+)\.csv$")
N_PERM=9999

STRUCT_A_ENVS={
    "Miniopterus_fuliginosus": [],
    "Rhinolophus_nippon": [1,2,3],
}
STRUCT_B_BATS={
    "Miniopterus_fuliginosus": ["A","B","C","D"],
    "Rhinolophus_nippon": ["A","B","C","D","E"],
}

def species_from_id(fid:int)->str:
    if 55033796 <= fid <= 55033850:
        return "Miniopterus_fuliginosus"
    if 55033853 <= fid <= 55033985:
        return "Rhinolophus_nippon"
    raise RuntimeError(f"unmapped CSV id {fid}")

def get_article():
    req=urllib.request.Request(API,headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.load(r)

def get_bytes(url,maxn):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"text/csv,*/*"})
    with urllib.request.urlopen(req,timeout=90) as r:
        b=r.read(maxn+1)
    if len(b)>maxn:
        raise RuntimeError(f"download exceeds budget {maxn}")
    return b

def parse_csv_bytes(b):
    txt=b.decode("utf-8-sig",errors="strict")
    rdr=csv.DictReader(io.StringIO(txt))
    if rdr.fieldnames != ["Time (Seconds)","X","Y","Z","pulse"]:
        raise RuntimeError(f"header drift: {rdr.fieldnames}")
    rows=[]
    for row in rdr:
        vals=[]
        ok=True
        for k in ["Time (Seconds)","X","Y","Z"]:
            try:
                x=float(row[k])
            except Exception:
                ok=False; break
            if not math.isfinite(x):
                ok=False; break
            vals.append(x)
        if ok:
            rows.append(vals)
    if not rows:
        return np.empty((0,4),dtype=np.float64)
    a=np.asarray(rows,dtype=np.float64)
    # stable sort by time
    order=np.argsort(a[:,0],kind="mergesort")
    a=a[order]
    # retain first duplicate timestamp
    _,idx=np.unique(a[:,0],return_index=True)
    idx=np.sort(idx)
    a=a[idx]
    return a

def route_standardize(a):
    if a.shape[0] < 100:
        return None
    t=a[:,0]; xyz=a[:,1:4]
    dt=np.diff(t)
    if np.sum(dt>0) < 50:
        return None
    steps=np.linalg.norm(np.diff(xyz,axis=0),axis=1)
    total=float(np.sum(steps))
    if not math.isfinite(total) or total<=0:
        return None
    cum=np.concatenate([[0.0],np.cumsum(steps)])
    # retain first occurrence of unique cumulative distance
    _,idx=np.unique(cum,return_index=True)
    idx=np.sort(idx)
    if len(idx)<2:
        return None
    cu=cum[idx]/total
    xyz_u=xyz[idx]
    grid=np.linspace(0.0,1.0,101)
    out=np.column_stack([np.interp(grid,cu,xyz_u[:,k]) for k in range(3)])
    return out.astype(np.float64)

def trajectory_features(a):
    if a.shape[0] < 100:
        return None
    t=a[:,0]; xyz=a[:,1:4]
    dt=np.diff(t)
    dxyz=np.diff(xyz,axis=0)
    good=np.isfinite(dt) & (dt>0) & np.all(np.isfinite(dxyz),axis=1)
    if int(np.sum(good)) < 50:
        return None
    dtg=dt[good]
    dg=dxyz[good]
    v3=np.linalg.norm(dg,axis=1)/dtg
    vz=np.abs(dg[:,2])/dtg
    horiz=np.linalg.norm(dg[:,:2],axis=1)
    head_good=horiz>0
    headings=np.arctan2(dg[head_good,1],dg[head_good,0])
    dth_dt=[]
    if len(headings)>=2:
        # Need the matching dt sequence after horizontal filtering.
        dth_base_dt=dtg[head_good]
        dtheta=np.arctan2(np.sin(np.diff(headings)),np.cos(np.diff(headings)))
        dtturn=(dth_base_dt[1:]+dth_base_dt[:-1])/2.0
        valid_turn=np.isfinite(dtheta)&np.isfinite(dtturn)&(dtturn>0)
        dth_dt=np.abs(dtheta[valid_turn])/dtturn[valid_turn]
    dth_dt=np.asarray(dth_dt,dtype=np.float64)
    if len(dth_dt)<20:
        return None
    steps=np.linalg.norm(np.diff(xyz,axis=0),axis=1)
    total=float(np.sum(steps[np.isfinite(steps)]))
    if not math.isfinite(total) or total<=0:
        return None
    net=float(np.linalg.norm(xyz[-1]-xyz[0]))
    eff=net/total
    vr=float(np.max(xyz[:,2])-np.min(xyz[:,2]))
    feats=np.array([
        np.median(v3), np.percentile(v3,90),
        np.median(vz), np.percentile(vz,90),
        np.median(dth_dt), np.percentile(dth_dt,90),
        eff, vr,
    ],dtype=np.float64)
    if not np.all(np.isfinite(feats)):
        return None
    return feats

def a_env_stat(dm, labs):
    counts=collections.Counter(labs)
    target_by_bat=collections.defaultdict(list)
    n=len(labs)
    for ii,lab in enumerate(labs):
        if counts[lab] < 2:
            continue
        self_js=[j for j,x in enumerate(labs) if x==lab and j!=ii]
        if not self_js:
            continue
        dself=float(np.mean(dm[ii,self_js]))
        donor_means=[]
        for other in sorted(set(labs)):
            if other==lab: continue
            js=[j for j,x in enumerate(labs) if x==other]
            if js:
                donor_means.append(float(np.mean(dm[ii,js])))
        if not donor_means:
            continue
        target_by_bat[lab].append(float(np.mean(donor_means)-dself))
    if not target_by_bat:
        return None,{}
    be={b:float(np.mean(v)) for b,v in target_by_bat.items()}
    return float(np.mean(list(be.values()))),be

def a_stat_prepared(envdata, label_by_env):
    env_means=[]
    bat_env_vals=collections.defaultdict(list)
    for e,d in envdata.items():
        em,be=a_env_stat(d["dm"],label_by_env[e])
        if em is None:
            continue
        env_means.append(em)
        for b,v in be.items():
            bat_env_vals[b].append(v)
    if not env_means:
        return None,{}
    return float(np.mean(env_means)),{b:float(np.mean(v)) for b,v in bat_env_vals.items()}

def run_primary_a(sp, records):
    allowed=set(STRUCT_A_ENVS[sp])
    if not allowed:
        return {"status":"STOP_A_STRUCTURAL"}
    rec=[r for r in records if r["env"] in allowed and r["route"] is not None]
    eligible=[]
    for e in sorted(allowed):
        rr=[r for r in rec if r["env"]==e]
        cnt=collections.Counter(r["bat"] for r in rr)
        if sum(n>=2 for n in cnt.values())>=3:
            eligible.append(e)
    if len(eligible)<2:
        return {"status":"STOP_A_COORDINATE_SUPPORT","eligible_envs_after_coordinates":eligible}

    envdata={}
    obs_labels={}
    for e in eligible:
        rr=[r for r in rec if r["env"]==e]
        arr=np.stack([r["route"] for r in rr])
        n=len(rr)
        dm=np.zeros((n,n),dtype=np.float64)
        for i in range(n):
            for j in range(i+1,n):
                d=float(np.mean(np.linalg.norm(arr[i]-arr[j],axis=1)))
                dm[i,j]=dm[j,i]=d
        envdata[e]={"dm":dm}
        obs_labels[e]=[r["bat"] for r in rr]

    obs,batmeans=a_stat_prepared(envdata,obs_labels)
    if obs is None:
        return {"status":"STOP_A_STATISTIC"}
    nbat=len(batmeans)
    npos=sum(v>0 for v in batmeans.values())
    need=math.ceil(0.70*nbat)

    rng=np.random.default_rng(202610042201)
    null=np.empty(N_PERM,dtype=np.float64)
    for p in range(N_PERM):
        labs={}
        for e,vals0 in obs_labels.items():
            vals=np.array(vals0,dtype=object)
            rng.shuffle(vals)
            labs[e]=[str(x) for x in vals]
        st,_=a_stat_prepared(envdata,labs)
        null[p]=st if st is not None else np.nan
    valid=null[np.isfinite(null)]
    pval=(1+int(np.sum(valid>=obs)))/(1+len(valid))
    supported=(obs>0 and pval<=0.05 and npos>=need)
    return {
        "status":"PASS_A_OUTCOME" if supported else "FAIL_A_OUTCOME",
        "eligible_envs":eligible,
        "n_routes":sum(len(v) for v in obs_labels.values()),
        "A_species":obs,
        "individual_A":batmeans,
        "positive_individuals":npos,
        "n_individuals":nbat,
        "required_positive_individuals":need,
        "permutations_valid":int(len(valid)),
        "p_one_sided":float(pval),
        "null_mean":float(np.mean(valid)),
        "null_q025":float(np.quantile(valid,0.025)),
        "null_q975":float(np.quantile(valid,0.975)),
    }

def residualize_features(records, sp):
    rr=[r for r in records if r["feature"] is not None and r["bat"] in STRUCT_B_BATS[sp]]
    if not rr:
        return [],[]
    X=np.stack([r["feature"] for r in rr])
    env=np.array([r["env"] for r in rr])
    resid=np.empty_like(X)
    for e in sorted(set(env.tolist())):
        ix=np.where(env==e)[0]
        resid[ix]=X[ix]-np.mean(X[ix],axis=0,keepdims=True)
    s=np.std(resid,axis=0,ddof=1)
    keep=np.isfinite(s)&(s>0)
    if int(np.sum(keep))<6:
        return [],[]
    Z=resid[:,keep]/s[keep]
    out=[]
    for i,r in enumerate(rr):
        q=dict(r)
        q["zfeat"]=Z[i]
        out.append(q)
    return out,np.where(keep)[0].tolist()

def prepare_b_structure(records, labels):
    env_idx=collections.defaultdict(list)
    for i,r in enumerate(records):
        env_idx[r["env"]].append(i)
    presence=collections.defaultdict(set)
    for e,idxs in env_idx.items():
        for i in idxs:
            presence[labels[i]].add(e)
    candidate=sorted([b for b,es in presence.items() if len(es)>=3])
    return env_idx,presence,candidate

def b_stat_fast(records, labels, env_idx, presence, candidate):
    # Mean feature vector for each current label within each environment.
    elm={}
    for e,idxs in env_idx.items():
        groups=collections.defaultdict(list)
        for i in idxs:
            groups[labels[i]].append(records[i]["zfeat"])
        for b,vs in groups.items():
            elm[(e,b)]=np.mean(np.stack(vs),axis=0)

    # Environment-equal leave-one-environment-out centroids.
    centroid_by_target_env={}
    for e0 in env_idx:
        cents={}
        for b in candidate:
            per=[]
            for e in sorted(presence[b]):
                if e==e0: continue
                v=elm.get((e,b))
                if v is not None:
                    per.append(v)
            if len(per)>=2:
                cents[b]=np.mean(np.stack(per),axis=0)
        centroid_by_target_env[e0]=cents

    target_vals=collections.defaultdict(list)
    for i,q in enumerate(records):
        b=labels[i]
        if b not in candidate:
            continue
        cents=centroid_by_target_env[q["env"]]
        if b not in cents or len(cents)<3:
            continue
        own=float(np.linalg.norm(q["zfeat"]-cents[b]))
        others=[float(np.linalg.norm(q["zfeat"]-v)) for bb,v in cents.items() if bb!=b]
        if len(others)<2:
            continue
        target_vals[b].append(float(np.mean(others)-own))
    indiv={b:float(np.mean(v)) for b,v in target_vals.items() if v}
    if len(indiv)<3:
        return None,indiv
    return float(np.mean(list(indiv.values()))),indiv

def run_primary_b(sp,records):
    rec,feat_idx=residualize_features(records,sp)
    if len(feat_idx)<6:
        return {"status":"STOP_B_FEATURE_SUPPORT","retained_feature_indices":feat_idx}
    obs_labels=[r["bat"] for r in rec]
    env_idx,presence,candidate=prepare_b_structure(rec,obs_labels)
    obs,indiv=b_stat_fast(rec,obs_labels,env_idx,presence,candidate)
    if obs is None:
        return {"status":"STOP_B_COORDINATE_SUPPORT","retained_feature_indices":feat_idx}
    n=len(indiv); npos=sum(v>0 for v in indiv.values()); need=math.ceil(0.70*n)
    rng=np.random.default_rng(202610042202)
    null=np.empty(N_PERM,dtype=np.float64)
    # Label multisets within each environment are fixed; therefore presence/candidate support is fixed.
    for p in range(N_PERM):
        labs=list(obs_labels)
        for e,idxs in env_idx.items():
            vals=np.array([obs_labels[i] for i in idxs],dtype=object)
            rng.shuffle(vals)
            for k,i in enumerate(idxs):
                labs[i]=str(vals[k])
        st,_=b_stat_fast(rec,labs,env_idx,presence,candidate)
        null[p]=st if st is not None else np.nan
    valid=null[np.isfinite(null)]
    pval=(1+int(np.sum(valid>=obs)))/(1+len(valid))
    supported=(obs>0 and pval<=0.05 and npos>=need)
    return {
        "status":"PASS_B_OUTCOME" if supported else "FAIL_B_OUTCOME",
        "n_trajectories":len(rec),
        "retained_feature_indices":feat_idx,
        "candidate_bats":candidate,
        "K_species":obs,
        "individual_K":indiv,
        "positive_individuals":npos,
        "n_individuals":n,
        "required_positive_individuals":need,
        "permutations_valid":int(len(valid)),
        "p_one_sided":float(pval),
        "null_mean":float(np.mean(valid)),
        "null_q025":float(np.quantile(valid,0.025)),
        "null_q975":float(np.quantile(valid,0.975)),
    }

def main():
    a=get_article()
    records=[]
    integrity=[]
    for f in a.get("files") or []:
        name=f.get("name") or ""
        m=PAT.match(name)
        if not m: continue
        fid=int(f["id"]); size=int(f["size"])
        sp=species_from_id(fid)
        b=get_bytes(f["download_url"],size+4096)
        if len(b)!=size: raise RuntimeError(f"size mismatch {name}")
        got=hashlib.md5(b).hexdigest()
        exp=f.get("computed_md5") or f.get("supplied_md5")
        if exp and got!=exp: raise RuntimeError(f"md5 mismatch {name}")
        arr=parse_csv_bytes(b)
        route=route_standardize(arr)
        feat=trajectory_features(arr)
        records.append({
            "file_id":fid,"name":name,"species":sp,
            "env":int(m.group("env")),"bat":m.group("bat"),
            "trial_token":m.group("trial"),
            "n_finite_unique_time_rows":int(arr.shape[0]),
            "route":route,"feature":feat,
        })
        integrity.append({
            "file_id":fid,"name":name,"species":sp,
            "n_finite_unique_time_rows":int(arr.shape[0]),
            "route_valid":route is not None,
            "feature_valid":feat is not None,
        })
    result={
      "contracts":[
        "CONFIGURATION_CONDITIONED_IDENTITY_CONTRACT_V1.md",
        "PRIMARY_B_NULL_AMENDMENT_V1.md",
        "PRIMARY_B_STANDARDIZATION_AMENDMENT_V1.md",
        "ESTIMATOR_IMPLEMENTATION_APPENDIX_V1.md",
      ],
      "trajectory_outcomes_opened":True,
      "n_csv":len(records),
      "coordinate_support":integrity,
      "species":{},
    }
    for sp in ["Miniopterus_fuliginosus","Rhinolophus_nippon"]:
        rr=[r for r in records if r["species"]==sp]
        result["species"][sp]={
            "primary_A":run_primary_a(sp,rr),
            "primary_B":run_primary_b(sp,rr),
        }
    # remove large arrays before JSON serialization
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
