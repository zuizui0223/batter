#!/usr/bin/env python3
"""Frozen fixed two-axis external validation in Carollia perspicillata."""
from __future__ import annotations
import collections, hashlib, json, math, re, tempfile, urllib.request
import h5py, numpy as np

OWNER="00keveland"; REPO="Tunnel_2026"; PIN="59928a71887d521fec143080b0b187736c046a0e"
API=f"https://api.github.com/repos/{OWNER}/{REPO}/contents/Trial_Data_Carolia?ref={PIN}"
UA="batter-carollia-fixed-two-axis/1.0"
PAT=re.compile(r"^C(?P<bat>\d+)_(?P<trial>\d+)_(?P<date>\d+)_traj_bat_pos_RESULTS\.mat$")
NPERM=9999
SEED=202610051141

FIXED_BLOCKS={
 "20231216":["2","3","4"],
 "20231222":["5","6","7","8"],
}

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.github+json"})
    with urllib.request.urlopen(req,timeout=60) as r:return json.load(r)

def get_bytes(url,maxn=10_000_000):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/octet-stream"})
    with urllib.request.urlopen(req,timeout=90) as r:
        b=r.read(maxn+1)
    if len(b)>maxn:raise RuntimeError("download budget exceeded")
    return b

def deref_numeric(h,path):
    obj=h[path]
    if not isinstance(obj,h5py.Dataset):
        raise RuntimeError(f"{path} is not dataset")
    # MATLAB v7.3 scalar struct fields often store object references.
    arr=obj[()]
    # object/ref scalar or array
    if h5py.check_dtype(ref=obj.dtype) is not None or obj.dtype.kind=="O":
        refs=np.asarray(arr).reshape(-1)
        vals=[]
        for ref in refs:
            if not ref:continue
            target=h[ref]
            vals.append(np.asarray(target[()]))
        if not vals:raise RuntimeError(f"no refs in {path}")
        if len(vals)==1:return np.asarray(vals[0])
        return np.asarray(vals)
    return np.asarray(arr)

def normalize_track(t,pos):
    t=np.asarray(t,dtype=float).reshape(-1)
    p=np.asarray(pos,dtype=float)
    # MATLAB v7.3 matrices may appear transposed through h5py.
    if p.ndim!=2:
        raise ValueError("POS_NOT_2D")
    if p.shape[1]==3:
        pass
    elif p.shape[0]==3:
        p=p.T
    else:
        raise ValueError("POS_NOT_3COL")
    n=min(len(t),len(p))
    t=t[:n]; p=p[:n]
    ok=np.isfinite(t)&np.all(np.isfinite(p),axis=1)
    t=t[ok];p=p[ok]
    if len(t)<100:raise ValueError("LT100_POINTS")
    order=np.argsort(t,kind="mergesort");t=t[order];p=p[order]
    _,idx=np.unique(t,return_index=True);idx=np.sort(idx)
    t=t[idx];p=p[idx]
    if len(t)<100:raise ValueError("LT100_UNIQUE_TIME")
    dt=np.diff(t);dp=np.diff(p,axis=0)
    good=dt>0
    if int(np.sum(good))<50:raise ValueError("LT50_POSITIVE_DT")
    dtg=dt[good];dpg=dp[good]
    v3=np.linalg.norm(dpg,axis=1)/dtg
    vz=np.abs(dpg[:,2])/dtg
    horiz=np.linalg.norm(dpg[:,:2],axis=1)
    hg=horiz>0
    headings=np.arctan2(dpg[hg,1],dpg[hg,0])
    hdt=dtg[hg]
    turns=[]
    if len(headings)>=2:
        dth=np.arctan2(np.sin(np.diff(headings)),np.cos(np.diff(headings)))
        dtturn=(hdt[1:]+hdt[:-1])/2.0
        tg=np.isfinite(dth)&np.isfinite(dtturn)&(dtturn>0)
        turns=np.abs(dth[tg])/dtturn[tg]
    turns=np.asarray(turns,float)
    if len(turns)<20:raise ValueError("LT20_TURNS")
    steps=np.linalg.norm(np.diff(p,axis=0),axis=1)
    total=float(np.sum(steps[np.isfinite(steps)]))
    dur=float(t[-1]-t[0])
    if not (math.isfinite(total) and total>0):raise ValueError("NONPOS_PATH")
    if not (math.isfinite(dur) and dur>0):raise ValueError("NONPOS_DURATION")
    net=float(np.linalg.norm(p[-1]-p[0]))
    eff=net/total
    vr=float(np.max(p[:,2])-np.min(p[:,2]))
    feat=np.array([
      np.median(v3),np.percentile(v3,90),
      np.median(vz),np.percentile(vz,90),
      np.median(turns),np.percentile(turns,90),
      eff,vr
    ],float)
    if not np.all(np.isfinite(feat)):raise ValueError("NONFINITE_FEATURE")
    return feat,{"n_points":len(t),"n_speed_intervals":len(v3),"n_turns":len(turns),"duration":dur,"path_length":total}

