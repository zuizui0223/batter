#!/usr/bin/env python3
"""Transparent H-V allocation-axis identity diagnostic in P. hastatus."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("B",HERE/"phyllostomus_fixed_bin_harmonization_v2.py")
B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)

NPERM=9999
PANELS={"2022":"phyllostomus_2022","2023":"phyllostomus_2023"}
SEEDS={
 ("2022","A"):202610051501,("2023","A"):202610051502,
 ("2022","I"):202610051503,("2023","I"):202610051504,
}

def rows_axes(panel):
    rows,audit=B.prepare(panel)
    if not rows or not audit["colony_retention_pass"]: return None,audit
    h=B.standardize(rows,"F2_raw","H")
    v=B.standardize(rows,"F3_raw","V")
    if h is None or v is None:return None,audit
    out=[]
    for a,b in zip(h,v):
        if (a["cohort"],a["session"],a["iid"])!=(b["cohort"],b["session"],b["iid"]):
            raise RuntimeError("row alignment drift")
        H=float(a["H"]);V=float(b["V"])
        q=dict(a)
        q["H"]=H;q["V"]=V
        q["A"]=(H-V)/math.sqrt(2.0)
        q["I"]=(H+V)/math.sqrt(2.0)
        out.append(q)
    return out,audit

def stat(rows,labels,key):
    byco=collections.defaultdict(list)
    for i,r in enumerate(rows):byco[r["cohort"]].append(i)
    per=collections.defaultdict(list)
    for co,idxs in byco.items():
        groups=collections.defaultdict(list)
        for i in idxs:groups[labels[i]].append(rows[i][key])
        for i in idxs:
            lab=labels[i]
            selfv=[rows[j][key] for j in idxs if labels[j]==lab and j!=i]
            if not selfv:continue
            donors=[]
            for d,vals in groups.items():
                if d==lab:continue
                if vals:donors.append(float(np.mean(vals)))
            if len(donors)<2:continue
            z=float(rows[i][key]);sc=float(np.mean(selfv))
            K=float(np.mean([abs(z-x) for x in donors])-abs(z-sc))
            per[(co,lab)].append(K)
    ind={"::".join(k):float(np.mean(v)) for k,v in per.items() if v}
    if len(ind)<3:return None,{}
    return float(np.mean(list(ind.values()))),ind

def perm_labels(rows,rng):
    labs=[r["iid"] for r in rows];out=list(labs)
    byco=collections.defaultdict(list)
    for i,r in enumerate(rows):byco[r["cohort"]].append(i)
    for idxs in byco.values():
        vals=np.asarray([labs[i] for i in idxs],dtype=object);rng.shuffle(vals)
        for k,i in enumerate(idxs):out[i]=str(vals[k])
    return out

def identity(rows,year,key):
    obs,ind=stat(rows,[r["iid"] for r in rows],key)
    if obs is None:return {"status":"STOP_OBSERVED"}
    rng=np.random.default_rng(SEEDS[(year,key)])
    null=np.empty(NPERM,float)
    for k in range(NPERM):
        s,_=stat(rows,perm_labels(rows,rng),key)
        if s is None:raise RuntimeError("invalid permutation")
        null[k]=s
    p=float((1+np.sum(null>=obs))/(NPERM+1))
    pos=sum(v>0 for v in ind.values());frac=pos/len(ind)
    return {
      "status":"DONE","K":float(obs),"individual_K":ind,
      "positive_individuals":pos,"n_individuals":len(ind),
      "positive_fraction":frac,"p_one_sided":p,
      "null_mean":float(null.mean()),"null_q025":float(np.quantile(null,.025)),
      "null_q975":float(np.quantile(null,.975)),
      "seed":SEEDS[(year,key)],
      "diagnostic_verdict":"SUPPORTED" if (obs>0 and p<=.05 and frac>=.70) else "UNSUPPORTED"
    }

def geometry(rows):
    by=collections.defaultdict(list)
    for r in rows:by[(r["cohort"],r["iid"])].append([r["H"],r["V"]])
    pts=np.vstack([np.mean(np.asarray(v,float),axis=0) for v in by.values()])
    C=np.cov(pts.T,ddof=1)
    vals,vecs=np.linalg.eigh(C)
    v=vecs[:,np.argmax(vals)]
    A=np.array([1.,-1.])/math.sqrt(2)
    I=np.array([1.,1.])/math.sqrt(2)
    if np.dot(v,A)<0:v=-v
    return {
      "pc1_vector":v.tolist(),
      "eigenvalues_desc":sorted(vals.tolist(),reverse=True),
      "pc1_variance_fraction":float(max(vals)/sum(vals)),
      "cosine_to_A":float(np.dot(v,A)/(np.linalg.norm(v)*np.linalg.norm(A))),
      "cosine_to_I":float(np.dot(v,I)/(np.linalg.norm(v)*np.linalg.norm(I))),
      "n_individuals":len(by)
    }

def run(year,panel):
    rows,audit=rows_axes(panel)
    if rows is None:return {"status":"STOP_SUPPORT","audit":audit}
    return {
      "status":"DONE","n_sessions":len(rows),
      "allocation_A":identity(rows,year,"A"),
      "overall_I":identity(rows,year,"I"),
      "axis_geometry":geometry(rows)
    }

def main():
    print(json.dumps({
      "contract":"FIELD_ALLOCATION_AXIS_CONTRACT_V1.md",
      "status":"POST_OUTCOME_INTERPRETABILITY_DIAGNOSTIC",
      "years":{y:run(y,p) for y,p in PANELS.items()}
    },ensure_ascii=False,indent=2))
if __name__=="__main__":main()
