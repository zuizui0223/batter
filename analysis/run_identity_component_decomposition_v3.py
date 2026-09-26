#!/usr/bin/env python3
from __future__ import annotations
import itertools, json
from pathlib import Path
import numpy as np
import run_individual_vertical_strategy_v1 as v1

ROOT=Path(__file__).resolve().parents[1]
C=ROOT/"analysis/identity_component_decomposition_contract_v3.json"
BASE=ROOT/"analysis/individual_vertical_strategy_contract_v1.json"
V2=ROOT/"results/spatial_interaction_refinement_result_v2.json"
OUT=ROOT/"results/identity_component_decomposition_result_v3.json"

def exact(matrix):
    n=matrix.shape[0]
    obs=float(np.mean([matrix[i,i] for i in range(n)]))
    vals=[]; ge=0
    for perm in itertools.permutations(range(n)):
        stat=float(np.mean([matrix[perm[j],j] for j in range(n)]))
        vals.append(stat); ge+=int(stat>=obs-1e-15)
    a=np.asarray(vals)
    return {
      "observed_diagonal_mean_gain":obs,
      "permutation_count":len(vals),
      "one_sided_p":ge/len(vals),
      "null_mean":float(a.mean()),
      "null_q05":float(np.quantile(a,.05)),
      "null_q95":float(np.quantile(a,.95))
    }

def build(halves,k,alpha,lam,cells):
    ids=sorted(halves)
    zcounts={i:np.zeros(k,dtype=float) for i in ids}
    ccounts={i:np.zeros(len(cells),dtype=float) for i in ids}
    cindex={c:i for i,c in enumerate(cells)}
    for iid in ids:
      for _,_,cell,z in halves[iid]["early"]:
        zcounts[iid][z]+=1
        ccounts[iid][cindex[cell]]+=1
    spz=np.mean(np.stack([v1.smooth(zcounts[i],alpha) for i in ids]),axis=0)
    spc=np.mean(np.stack([v1.smooth(ccounts[i],alpha) for i in ids]),axis=0)
    iz={}; ic={}
    for iid in ids:
      nz=float(zcounts[iid].sum()); nc=float(ccounts[iid].sum())
      iz[iid]=(zcounts[iid]+lam*spz)/(nz+lam)
      ic[iid]=(ccounts[iid]+lam*spc)/(nc+lam)
    return ids,spz,spc,iz,ic,cindex

def matrices(halves,ids,spz,spc,iz,ic,cindex):
    n=len(ids)
    mz=np.zeros((n,n)); mc=np.zeros((n,n))
    for j,target in enumerate(ids):
      ev=halves[target]["late"]
      zbase=float(np.mean([v1.safe_log(spz[z]) for _,_,_,z in ev]))
      cbase=float(np.mean([v1.safe_log(spc[cindex[cell]]) for _,_,cell,_ in ev]))
      for i,source in enumerate(ids):
        mz[i,j]=float(np.mean([v1.safe_log(iz[source][z]) for _,_,_,z in ev]))-zbase
        mc[i,j]=float(np.mean([v1.safe_log(ic[source][cindex[cell]]) for _,_,cell,_ in ev]))-cbase
    return mz,mc

def one(halves,k,base,c,lam):
    alpha=float(c["inherited"]["jeffreys_alpha"])
    cells=list(base["frozen_geometry"]["eligible_cells"])
    ids,spz,spc,iz,ic,cindex=build(halves,k,alpha,float(lam),cells)
    mz,mc=matrices(halves,ids,spz,spc,iz,ic,cindex)
    out={}
    for name,m in (("altitude_identity",mz),("horizontal_identity",mc)):
      diag=np.asarray([m[i,i] for i in range(len(ids))])
      t=exact(m)
      pos=int(np.sum(diag>0))
      out[name]={
        "matrix":m.tolist(),
        "individual_diagonal_gain":{iid:float(diag[i]) for i,iid in enumerate(ids)},
        "positive_diagonal_count":pos,
        "permutation_test":t,
        "support":bool(t["one_sided_p"]<=0.05 and pos>=6)
      }
    return {"lambda":lam,"individual_ids":ids,**out}

def synth(primary,v2):
    alt=primary["altitude_identity"]["support"]
    hor=primary["horizontal_identity"]["support"]
    interaction=bool(v2["primary"]["primary_pass"])
    if interaction:
      return "location_specific_vertical_interaction_supported"
    if alt and hor:
      return "compound_altitude_and_horizontal_specialization"
    if alt:
      return "primarily_altitude_specialization"
    if hor:
      return "primarily_horizontal_fidelity"
    return "unresolved_identity_mechanism"

def main():
    c=json.loads(C.read_text()); base=json.loads(BASE.read_text()); v2=json.loads(V2.read_text())
    raw,rows,k,_=v1.load_events(base); halves=v1.split_events(rows,base)
    primary=one(halves,k,base,c,int(c["inherited"]["primary_lambda"]))
    sens={str(x):one(halves,k,base,c,int(x)) for x in c["inherited"]["sensitivity_lambdas"]}
    result={
      "schema":"batter.identity_component_decomposition.result.v3",
      "individual_count":len(halves),
      "primary":primary,
      "v2_location_specific_interaction_support":bool(v2["primary"]["primary_pass"]),
      "synthesis_category":synth(primary,v2),
      "sensitivities":sens,
      "sensitivities_cannot_replace_primary":True,
      "sequential_followup_not_independent":True,
      "prohibited":c["prohibited"]
    }
    import hashlib
    result["fingerprint"]=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
  raise SystemExit(main())
