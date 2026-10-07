#!/usr/bin/env python3
from __future__ import annotations
import collections, importlib.util, json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("F",HERE/"flight_intensity_scalar_v1.py")
F=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(F)

B=9999
SEED=20261007901

def rows():
    rr,envs=F.load_scalar_rows()
    return rr,envs

def target_records(rr,envs):
    out=[]
    bats=sorted(set(r["bat"] for r in rr))
    for i,t in enumerate(rr):
        b=t["bat"]; e=t["env"]; y=float(t["flight_intensity"])
        other_env=[]
        for ee in envs:
            if ee==e: continue
            vals=[float(r["flight_intensity"]) for r in rr if r["bat"]==b and r["env"]==ee]
            if vals: other_env.append(float(np.mean(vals)))
        same=[float(r["flight_intensity"]) for j,r in enumerate(rr)
              if j!=i and r["bat"]==b and r["env"]==e]
        if len(other_env)<2 or len(same)<1:
            continue
        th=float(np.mean(other_env))
        cc=float(np.mean(same))
        e0=y*y
        et=(y-th)**2
        ec=(y-cc)**2
        out.append({
            "bat":b,"env":int(e),"target_index":i,"y":y,
            "theta_pred":th,"context_pred":cc,
            "E0":e0,"Etheta":et,"Econtext":ec,
            "Gtheta":e0-et,
            "Gh":et-ec,
            "Gtotal":e0-ec
        })
    return out

def aggregate(records, sampled_bats=None):
    bats=sorted(set(r["bat"] for r in records))
    if sampled_bats is None: sampled_bats=bats
    inst=[]
    perbat={}
    for b in bats:
        br=[r for r in records if r["bat"]==b]
        envvals=[]
        for e in sorted(set(r["env"] for r in br)):
            er=[r for r in br if r["env"]==e]
            envvals.append({
                "Gtheta":float(np.mean([r["Gtheta"] for r in er])),
                "Gh":float(np.mean([r["Gh"] for r in er])),
                "Gtotal":float(np.mean([r["Gtotal"] for r in er])),
                "n_targets":len(er)
            })
        if envvals:
            perbat[b]={
                "n_environments":len(envvals),
                "n_targets":len(br),
                "Gtheta":float(np.mean([x["Gtheta"] for x in envvals])),
                "Gh":float(np.mean([x["Gh"] for x in envvals])),
                "Gtotal":float(np.mean([x["Gtotal"] for x in envvals]))
            }
    for b in sampled_bats:
        if b in perbat: inst.append(perbat[b])
    if not inst: raise RuntimeError("no support")
    return {
        "Gtheta":float(np.mean([x["Gtheta"] for x in inst])),
        "Gh":float(np.mean([x["Gh"] for x in inst])),
        "Gtotal":float(np.mean([x["Gtotal"] for x in inst])),
        "per_bat":perbat
    }

def bootstrap(records):
    bats=sorted(set(r["bat"] for r in records))
    obs=aggregate(records,bats)
    rng=np.random.default_rng(SEED)
    vals={k:[] for k in ["Gtheta","Gh","Gtotal"]}
    for _ in range(B):
        samp=list(rng.choice(np.asarray(bats,dtype=object),size=len(bats),replace=True))
        q=aggregate(records,samp)
        for k in vals: vals[k].append(q[k])
    ci={}
    for k,a0 in vals.items():
        a=np.asarray(a0,float)
        ci[k]={
            "mean":obs[k],
            "ci95_low":float(np.quantile(a,.025)),
            "ci95_high":float(np.quantile(a,.975)),
            "supported":bool(obs[k]>0 and np.quantile(a,.025)>0)
        }
    return obs,ci

def descriptive_theta(rr,envs):
    out={}
    for b in sorted(set(r["bat"] for r in rr)):
        cents=[]
        for e in envs:
            vals=[float(r["flight_intensity"]) for r in rr if r["bat"]==b and r["env"]==e]
            if vals:cents.append(float(np.mean(vals)))
        out[b]={
            "theta_full":float(np.mean(cents)),
            "between_environment_sd":float(np.std(cents,ddof=1)) if len(cents)>1 else None,
            "n_environments_total":len(cents)
        }
    return out

def main():
    rr,envs=rows()
    if len(rr)!=45:raise RuntimeError(f"trajectory drift {len(rr)}")
    rec=target_records(rr,envs)
    bats=sorted(set(r["bat"] for r in rec))
    if len(bats)<3:raise RuntimeError(f"insufficient bats {bats}")
    obs,ci=bootstrap(rec)
    d=descriptive_theta(rr,envs)
    per=obs["per_bat"]
    for b in per:
        per[b].update(d[b])
    raw={
        k:float(np.mean([r[k] for r in rec]))
        for k in ["Gtheta","Gh","Gtotal"]
    }
    identity=max(abs(r["Gtotal"]-(r["Gtheta"]+r["Gh"])) for r in rec) if rec else None
    out={
        "status":"POST_PRIMARY_MECHANISM_DIAGNOSTIC",
        "contract":"THETA_CONTEXT_DECOMPOSITION_CONTRACT_V1.md",
        "species":"Rhinolophus nippon",
        "n_eligible_targets":len(rec),
        "eligible_bats":bats,
        "equal_bat":{k:obs[k] for k in ["Gtheta","Gh","Gtotal"]},
        "bootstrap":ci,
        "raw_target_weighted":raw,
        "per_bat":per,
        "max_additive_identity_error":identity,
        "target_records":rec
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
