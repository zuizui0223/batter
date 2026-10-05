#!/usr/bin/env python3
"""Bivariate horizontal × vertical fixed-bin carrier diagnostic for P. hastatus."""
from __future__ import annotations
import collections, importlib.util, json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("B",HERE/"phyllostomus_fixed_bin_harmonization_v2.py")
B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)

NPERM=9999
SEEDS={"2022":202610051441,"2023":202610051442}
PANELS={"2022":"phyllostomus_2022","2023":"phyllostomus_2023"}

def standardize_2d(rows):
    q=[dict(r) for r in rows]
    for co in sorted({r["cohort"] for r in q}):
        ix=[i for i,r in enumerate(q) if r["cohort"]==co]
        H=np.vstack([q[i]["F2_raw"] for i in ix]).astype(float)
        V=np.vstack([q[i]["F3_raw"] for i in ix]).astype(float)
        if len(ix)<2:return None
        hm,hs=H.mean(axis=0),H.std(axis=0,ddof=1)
        vm,vs=V.mean(axis=0),V.std(axis=0,ddof=1)
        if np.any(~np.isfinite(hs)) or np.any(hs<=0) or np.any(~np.isfinite(vs)) or np.any(vs<=0):
            return None
        for j,i in enumerate(ix):
            h=float(np.mean((H[j]-hm)/hs))
            v=float(np.mean((V[j]-vm)/vs))
            q[i]["policy2"]=np.asarray([h,v],float)
    return q

def stat(rows,labels):
    byco=collections.defaultdict(list)
    for idx,r in enumerate(rows):byco[r["cohort"]].append(idx)
    per=collections.defaultdict(list)
    for co,idxs in byco.items():
        sums={}
        counts=collections.Counter()
        groups=collections.defaultdict(list)
        for i in idxs:
            lab=labels[i];groups[lab].append(rows[i]["policy2"]);counts[lab]+=1
        cents={lab:np.mean(np.vstack(v),axis=0) for lab,v in groups.items()}
        for i in idxs:
            lab=labels[i];q=rows[i]["policy2"]
            if counts[lab]<2:continue
            selfv=[rows[j]["policy2"] for j in idxs if j!=i and labels[j]==lab]
            if not selfv:continue
            selfc=np.mean(np.vstack(selfv),axis=0)
            donors=[c for dl,c in cents.items() if dl!=lab]
            if len(donors)<2:continue
            ds=float(np.linalg.norm(q-selfc))
            do=float(np.mean([np.linalg.norm(q-d) for d in donors]))
            per[(co,lab)].append(do-ds)
    indiv={f"{co}:{lab}":float(np.mean(v)) for (co,lab),v in per.items() if v}
    if len(indiv)<5:return None,indiv
    return float(np.mean(list(indiv.values()))),indiv

def perm_labels(rows,rng):
    labs=[r["iid"] for r in rows];out=list(labs)
    byco=collections.defaultdict(list)
    for i,r in enumerate(rows):byco[r["cohort"]].append(i)
    for idxs in byco.values():
        x=np.asarray([labs[i] for i in idxs],dtype=object);rng.shuffle(x)
        for k,i in enumerate(idxs):out[i]=str(x[k])
    return out

def run_year(year,panel):
    rows,audit=B.prepare(panel)
    nind=len(set((r["cohort"],r["iid"]) for r in rows))
    if nind<5 or not audit["colony_retention_pass"]:
        return {"status":"STOP_STRUCTURAL_OR_COLONY_SUPPORT","eligible_individuals":nind,**audit}
    rr=standardize_2d(rows)
    if rr is None:return {"status":"STOP_STANDARDIZATION","eligible_individuals":nind,**audit}
    labs=[r["iid"] for r in rr]
    obs,ind=stat(rr,labs)
    if obs is None:return {"status":"STOP_OBSERVED_SUPPORT","eligible_individuals":nind}
    rng=np.random.default_rng(SEEDS[year]);null=[]
    for _ in range(NPERM):
        s,_=stat(rr,perm_labels(rr,rng))
        if s is not None:null.append(s)
    a=np.asarray(null,float)
    pos=sum(v>0 for v in ind.values())
    return {
      "status":"DONE","H2_year":float(obs),"individual_H2":ind,
      "positive_individuals":pos,"n_individuals":len(ind),
      "positive_fraction":float(pos/len(ind)),
      "eligible_sessions":len(rr),
      "valid_permutations":int(len(a)),"seed":SEEDS[year],
      "p_one_sided":float((1+np.sum(a>=obs))/(1+len(a))),
      "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
      "null_q975":float(np.quantile(a,.975)),
      "diagnostic_verdict":"SUPPORTED_BIVARIATE_CARRIER"
        if obs>0 and pos/len(ind)>=.70 and len(a)>=9500 and (1+np.sum(a>=obs))/(1+len(a))<=.05
        else "UNSUPPORTED_BIVARIATE_CARRIER",
      "colony_retention_pass":audit["colony_retention_pass"],
    }

def main():
    out={
      "contract":"PHYLLOSTOMUS_FIXED_BIN_BIVARIATE_CARRIER_CONTRACT_V1.md",
      "status":"POST_OUTCOME_DIMENSIONALITY_DIAGNOSTIC",
      "years":{y:run_year(y,p) for y,p in PANELS.items()}
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
