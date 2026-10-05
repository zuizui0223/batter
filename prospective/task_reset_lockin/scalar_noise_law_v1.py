#!/usr/bin/env python3
"""Scalar-noise law diagnostics for the Rhino one-parameter FlightIntensity model."""
from __future__ import annotations

import importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent

spec=importlib.util.spec_from_file_location("C",HERE/"one_parameter_calibration_v1.py")
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)

spec2=importlib.util.spec_from_file_location("F",HERE/"flight_intensity_scalar_v1.py")
F=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(F)

NPERM=9999
SEED_R2=202610050901
SEED_M=202610050902
SEED_G=202610050903
MIN_VALID=9500

def points_from_cal(q):
    return [(float(d["predicted_difference"]),float(d["observed_difference"])) for d in q["points"]]

def r2_stats(q):
    pts=points_from_cal(q)
    x=np.asarray([a for a,b in pts],float)
    y=np.asarray([b for a,b in pts],float)
    den=float(np.sum(y*y))
    if not (den>0 and np.all(np.isfinite(x)) and np.all(np.isfinite(y))):
        return None
    err=y-x
    return {
      "R2_zero":float(1.0-np.sum(err*err)/den),
      "RMSE":float(np.sqrt(np.mean(err*err))),
      "MAE":float(np.mean(np.abs(err))),
      "n":int(len(x)),
    }

def margin_stats(q):
    vals=[]
    for d in q["points"]:
        x=float(d["predicted_difference"]);y=float(d["observed_difference"])
        if x==0 or y==0:continue
        vals.append((abs(x), 1 if math.copysign(1,x)==math.copysign(1,y) else 0))
    if not vals:return None
    correct=[m for m,c in vals if c==1]
    errors=[m for m,c in vals if c==0]
    if not correct or not errors:return None
    margins=np.asarray([m for m,c in vals],float)
    q25=float(np.quantile(margins,.25));q50=float(np.quantile(margins,.50))
    errm=np.asarray(errors,float)
    return {
      "M_mean_margin_correct_minus_error":float(np.mean(correct)-np.mean(errors)),
      "mean_margin_correct":float(np.mean(correct)),
      "mean_margin_error":float(np.mean(errors)),
      "median_margin_correct":float(np.median(correct)),
      "median_margin_error":float(np.median(errors)),
      "n_correct":len(correct),"n_errors":len(errors),
      "error_fraction_lowest_half":float(np.mean(errm<=q50)),
      "error_fraction_lowest_quartile":float(np.mean(errm<=q25)),
      "margin_q25":q25,"margin_q50":q50,
    }

def logistic_gamma(q):
    vals=[]
    for d in q["points"]:
        x=float(d["predicted_difference"]);y=float(d["observed_difference"])
        if x==0 or y==0:continue
        vals.append((abs(x), 1.0 if math.copysign(1,x)==math.copysign(1,y) else 0.0))
    if len(vals)<5:return None
    X=np.column_stack([np.ones(len(vals)),np.asarray([m for m,c in vals],float)])
    y=np.asarray([c for m,c in vals],float)
    if len(np.unique(y))<2:return None
    beta=np.zeros(2,float)
    for _ in range(100):
        eta=X@beta
        eta=np.clip(eta,-30,30)
        p=1/(1+np.exp(-eta))
        w=p*(1-p)
        if np.any(w<=1e-12): w=np.maximum(w,1e-12)
        g=X.T@(y-p)
        H=X.T@(w[:,None]*X)
        try:step=np.linalg.solve(H,g)
        except np.linalg.LinAlgError:return None
        beta_new=beta+step
        if not np.all(np.isfinite(beta_new)):return None
        if np.max(np.abs(step))<1e-10:
            beta=beta_new;break
        beta=beta_new
    else:
        return None
    margins=np.asarray([m for m,c in vals],float)
    qs=np.quantile(margins,[.25,.5,.75])
    pred={}
    for lab,m in zip(["q25","q50","q75"],qs):
        z=float(beta[0]+beta[1]*m)
        pred[lab]={"margin":float(m),"Pr_correct":float(1/(1+math.exp(-max(-30,min(30,z)))))}
    return {"alpha":float(beta[0]),"gamma":float(beta[1]),"predicted_correctness":pred,"n":len(vals)}

