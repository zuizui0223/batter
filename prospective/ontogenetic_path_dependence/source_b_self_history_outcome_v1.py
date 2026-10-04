#!/usr/bin/env python3
"""Prospective Source B first-flight self-history outcome v1.

Implements SOURCE_B_SELF_HISTORY_ESTIMATOR_CONTRACT_V1.md exactly.
Do not edit estimator choices after first successful outcome opening.
"""
from __future__ import annotations

import hashlib, json, math, tempfile, urllib.parse, urllib.request
from collections import defaultdict

import numpy as np
import scipy.io
from scipy.spatial import cKDTree
from scipy.stats import rankdata

BASE="https://data.mendeley.com/public-api"
DS="n9d8gbz3xr"; VERSION=1
UA="batter-source-b-self-history-outcome/1.0"

ROOTS={
    "GPS_2016_2017":"e92b9150-3ee7-49c7-9f1f-b34e6aba6ac9",
    "GPS_2017_2018":"d66d9326-798c-4d88-9491-85d903cf1b75",
}

N_PERM=9999
SEED=20261004021
VALID_FIX_MIN=20
TARGET_ORDINALS=range(3,21)  # 3..20
HISTORY_CAP=5

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.mendeley-public-dataset.1+json"})
    with urllib.request.urlopen(req,timeout=45) as r:return json.load(r)

def get_bytes(url,max_bytes=15_000_000):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=120) as r:
        n=r.headers.get("Content-Length")
        if n and int(n)>max_bytes: raise RuntimeError(f"refuse size {n}")
        b=r.read(max_bytes+1)
    if len(b)>max_bytes: raise RuntimeError("oversize")
    return b

def folders():
    r=get_json(f"{BASE}/datasets/{DS}/folders/{VERSION}")
    return r if isinstance(r,list) else r.get("folders") or r.get("items") or r.get("results") or []

def files(folder_id):
    u=f"{BASE}/datasets/{DS}/files?folder_id={urllib.parse.quote(folder_id)}&version={VERSION}&$start=0&$limit=1000"
    r=get_json(u)
    return r if isinstance(r,list) else r.get("files") or r.get("items") or r.get("results") or []

def meta(fid): return get_json(f"{BASE}/datasets/{DS}/files/{fid}")

def get_field(obj,name):
    if obj is None:return None
    if isinstance(obj,dict):return obj.get(name)
    if hasattr(obj,name):return getattr(obj,name)
    if isinstance(obj,np.void) and obj.dtype.names and name in obj.dtype.names:return obj[name]
    if isinstance(obj,np.ndarray) and obj.dtype.names and name in obj.dtype.names:return obj[name]
    return None

def numeric_flat(v):
    if v is None:return np.array([],float)
    try:
        a=np.asarray(v)
        if a.dtype==object:
            vals=[]
            for x in a.ravel():
                try: vals.extend(np.asarray(x,dtype=float).ravel().tolist())
                except Exception: pass
            return np.asarray(vals,float)
        return np.asarray(a,dtype=float).ravel()
    except Exception:
        return np.array([],float)

def track_arrays(day):
    tr=get_field(day,"track")
    x=numeric_flat(get_field(tr,"x")); y=numeric_flat(get_field(tr,"y")); t=numeric_flat(get_field(tr,"time"))
    if len(x)==len(y)==len(t) and len(x)>0:return x,y,t
    try: elems=np.asarray(tr,dtype=object).ravel()
    except Exception: elems=[]
    xs=[];ys=[];ts=[]
    for e in elems:
        xv=numeric_flat(get_field(e,"x")); yv=numeric_flat(get_field(e,"y")); tv=numeric_flat(get_field(e,"time"))
        if len(xv)==len(yv)==len(tv)==1:
            xs.append(xv[0]);ys.append(yv[0]);ts.append(tv[0])
    return np.asarray(xs,float),np.asarray(ys,float),np.asarray(ts,float)

def standardize_day(day):
    x,y,t=track_arrays(day)
    if not (len(x)==len(y)==len(t)) or len(x)==0:return None
    ok=np.isfinite(x)&np.isfinite(y)&np.isfinite(t)
    x=x[ok];y=y[ok];t=t[ok]
    if len(t)==0:return None
    o=np.argsort(t,kind="mergesort"); x=x[o];y=y[o];t=t[o]
    sec=(t-t[0])*86400.0
    bins=np.floor(sec/30.0+1e-9).astype(np.int64)
    keep=np.r_[True,bins[1:]!=bins[:-1]]
    xy=np.column_stack([x[keep],y[keep]])
    return xy if len(xy)>=VALID_FIX_MIN else None

