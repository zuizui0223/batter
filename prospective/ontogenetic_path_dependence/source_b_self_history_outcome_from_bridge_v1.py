#!/usr/bin/env python3
"""Source B first-flight primary outcome from MATLAB-native standardized bridge v2.

Implements the frozen scientific estimator; bridge serialization only replaces
raw-MAT parsing and does not change the statistical design.
"""
from __future__ import annotations

import csv,json,math,pathlib
from collections import defaultdict
import numpy as np
import scipy.io
from scipy.spatial import cKDTree
from scipy.stats import rankdata

ROOT=pathlib.Path("prospective/ontogenetic_path_dependence/matlab_bridge_v2")
N_PERM=9999
SEED=20261004021
TARGET_ORDINALS=range(3,21)
HISTORY_CAP=5

def load_manifest():
    with (ROOT/"manifest.csv").open(newline="") as f:
        return list(csv.DictReader(f))

def load_days(path):
    m=scipy.io.loadmat(path,squeeze_me=True,struct_as_record=False,variable_names=["xyDays"])
    x=m.get("xyDays")
    if x is None:return []
    arr=np.asarray(x,dtype=object).ravel()
    out=[]
    for a in arr:
        z=np.asarray(a,dtype=float)
        if z.ndim==1 and z.size==2:z=z.reshape(1,2)
        if z.ndim!=2 or z.shape[1]!=2:raise RuntimeError(f"bad bridge day shape {z.shape}")
        out.append(z)
    return out

def load_all():
    data=defaultdict(dict)
    manifest=load_manifest()
    for r in manifest:
        p=pathlib.Path(r["bridge_path"])
        days=load_days(p)
        expected=int(float(r["n_exported_days"]))
        if len(days)!=expected:raise RuntimeError(f"bridge count mismatch {r['individual']}")
        data[r["cohort"]][r["individual"]]=days
    return data,manifest

def mean_min_dist(target_xy,history_days):
    vals=[]
    for h in history_days:
        d=cKDTree(h).query(target_xy,k=1,workers=1)[0]
        vals.append(float(np.mean(d)))
    return float(np.mean(vals))

def spearman_fixed_x(y):
    y=np.asarray(y,float)
    x=np.arange(1,len(y)+1,dtype=float)
    ry=rankdata(y,method="average")
    sx=x-x.mean();sy=ry-ry.mean()
    den=float(np.sqrt(np.sum(sx*sx)*np.sum(sy*sy)))
    return float(np.sum(sx*sy)/den) if den>0 else 0.0

def prepare(data):
    events=[]
    primary_names={}
    for cohort,people in data.items():
        all_names=sorted(people)
        complete=sorted([n for n,d in people.items() if len(d)>=20])
        primary_names[cohort]=complete
        if len(complete)==0:
            continue
        if len(complete)<4:
            raise RuntimeError(f"{cohort}: target cohort has <4 complete-history juveniles")
        for target_name in complete:
            for t in TARGET_ORDINALS:
                tidx=t-1
                target=people[target_name][tidx]
                start=max(0,tidx-HISTORY_CAP)
                donor_names=[]
                D=[]
                for donor in all_names:
                    if len(people[donor])<t:continue
                    hist=people[donor][start:tidx]
                    if len(hist)<2:continue
                    donor_names.append(donor)
                    D.append(mean_min_dist(target,hist))
                if target_name not in donor_names:
                    raise RuntimeError(f"target self absent {cohort}/{target_name}/t{t}")
                if len(donor_names)<4:
                    raise RuntimeError(f"<self+3 donors {cohort}/{target_name}/t{t}")
                events.append({"cohort":cohort,"target":target_name,"t":t,
                               "donor_names":donor_names,"D":np.asarray(D,float)})
    return events,primary_names

