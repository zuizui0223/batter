#!/usr/bin/env python3
"""Post-primary exact condition decomposition of Yamada speed-state persistence."""
from __future__ import annotations
import itertools, importlib.util, json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"personal_speed_state_v1.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)

SEED=202610052121
NCONTRAST=99999

def cond_stat(z,cond,assignment):
    bats=sorted([b for (c,t,b) in z if c==cond and t=="12"],key=int)
    vals={}
    for b in bats:
        late=z[(cond,"12",b)]
        ds=abs(late-assignment[b])
        do=float(np.mean([abs(late-assignment[j]) for j in bats if j!=b]))
        vals[b]=do-ds
    return float(np.mean(list(vals.values()))),vals

def corr_acc(z,cond,assignment):
    bats=sorted([b for (c,t,b) in z if c==cond and t=="12"],key=int)
    x=np.asarray([assignment[b] for b in bats],float)
    y=np.asarray([z[(cond,"12",b)] for b in bats],float)
    r=float(np.corrcoef(x,y)[0,1])
    a=[]
    for i in range(len(bats)):
        for j in range(i+1,len(bats)):
            dx=x[i]-x[j];dy=y[i]-y[j]
            a.append(.5 if dx==0 or dy==0 else (1.0 if np.sign(dx)==np.sign(dy) else 0.0))
    return r,float(np.mean(a))

def exact_condition(z,cond):
    bats=sorted([b for (c,t,b) in z if c==cond and t=="1"],key=int)
    early=np.asarray([z[(cond,"1",b)] for b in bats],float)
    obs={b:float(v) for b,v in zip(bats,early)}
    K,Ki=cond_stat(z,cond,obs);r,acc=corr_acc(z,cond,obs)
    nullK=[];nullr=[];nulla=[]
    for perm in itertools.permutations(early.tolist()):
        mp={b:float(v) for b,v in zip(bats,perm)}
        q,_=cond_stat(z,cond,mp);rr,aa=corr_acc(z,cond,mp)
        nullK.append(q);nullr.append(rr);nulla.append(aa)
    nk=np.asarray(nullK);nr=np.asarray(nullr);na=np.asarray(nulla)
    return {
      "K":K,"individual_K":Ki,"positive_bats":sum(v>0 for v in Ki.values()),
      "positive_fraction":sum(v>0 for v in Ki.values())/len(Ki),
      "exact_permutations":len(nk),
      "K_null_mean":float(nk.mean()),"K_null_q025":float(np.quantile(nk,.025)),"K_null_q975":float(np.quantile(nk,.975)),
      "p_K_one_sided":float((1+np.sum(nk>=K))/(1+len(nk))),
      "pearson_r":r,"r_null_mean":float(nr.mean()),"p_r_one_sided":float((1+np.sum(nr>=r))/(1+len(nr))),
      "pair_order_accuracy":acc,"accuracy_null_mean":float(na.mean()),"p_accuracy_one_sided":float((1+np.sum(na>=acc))/(1+len(na))),
      "_nullK":nk
    }

def main():
    rows=P.read_rows();z,rawmeans,changes=P.standardize(rows)
    c1=exact_condition(z,"1");c2=exact_condition(z,"2")
    obs_delta=c2["K"]-c1["K"]
    rng=np.random.default_rng(SEED)
    # Resample independently from exact null distributions.
    n1=c1["_nullK"];n2=c2["_nullK"]
    d=n2[rng.integers(0,len(n2),NCONTRAST)]-n1[rng.integers(0,len(n1),NCONTRAST)]
    pdelta=float((1+np.sum(np.abs(d)>=abs(obs_delta)))/(1+NCONTRAST))
    for c in (c1,c2):c.pop("_nullK",None)
    out={
      "contract":"CONDITION_PERSISTENCE_DIAGNOSTIC_CONTRACT_V1.md",
      "status":"POST_PRIMARY_MECHANISM_DIAGNOSTIC",
      "condition1_permeable":c1,
      "condition2_reflective":c2,
      "contrast_reflective_minus_permeable":{
        "delta_K":obs_delta,"randomization_draws":NCONTRAST,"seed":SEED,
        "null_mean":float(d.mean()),"null_q025":float(np.quantile(d,.025)),"null_q975":float(np.quantile(d,.975)),
        "p_two_sided":pdelta
      },
      "published_shift_reproduction":{
        "permeable_mean_change":float(np.mean(list(changes["1"].values()))),
        "reflective_mean_change":float(np.mean(list(changes["2"].values())))
      }
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