def setup():
    rows,envs=F.load_scalar_rows()
    cm=C.cluster_centroids(rows,envs)
    ls=F.labelsets(rows,envs)
    obsmap=F.observed_mapping(rows,envs)
    obs=C.calibration(cm,envs,obsmap)
    if obs is None:raise RuntimeError("observed calibration failed")
    return cm,envs,ls,obs

def perm_null(cm,envs,ls,seed,which):
    rng=np.random.default_rng(seed)
    vals=[]
    for _ in range(NPERM):
        mp=F.perm_mapping(ls,rng)
        q=C.calibration(cm,envs,mp)
        if q is None:continue
        if which=="r2":
            s=r2_stats(q);v=None if s is None else s["R2_zero"]
        elif which=="margin":
            s=margin_stats(q);v=None if s is None else s["M_mean_margin_correct_minus_error"]
        elif which=="gamma":
            s=logistic_gamma(q);v=None if s is None else s["gamma"]
        else:raise ValueError(which)
        if v is not None and math.isfinite(v):vals.append(v)
    return np.asarray(vals,float)

def main():
    cm,envs,ls,obscal=setup()
    R=r2_stats(obscal);M=margin_stats(obscal);G=logistic_gamma(obscal)
    if R is None or M is None or G is None:raise RuntimeError("observed scalar-noise support failed")

    nr=perm_null(cm,envs,ls,SEED_R2,"r2")
    nm=perm_null(cm,envs,ls,SEED_M,"margin")
    ng=perm_null(cm,envs,ls,SEED_G,"gamma")
    if len(nr)<MIN_VALID or len(nm)<MIN_VALID or len(ng)<MIN_VALID:
        verdict="STOP_RANDOMIZATION_SUPPORT"
    else:
        verdict="DONE"

    def cal(v,null):
        return {
          "valid_permutations":int(len(null)),
          "null_mean":float(np.mean(null)),
          "null_q025":float(np.quantile(null,.025)),
          "null_q975":float(np.quantile(null,.975)),
          "p_one_sided":float((1+np.sum(null>=v))/(1+len(null))),
        }

    out={
      "contract":"SCALAR_NOISE_LAW_CONTRACT_V1.md",
      "status":"POST_PRIMARY_MATHEMATICAL_STRUCTURE_DIAGNOSTIC",
      "species":"Rhinolophus nippon",
      "N1_no_refit_predictive_R2":{**R,**cal(R["R2_zero"],nr)},
      "N2_margin_error_concentration":{**M,**cal(M["M_mean_margin_correct_minus_error"],nm)},
      "N3_logistic_margin_confidence":{**G,**cal(G["gamma"],ng)},
      "requested_permutations":NPERM,
      "seeds":{"R2":SEED_R2,"margin":SEED_M,"gamma":SEED_G},
      "diagnostic_status":verdict,
    }
    if verdict=="DONE":
        out["diagnostic_verdict"]=(
          "SUPPORTED_SCALAR_PLUS_NOISE_LAW"
          if R["R2_zero"]>0
          and out["N1_no_refit_predictive_R2"]["p_one_sided"]<=.05
          and M["M_mean_margin_correct_minus_error"]>0
          and out["N2_margin_error_concentration"]["p_one_sided"]<=.05
          and G["gamma"]>0
          and out["N3_logistic_margin_confidence"]["p_one_sided"]<=.05
          else "PARTIAL_OR_UNSUPPORTED_SCALAR_PLUS_NOISE_LAW"
        )
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