def read_trial(raw):
    with tempfile.NamedTemporaryFile(suffix=".mat") as tmp:
        tmp.write(raw);tmp.flush()
        with h5py.File(tmp.name,"r") as h:
            t=deref_numeric(h,"RESULTS/track/tSec")
            p=deref_numeric(h,"RESULTS/track/pos_sm")
    return normalize_track(t,p)

def standardize_by_block(rows):
    for date in FIXED_BLOCKS:
        rr=[r for r in rows if r["date"]==date and r["valid"]]
        M=np.vstack([r["feature"] for r in rr])
        mu=M.mean(axis=0);sd=M.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):
            raise RuntimeError(f"bad block SD {date}")
        for r in rr:
            z=(r["feature"]-mu)/sd
            r["z"]=z
            r["I"]=float(np.mean(z[:4]))
            r["M"]=float(np.mean(np.array([-z[0],z[4],z[5],z[6],z[7]],float)))

def stat(rows,labels=None,component="2D"):
    # labels maps row index -> current bat label; default observed
    if labels is None:labels=[r["bat"] for r in rows]
    perbat=collections.defaultdict(list);block_means={}
    for date,bats_fixed in FIXED_BLOCKS.items():
        idx=[i for i,r in enumerate(rows) if r["date"]==date and r["valid"]]
        # self/donor centroids under current labels
        groups=collections.defaultdict(list)
        for i in idx:
            groups[labels[i]].append(i)
        target_by_bat=collections.defaultdict(list)
        for i in idx:
            lab=labels[i]
            own=[j for j in groups[lab] if j!=i]
            if not own:continue
            donors=[b for b in sorted(groups) if b!=lab and groups[b]]
            if len(donors)<2:continue
            def vec(j):
                if component=="I":return np.array([rows[j]["I"]],float)
                if component=="M":return np.array([rows[j]["M"]],float)
                return np.array([rows[j]["I"],rows[j]["M"]],float)
            q=vec(i)
            ownc=np.mean(np.vstack([vec(j) for j in own]),axis=0)
            donorcs=[np.mean(np.vstack([vec(j) for j in groups[b]]),axis=0) for b in donors]
            ds=float(np.linalg.norm(q-ownc))
            do=float(np.mean([np.linalg.norm(q-c) for c in donorcs]))
            target_by_bat[lab].append(do-ds)
        bmeans={b:float(np.mean(v)) for b,v in target_by_bat.items() if v}
        if len(bmeans)<3:return None
        block_means[date]=float(np.mean(list(bmeans.values())))
        for b,v in bmeans.items():perbat[(date,b)].append(v)
    # each biological individual occurs in one date block only; flatten by label string prefixed date
    indiv={f"{d}:{b}":float(np.mean(v)) for (d,b),v in perbat.items()}
    overall=float(np.mean(list(block_means.values())))
    return {"K":overall,"block_means":block_means,"bat_means":indiv}

