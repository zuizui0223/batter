#!/usr/bin/env python3
"""2-D horizontal/vertical field policy identity in harmonized P. hastatus data."""
from __future__ import annotations
import collections, importlib.util, json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("B",HERE/"phyllostomus_fixed_bin_harmonization_v2.py")
B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)

NPERM=9999
SEEDS={"2022":202610051461,"2023":202610051462}
PANELS={"2022":"phyllostomus_2022","2023":"phyllostomus_2023"}

REFERENCE={
 "2022":{"I":0.19033943678994567,"H":0.24253594916865998,"V":0.6043071763781303},
 "2023":{"I":0.006807112599012755,"H":0.20391429784459977,"V":0.2063570645273645},
}

def rows_2d(panel):
    rows,audit=B.prepare(panel)
    if not rows or not audit["colony_retention_pass"]:return None,audit
    h=B.standardize(rows,"F2_raw","H")
    v=B.standardize(rows,"F3_raw","V")
    if h is None or v is None:return None,audit
    out=[]
    for a,b in zip(h,v):
        if (a["cohort"],a["session"],a["iid"])!=(b["cohort"],b["session"],b["iid"]):
            raise RuntimeError("row alignment drift")
        q=dict(a);q["policy2"]=np.asarray([float(a["H"]),float(b["V"])],float);out.append(q)
    return out,audit

def statistic(rows,labels):
    # labels correspond to complete sessions; cohorts fixed.
    per_ind=collections.defaultdict(list)
    byco=collections.defaultdict(list)
    for k,r in enumerate(rows):byco[r["cohort"]].append(k)
    for co,idxs in byco.items():
        labs=[labels[i] for i in idxs]
        # all-session centroids under current assigned labels
        groups=collections.defaultdict(list)
        for local,i in enumerate(idxs):groups[labs[local]].append(rows[i]["policy2"])
        for local,i in enumerate(idxs):
            lab=labs[local]
            self_indices=[j for j in idxs if labels[j]==lab and j!=i]
            if not self_indices:continue
            self_cent=np.mean(np.vstack([rows[j]["policy2"] for j in self_indices]),axis=0)
            donors=[]
            for d in sorted(groups):
                if d==lab:continue
                vals=[rows[j]["policy2"] for j in idxs if labels[j]==d]
                if vals:donors.append(np.mean(np.vstack(vals),axis=0))
            if len(donors)<2:continue
            z=rows[i]["policy2"]
            ds=float(np.linalg.norm(z-self_cent))
            do=float(np.mean([np.linalg.norm(z-d) for d in donors]))
            per_ind[(co,lab)].append(do-ds)
    ind={"::".join(k):float(np.mean(v)) for k,v in per_ind.items() if v}
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

def run(year,panel):
    rows,audit=rows_2d(panel)
    if rows is None:return {"status":"STOP_SUPPORT","audit":audit}
    obs,ind=statistic(rows,[r["iid"] for r in rows])
    if obs is None:return {"status":"STOP_OBSERVED"}
    rng=np.random.default_rng(SEEDS[year]);null=[]
    for _ in range(NPERM):
        s,_=statistic(rows,perm_labels(rows,rng))
        if s is not None:null.append(s)
    a=np.asarray(null,float)
    pos=sum(v>0 for v in ind.values());frac=pos/len(ind)
    p=float((1+np.sum(a>=obs))/(1+len(a)))
    supported=obs>0 and p<=.05 and frac>=.70
    return {
      "status":"DONE","K_2D":float(obs),"individual_K":ind,
      "positive_individuals":pos,"n_individuals":len(ind),"positive_fraction":frac,
      "n_sessions":len(rows),"valid_permutations":int(len(a)),"seed":SEEDS[year],
      "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
      "null_q975":float(np.quantile(a,.975)),"p_one_sided":p,
      "reference_fixed_bin_scalar_H":REFERENCE[year],
      "diagnostic_verdict":"SUPPORTED_2D_FIELD_POLICY" if supported else "UNSUPPORTED_2D_FIELD_POLICY"
    }

def main():
    print(json.dumps({
      "contract":"FIELD_TWO_COMPONENT_POLICY_CARRIER_CONTRACT_V1.md",
      "status":"POST_OUTCOME_MECHANISM_DIAGNOSTIC",
      "years":{yr:run(yr,p) for yr,p in PANELS.items()}
    },ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
