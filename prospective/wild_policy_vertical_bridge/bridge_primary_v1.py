#!/usr/bin/env python3
"""Frozen wild horizontal-policy -> held-out vertical-fingerprint bridge.

This script is fail-closed: it will not run unless STRUCTURAL_GATE_FREEZE_V1.json
exists and explicitly authorizes the requested panel.
"""
from __future__ import annotations
import argparse, collections, json, math, sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
for p in (ROOT, ROOT/"src"):
    if str(p) not in sys.path:
        sys.path.insert(0,str(p))
import scripts.run_tag_altitude_bias_shape as shape

HERE=ROOT/"prospective/wild_policy_vertical_bridge"
FREEZE=HERE/"STRUCTURAL_GATE_FREEZE_V1.json"

MAX_DT=1800.0
GRID=2000.0
MIN_SPEED_INTERVALS=30
MIN_TURNS=20
MIN_EVENTS_STRATUM=10
MIN_SHARED_STRATA=3
EDGES=np.asarray([-np.inf,-400.,-200.,-100.,-50.,0.,50.,100.,200.,400.,np.inf],float)
NPERM=9999
SEEDS={
 "hypsignathus":202610051101,
 "phyllostomus_2022":202610051102,
 "phyllostomus_2023":202610051103,
 "phyllostomus_2016":202610051104,
}

def turn_angle(v1x,v1y,v2x,v2y):
    a=math.hypot(v1x,v1y);b=math.hypot(v2x,v2y)
    if a<=0 or b<=0:return None
    c=max(-1.0,min(1.0,(v1x*v2x+v1y*v2y)/(a*b)))
    return math.acos(c)

def session_features_and_endpoints(vals):
    vals=sorted(vals,key=lambda r:r["t"])
    speeds=[];turn_rates=[];eps=[]
    path=0.0;first_xy=None;last_xy=None
    for i in range(1,len(vals)):
        a,b=vals[i-1],vals[i]
        dt=(b["t"]-a["t"]).total_seconds()
        if math.isfinite(dt) and 0<dt<=MAX_DT:
            d=math.hypot(b["x"]-a["x"],b["y"]-a["y"])
            if math.isfinite(d):
                path+=d
                if first_xy is None:first_xy=(a["x"],a["y"])
                last_xy=(b["x"],b["y"])
    for i in range(2,len(vals)):
        a,b,d=vals[i-2],vals[i-1],vals[i]
        dt1=(b["t"]-a["t"]).total_seconds()
        dt2=(d["t"]-b["t"]).total_seconds()
        if not all(math.isfinite(x) and 0<x<=MAX_DT for x in (dt1,dt2)):continue
        v1x,v1y=b["x"]-a["x"],b["y"]-a["y"]
        v2x,v2y=d["x"]-b["x"],d["y"]-b["y"]
        ang=turn_angle(v1x,v1y,v2x,v2y)
        if ang is None:continue
        sp=math.hypot(v2x,v2y)/dt2
        tr=ang/((dt1+dt2)/2.0)
        if not (math.isfinite(sp) and math.isfinite(tr)):continue
        speeds.append(float(sp));turn_rates.append(float(tr))
        eps.append({"x":d["x"],"y":d["y"],"h":d["h"],"speed":float(sp),"turn_angle":float(ang)})
    valid=(len(speeds)>=MIN_SPEED_INTERVALS and len(turn_rates)>=MIN_TURNS and path>0 and first_xy is not None and last_xy is not None)
    feat=None
    if valid:
        net=math.hypot(last_xy[0]-first_xy[0],last_xy[1]-first_xy[1])
        eff=net/path
        feat=np.asarray([
          np.median(speeds),np.percentile(speeds,90),
          np.median(turn_rates),np.percentile(turn_rates,90),
          eff
        ],float)
        if not np.all(np.isfinite(feat)):valid=False;feat=None
    return {"valid_policy":valid,"feature":feat,"endpoints":eps}

def rank_average(x):
    x=np.asarray(x,float);order=np.argsort(x,kind="mergesort")
    ranks=np.empty(len(x),float)
    i=0
    while i<len(x):
        j=i+1
        while j<len(x) and x[order[j]]==x[order[i]]:j+=1
        r=(i+1+j)/2.0
        ranks[order[i:j]]=r
        i=j
    return ranks

def spearman(x,y):
    if len(x)<3:return None
    a=rank_average(x);b=rank_average(y)
    sa=float(np.std(a,ddof=1));sb=float(np.std(b,ddof=1))
    if sa<=0 or sb<=0:return None
    return float(np.corrcoef(a,b)[0,1])