def load_valid_days(b):
    with tempfile.NamedTemporaryFile(suffix=".mat") as tmp:
        tmp.write(b);tmp.flush()
        m=scipy.io.loadmat(tmp.name,squeeze_me=True,struct_as_record=False,variable_names=["data"])
    d=m.get("data")
    if d is None:return []
    days=list(np.asarray(d,dtype=object).ravel())
    out=[]
    for day in days:
        xy=standardize_day(day)
        if xy is not None: out.append(xy)
    return out

def load_all():
    fs=folders(); by_parent=defaultdict(list)
    for f in fs:by_parent[str(f.get("parent_id"))].append(f)
    result={}
    file_receipts=[]
    for cohort,rid in ROOTS.items():
        result[cohort]={}
        for folder in sorted(by_parent.get(rid,[]),key=lambda z:str(z.get("name"))):
            name=folder.get("name"); fid=str(folder.get("id"))
            rr=[x for x in files(fid) if (x.get("filename") or "").lower()=="data.mat"]
            if len(rr)!=1: raise RuntimeError(f"{cohort}/{name}: data.mat count {len(rr)}")
            row=rr[0]; cd=row.get("content_details") or {}; sz=int(cd.get("size") or row.get("size") or 0); sha=cd.get("sha256_hash")
            mm=meta(row["id"]); url=(mm.get("content_details") or {}).get("download_url")
            if not url or sz<=0 or not sha: raise RuntimeError(f"{cohort}/{name}: bad metadata")
            b=get_bytes(url,max(1_000_000,sz+4096))
            got=hashlib.sha256(b).hexdigest()
            if len(b)!=sz or got!=sha: raise RuntimeError(f"{cohort}/{name}: identity mismatch")
            valid=load_valid_days(b)
            result[cohort][name]=valid
            file_receipts.append({"cohort":cohort,"individual":name,"file_id":row["id"],"bytes":sz,"sha256":sha,"n_valid_days":len(valid)})
    return result,file_receipts

def mean_min_dist(target_xy,history_days):
    vals=[]
    for h in history_days:
        tree=cKDTree(h)
        d=tree.query(target_xy,k=1,workers=1)[0]
        vals.append(float(np.mean(d)))
    return float(np.mean(vals))

def spearman_fixed_x(y):
    y=np.asarray(y,float)
    x=np.arange(1,len(y)+1,dtype=float)
    ry=rankdata(y,method="average")
    sx=x-x.mean(); sy=ry-ry.mean()
    den=float(np.sqrt(np.sum(sx*sx)*np.sum(sy*sy)))
    return float(np.sum(sx*sy)/den) if den>0 else 0.0

def prepare_event_distances(data):
    events=[]
    cohort_names={}
    for cohort,people in data.items():
        names=sorted(people)
        cohort_names[cohort]=names
        if sum(len(people[n])>=20 for n in names)<4:
            raise RuntimeError(f"{cohort}: donor structural gate failed")
        for i,name in enumerate(names):
            if len(people[name])<20: continue
            for t_ord in TARGET_ORDINALS:
                tidx=t_ord-1
                target=people[name][tidx]
                start=max(0,tidx-HISTORY_CAP)
                # target ordinal 3 => histories indices 0,1 because tidx=2 and slice [0:2]
                dvec=[]
                donor_names=[]
                for donor in names:
                    if len(people[donor])<t_ord: continue
                    hist=people[donor][start:tidx]
                    if len(hist)<2: continue
                    dvec.append(mean_min_dist(target,hist))
                    donor_names.append(donor)
                if name not in donor_names or len(donor_names)<4:
                    raise RuntimeError(f"{cohort}/{name}/t{t_ord}: donor support")
                events.append({
                    "cohort":cohort,"target":name,"t":t_ord,"e":t_ord-1,
                    "donor_names":donor_names,"D":np.asarray(dvec,float),
                })
    return events,cohort_names

def r_for_assigned(event,assigned_name):
    names=event["donor_names"]; D=event["D"]
    j=names.index(assigned_name)
    if len(D)<=1:return float("nan")
    other=(float(np.sum(D))-float(D[j]))/(len(D)-1)
    return other-float(D[j])

