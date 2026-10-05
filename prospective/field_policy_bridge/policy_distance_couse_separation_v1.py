#!/usr/bin/env python3
"""Pairwise persistent policy distance versus frozen synchronous vertical separation."""
from __future__ import annotations
import collections, importlib.util, json, math, sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

BV=loadmod("BV",HERE/"phyllostomus_fixed_bin_bivariate_carrier_v1.py")
CO=loadmod("CO",ROOT/"post_freeze_extensions/3d_niche_partition/run_couse_vertical_separation_v1.py")

NPERM=9999
PANELS={
    "2022":("phyllostomus_2022",202610051531),
    "2023":("phyllostomus_2023",202610051532),
}

def ranks_average(x):
    x=np.asarray(x,float)
    order=np.argsort(x,kind="mergesort")
    ranks=np.empty(len(x),float)
    i=0
    while i<len(order):
        j=i+1
        while j<len(order) and x[order[j]]==x[order[i]]:
            j+=1
        rank=(i+1+j)/2.0
        ranks[order[i:j]]=rank
        i=j
    return ranks

def spearman(x,y):
    if len(x)<3:return math.nan
    rx=ranks_average(x);ry=ranks_average(y)
    if np.std(rx,ddof=1)<=0 or np.std(ry,ddof=1)<=0:return math.nan
    return float(np.corrcoef(rx,ry)[0,1])

def policy_centroids(panel):
    rows,audit=BV.B.prepare(panel)
    if not rows or not audit["colony_retention_pass"]:
        return None,audit
    rr=BV.standardize_2d(rows)
    if rr is None:return None,audit
    by=collections.defaultdict(list)
    for r in rr:
        by[(str(r["cohort"]),str(r["iid"]))].append(np.asarray(r["policy2"],float))
    out={k:np.mean(np.vstack(v),axis=0) for k,v in by.items()}
    return out,audit

def frozen_dyads(panel):
    cfg=json.loads(CO.CFG.read_text(encoding="utf-8"))
    receipt=json.loads(CO.RECEIPT.read_text(encoding="utf-8"))
    xy=CO.shift.pre.load_xy_time(panel)
    _,encounters,dyads,inds,esha,_=CO.reconstruct_primary(panel,xy,cfg,receipt)

    records,contract=CO.load_panel_records(panel)
    CO.add_terrain_relative_z(panel,records,contract)
    rr,_,_,_,esha_z,_=CO.reconstruct_primary(panel,records,cfg,receipt)
    if esha_z!=esha:raise RuntimeError("encounter SHA drift")

    lookup=CO.make_record_lookup(rr)
    gd,ga,pa,gb,pb,di,dyad_list=CO.build_phase_groups(rr,lookup,encounters)
    za=CO.observed_endpoint_values(gd,ga,pa)
    zb=CO.observed_endpoint_values(gd,gb,pb)
    _,meds=CO.panel_stat(np.abs(za-zb),di,len(dyad_list))

    out=[]
    for k,d in enumerate(dyad_list):
        out.append({
          "cohort":str(d[0]),"a":str(d[1]),"b":str(d[2]),
          "observed_median_separation_m":float(meds[k]),
          "encounters":int(np.sum(di==k)),
        })
    return out,esha

def geometry_rows(dyads,theta):
    rows=[]
    for d in dyads:
        ka=(d["cohort"],d["a"]);kb=(d["cohort"],d["b"])
        if ka not in theta or kb not in theta:continue
        a=theta[ka];b=theta[kb]
        dp=float(np.linalg.norm(a-b))
        Aa=float((a[0]-a[1])/math.sqrt(2))
        Ab=float((b[0]-b[1])/math.sqrt(2))
        rows.append({**d,"D_policy":dp,"D_alloc":abs(Aa-Ab)})
    return rows

def permute_theta(theta,rng):
    out={}
    byco=collections.defaultdict(list)
    for key in theta:byco[key[0]].append(key)
    for co,keys in byco.items():
        keys=sorted(keys)
        vals=[theta[k] for k in keys]
        p=rng.permutation(len(vals))
        for k,z in zip(keys,p):
            out[k]=vals[int(z)]
    return out

def run(year,panel,seed):
    theta,audit=policy_centroids(panel)
    if theta is None:return {"status":"STOP_POLICY_SUPPORT","audit":audit}
    dyads,esha=frozen_dyads(panel)
    obsrows=geometry_rows(dyads,theta)
    if len(obsrows)<5:
        return {"status":"STOP_DYAD_POLICY_OVERLAP","n_eligible_dyads":len(obsrows)}

    sep=np.asarray([r["observed_median_separation_m"] for r in obsrows],float)
    dpol=np.asarray([r["D_policy"] for r in obsrows],float)
    dall=np.asarray([r["D_alloc"] for r in obsrows],float)
    rho=spearman(dpol,sep)
    rhoA=spearman(dall,sep)
    if not math.isfinite(rho):return {"status":"STOP_PRIMARY_STATISTIC"}

    rng=np.random.default_rng(seed)
    null=[]
    for _ in range(NPERM):
        rr=geometry_rows(dyads,permute_theta(theta,rng))
        # exactly the same dyads should remain after policy permutation
        if len(rr)!=len(obsrows):
            raise RuntimeError("eligible dyad count changed under policy permutation")
        q=spearman([x["D_policy"] for x in rr],[x["observed_median_separation_m"] for x in rr])
        if math.isfinite(q):null.append(q)
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=rho))/(1+len(a))) if len(a) else None
    verdict="POSITIVE_POLICY_DISTANCE_SEPARATION" if (rho>0 and p is not None and p<=.05 and len(a)>=9500) else "NO_POSITIVE_POLICY_DISTANCE_SEPARATION"

    return {
      "status":"DONE" if len(a)>=9500 else "STOP_RANDOMIZATION_SUPPORT",
      "panel":panel,
      "encounter_set_sha256":esha,
      "n_frozen_dyads":len(dyads),
      "n_policy_matched_dyads":len(obsrows),
      "dyads":obsrows,
      "rho_policy_distance_vs_separation":rho,
      "rho_allocation_distance_vs_separation":rhoA,
      "requested_permutations":NPERM,
      "valid_permutations":int(len(a)),
      "seed":seed,
      "null_mean":float(a.mean()) if len(a) else None,
      "null_q025":float(np.quantile(a,.025)) if len(a) else None,
      "null_q975":float(np.quantile(a,.975)) if len(a) else None,
      "p_policy_one_sided":p,
      "P2_excess_separation_status":"STOP_DYAD_NULL_MEANS_NOT_RECOVERED",
      "diagnostic_verdict":verdict,
    }

def main():
    print(json.dumps({
      "contract":"POLICY_DISTANCE_COUSE_SEPARATION_CONTRACT_V1.md",
      "status":"POST_OUTCOME_MECHANISM_DIAGNOSTIC",
      "years":{y:run(y,p,s) for y,(p,s) in PANELS.items()}
    },ensure_ascii=False,indent=2))

if __name__=="__main__":main()
