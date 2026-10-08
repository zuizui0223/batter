#!/usr/bin/env python3
"""Cross-fit peer-calibrated environmental gain on the five-bat FlightIntensity archive."""
from __future__ import annotations
import argparse
import collections
import importlib.util
import json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
NPERM=9999
SEED=20261008131


def read_table(path=None):
    if path:
        j=json.loads(Path(path).read_text(encoding="utf8"))
        if "theta_by_bat" in j:
            return {b:{str(e):float(y) for e,y in d["environment_centroids"].items()}
                    for b,d in j["theta_by_bat"].items()}
        return j
    src=HERE/"flight_intensity_scalar_v1.py"
    spec=importlib.util.spec_from_file_location("source",src)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    rows,_=mod.load_scalar_rows()
    tmp=collections.defaultdict(list)
    for r in rows:
        tmp[(str(r["bat"]),str(r["env"]))].append(float(r["flight_intensity"]))
    return {b:{e:float(np.mean(v)) for (bb,e),v in tmp.items() if b==bb}
            for b in sorted({bb for bb,e in tmp})}


def evaluate(t):
    assert sorted(t)==["A","B","C","D","E"]
    assert sum(len(x) for x in t.values())==25
    envs=sorted({e for d in t.values() for e in d},key=int)
    rows=[]
    for e in envs:
        present=sorted(b for b in t if e in t[b])
        if len(present)<3:
            continue
        for bat in present:
            peers=[j for j in present if j!=bat]
            self_train=[y for ee,y in t[bat].items() if ee!=e]
            self_theta=float(np.mean(self_train))
            peertheta={j:float(np.mean([y for ee,y in t[j].items() if ee!=e])) for j in peers}
            numerator=1.0+sum(peertheta[j]*t[j][e] for j in peers)
            denom=1.0+sum(peertheta[j]**2 for j in peers)
            alpha=float(np.clip(numerator/denom,0.0,2.0))
            y=t[bat][e]
            pred0=self_theta
            pred1=alpha*self_theta
            err0=(y-pred0)**2
            err1=(y-pred1)**2
            rows.append({
                "bat":bat,"environment":e,"n_peers":len(peers),
                "target":float(y),"theta_self_past":self_theta,
                "alpha_from_peers":alpha,"pred_fixed":pred0,"pred_peer_gain":pred1,
                "error_fixed":float(err0),"error_peer_gain":float(err1),
                "gain":float(err0-err1)
            })
    if len(rows)!=23:
        raise RuntimeError(f"expected 23 eligible bat-env targets, got {len(rows)}")
    d={}
    for bat in sorted(t):
        rs=[r for r in rows if r["bat"]==bat]
        d[bat]={
            "n_targets":len(rs),
            "gain":float(np.mean([r["gain"] for r in rs])),
            "mse_fixed":float(np.mean([r["error_fixed"] for r in rs])),
            "mse_peer_gain":float(np.mean([r["error_peer_gain"] for r in rs]))
        }
    G=float(np.mean([v["gain"] for v in d.values()]))
    M0=float(np.mean([v["mse_fixed"] for v in d.values()]))
    M1=float(np.mean([v["mse_peer_gain"] for v in d.values()]))
    return {"n_targets":len(rows),"per_bat":d,"G":G,
            "MSE_fixed":M0,"MSE_peer_gain":M1,
            "relative_mse_reduction":1.0-M1/M0,"targets":rows}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--centroids-json")
    p.add_argument("--out",default="theta_peer_environment_gain_v1.json")
    args=p.parse_args()
    tab=read_table(args.centroids_json)
    a=evaluate(tab)
    bids=sorted(a["per_bat"])
    vals=np.array([a["per_bat"][b]["gain"] for b in bids],float)
    rng=np.random.default_rng(SEED)
    idx=rng.integers(0,len(bids),size=(NPERM,len(bids)))
    bmeans=vals[idx].mean(axis=1)
    lo,hi=np.quantile(bmeans,[.025,.975])
    supported=bool(a["G"]>0 and lo>0 and np.sum(vals>0)>=3)
    result={
        "study":"batter-peer-environment-gain-v1",
        "status":"POST_OUTCOME_MECHANISM_DIAGNOSTIC",
        "observed":a,
        "uncertainty":{
            "bootstrap_B":NPERM,"seed":SEED,
            "ci95_low":float(lo),"ci95_high":float(hi),
            "positive_bats":int(np.sum(vals>0)),
            "descriptive_support":supported
        },
        "claim_ceiling":"Peer-informed test-environment prediction; not entirely past-only, not causal, only 5 bats."
    }
    Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps({"G":a["G"],"MSE_fixed":a["MSE_fixed"],
                     "MSE_peer_gain":a["MSE_peer_gain"],
                     "reduction":a["relative_mse_reduction"],
                     "bootstrap95":[float(lo),float(hi)],
                     "positive_bats":int(np.sum(vals>0)),
                     "per_bat":a["per_bat"],"supported":supported},sort_keys=True))


if __name__=="__main__":
    main()