def summarize_mapping(events,cohort_names,mapping):
    by_ind=defaultdict(list)
    by_t=defaultdict(list)
    for ev in events:
        assigned=mapping[ev["cohort"]][ev["target"]]
        r=r_for_assigned(ev,assigned)
        by_ind[(ev["cohort"],ev["target"])].append((ev["t"],r))
        by_t[ev["t"]].append(r)
    bis=[]; late=[]; details={}
    for key,rows in by_ind.items():
        rows=sorted(rows)
        rs=[r for _,r in rows]
        b=spearman_fixed_x(rs)
        l=float(np.mean([r for t,r in rows if 11<=t<=20]))
        bis.append(b);late.append(l)
        details[key]={"B_i":b,"L_i":l,"R":[{"t":t,"R":r} for t,r in rows]}
    B=float(np.mean(bis)); L=float(np.mean(late))
    curve={str(t):float(np.mean(v)) for t,v in sorted(by_t.items())}
    return B,L,np.asarray(bis,float),details,curve

def identity_mapping(cohort_names):
    return {c:{n:n for n in names} for c,names in cohort_names.items()}

def perm_mapping(cohort_names,rng):
    out={}
    for c,names in cohort_names.items():
        p=list(rng.permutation(names))
        out[c]={n:p[i] for i,n in enumerate(names)}
    return out

def quantiles(a):
    return {str(q):float(np.quantile(a,q)) for q in [0.025,0.5,0.975]}

def main():
    data,receipts=load_all()
    primary=[(c,n) for c,p in data.items() for n,v in p.items() if len(v)>=20]
    if len(primary)<5: raise RuntimeError("frozen >=5 individual gate failed after coordinate opening")
    for c,p in data.items():
        if sum(len(v)>=20 for v in p.values())<4: raise RuntimeError(f"{c}: <target+3 donors")

    events,cohort_names=prepare_event_distances(data)
    Bobs,Lobs,bis,details,curve=summarize_mapping(events,cohort_names,identity_mapping(cohort_names))

    rng=np.random.default_rng(SEED)
    bnull=np.empty(N_PERM,float); lnull=np.empty(N_PERM,float)
    for k in range(N_PERM):
        m=perm_mapping(cohort_names,rng)
        bnull[k],lnull[k],_,_,_=summarize_mapping(events,cohort_names,m)

    pB=(1+int(np.sum(bnull>=Bobs)))/(N_PERM+1)
    pL=(1+int(np.sum(lnull>=Lobs)))/(N_PERM+1)
    npos=int(np.sum(bis>0)); nind=len(bis)
    minpos=int(math.ceil(0.70*nind))
    support=(Bobs-float(np.mean(bnull))>0 and pB<=0.05 and npos>=minpos)

    individual_rows=[]
    for (c,n),d in sorted(details.items()):
        individual_rows.append({"cohort":c,"individual":n,"B_i":d["B_i"],"L_i":d["L_i"]})

    out={
        "contract":"SOURCE_B_SELF_HISTORY_ESTIMATOR_CONTRACT_V1.md",
        "outcome_opened":True,
        "n_primary_evaluable_individuals":nind,
        "n_target_events":len(events),
        "valid_day_counts":[{"cohort":r["cohort"],"individual":r["individual"],"n_valid_days":r["n_valid_days"]} for r in receipts],
        "primary":{
            "B_obs":Bobs,
            "B_null_mean":float(np.mean(bnull)),
            "B_excess":Bobs-float(np.mean(bnull)),
            "B_null_quantiles":quantiles(bnull),
            "p_upper":pB,
            "positive_B_i":npos,
            "required_positive_B_i":minpos,
            "positive_fraction":npos/nind,
            "verdict":"PASS_EXPERIENCE_DEPENDENT_PERSONAL_HISTORY" if support else "FAIL_PRIMARY_FORMATION_RULE",
        },
        "secondary_late":{
            "L_obs_m":Lobs,
            "L_null_mean_m":float(np.mean(lnull)),
            "L_excess_m":Lobs-float(np.mean(lnull)),
            "L_null_quantiles_m":quantiles(lnull),
            "p_upper":pL,
        },
        "individuals":individual_rows,
        "descriptive_R_by_target_ordinal_m":curve,
        "permutations":N_PERM,
        "seed":SEED,
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