def perm_labels(rows,rng):
    labels=[r["bat"] for r in rows]
    for date in FIXED_BLOCKS:
        idx=[i for i,r in enumerate(rows) if r["date"]==date and r["valid"]]
        vals=np.array([labels[i] for i in idx],dtype=object)
        rng.shuffle(vals)
        for k,i in enumerate(idx):labels[i]=str(vals[k])
    return labels

def main():
    listing=get_json(API)
    rows=[];audit=[]
    for f in listing:
        name=f.get("name") or "";m=PAT.match(name)
        if not m:continue
        bat=m.group("bat");date=m.group("date")
        if date not in FIXED_BLOCKS or bat not in FIXED_BLOCKS[date]:
            continue
        rawurl=f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{PIN}/Trial_Data_Carolia/{name}"
        b=get_bytes(rawurl)
        rec={"filename":name,"bat":bat,"trial":m.group("trial"),"date":date,
             "bytes":len(b),"sha256":hashlib.sha256(b).hexdigest(),"valid":False}
        try:
            feat,sup=read_trial(b)
            rec.update({"valid":True,"feature":feat,**sup})
        except Exception as e:
            rec["invalid_reason"]=str(e)
        rows.append(rec)
        audit.append({k:v for k,v in rec.items() if k!="feature"})

    counts=collections.defaultdict(lambda:collections.Counter())
    for r in rows:
        if r["valid"]:counts[r["date"]][r["bat"]]+=1

    # strict fixed support: every fixed eligible bat retains >=3 valid trials
    support_ok=all(counts[d][b]>=3 for d,bs in FIXED_BLOCKS.items() for b in bs)
    if not support_ok:
        print(json.dumps({
          "contract":"CAROLLIA_FIXED_TWO_AXIS_VALIDATION_CONTRACT_V1.md",
          "status":"STOP_NUMERIC_SUPPORT",
          "valid_counts":{d:dict(c) for d,c in counts.items()},
          "audit":audit
        },ensure_ascii=False,indent=2));return

    standardize_by_block(rows)
    obs=stat(rows,None,"2D")
    oi=stat(rows,None,"I");om=stat(rows,None,"M")
    if obs is None:raise RuntimeError("observed statistic failed")

    rng=np.random.default_rng(SEED);null=[]
    for _ in range(NPERM):
        lab=perm_labels(rows,rng)
        q=stat(rows,lab,"2D")
        if q is not None:null.append(q["K"])
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs["K"]))/(1+len(a)))
    pos=sum(v>0 for v in obs["bat_means"].values());n=len(obs["bat_means"])
    blockpos=all(v>0 for v in obs["block_means"].values())
    supported=bool(obs["K"]>0 and p<=.05 and pos/n>=.70 and blockpos and len(a)>=9500)

    out={
      "contract":"CAROLLIA_FIXED_TWO_AXIS_VALIDATION_CONTRACT_V1.md",
      "status":"DONE",
      "species":"Carollia perspicillata",
      "source_pin":PIN,
      "valid_counts":{d:dict(c) for d,c in counts.items()},
      "audit":audit,
      "C1_fixed_2D":{
        **obs,
        "positive_bats":pos,"n_bats":n,"positive_fraction":pos/n,
        "requested_permutations":NPERM,"valid_permutations":int(len(a)),
        "seed":SEED,"null_mean":float(a.mean()),
        "null_q025":float(np.quantile(a,.025)),"null_q975":float(np.quantile(a,.975)),
        "p_one_sided":p,
      },
      "C2_components":{"I_K":oi["K"] if oi else None,"M_K":om["K"] if om else None},
      "external_verdict":"SUPPORTED_FIXED_TWO_AXIS_EXTERNAL" if supported else "UNSUPPORTED_FIXED_TWO_AXIS_EXTERNAL"
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
