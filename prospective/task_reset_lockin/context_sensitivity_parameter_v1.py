#!/usr/bin/env python3
from __future__ import annotations
import itertools, json, math, importlib.util
from collections import defaultdict
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("F",HERE/"flight_intensity_scalar_v1.py")
F=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(F)

BATS=["A","B","C","D","E"]

def centroids():
    rows,envs=F.load_scalar_rows()
    cm={}
    for b in BATS:
        for e in envs:
            vals=[float(r["flight_intensity"]) for r in rows if r["bat"]==b and r["env"]==e]
            if vals:cm[(b,e)]=float(np.mean(vals))
    return cm,envs

def theta(cm,b,e0):
    vals=[v for (bb,e),v in cm.items() if bb==b and e!=e0]
    if len(vals)<3:return None
    return float(np.mean(vals)),len(vals)

def sigma(cm,b,e0):
    vals=[v for (bb,e),v in cm.items() if bb==b and e!=e0]
    if len(vals)<3:return None
    s=float(np.std(vals,ddof=1))
    return s if math.isfinite(s) and s>0 else None

def common_sigma(cm,envs,e0):
    residuals=[]
    for b in BATS:
        vals=[(e,v) for (bb,e),v in cm.items() if bb==b and e!=e0]
        if len(vals)<3:continue
        mu=float(np.mean([v for e,v in vals]))
        residuals.extend([v-mu for e,v in vals])
    if len(residuals)<2:return None
    s=float(np.std(np.asarray(residuals,float),ddof=1))
    return s if math.isfinite(s) and s>0 else None

def lognorm(y,mu,var):
    if not(math.isfinite(var) and var>0):raise RuntimeError("bad variance")
    return -0.5*(math.log(2*math.pi*var)+(y-mu)**2/var)

def sigma_profiles(cm,envs):
    return {(b,e):sigma(cm,b,e) for b in BATS for e in envs}

def records(cm,envs,assignment):
    sig=sigma_profiles(cm,envs)
    out=[]
    for (b,e),y in sorted(cm.items()):
        obj=theta(cm,b,e)
        if obj is None:continue
        mu,n=obj
        source=assignment[b]
        s=sig.get((source,e))
        if s is None:
            raise RuntimeError(f"sigma support source={source} target_env={e}")
        sc=common_sigma(cm,envs,e)
        if sc is None:raise RuntimeError(f"common sigma support env={e}")
        vp=s*s*(1+1/n)
        vc=sc*sc*(1+1/n)
        lp=lognorm(y,mu,vp)
        lc=lognorm(y,mu,vc)
        out.append({
          "bat":b,"env":e,"y":y,"theta":mu,"n_train":n,
          "sigma_source":source,"sigma_personal":s,"sigma_common":sc,
          "log_personal":lp,"log_common":lc,"gain":lp-lc
        })
    return out

def aggregate(rows):
    per={}
    for b in BATS:
        rr=[r for r in rows if r["bat"]==b]
        if rr:per[b]=float(np.mean([r["gain"] for r in rr]))
    if len(per)!=5:raise RuntimeError(f"bat support {per}")
    return float(np.mean(list(per.values()))),per

def main():
    cm,envs=centroids()
    if len(cm)!=25:raise RuntimeError(f"expected 25 centroids got {len(cm)}")
    ident={b:b for b in BATS}
    obsrows=records(cm,envs,ident)
    obs,per=aggregate(obsrows)
    null=[]; detail=[]
    for p in itertools.permutations(BATS):
        mp=dict(zip(BATS,p))
        rr=records(cm,envs,mp)
        g,_=aggregate(rr)
        null.append(g); detail.append({"map":mp,"G":g})
    a=np.asarray(null,float)
    p=float(np.mean(a>=obs-1e-15))
    pos=sum(v>0 for v in per.values())
    full={}
    for b in BATS:
        vals=[v for (bb,e),v in cm.items() if bb==b]
        full[b]={"theta":float(np.mean(vals)),"sigma":float(np.std(vals,ddof=1)),"n_env":len(vals)}
    order=sorted(BATS,key=lambda b:full[b]["sigma"],reverse=True)
    out={
      "status":"POST_PRIMARY_MATHEMATICAL_STRUCTURE_DIAGNOSTIC",
      "contract":"CONTEXT_SENSITIVITY_PARAMETER_CONTRACT_V1.md",
      "n_centroids":len(cm),"observed_Gsigma":obs,
      "bat_Gsigma":per,"positive_bats":pos,
      "exact_permutations":len(null),"p_one_sided":p,
      "null_mean":float(a.mean()),"null_min":float(a.min()),"null_max":float(a.max()),
      "supported":bool(obs>0 and p<=.05 and pos>=4),
      "full_parameters":full,"sigma_order_high_to_low":order,
      "target_records":obsrows,"permutations":detail
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
