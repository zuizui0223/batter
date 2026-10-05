#!/usr/bin/env python3
"""Individual-specific peer-context reaction norm for wild P. hastatus H/V policy."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("BV",HERE/"phyllostomus_fixed_bin_bivariate_carrier_v1.py")
BV=importlib.util.module_from_spec(spec);spec.loader.exec_module(BV)

NPERM=9999
MIN_VALID=9500
SEEDS={"2022":202610052101,"2023":202610052102}
EPS=1e-12

def day_records(panel):
    x,audit=BV.B.prepare(panel)
    if not x or not audit["colony_retention_pass"]:
        return None,audit
    rr=BV.standardize_2d(x)
    if rr is None:
        return None,audit

    path=BV.B.W.PANELS[panel][0]
    raw,_,_,_=BV.B.W.load_session_rows(panel,path)
    day={}
    for key,vals in raw.items():
        if vals:
            day[(str(key[0]),str(key[1]),str(key[2]))]=min(z[0] for z in vals).date().isoformat()

    tmp=collections.defaultdict(list)
    for r in rr:
        k=(str(r["cohort"]),str(r["session"]),str(r["iid"]))
        if k not in day: continue
        tmp[(str(r["cohort"]),day[k],str(r["iid"]))].append(np.asarray(r["policy2"],float))

    base=[]
    for (co,d,iid),vals in sorted(tmp.items()):
        base.append({"cohort":co,"day":d,"iid":iid,"y":np.mean(np.vstack(vals),axis=0)})

    byday=collections.defaultdict(list)
    for idx,r in enumerate(base): byday[(r["cohort"],r["day"])].append(idx)

    out=[]
    for dk,idxs in byday.items():
        if len(idxs)<3: continue
        total=np.sum(np.vstack([base[i]["y"] for i in idxs]),axis=0)
        n=len(idxs)
        for i in idxs:
            r=base[i]
            out.append({**r,"daykey":f"{r['cohort']}::{r['day']}",
                        "indkey":f"{r['cohort']}::{r['iid']}",
                        "c":(total-r["y"])/(n-1),
                        "n_peers":n-1})
    return out,audit

def rebuild_with_labels(base,labels):
    rows=[]
    byday=collections.defaultdict(list)
    for k,r in enumerate(base):
        z={**r,"iid":str(labels[k]),"indkey":f"{r['cohort']}::{labels[k]}"}
        rows.append(z);byday[z["daykey"]].append(k)
    for idxs in byday.values():
        total=np.sum(np.vstack([rows[i]["y"] for i in idxs]),axis=0)
        n=len(idxs)
        for i in idxs:
            rows[i]["c"]=(total-rows[i]["y"])/(n-1)
            rows[i]["n_peers"]=n-1
    return rows

def slope_intercept(train):
    Y=np.vstack([r["y"] for r in train])
    C=np.vstack([r["c"] for r in train])
    yb=Y.mean(axis=0);cb=C.mean(axis=0)
    yc=Y-yb;cc=C-cb
    den=float(np.sum(cc*cc))
    if not math.isfinite(den) or den<=EPS:return None
    b=float(np.sum(cc*yc)/den)
    theta=yb-b*cb
    return b,theta,yb,cb

def shared_slope(train):
    by=collections.defaultdict(list)
    for r in train:by[r["indkey"]].append(r)
    num=0.0;den=0.0;n_groups=0
    for vals in by.values():
        if len(vals)<2:continue
        Y=np.vstack([r["y"] for r in vals]);C=np.vstack([r["c"] for r in vals])
        yb=Y.mean(axis=0);cb=C.mean(axis=0)
        yc=Y-yb;cc=C-cb
        d=float(np.sum(cc*cc))
        if not math.isfinite(d) or d<=EPS:continue
        num += float(np.sum(cc*yc));den += d;n_groups += 1
    if n_groups<3 or not math.isfinite(den) or den<=EPS:return None
    return float(num/den)

def statistic(rows):
    byind=collections.defaultdict(list);byday=collections.defaultdict(list)
    for r in rows:
        byind[r["indkey"]].append(r);byday[r["daykey"]].append(r)

    shared_cache={}
    indivfit_cache={}
    per=collections.defaultdict(list)
    slopes=collections.defaultdict(list)
    e0=[];e1=[];e2=[];y0=[]

    for target in rows:
        ik=target["indkey"];dk=target["daykey"]
        train_i=[r for r in byind[ik] if r["daykey"]!=dk]
        if len(train_i)<4:continue

        ck=(ik,dk)
        if ck not in indivfit_cache:
            indivfit_cache[ck]=slope_intercept(train_i)
        fi=indivfit_cache[ck]
        if fi is None:continue
        bi,thetai,ybar,cbar=fi

        if dk not in shared_cache:
            train_all=[r for r in rows if r["daykey"]!=dk]
            shared_cache[dk]=shared_slope(train_all)
        bs=shared_cache[dk]
        if bs is None:continue

        theta_shared=ybar-bs*cbar
        p0=ybar
        p1=theta_shared+bs*target["c"]
        p2=thetai+bi*target["c"]
        y=target["y"]
        q0=float(np.sum((y-p0)**2))
        q1=float(np.sum((y-p1)**2))
        q2=float(np.sum((y-p2)**2))
        per[ik].append((q1-q2,q0-q1))
        slopes[ik].append(bi)
        e0.append(q0);e1.append(q1);e2.append(q2);y0.append(float(np.sum(y*y)))

    ind_rn={k:float(np.mean([z[0] for z in v])) for k,v in per.items() if len(v)>=2}
    ind_shared={k:float(np.mean([z[1] for z in v])) for k,v in per.items() if len(v)>=2}
    ind_b={k:float(np.mean(slopes[k])) for k in ind_rn}
    if len(ind_rn)<5:return None

    keep=set(ind_rn)
    # Recalculate pooled R2 on targets belonging to contributing individuals only.
    E0=[];E1=[];E2=[];Y0=[]
    for target in rows:
        ik=target["indkey"];dk=target["daykey"]
        if ik not in keep:continue
        train_i=[r for r in byind[ik] if r["daykey"]!=dk]
        if len(train_i)<4:continue
        fi=indivfit_cache.get((ik,dk))
        bs=shared_cache.get(dk)
        if fi is None or bs is None:continue
        bi,thetai,ybar,cbar=fi
        y=target["y"];p0=ybar;p1=(ybar-bs*cbar)+bs*target["c"];p2=thetai+bi*target["c"]
        E0.append(float(np.sum((y-p0)**2)));E1.append(float(np.sum((y-p1)**2)))
        E2.append(float(np.sum((y-p2)**2)));Y0.append(float(np.sum(y*y)))

    if len(E2)<15 or sum(Y0)<=0:return None
    return {
      "G_RN":float(np.mean(list(ind_rn.values()))),
      "G_shared":float(np.mean(list(ind_shared.values()))),
      "individual_G_RN":ind_rn,
      "individual_G_shared":ind_shared,
      "individual_mean_b":ind_b,
      "positive_individuals_RN":int(sum(v>0 for v in ind_rn.values())),
      "n_individuals":int(len(ind_rn)),
      "positive_fraction_RN":float(sum(v>0 for v in ind_rn.values())/len(ind_rn)),
      "n_targets":int(len(E2)),
      "R2_M0":float(1-sum(E0)/sum(Y0)),
      "R2_M1_shared":float(1-sum(E1)/sum(Y0)),
      "R2_M2_individual":float(1-sum(E2)/sum(Y0)),
    }

def permuted_labels(rows,rng):
    labs=[r["iid"] for r in rows]
    out=list(labs)
    byday=collections.defaultdict(list)
    for i,r in enumerate(rows):byday[r["daykey"]].append(i)
    for idxs in byday.values():
        x=np.asarray([labs[i] for i in idxs],dtype=object)
        rng.shuffle(x)
        for k,i in enumerate(idxs):out[i]=str(x[k])
    return out

def run(year,panel):
    base,audit=day_records(panel)
    if base is None:return {"status":"STOP_SOURCE_SUPPORT","audit":audit}
    obs=statistic(base)
    if obs is None:return {"status":"STOP_STRUCTURAL_SUPPORT","n_day_units":len(base),"audit":audit}

    rng=np.random.default_rng(SEEDS[year]);null=[]
    for _ in range(NPERM):
        labs=permuted_labels(base,rng)
        q=statistic(rebuild_with_labels(base,labs))
        if q is not None and math.isfinite(q["G_RN"]):
            null.append(q["G_RN"])
    a=np.asarray(null,float)
    if len(a)<MIN_VALID:
        return {"status":"STOP_RANDOMIZATION_SUPPORT","observed":obs,
                "valid_permutations":int(len(a)),"audit":audit}
    p=float((1+np.sum(a>=obs["G_RN"]))/(1+len(a)))
    supported=bool(obs["G_RN"]>0 and p<=.05 and obs["positive_fraction_RN"]>=.70)
    return {
      "status":"DONE","n_day_units":len(base),**obs,
      "requested_permutations":NPERM,"valid_permutations":int(len(a)),
      "seed":SEEDS[year],"null_mean":float(a.mean()),
      "null_q025":float(np.quantile(a,.025)),"null_q975":float(np.quantile(a,.975)),
      "p_one_sided":p,
      "diagnostic_verdict":"SUPPORTED_INDIVIDUAL_REACTION_NORM" if supported else "UNSUPPORTED_INDIVIDUAL_REACTION_NORM"
    }

def main():
    print(json.dumps({
      "contract":"INDIVIDUAL_PEER_CONTEXT_REACTION_NORM_CONTRACT_V1.md",
      "status":"POST_JAE_POST_OUTCOME_MECHANISM_DIAGNOSTIC",
      "years":{y:run(y,p) for y,p in BV.PANELS.items()}
    },indent=2))

if __name__=="__main__":main()