def zbin(v):
    return int(np.searchsorted(EDGES,v,side="right")-1)

def hellinger(p,q):
    return float(math.sqrt(max(0.0,1.0-float(np.sum(np.sqrt(p*q))))))

def load_panel(panel,freeze_panel):
    records,_=shape.panel_raw(panel)
    by_session=collections.defaultdict(list)
    for r in records:
        by_session[(r["cohort"],r["iid"],r["session"])].append(r)

    sess={}
    endpoints_by_cohort=collections.defaultdict(list)
    for key,vals in sorted(by_session.items()):
        m=session_features_and_endpoints(vals)
        m["start"]=min(r["t"] for r in vals)
        m["height_median"]=float(np.median([r["h"] for r in vals]))
        sess[key]=m
        for ep in m["endpoints"]:endpoints_by_cohort[key[0]].append(ep)

    # Check frozen threshold reproduction.
    thresholds={}
    for c,eps in endpoints_by_cohort.items():
        thresholds[c]={
          "speed_median":float(np.median([x["speed"] for x in eps])),
          "turn_angle_median":float(np.median([x["turn_angle"] for x in eps]))
        }
    for c,t in freeze_panel["thresholds"].items():
        for k,v in t.items():
            if not math.isclose(thresholds[c][k],float(v),rel_tol=1e-12,abs_tol=1e-12):
                raise RuntimeError(f"{panel}: threshold drift {c} {k}")

    # Chronological odd/even split.
    by_ind=collections.defaultdict(list)
    for (c,i,s),m in sess.items():by_ind[(c,i)].append((s,m))
    split={}
    for key,ss in by_ind.items():
        ss=sorted(ss,key=lambda x:(x[1]["start"],str(x[0])))
        split[key]={"odd":[],"even":[]}
        for idx,(sid,m) in enumerate(ss,1):
            split[key]["odd" if idx%2==1 else "even"].append((sid,m))

    frozen_keys={(x["cohort"],x["iid"]) for x in freeze_panel["eligible_individuals"]}
    if not frozen_keys:raise RuntimeError(panel+": empty frozen individual set")
    return split,thresholds,frozen_keys

def policy_coords(split,frozen_keys,policy_side):
    # Training-only standardization separately within cohort.
    session_rows=collections.defaultdict(list)
    for key in sorted(frozen_keys):
        for sid,m in split[key][policy_side]:
            if m["valid_policy"]:
                session_rows[key[0]].append((key,m["feature"]))
    coords={}
    for cohort,rows in session_rows.items():
        M=np.vstack([v for key,v in rows])
        mu=M.mean(axis=0);sd=M.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):
            raise RuntimeError(f"bad policy SD cohort {cohort} side {policy_side}")
        tmp=collections.defaultdict(list)
        for key,v in rows:
            z=(v-mu)/sd
            H=float(np.mean(z[:2]))
            Maneuver=float(np.mean([-z[0],z[2],z[3],z[4]]))
            tmp[key].append((H,Maneuver))
        for key,vals in tmp.items():
            if len(vals)<2:raise RuntimeError(f"policy support drift {key} {policy_side}")
            coords[key]=np.mean(np.asarray(vals,float),axis=0)
    if set(coords)!=set(frozen_keys):
        raise RuntimeError("policy coordinate individual set drift")
    return coords

def vertical_profiles(split,thresholds,frozen_keys,target_side):
    # Histograms by individual x fine-cell/state from held-out sessions only.
    hist=collections.defaultdict(lambda:np.zeros(len(EDGES)-1,float))
    count=collections.Counter()
    for key in sorted(frozen_keys):
        cohort,iid=key;th=thresholds[cohort]
        for sid,m in split[key][target_side]:
            med=m["height_median"]
            for ep in m["endpoints"]:
                sb=int(ep["speed"]>th["speed_median"])
                tb=int(ep["turn_angle"]>th["turn_angle_median"])
                state=sb*2+tb
                stratum=(math.floor(ep["x"]/GRID),math.floor(ep["y"]/GRID),state)
                zb=zbin(float(ep["h"]-med))
                if 0<=zb<len(EDGES)-1:
                    hist[(key,stratum)][zb]+=1.0
                    count[(key,stratum)]+=1
    return hist,count

