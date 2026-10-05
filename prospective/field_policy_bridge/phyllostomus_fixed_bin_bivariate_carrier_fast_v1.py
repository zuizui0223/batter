#!/usr/bin/env python3
"""Fast numerically equivalent bivariate HxV carrier calibration."""
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("S",HERE/"phyllostomus_fixed_bin_bivariate_carrier_v1.py")
S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)
NPERM=9999

def encode(rows):
    out=[]
    for co in sorted({r["cohort"] for r in rows}):
        rr=[r for r in rows if r["cohort"]==co]
        ids=sorted({r["iid"] for r in rr}); mp={x:k for k,x in enumerate(ids)}
        X=np.vstack([r["policy2"] for r in rr]).astype(float)
        lab=np.asarray([mp[r["iid"]] for r in rr],int)
        cnt=np.bincount(lab,minlength=len(ids)).astype(int)
        if np.any(cnt<2): raise RuntimeError(co)
        out.append((co,ids,X,lab,cnt))
    return out

def cohort_stat(X,lab,cnt):
    L=len(cnt); n=len(lab)
    sums=np.zeros((L,2),float); np.add.at(sums,lab,X)
    cents=sums/cnt[:,None]
    D=np.linalg.norm(X[:,None,:]-cents[None,:,:],axis=2)
    donor=(D.sum(axis=1)-D[np.arange(n),lab])/(L-1)
    selfc=(sums[lab]-X)/(cnt[lab,None]-1)
    adv=donor-np.linalg.norm(X-selfc,axis=1)
    return np.bincount(lab,weights=adv,minlength=L)/cnt

def full(cohorts,override=None):
    vals=[]; detail={}
    for z,(co,ids,X,lab,cnt) in enumerate(cohorts):
        ll=lab if override is None else override[z]
        im=cohort_stat(X,ll,cnt)
        vals.extend(im.tolist())
        if override is None:
            for k,v in enumerate(im): detail[f"{co}:{ids[k]}"]=float(v)
    return float(np.mean(vals)),detail

def run(year,panel,seed):
    rows,audit=S.B.prepare(panel)
    if len(set((r["cohort"],r["iid"]) for r in rows))<5 or not audit["colony_retention_pass"]:
        return {"status":"STOP_STRUCTURAL_OR_COLONY_SUPPORT"}
    rr=S.standardize_2d(rows)
    if rr is None:return {"status":"STOP_STANDARDIZATION"}
    cohorts=encode(rr); obs,ind=full(cohorts)
    rng=np.random.default_rng(seed); null=np.empty(NPERM,float)
    for z in range(NPERM):
        null[z]=full(cohorts,[rng.permutation(c[3]) for c in cohorts])[0]
    pos=sum(v>0 for v in ind.values()); frac=pos/len(ind)
    p=float((1+np.sum(null>=obs))/(NPERM+1))
    return {"status":"DONE","H2_year":obs,"individual_H2":ind,
      "positive_individuals":pos,"n_individuals":len(ind),"positive_fraction":frac,
      "eligible_sessions":len(rr),"valid_permutations":NPERM,"seed":seed,
      "p_one_sided":p,"null_mean":float(null.mean()),
      "null_q025":float(np.quantile(null,.025)),"null_q975":float(np.quantile(null,.975)),
      "diagnostic_verdict":"SUPPORTED_BIVARIATE_CARRIER" if obs>0 and frac>=.70 and p<=.05 else "UNSUPPORTED_BIVARIATE_CARRIER"}

def main():
    print(json.dumps({"contract":"PHYLLOSTOMUS_FIXED_BIN_BIVARIATE_CARRIER_CONTRACT_V1.md",
      "implementation":"vectorized_exact_equivalent_v1","status":"POST_OUTCOME_DIMENSIONALITY_DIAGNOSTIC",
      "years":{"2022":run("2022","phyllostomus_2022",202610051441),
               "2023":run("2023","phyllostomus_2023",202610051442)}} ,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
