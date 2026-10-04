#!/usr/bin/env python3
"""Post-primary absolute-position diagnostics for Rhino Primary A."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"rhino_configuration_identity_primary_v1.py")
P=importlib.util.module_from_spec(spec); spec.loader.exec_module(P)

NPERM=9999
ENVS=[1,2,3]

def vec_stat(traj, extractor, seed, zscore=False):
    rt=[r for r in traj if r["route_valid"] and r["env"] in ENVS]
    env_info={}
    D={}
    for e in ENVS:
        rr=[r for r in rt if r["env"]==e]
        labels=[r["bat"] for r in rr]
        vec=np.vstack([extractor(r["route101"]) for r in rr]).astype(float)
        if zscore:
            mu=vec.mean(axis=0)
            sd=vec.std(axis=0,ddof=1)
            if np.any(~np.isfinite(sd)) or np.any(sd<=0):
                raise RuntimeError(f"nonfinite/zero SD env={e}")
            vec=(vec-mu)/sd
        n=len(rr); dm=np.zeros((n,n),dtype=float)
        for i in range(n):
            for j in range(i+1,n):
                d=float(np.linalg.norm(vec[i]-vec[j]))
                dm[i,j]=dm[j,i]=d
        env_info[e]={"rr":rr,"labels":labels,"D":dm}

    def calc(label_maps):
        envmeans=[]; bat_env=collections.defaultdict(list)
        for e in ENVS:
            rr=env_info[e]["rr"]; labs=label_maps[e]; dm=env_info[e]["D"]
            cnt=collections.Counter(labs)
            targets=sorted([b for b,n in cnt.items() if n>=2])
            per=collections.defaultdict(list)
            for i,b in enumerate(labs):
                if b not in targets: continue
                selfidx=[j for j,x in enumerate(labs) if x==b and j!=i]
                donors=sorted(set(labs)-{b})
                if not selfidx or not donors: continue
                ds=float(np.mean([dm[i,j] for j in selfidx]))
                dom=[]
                for db in donors:
                    idx=[j for j,x in enumerate(labs) if x==db]
                    if idx: dom.append(float(np.mean([dm[i,j] for j in idx])))
                if dom: per[b].append(float(np.mean(dom)-ds))
            bm={b:float(np.mean(v)) for b,v in per.items() if v}
            if not bm:return None
            envmeans.append(float(np.mean(list(bm.values()))))
            for b,v in bm.items():bat_env[b].append(v)
        return float(np.mean(envmeans)),{b:float(np.mean(v)) for b,v in bat_env.items()}

    obs_labels={e:list(env_info[e]["labels"]) for e in ENVS}
    obs=calc(obs_labels)
    if obs is None: raise RuntimeError("observed support fail")
    stat,bm=obs
    rng=np.random.default_rng(seed)
    null=np.empty(NPERM,float)
    for k in range(NPERM):
        mp={}
        for e in ENVS:
            labs=np.array(obs_labels[e],dtype=object)
            mp[e]=list(rng.permutation(labs))
        q=calc(mp)
        if q is None: raise RuntimeError("permutation support fail")
        null[k]=q[0]
    p=float((1+np.sum(null>=stat))/(1+NPERM))
    return {
      "statistic":stat,
      "bat_means":bm,
      "positive_bats":sum(v>0 for v in bm.values()),
      "n_bats":len(bm),
      "positive_fraction":sum(v>0 for v in bm.values())/len(bm),
      "permutations":NPERM,"seed":seed,
      "null_mean":float(np.mean(null)),
      "null_q025":float(np.quantile(null,.025)),
      "null_q975":float(np.quantile(null,.975)),
      "p_one_sided":p,
    }

def main():
    traj=P.load_rhino()
    out={
      "contract":"POST_PRIMARY_ABSOLUTE_POSITION_CONTRACT_V1.md",
      "status":"POST_PRIMARY_DIAGNOSTIC_NOT_CONFIRMATORY",
      "species":"Rhinolophus nippon",
      "S1_start_position":vec_stat(traj,lambda r:r[0],202610042221),
      "S2_end_position":vec_stat(traj,lambda r:r[-1],202610042222),
      "S3_displacement_vector":vec_stat(traj,lambda r:r[-1]-r[0],202610042223),
      "S4_start_end_joint_zscored":vec_stat(traj,lambda r:np.concatenate([r[0],r[-1]]),202610042224,True),
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