def build_pairs(coords,hist,count,frozen_pairs):
    rows=[]
    for p in frozen_pairs:
        a=(p["cohort"],p["i"]);b=(p["cohort"],p["j"])
        if a not in coords or b not in coords:raise RuntimeError("pair policy key drift")
        sa={s for (k,s),n in count.items() if k==a and n>=MIN_EVENTS_STRATUM}
        sb={s for (k,s),n in count.items() if k==b and n>=MIN_EVENTS_STRATUM}
        shared=sorted(sa&sb)
        if len(shared)<MIN_SHARED_STRATA:raise RuntimeError("pair vertical support drift")
        ds=[]
        for s in shared:
            pa=hist[(a,s)].copy();pb=hist[(b,s)].copy()
            pa/=pa.sum();pb/=pb.sum()
            ds.append(hellinger(pa,pb))
        dvert=float(np.mean(ds))
        dpol=float(np.linalg.norm(coords[a]-coords[b]))
        rows.append({"a":a,"b":b,"D_policy":dpol,"D_vertical":dvert,"n_shared_strata":len(shared)})
    return rows

def permuted_policy_dist(rows,coords,mapping):
    x=[]
    for r in rows:
        a,b=r["a"],r["b"]
        aa=(a[0],mapping[a]);bb=(b[0],mapping[b])
        x.append(float(np.linalg.norm(coords[aa]-coords[bb])))
    return x

def panel_run(panel,freeze_panel):
    split,thresholds,keys=load_panel(panel,freeze_panel)
    folds=[
      ("odd_to_even","odd","even",freeze_panel["pair_support_even"]),
      ("even_to_odd","even","odd",freeze_panel["pair_support_odd"])
    ]
    data={}
    for name,ps,ts,pairs in folds:
        coords=policy_coords(split,keys,ps)
        hist,count=vertical_profiles(split,thresholds,keys,ts)
        rows=build_pairs(coords,hist,count,pairs)
        rho=spearman([r["D_policy"] for r in rows],[r["D_vertical"] for r in rows])
        if rho is None:raise RuntimeError(panel+" observed rho invalid")
        data[name]={"coords":coords,"rows":rows,"rho":rho}
    observed=float(np.mean([data["odd_to_even"]["rho"],data["even_to_odd"]["rho"]]))

    by_cohort=collections.defaultdict(list)
    for c,i in sorted(keys):by_cohort[c].append(i)
    rng=np.random.default_rng(SEEDS[panel])
    null=[]
    for _ in range(NPERM):
        mp={}
        for c,ids in by_cohort.items():
            ids=sorted(ids);pp=list(rng.permutation(np.asarray(ids,dtype=object)))
            for old,new in zip(ids,pp):mp[(c,old)]=str(new)
        foldr=[]
        for name in ("odd_to_even","even_to_odd"):
            dd=data[name]
            xp=permuted_policy_dist(dd["rows"],dd["coords"],mp)
            yp=[r["D_vertical"] for r in dd["rows"]]
            rr=spearman(xp,yp)
            if rr is None:break
            foldr.append(rr)
        if len(foldr)==2:null.append(float(np.mean(foldr)))
    null=np.asarray(null,float)
    if len(null)<9500:raise RuntimeError(panel+" insufficient valid permutations")
    p=float((1+np.sum(null>=observed))/(1+len(null)))
    pass_panel=(data["odd_to_even"]["rho"]>0 and data["even_to_odd"]["rho"]>0 and observed>0 and p<=.05)
    return {
      "panel":panel,
      "rho_odd_policy_to_even_vertical":data["odd_to_even"]["rho"],
      "rho_even_policy_to_odd_vertical":data["even_to_odd"]["rho"],
      "R_mean":observed,
      "pairs_odd_to_even":len(data["odd_to_even"]["rows"]),
      "pairs_even_to_odd":len(data["even_to_odd"]["rows"]),
      "permutations":int(len(null)),
      "seed":SEEDS[panel],
      "null_mean":float(np.mean(null)),
      "null_q025":float(np.quantile(null,.025)),
      "null_q975":float(np.quantile(null,.975)),
      "p_one_sided":p,
      "pass":bool(pass_panel)
    }

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--panel",required=True);args=ap.parse_args()
    if not FREEZE.exists():
        raise SystemExit("STOP: STRUCTURAL_GATE_FREEZE_V1.json absent")
    fr=json.loads(FREEZE.read_text())
    panel=args.panel
    fp=fr.get("panels",{}).get(panel)
    if not fp or fp.get("verdict")!="PASS_TO_VERTICAL_BRIDGE":
        raise SystemExit(f"STOP: panel not authorized by frozen preflight: {panel}")
    out={
      "contract":"BRIDGE_CONTRACT_V1.md",
      "cohort_amendment":"COHORT_STRATIFICATION_AMENDMENT_V1.md",
      "freeze_sha256":fr.get("source_preflight_sha256"),
      "result":panel_run(panel,fp)
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