def R(event,assigned):
    names=event["donor_names"]
    if assigned not in names:raise RuntimeError("assigned pseudo-self structurally absent")
    D=event["D"];j=names.index(assigned)
    other=(float(D.sum())-float(D[j]))/(len(D)-1)
    return other-float(D[j])

def identity_map(primary):
    return {c:{n:n for n in names} for c,names in primary.items()}

def perm_map(primary,rng):
    out={}
    for c,names in primary.items():
        p=list(rng.permutation(names))
        out[c]={n:p[i] for i,n in enumerate(names)}
    return out

def summarize(events,mapping):
    by=defaultdict(list);by_t=defaultdict(list)
    for ev in events:
        assigned=mapping[ev["cohort"]][ev["target"]]
        r=R(ev,assigned)
        by[(ev["cohort"],ev["target"])].append((ev["t"],r))
        by_t[ev["t"]].append(r)
    bis=[];lis=[];individual=[]
    for (cohort,name),rows in sorted(by.items()):
        rows=sorted(rows)
        rs=[r for _,r in rows]
        bi=spearman_fixed_x(rs)
        li=float(np.mean([r for t,r in rows if 11<=t<=20]))
        bis.append(bi);lis.append(li)
        individual.append({"cohort":cohort,"individual":name,"B_i":bi,"L_i":li})
    B=float(np.mean(bis));L=float(np.mean(lis))
    curve={str(t):float(np.mean(v)) for t,v in sorted(by_t.items())}
    return B,L,np.asarray(bis),individual,curve

def q(a):
    return {str(x):float(np.quantile(a,x)) for x in (0.025,0.5,0.975)}

def main():
    data,manifest=load_all()
    events,primary=prepare(data)
    n_primary=sum(len(v) for v in primary.values())
    if n_primary<5:
        raise RuntimeError("frozen overall >=5 primary-individual gate failed")
    Bobs,Lobs,bis,individual,curve=summarize(events,identity_map(primary))

    rng=np.random.default_rng(SEED)
    bnull=np.empty(N_PERM);lnull=np.empty(N_PERM)
    for k in range(N_PERM):
        bnull[k],lnull[k],_,_,_=summarize(events,perm_map(primary,rng))

    meanB=float(np.mean(bnull));meanL=float(np.mean(lnull))
    pB=(1+int(np.sum(bnull>=Bobs)))/(N_PERM+1)
    pL=(1+int(np.sum(lnull>=Lobs)))/(N_PERM+1)
    npos=int(np.sum(bis>0));n=len(bis);need=int(math.ceil(0.70*n))
    supported=(Bobs-meanB>0 and pB<=0.05 and npos>=need)

    out={
      "contract":"SOURCE_B_SELF_HISTORY_ESTIMATOR_CONTRACT_V1.md",
      "bridge":"SOURCE_B_MATLAB_STANDARDIZED_COORDINATE_BRIDGE_V2.md",
      "permutation_clarification":"SOURCE_B_PERMUTATION_ELIGIBILITY_CLARIFICATION_V1.md",
      "outcome_opened":True,
      "primary_complete_history_by_cohort":primary,
      "n_primary_evaluable_individuals":n,
      "n_target_events":len(events),
      "primary":{
        "B_obs":Bobs,"B_null_mean":meanB,"B_excess":Bobs-meanB,
        "B_null_quantiles":q(bnull),"p_upper":pB,
        "positive_B_i":npos,"required_positive_B_i":need,
        "positive_fraction":npos/n,
        "verdict":"PASS_EXPERIENCE_DEPENDENT_PERSONAL_HISTORY" if supported else "FAIL_PRIMARY_FORMATION_RULE",
      },
      "secondary_late":{
        "L_obs":Lobs,"L_null_mean":meanL,"L_excess":Lobs-meanL,
        "L_null_quantiles":q(lnull),"p_upper":pL,
      },
      "individuals":individual,
      "descriptive_R_by_target_ordinal":curve,
      "permutations":N_PERM,"seed":SEED,
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
