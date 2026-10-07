#!/usr/bin/env python3
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"rhino_configuration_identity_primary_v1.py")
P=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(P)

NPERM=9999
SEED=20261007921

def env_structure(traj):
    rt=[r for r in traj if r["route_valid"]]
    envs=sorted(set(r["env"] for r in rt))
    eligible=[]
    data={}
    for e in envs:
        rr=[r for r in rt if r["env"]==e]
        counts=collections.Counter(r["bat"] for r in rr)
        repeated=sorted([b for b,n in counts.items() if n>=2])
        if len(repeated)>=3:
            eligible.append(e)
        data[e]={"rr":rr,"counts":counts,"repeated":repeated}
    if eligible!=[1,2,3]:
        raise RuntimeError(f"eligible env drift: {eligible}")
    return data,eligible

def route_error(y,p):
    return float(np.mean(np.linalg.norm(np.asarray(y)-np.asarray(p),axis=1)))

def predict_target(rr,labels,idx):
    lab=labels[idx]
    self_idx=[j for j,x in enumerate(labels) if x==lab and j!=idx]
    if not self_idx:
        return None
    donor_labels=sorted(set(labels)-{lab})
    if len(donor_labels)<2:
        return None

    donor_means=[]
    donor_centered=[]
    for dl in donor_labels:
        js=[j for j,x in enumerate(labels) if x==dl]
        if not js: continue
        R=np.mean(np.stack([rr[j]["route101"] for j in js]),axis=0)
        donor_means.append(R)
        donor_centered.append(R-np.mean(R,axis=0,keepdims=True))
    if len(donor_means)<2:
        return None

    m0=np.mean(np.stack(donor_means),axis=0)
    shape=np.mean(np.stack(donor_centered),axis=0)

    self_cent=np.mean(np.vstack([
        np.mean(np.asarray(rr[j]["route101"]),axis=0) for j in self_idx
    ]),axis=0)
    m1=shape+self_cent.reshape(1,3)

    m2=np.mean(np.stack([rr[j]["route101"] for j in self_idx]),axis=0)
    y=np.asarray(rr[idx]["route101"])
    return route_error(y,m0),route_error(y,m1),route_error(y,m2)

def aggregate(data,eligible,label_maps):
    env_out={}
    bat_env=collections.defaultdict(dict)
    target_rows=[]
    for e in eligible:
        rr=data[e]["rr"]
        labels=label_maps[e]
        perbat=collections.defaultdict(list)
        for i,lab in enumerate(labels):
            # Under a fixed-count label permutation, target labels are exactly repeated labels.
            if labels.count(lab)<2:
                continue
            q=predict_target(rr,labels,i)
            if q is None: continue
            e0,e1,e2=q
            perbat[lab].append((e0,e1,e2))
            target_rows.append({"env":e,"bat":lab,"name":rr[i]["name"],"E0":e0,"E1":e1,"E2":e2})
        if not perbat:
            return None
        bm={}
        for b,vals in perbat.items():
            A=np.asarray(vals,float)
            bm[b]=A.mean(axis=0)
            bat_env[(e,b)]={"E0":float(A[:,0].mean()),"E1":float(A[:,1].mean()),"E2":float(A[:,2].mean())}
        M=np.vstack(list(bm.values()))
        env_out[e]=M.mean(axis=0)

    if len(env_out)!=len(eligible):
        return None
    E=np.vstack([env_out[e] for e in eligible]).mean(axis=0)
    E0,E1,E2=[float(x) for x in E]
    Ic=E0-E1
    If=E0-E2
    Is=E1-E2
    Rc=Ic/If if If>0 else None
    return {
      "E0":E0,"E1":E1,"E2":E2,
      "centroid_gain":Ic,"full_gain":If,"extra_shape_gain":Is,
      "centroid_retention":Rc,
      "environment_errors":{str(e):{"E0":float(env_out[e][0]),"E1":float(env_out[e][1]),"E2":float(env_out[e][2])} for e in eligible},
      "bat_environment_errors":{f"{e}:{b}":v for (e,b),v in sorted(bat_env.items())},
      "target_rows":target_rows
    }

def main():
    traj=P.load_rhino()
    data,eligible=env_structure(traj)
    observed={e:[r["bat"] for r in data[e]["rr"]] for e in eligible}
    obs=aggregate(data,eligible,observed)
    if obs is None: raise RuntimeError("observed support failed")

    rng=np.random.default_rng(SEED)
    null=[]
    for _ in range(NPERM):
        maps={e:list(rng.permutation(np.asarray(observed[e],dtype=object))) for e in eligible}
        q=aggregate(data,eligible,maps)
        if q is None: raise RuntimeError("permutation support failed")
        null.append(q["centroid_gain"])
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs["centroid_gain"]-1e-15))/(NPERM+1))

    If=obs["full_gain"]; Is=obs["extra_shape_gain"]; Rc=obs["centroid_retention"]
    compress=bool(
      obs["centroid_gain"]>0 and If>0 and Rc is not None and Rc>=.80 and Is<=.20*If
    )
    out={
      "contract":"ROUTE_CENTROID_COMPRESSION_CONTRACT_V1.md",
      "status":"POST_PRIMARY_COMPRESSION_DIAGNOSTIC",
      "species":"Rhinolophus nippon",
      "eligible_environments":eligible,
      "observed":obs,
      "permutation":{
        "n":NPERM,"seed":SEED,"null_mean":float(a.mean()),
        "null_q025":float(np.quantile(a,.025)),"null_q975":float(np.quantile(a,.975)),
        "p_centroid_gain_one_sided":p
      },
      "centroid_compressible":compress,
      "interpretation":"THREE_PARAMETER_TASK_SPECIFIC_ROUTE_COMPRESSION" if compress else "ADDITIONAL_PERSONAL_ROUTE_SHAPE_REQUIRED"
    }
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
