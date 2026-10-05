#!/usr/bin/env python3
"""Horizontal–vertical individual policy coupling in fixed-bin P. hastatus data."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("B",HERE/"phyllostomus_fixed_bin_harmonization_v2.py")
B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)

NPERM=9999
SEEDS={"2022":202610051451,"2023":202610051452}
PANELS={"2022":"phyllostomus_2022","2023":"phyllostomus_2023"}

def component_rows(panel):
    rows,audit=B.prepare(panel)
    if len(rows)==0 or not audit["colony_retention_pass"]:
        return None,audit
    h=B.standardize(rows,"F2_raw","H")
    v=B.standardize(rows,"F3_raw","V")
    if h is None or v is None:
        return None,audit
    # Preserve exact row identity/order from the same frozen session set.
    hv=[]
    for rh,rv in zip(h,v):
        if (rh["cohort"],rh["session"],rh["iid"])!=(rv["cohort"],rv["session"],rv["iid"]):
            raise RuntimeError("H/V session alignment drift")
        q=dict(rh);q["V"]=float(rv["V"]);hv.append(q)
    return hv,audit

def individual_coords(rows):
    d=collections.defaultdict(lambda:{"H":[],"V":[]})
    for r in rows:
        k=(r["cohort"],r["iid"])
        d[k]["H"].append(float(r["H"]));d[k]["V"].append(float(r["V"]))
    out=[]
    for (co,iid),v in sorted(d.items()):
        if len(v["H"])<2:continue
        out.append({"cohort":co,"iid":iid,"theta_H":float(np.mean(v["H"])),
                    "theta_V":float(np.mean(v["V"])),"n_sessions":len(v["H"])})
    return out

def covariance_summary(coords, perm=None):
    cohorts=sorted(set(x["cohort"] for x in coords))
    covs=[];counts={}
    for co in cohorts:
        rr=[x for x in coords if x["cohort"]==co]
        if len(rr)<3:continue
        H=np.asarray([x["theta_H"] for x in rr],float)
        V=np.asarray([x["theta_V"] for x in rr],float)
        if perm is not None:
            V=np.asarray([perm[(co,x["iid"])] for x in rr],float)
        X=np.column_stack([H-H.mean(),V-V.mean()])
        C=np.cov(X,rowvar=False,ddof=1)
        if np.all(np.isfinite(C)):
            covs.append(C);counts[co]=len(rr)
    if not covs:return None
    C=np.mean(np.stack(covs),axis=0)
    if C[0,0]<=0 or C[1,1]<=0:return None
    r=float(C[0,1]/math.sqrt(C[0,0]*C[1,1]))
    w,V=np.linalg.eigh(C)
    order=np.argsort(w)[::-1];w=w[order];V=V[:,order]
    v=V[:,0]
    if v[0]<0:v=-v
    fi=np.array([1.0,1.0])/math.sqrt(2)
    cos=float(np.dot(v,fi)/(np.linalg.norm(v)*np.linalg.norm(fi)))
    angle=float(math.degrees(math.atan2(v[1],v[0])))
    return {
      "covariance":C.tolist(),
      "r_HV":r,
      "eigenvalues":w.tolist(),
      "pc1_variance_fraction":float(w[0]/w.sum()),
      "pc1_vector":v.tolist(),
      "cosine_pc1_to_FlightIntensity":cos,
      "pc1_angle_deg_from_H":angle,
      "cohort_individual_counts":counts,
    }

def null(coords,seed):
    rng=np.random.default_rng(seed)
    byco=collections.defaultdict(list)
    for x in coords:byco[x["cohort"]].append(x)
    vals=[]
    for _ in range(NPERM):
        p={}
        for co,rr in byco.items():
            vv=np.asarray([x["theta_V"] for x in rr],float)
            rng.shuffle(vv)
            for x,v in zip(rr,vv):p[(co,x["iid"])]=float(v)
        s=covariance_summary(coords,p)
        if s is not None and math.isfinite(s["r_HV"]):vals.append(s["r_HV"])
    return np.asarray(vals,float)

def run(year,panel):
    rows,audit=component_rows(panel)
    if rows is None:return {"status":"STOP_SUPPORT","audit":audit}
    coords=individual_coords(rows)
    obs=covariance_summary(coords)
    if obs is None:return {"status":"STOP_COVARIANCE","n_individuals":len(coords)}
    nul=null(coords,SEEDS[year])
    return {
      "status":"DONE","n_sessions":len(rows),"n_individuals":len(coords),
      "individual_coordinates":coords,
      "observed":obs,
      "valid_permutations":int(len(nul)),
      "seed":SEEDS[year],
      "null_mean_r":float(nul.mean()),
      "null_q025_r":float(np.quantile(nul,.025)),
      "null_q975_r":float(np.quantile(nul,.975)),
      "p_positive_r":float((1+np.sum(nul>=obs["r_HV"]))/(1+len(nul))),
    }

def main():
    y={yr:run(yr,p) for yr,p in PANELS.items()}
    contrast=None
    if all(y[k].get("status")=="DONE" for k in ("2022","2023")):
        a=y["2022"]["observed"];b=y["2023"]["observed"]
        contrast={
          "delta_r_2022_minus_2023":a["r_HV"]-b["r_HV"],
          "delta_cosine_to_I_2022_minus_2023":a["cosine_pc1_to_FlightIntensity"]-b["cosine_pc1_to_FlightIntensity"],
          "pc1_angle_change_2023_minus_2022_deg":b["pc1_angle_deg_from_H"]-a["pc1_angle_deg_from_H"],
        }
    print(json.dumps({
      "contract":"HORIZONTAL_VERTICAL_POLICY_COUPLING_CONTRACT_V1.md",
      "status":"POST_OUTCOME_MECHANISM_DIAGNOSTIC",
      "years":y,"year_contrast":contrast
    },ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
