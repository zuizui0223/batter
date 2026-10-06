#!/usr/bin/env python3
"""Fixed Rhino-defined scale-free geometry identity in independent Carollia."""
from __future__ import annotations

import collections, importlib.util, json, math, tempfile
from pathlib import Path

import h5py
import numpy as np

HERE=Path(__file__).resolve().parent

spec=importlib.util.spec_from_file_location("P",HERE/"carollia_fixed_two_axis_validation_v1.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)

spec2=importlib.util.spec_from_file_location("T",HERE/"carollia_turn_conditioned_null_v1.py")
T=importlib.util.module_from_spec(spec2);spec.loader.exec_module(T)

spec3=importlib.util.spec_from_file_location("G",HERE/"geometry_only_policy_v1.py")
G=importlib.util.module_from_spec(spec3);spec3.loader.exec_module(G)

NPERM=9999
MIN_VALID=9500
SEED=202610061301

FAMILIES={
    "G":[0,1,2,3],
    "H":[4,5],
    "V":[6,7],
}

def cleaned_route(raw):
    with tempfile.NamedTemporaryFile(suffix=".mat") as tmp:
        tmp.write(raw);tmp.flush()
        with h5py.File(tmp.name,"r") as h:
            t=P.deref_numeric(h,"RESULTS/track/tSec")
            pos=P.deref_numeric(h,"RESULTS/track/pos_sm")
    t=np.asarray(t,dtype=float).reshape(-1)
    p=np.asarray(pos,dtype=float)
    if p.ndim!=2:
        raise ValueError("POS_NOT_2D")
    if p.shape[1]==3:
        pass
    elif p.shape[0]==3:
        p=p.T
    else:
        raise ValueError("POS_NOT_3COL")
    n=min(len(t),len(p))
    t=t[:n];p=p[:n]
    ok=np.isfinite(t)&np.all(np.isfinite(p),axis=1)
    t=t[ok];p=p[ok]
    order=np.argsort(t,kind="mergesort");t=t[order];p=p[order]
    _,idx=np.unique(t,return_index=True);idx=np.sort(idx)
    t=t[idx];p=p[idx]
    if len(t)<100:
        raise ValueError("LT100_UNIQUE_TIME")
    d=np.diff(p,axis=0)
    seg=np.linalg.norm(d,axis=1)
    path=float(np.sum(seg[np.isfinite(seg)]))
    dur=float(t[-1]-t[0])
    if not (math.isfinite(path) and path>0):
        raise ValueError("NONPOS_PATH")
    if not (math.isfinite(dur) and dur>0):
        raise ValueError("NONPOS_DURATION")

    cum=np.concatenate(([0.0],np.cumsum(seg)))
    keep=np.concatenate(([True],np.diff(cum)>0))
    cum2=cum[keep];p2=p[keep]
    if len(cum2)<2 or not (cum2[-1]>0):
        raise ValueError("ROUTE_INTERPOLATION_SUPPORT")
    s=cum2/cum2[-1]
    grid=np.linspace(0.0,1.0,101)
    route101=np.column_stack([np.interp(grid,s,p2[:,k]) for k in range(3)])
    return route101,path,dur,len(t)

def geometry_feature_from_raw(raw):
    # Enforce the existing frozen Carollia trajectory support first.
    _,support=P.read_trial(raw)
    route101,path,dur,n=cleaned_route(raw)
    feat=G.geometry_features({
        "route_valid":True,
        "route101":route101,
        "path_length":path,
    })
    if feat is None or len(feat)!=8 or not np.all(np.isfinite(feat)):
        raise ValueError("GEOMETRY_FEATURE_SUPPORT")
    return np.asarray(feat,float),support

def load_rows():
    listing=P.get_json(P.API)
    rows=[]
    counts=collections.defaultdict(collections.Counter)
    audit=[]
    for f in listing:
        name=f.get("name") or ""
        m=P.PAT.match(name)
        if not m:
            continue
        bat=m.group("bat");date=m.group("date")
        if date not in P.FIXED_BLOCKS or bat not in P.FIXED_BLOCKS[date]:
            continue
        rawurl=f"https://raw.githubusercontent.com/{P.OWNER}/{P.REPO}/{P.PIN}/Trial_Data_Carolia/{name}"
        raw=P.get_bytes(rawurl)
        rec={
            "filename":name,"bat":bat,"trial":m.group("trial"),"date":date,
            "valid":False,
        }
        try:
            feat,support=geometry_feature_from_raw(raw)
            ang=T.read_turn_angles(raw)
            if len(ang)==0:
                turn_class="no_annotated_turn"
            else:
                turn_class="le90" if float(np.max(ang))<=90.0 else "gt90"
            rec.update({
                "valid":True,"gfeat":feat,"turn_class":turn_class,
                "n_annotated_turns":int(len(ang)),
                **support
            })
            counts[date][bat]+=1
        except Exception as e:
            rec["invalid_reason"]=str(e)
        rows.append(rec)
        audit.append({k:v for k,v in rec.items() if k!="gfeat"})

    support_ok=all(counts[d][b]>=3 for d,bs in P.FIXED_BLOCKS.items() for b in bs)
    if not support_ok:
        return None,{
            "status":"STOP_NUMERIC_SUPPORT",
            "valid_counts":{d:dict(c) for d,c in counts.items()},
            "audit":audit,
        }

    for date in P.FIXED_BLOCKS:
        rr=[r for r in rows if r["date"]==date and r["valid"]]
        X=np.vstack([r["gfeat"] for r in rr])
        mu=X.mean(axis=0);sd=X.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):
            raise RuntimeError(f"bad geometry SD block {date}: {sd}")
        for r in rr:
            r["zgeom"]=(r["gfeat"]-mu)/sd

    return rows,{
        "status":"PASS_NUMERIC_SUPPORT",
        "valid_counts":{d:dict(c) for d,c in counts.items()},
        "audit":audit,
    }

