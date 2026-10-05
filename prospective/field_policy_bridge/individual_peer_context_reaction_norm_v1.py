#!/usr/bin/env python3
"""Individual-specific peer-context reaction norm for wild P. hastatus H/V policy.

Exact implementation of INDIVIDUAL_PEER_CONTEXT_REACTION_NORM_CONTRACT_V1.md.
Uses sufficient statistics only for speed; estimator and null are unchanged.
"""
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
    for idx,r in enumerate(base):byday[(r["cohort"],r["day"])].append(idx)

    out=[]
    for _,idxs in byday.items():
        if len(idxs)<3: continue
        total=np.sum(np.vstack([base[i]["y"] for i in idxs]),axis=0)
        n=len(idxs)
        for i in idxs:
            r=base[i]
            out.append({
              **r,
              "daykey":f"{r['cohort']}::{r['day']}",
              "c":(total-r["y"])/(n-1),
              "n_peers":n-1
            })
    return out,audit

def add_stat(t,r):
    y=r["y"];c=r["c"]
    t["n"]+=1
    t["sy"]+=y
    t["sc"]+=c
    t["scc"]+=float(c@c)
    t["scy"]+=float(c@y)

def sub_record(t,r):
    return {
      "n":t["n"]-1,
      "sy":t["sy"]-r["y"],
      "sc":t["sc"]-r["c"],
      "scc":t["scc"]-float(r["c"]@r["c"]),
      "scy":t["scy"]-float(r["c"]@r["y"]),
    }

def centered_slope(t,min_n):
    n=t["n"]
    if n<min_n:return None
    sy=t["sy"];sc=t["sc"]
    den=float(t["scc"]-(sc@sc)/n)
    if not math.isfinite(den) or den<=EPS:return None
    num=float(t["scy"]-(sc@sy)/n)
    b=num/den
    ybar=sy/n;cbar=sc/n
    return float(b),ybar,cbar

def statistic(rows,labels):
    totals={}
    day_rows=collections.defaultdict(dict)
    rowmeta=[]
    for idx,r in enumerate(rows):
        lab=str(labels[idx]);ik=f"{r['cohort']}::{lab}"
        if ik not in totals:
            totals[ik]={"n":0,"sy":np.zeros(2,float),"sc":np.zeros(2,float),"scc":0.0,"scy":0.0}
        add_stat(totals[ik],r)
        # within a cohort-day every biological label occurs once after day collapse
        if ik in day_rows[r["daykey"]]:
            return None
        day_rows[r["daykey"]][ik]=r
        rowmeta.append((ik,r))

    shared_cache={}
    for dk,removed in day_rows.items():
        num=0.0;den=0.0;ng=0
        for ik,t0 in totals.items():
            t=sub_record(t0,removed[ik]) if ik in removed else t0
            fit=centered_slope(t,2)
            if fit is None:continue
            b,yb,cb=fit
            # Recover numerator/denominator exactly from sufficient statistics.
            n=t["n"];sc=t["sc"];sy=t["sy"]
            d=float(t["scc"]-(sc@sc)/n)
            q=float(t["scy"]-(sc@sy)/n)
            if d<=EPS or not math.isfinite(d):continue
            num+=q;den+=d;ng+=1
        shared_cache[dk]=float(num/den) if ng>=3 and den>EPS and math.isfinite(den) else None

    target=[]
    per_rn=collections.defaultdict(list)
    per_shared=collections.defaultdict(list)
    per_b=collections.defaultdict(list)

    for ik,r in rowmeta:
        train=sub_record(totals[ik],r)
        fi=centered_slope(train,4)
        bs=shared_cache.get(r["daykey"])
        if fi is None or bs is None:continue
        bi,ybar,cbar=fi
        theta_i=ybar-bi*cbar
        theta_s=ybar-bs*cbar
        y=r["y"]
        p0=ybar
        p1=theta_s+bs*r["c"]
        p2=theta_i+bi*r["c"]
        q0=float(np.sum((y-p0)**2))
        q1=float(np.sum((y-p1)**2))
        q2=float(np.sum((y-p2)**2))
        rn=q1-q2;sh=q0-q1
        per_rn[ik].append(rn);per_shared[ik].append(sh);per_b[ik].append(bi)
        target.append((ik,q0,q1,q2,float(y@y)))

    keep={k for k,v in per_rn.items() if len(v)>=2}
    if len(keep)<5:return None
    use=[z for z in target if z[0] in keep]
    if len(use)<15:return None

    ind_rn={k:float(np.mean(per_rn[k])) for k in sorted(keep)}
    ind_shared={k:float(np.mean(per_shared[k])) for k in sorted(keep)}
    ind_b={k:float(np.mean(per_b[k])) for k in sorted(keep)}
    y0=sum(z[4] for z in use)
    if y0<=0:return None
    e0=sum(z[1] for z in use);e1=sum(z[2] for z in use);e2=sum(z[3] for z in use)
    pos=sum(v>0 for v in ind_rn.values())
    return {
      "G_RN":float(np.mean(list(ind_rn.values()))),
      "G_shared":float(np.mean(list(ind_shared.values()))),
      "individual_G_RN":ind_rn,
      "individual_G_shared":ind_shared,
      "individual_mean_b":ind_b,
      "positive_individuals_RN":int(pos),
      "n_individuals":int(len(ind_rn)),
      "positive_fraction_RN":float(pos/len(ind_rn)),
      "n_targets":int(len(use)),
      "R2_M0":float(1-e0/y0),
      "R2_M1_shared":float(1-e1/y0),
      "R2_M2_individual":float(1-e2/y0),
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
    obslabels=[r["iid"] for r in base]
    obs=statistic(base,obslabels)
    if obs is None:return {"status":"STOP_STRUCTURAL_SUPPORT","n_day_units":len(base),"audit":audit}

    rng=np.random.default_rng(SEEDS[year]);null=[]
    for _ in range(NPERM):
        q=statistic(base,permuted_labels(base,rng))
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
      "implementation":"exact sufficient-statistics acceleration",
      "years":{y:run(y,p) for y,p in BV.PANELS.items()}
    },indent=2))

if __name__=="__main__":main()
