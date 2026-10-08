#!/usr/bin/env python3
"""Post-outcome audit: algebraic subset-MSE identity and genuine cross-environment correspondence test."""
from __future__ import annotations

import argparse
import collections
import importlib.util
import itertools
import json
import math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
SOURCE=HERE/"flight_intensity_scalar_v1.py"
NPERM=19999
SEED=20261008111
BOOT=9999
BOOT_SEED=20261008112


def centroids_from_source():
    spec=importlib.util.spec_from_file_location("F",SOURCE)
    f=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(f)
    rows,_=f.load_scalar_rows()
    grouping=collections.defaultdict(list)
    for row in rows:
        grouping[(str(row["bat"]),str(row["env"]))].append(float(row["flight_intensity"]))
    return {b:{e:float(np.mean(vals)) for (bi,e),vals in grouping.items() if bi==b}
            for b in sorted({bi for bi,e in grouping})}


def centroids_from_json(path):
    j=json.loads(Path(path).read_text(encoding="utf-8"))
    if "theta_by_bat" in j:
        return {bat:{str(e):float(y) for e,y in d["environment_centroids"].items()}
                for bat,d in j["theta_by_bat"].items()}
    return {bat:{str(e):float(y) for e,y in d.items()} for bat,d in j.items()}


def assert_structure(table):
    if sorted(table)!=["A","B","C","D","E"]:
        raise RuntimeError("Expected exactly original A-E bats")
    if sum(len(e) for e in table.values())!=25:
        raise RuntimeError("Expected exactly 25 bat x configuration centroids")
    expected={"A":5,"B":4,"C":5,"D":6,"E":5}
    if {b:len(x) for b,x in table.items()}!=expected:
        raise RuntimeError("Unexpected environment counts")
    envs=sorted(set(e for vals in table.values() for e in vals),key=int)
    if envs!=[str(e) for e in range(1,8)]:
        raise RuntimeError("Unexpected environment set")


def compute(table):
    means=[]
    for bat,obs in sorted(table.items()):
        zero=[];personal=[];gain=[]
        for e,y in obs.items():
            x=[v for ee,v in obs.items() if ee!=e]
            if len(x)<3:
                raise RuntimeError("Insufficient history in target")
            prediction=float(np.mean(x))
            z=float(y*y);p=float((y-prediction)**2)
            zero.append(z);personal.append(p);gain.append(z-p)
        mean0=float(np.mean(zero)); meanp=float(np.mean(personal))
        means.append({
            "bat":bat,"mse_zero":mean0,"mse_personal":meanp,
            "gain":float(np.mean(gain)),
            "r2_vs_zero":float(1-meanp/mean0),
            "target_count":len(obs)
        })
    G=float(np.mean([x["gain"] for x in means]))
    baseline=float(np.mean([x["mse_zero"] for x in means]))
    mse=float(np.mean([x["mse_personal"] for x in means]))
    return {"G":G,"MSE_zero":baseline,"MSE_personal":mse,
            "R2_vs_zero":1-mse/baseline,
            "per_bat":{x["bat"]:x for x in means}}


def subset_algebra_error(table):
    errs=[];example={}
    for b,obs in table.items():
        for e,y in obs.items():
            tr=np.asarray([v for ee,v in obs.items() if ee!=e],float)
            N=len(tr);full=float((y-np.mean(tr))**2)
            s2=float(np.var(tr,ddof=1))
            for m in (1,2,3):
                brute=float(np.mean([
                    (y-float(np.mean(ss)))**2 for ss in itertools.combinations(tr,m)
                ]))
                forced=full+(N-m)/(N*m)*s2
                errs.append(abs(brute-forced))
            example[b]={"n_obs_envs":len(obs),
                        "forced_fraction_to_full_at_3":1-(N-3)/(3*(N-1))}
    err=max(errs)
    if err>1e-10:raise RuntimeError(f"Subset algebra mismatch: {err}")
    return {"max_abs_identity_error":err,"fractions_only_from_counts":example}


def permute_within_environment(table,rng):
    perm={b:dict(obs) for b,obs in table.items()}
    envs=sorted({e for obs in table.values() for e in obs},key=int)
    for e in envs:
        members=sorted(b for b in table if e in table[b])
        ys=[table[b][e] for b in members]
        order=rng.permutation(len(ys))
        for idx,b in enumerate(members):
            perm[b][e]=float(ys[int(order[idx])])
    return perm


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--centroids-json",default=None)
    parser.add_argument("--out",default="theta_correspondence_audit_result_v1.json")
    args=parser.parse_args()
    table=(centroids_from_json(args.centroids_json) if args.centroids_json
           else centroids_from_source())
    assert_structure(table)
    alg=subset_algebra_error(table)
    observed=compute(table)
    rng=np.random.default_rng(SEED)
    null=np.empty(NPERM,float)
    for k in range(NPERM):
        null[k]=compute(permute_within_environment(table,rng))["G"]
    perm_p=float((1+np.count_nonzero(null>=observed["G"]-1e-15))/(NPERM+1))
    bats=sorted(table)
    rboot=np.random.default_rng(BOOT_SEED)
    own=np.asarray([observed["per_bat"][b]["gain"] for b in bats])
    draws=rboot.integers(0,len(bats),size=(BOOT,len(bats)))
    boot=np.mean(own[draws],axis=1)
    jack={bat:float(np.mean([observed["per_bat"][bb]["gain"] for bb in bats if bb!=bat]))
          for bat in bats}
    out={
        "status":"POST_OUTCOME_DIAGNOSTIC_NOT_INDEPENDENT_CONFIRMATION",
        "parent_flight_scalar_source":"rhino-flight-intensity-theta-summary-v1",
        "primary":"equal-bat held-out MSE gain over zero",
        "observed":observed,
        "algebra_audit":alg,
        "permutation":{
            "B":NPERM,"seed":SEED,
            "null_mean":float(null.mean()),
            "null_ci95":[float(np.quantile(null,.025)),float(np.quantile(null,.975))],
            "p_one_sided":perm_p,
            "supported":bool(observed["G"]>0 and perm_p<=.05)
        },
        "bat_cluster_bootstrap":{
            "B":BOOT,"seed":BOOT_SEED,
            "ci95":[float(np.quantile(boot,.025)),float(np.quantile(boot,.975))]
        },
        "leave_one_bat_out_programme_gains":jack
    }
    Path(args.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "observed_G":observed["G"],
        "R2":observed["R2_vs_zero"],
        "per_bat":{b:{"gain":d["gain"],"R2":d["r2_vs_zero"]}
                   for b,d in observed["per_bat"].items()},
        "permutation":out["permutation"],
        "bootstrap95":out["bat_cluster_bootstrap"]["ci95"],
        "algebra_max_error":alg["max_abs_identity_error"]
    },sort_keys=True))


if __name__=="__main__":
    main()
