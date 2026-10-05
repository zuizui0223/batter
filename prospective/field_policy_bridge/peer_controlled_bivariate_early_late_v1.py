#!/usr/bin/env python3
"""Peer-controlled bivariate early-to-late persistence in wild P. hastatus."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("BV",HERE/"phyllostomus_fixed_bin_bivariate_carrier_v1.py")
BV=importlib.util.module_from_spec(spec);spec.loader.exec_module(BV)

NPERM=9999
MIN_VALID=9500
SEEDS={"2022":202610051611,"2023":202610051612}
PANELS=BV.PANELS
WINDOW=12*3600.0

def ranks_average(x):
    x=np.asarray(x,float)
    order=np.argsort(x,kind="mergesort")
    r=np.empty(len(x),float);i=0
    while i<len(order):
        j=i+1
        while j<len(order) and x[order[j]]==x[order[i]]:j+=1
        rr=(i+1+j)/2.0
        r[order[i:j]]=rr;i=j
    return r

def spearman(x,y):
    if len(x)<3:return None
    rx=ranks_average(x);ry=ranks_average(y)
    if np.std(rx,ddof=1)<=0 or np.std(ry,ddof=1)<=0:return None
    return float(np.corrcoef(rx,ry)[0,1])

def load_rows(panel):
    rows,audit=BV.B.prepare(panel)
    if not rows or not audit["colony_retention_pass"]:
        return None,audit
    rr=BV.standardize_2d(rows)
    if rr is None:return None,audit

    path=BV.B.W.PANELS[panel][0]
    raw,_,_,_=BV.B.W.load_session_rows(panel,path)
    t0={}
    for key,vals in raw.items():
        if vals:t0[(str(key[0]),str(key[1]),str(key[2]))]=min(x[0] for x in vals).timestamp()

    out=[]
    for r in rr:
        key=(str(r["cohort"]),str(r["session"]),str(r["iid"]))
        if key not in t0:continue
        q=dict(r);q["start"]=float(t0[key]);q["policy2"]=np.asarray(r["policy2"],float);out.append(q)
    return out,audit

def peer_residual(rows):
    byco=collections.defaultdict(list)
    for r in rows:byco[str(r["cohort"])].append(r)
    out=[];peer_counts=[]
    for co,rr in byco.items():
        for q in rr:
            donors=collections.defaultdict(list)
            tq=float(q["start"])
            for p in rr:
                if str(p["iid"])==str(q["iid"]):continue
                if abs(float(p["start"])-tq)<=WINDOW:
                    donors[str(p["iid"])].append(np.asarray(p["policy2"],float))
            if len(donors)<2:continue
            dmeans=[np.mean(np.vstack(v),axis=0) for v in donors.values()]
            z=dict(q)
            z["resid2"]=np.asarray(q["policy2"],float)-np.mean(np.vstack(dmeans),axis=0)
            z["n_peer_individuals"]=len(donors)
            out.append(z);peer_counts.append(len(donors))
    return out,peer_counts

def build_split(rows):
    by=collections.defaultdict(list)
    for r in rows:by[(str(r["cohort"]),str(r["iid"]))].append(r)
    split={}
    for key,v in by.items():
        v=sorted(v,key=lambda r:(float(r["start"]),str(r["session"])))
        if len(v)<4:continue
        k=len(v)//2
        early=v[:k];late=v[k:]
        if len(early)<2 or len(late)<2:continue
        split[key]={
          "early":early,
          "late":late,
          "early_centroid":np.mean(np.vstack([r["resid2"] for r in early]),axis=0),
          "late_centroid":np.mean(np.vstack([r["resid2"] for r in late]),axis=0),
        }
    return split

def stat(split,mapping=None):
    perind=collections.defaultdict(list)
    byco=collections.defaultdict(list)
    for (co,iid) in split:byco[co].append(iid)
    for co,ids in byco.items():
        ids=sorted(ids)
        if len(ids)<3:continue
        cent={}
        for lab in ids:
            src=mapping[(co,lab)] if mapping is not None else lab
            cent[lab]=split[(co,src)]["early_centroid"]
        for iid in ids:
            donors=[j for j in ids if j!=iid]
            if len(donors)<2:continue
            for r in split[(co,iid)]["late"]:
                q=np.asarray(r["resid2"],float)
                ds=float(np.linalg.norm(q-cent[iid]))
                do=float(np.mean([np.linalg.norm(q-cent[j]) for j in donors]))
                perind[(co,iid)].append(do-ds)
    ind={"::".join(k):float(np.mean(v)) for k,v in perind.items() if v}
    if len(ind)<3:return None,{}
    return float(np.mean(list(ind.values()))),ind

def perm_mapping(split,rng):
    byco=collections.defaultdict(list)
    for co,iid in split:byco[co].append(iid)
    mp={}
    for co,ids in byco.items():
        ids=sorted(ids)
        vals=np.asarray(ids,dtype=object)
        rng.shuffle(vals)
        for target,src in zip(ids,vals):mp[(co,target)]=str(src)
    return mp

def secondary(split):
    byco=collections.defaultdict(list)
    for key,v in split.items():byco[key[0]].append((key[1],v))
    out={}
    for co,items in byco.items():
        if len(items)<3:continue
        e=np.vstack([v["early_centroid"] for iid,v in items])
        l=np.vstack([v["late_centroid"] for iid,v in items])
        out[co]={
          "n":len(items),
          "rho_H":spearman(e[:,0],l[:,0]),
          "rho_V":spearman(e[:,1],l[:,1]),
          "mean_early_late_centroid_distance":float(np.mean(np.linalg.norm(e-l,axis=1))),
        }
    return out

def run(year,panel):
    rows,audit=load_rows(panel)
    if rows is None:return {"status":"STOP_SOURCE_SUPPORT","audit":audit}
    resid,peer_counts=peer_residual(rows)
    split=build_split(resid)
    obs,ind=stat(split)
    support={
      "source_policy_sessions":len(rows),
      "peer_controlled_sessions":len(resid),
      "peer_control_coverage_fraction":len(resid)/len(rows) if rows else None,
      "peer_individual_count_summary":{
        "min":int(min(peer_counts)) if peer_counts else None,
        "median":float(np.median(peer_counts)) if peer_counts else None,
        "max":int(max(peer_counts)) if peer_counts else None,
      },
      "eligible_individuals":len(split),
      "eligible_by_cohort":dict(collections.Counter(co for co,iid in split)),
      "n_late_targets":sum(len(v["late"]) for v in split.values()),
    }
    if obs is None or len(split)<5:
        return {"status":"STOP_OBSERVED_SUPPORT","audit":audit,**support}

    rng=np.random.default_rng(SEEDS[year]);null=[]
    for _ in range(NPERM):
        q,_=stat(split,perm_mapping(split,rng))
        if q is not None and math.isfinite(q):null.append(q)
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs))/(1+len(a))) if len(a) else None
    pos=sum(v>0 for v in ind.values());frac=pos/len(ind)
    supported=bool(len(a)>=MIN_VALID and obs>0 and p is not None and p<=.05 and frac>=.70)
    return {
      "status":"DONE" if len(a)>=MIN_VALID else "STOP_RANDOMIZATION_SUPPORT",
      "audit":audit,**support,
      "K_2D_early_to_late":float(obs),
      "individual_K":ind,
      "positive_individuals":pos,
      "n_individuals":len(ind),
      "positive_fraction":frac,
      "secondary":secondary(split),
      "requested_permutations":NPERM,
      "valid_permutations":int(len(a)),
      "seed":SEEDS[year],
      "null_mean":float(a.mean()) if len(a) else None,
      "null_q025":float(np.quantile(a,.025)) if len(a) else None,
      "null_q975":float(np.quantile(a,.975)) if len(a) else None,
      "p_one_sided":p,
      "diagnostic_verdict":"SUPPORTED_PEER_CONTROLLED_2D_STABLE_POLICY" if supported else "UNSUPPORTED_PEER_CONTROLLED_2D_STABLE_POLICY"
    }

def main():
    print(json.dumps({
      "contract":"PEER_CONTROLLED_BIVARIATE_EARLY_LATE_CONTRACT_V1.md",
      "status":"POST_OUTCOME_STABLE_POLICY_FALSIFICATION_DIAGNOSTIC",
      "years":{y:run(y,p) for y,p in PANELS.items()}
    },ensure_ascii=False,indent=2))

if __name__=="__main__":main()
