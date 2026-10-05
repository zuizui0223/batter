#!/usr/bin/env python3
"""Leave-one-individual max-stat robustness for policy distance vs co-use separation."""
from __future__ import annotations
import importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"policy_distance_couse_separation_receipt_v2.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)

NPERM=9999
MIN_VALID=9500
SEEDS={"2022":202610052201,"2023":202610052202}

def deletion_profile(dyads,theta):
    base=P.geometry_rows(dyads,theta)
    nodes=sorted({(r["cohort"],r["a"]) for r in base}|{(r["cohort"],r["b"]) for r in base})
    rows=[]
    for co,iid in nodes:
        q=[r for r in base if not (r["cohort"]==co and (r["a"]==iid or r["b"]==iid))]
        if len(q)<5:continue
        rho=P.spearman([r["D_policy"] for r in q],[r["observed_median_separation_m"] for r in q])
        if math.isfinite(rho):
            rows.append({"deleted":f"{co}::{iid}","n_dyads":len(q),"rho":float(rho)})
    return rows

def run(year,panel):
    theta,audit=P.policy_centroids(panel)
    if theta is None:return {"status":"STOP_POLICY_SUPPORT","audit":audit}
    dyads,esha=P.frozen_dyads(panel)
    prof=deletion_profile(dyads,theta)
    if not prof:return {"status":"STOP_LOO_SUPPORT"}
    vals=np.asarray([x["rho"] for x in prof],float)
    tmax=float(vals.max())
    winner=prof[int(np.argmax(vals))]["deleted"]

    rng=np.random.default_rng(SEEDS[year]);null=[]
    for _ in range(NPERM):
        pp=deletion_profile(dyads,P.permute_theta(theta,rng))
        if not pp:continue
        v=[x["rho"] for x in pp if math.isfinite(x["rho"])]
        if v:null.append(max(v))
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=tmax))/(1+len(a))) if len(a) else None
    return {
      "status":"DONE" if len(a)>=MIN_VALID else "STOP_RANDOMIZATION_SUPPORT",
      "panel":panel,"encounter_set_sha256":esha,
      "deletion_profile":prof,
      "n_admissible_deletions":len(prof),
      "rho_min":float(vals.min()),"rho_median":float(np.median(vals)),"rho_max":tmax,
      "fraction_positive":float(np.mean(vals>0)),
      "fraction_ge_0_3":float(np.mean(vals>=0.3)),
      "maximizing_deletion":winner,
      "requested_permutations":NPERM,"valid_permutations":int(len(a)),
      "seed":SEEDS[year],
      "null_max_mean":float(a.mean()) if len(a) else None,
      "null_max_q025":float(np.quantile(a,.025)) if len(a) else None,
      "null_max_q975":float(np.quantile(a,.975)) if len(a) else None,
      "p_max_one_sided":p,
      "diagnostic_verdict":"LOO_POSITIVE_COUPLING_RESCUE" if (len(a)>=MIN_VALID and p is not None and p<=.05 and tmax>0) else "NO_ONE_INDIVIDUAL_DELETION_RESCUE"
    }

def main():
    print(json.dumps({
      "contract":"POLICY_DISTANCE_COUSE_LOO_CONTRACT_V1.md",
      "status":"POST_OUTCOME_NODE_DELETION_ROBUSTNESS",
      "years":{y:run(y,panel) for y,(panel,_) in P.PANELS.items()}
    },indent=2))

if __name__=="__main__":main()