def vec(r,dims):
    return np.asarray(r["zgeom"],float)[dims]

def stat(rows,labels=None,dims=slice(0,8)):
    if labels is None:
        labels=[r["bat"] for r in rows]
    perbat=collections.defaultdict(list)
    block_means={}
    for date in P.FIXED_BLOCKS:
        idx=[i for i,r in enumerate(rows) if r["date"]==date and r["valid"]]
        groups=collections.defaultdict(list)
        for i in idx:
            groups[labels[i]].append(i)
        target_by_bat=collections.defaultdict(list)
        for i in idx:
            lab=labels[i]
            own=[j for j in groups[lab] if j!=i]
            if not own:
                continue
            donors=[b for b in sorted(groups) if b!=lab and groups[b]]
            if len(donors)<2:
                continue
            q=vec(rows[i],dims)
            ownc=np.mean(np.vstack([vec(rows[j],dims) for j in own]),axis=0)
            donorcs=[
                np.mean(np.vstack([vec(rows[j],dims) for j in groups[b]]),axis=0)
                for b in donors
            ]
            ds=float(np.linalg.norm(q-ownc))
            do=float(np.mean([np.linalg.norm(q-x) for x in donorcs]))
            target_by_bat[lab].append(do-ds)
        bm={b:float(np.mean(v)) for b,v in target_by_bat.items() if v}
        if len(bm)<3:
            return None
        block_means[date]=float(np.mean(list(bm.values())))
        for b,v in bm.items():
            perbat[(date,b)].append(v)
    indiv={f"{d}:{b}":float(np.mean(v)) for (d,b),v in perbat.items()}
    return {
        "K":float(np.mean(list(block_means.values()))),
        "block_means":block_means,
        "bat_means":indiv,
    }

def conditional_perm_labels(rows,rng):
    labels=[r["bat"] for r in rows]
    strata=collections.defaultdict(list)
    for i,r in enumerate(rows):
        if r["valid"]:
            strata[(r["date"],r["turn_class"])].append(i)
    for idx in strata.values():
        vals=np.asarray([labels[i] for i in idx],dtype=object)
        rng.shuffle(vals)
        for k,i in enumerate(idx):
            labels[i]=str(vals[k])
    return labels

def main():
    rows,support=load_rows()
    if rows is None:
        print(json.dumps({
            "contract":"CAROLLIA_FIXED_GEOMETRY_EXTERNAL_CONTRACT_V1.md",
            **support
        },indent=2))
        return

    obs=stat(rows)
    if obs is None:
        raise RuntimeError("observed geometry statistic failed")
    fam={name:stat(rows,dims=np.asarray(idx,int)) for name,idx in FAMILIES.items()}

    rng=np.random.default_rng(SEED)
    null=[]
    for _ in range(NPERM):
        q=stat(rows,conditional_perm_labels(rows,rng))
        if q is not None and math.isfinite(q["K"]):
            null.append(q["K"])
    a=np.asarray(null,float)
    if len(a)<MIN_VALID:
        raise RuntimeError(f"randomization support {len(a)}")
    p=float((1+np.sum(a>=obs["K"]))/(1+len(a)))
    pos=sum(v>0 for v in obs["bat_means"].values())
    n=len(obs["bat_means"])
    supported=bool(
        obs["K"]>0 and p<=.05 and pos/n>=.70
        and all(v>0 for v in obs["block_means"].values())
    )

    strata=collections.defaultdict(list)
    for r in rows:
        if r["valid"]:
            strata[(r["date"],r["turn_class"])].append(r["bat"])
    stratainfo=[
        {"date":d,"turn_class":c,"n_trials":len(labs),
         "bat_counts":dict(collections.Counter(labs))}
        for (d,c),labs in sorted(strata.items())
    ]

    out={
        "contract":"CAROLLIA_FIXED_GEOMETRY_EXTERNAL_CONTRACT_V1.md",
        "status":"POST_PRIMARY_EXTERNAL_DIAGNOSTIC",
        "species":"Carollia perspicillata",
        "source_pin":P.PIN,
        **support,
        "E1_fixed_geometry":{
            **obs,
            "positive_bats":int(pos),"n_bats":int(n),
            "positive_fraction":float(pos/n),
            "requested_permutations":NPERM,
            "valid_permutations":int(len(a)),
            "seed":SEED,
            "null_mean":float(a.mean()),
            "null_q025":float(np.quantile(a,.025)),
            "null_q975":float(np.quantile(a,.975)),
            "p_one_sided":p,
            "verdict":"SUPPORTED_FIXED_GEOMETRY_EXTERNAL" if supported else "UNSUPPORTED_FIXED_GEOMETRY_EXTERNAL",
        },
        "family_localization_descriptive":{
            k:({"K":v["K"],"block_means":v["block_means"],"bat_means":v["bat_means"]} if v else None)
            for k,v in fam.items()
        },
        "turn_strata":stratainfo,
    }
    print(json.dumps(out,indent=2))

if __name__=="__main__":
    main()
