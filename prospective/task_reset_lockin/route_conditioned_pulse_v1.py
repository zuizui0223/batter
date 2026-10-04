#!/usr/bin/env python3
"""Route- and geometry-conditioned pulse identity sensitivities for Rhinolophus nippon."""
from __future__ import annotations
import importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,HERE/path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

P=loadmod("P","rhino_configuration_identity_primary_v1.py")
Q=loadmod("Q","rhino_pulse_identity_v1.py")
G=loadmod("G","geometry_only_policy_v1.py")
M=loadmod("M","movement_conditioned_pulse_v1.py")

NPERM=9999
MIN_VALID=9500
PULSE_NAMES=[
 "log_pulse_rate","median_log_ipi","p10_log_ipi","p90_log_ipi","iqr_log_ipi","sd_log_ipi"
]

def join_rows():
    move=P.load_rhino()
    pulse=Q.load_rows()
    mm={r["name"]:r for r in move if r.get("feature_valid") and r.get("route_valid")}
    qq={r["name"]:r for r in pulse if r.get("valid")}
    if len(mm)!=45 or len(qq)!=45 or set(mm)!=set(qq):
        raise RuntimeError(f"join mismatch movement={len(mm)} pulse={len(qq)}")
    rows=[]
    for name in sorted(mm):
        m=mm[name];q=qq[name]
        if m["env"]!=q["env"] or m["bat"]!=q["bat"]:
            raise RuntimeError(f"identity mismatch {name}")
        gf=G.geometry_features(m)
        if gf is None:
            raise RuntimeError(f"geometry feature failure {name}")
        centroid=np.mean(np.asarray(m["route101"],dtype=float),axis=0)
        rows.append({
          "name":name,"env":m["env"],"bat":m["bat"],
          "move":np.asarray(m["features"],dtype=float),
          "geom":np.asarray(gf,dtype=float),
          "centroid":np.asarray(centroid,dtype=float),
          "pulse":np.asarray(q["features"],dtype=float),
        })
    return rows

def env_z_matrix(rows,key):
    nfeat=len(rows[0][key])
    Z=np.zeros((len(rows),nfeat),dtype=float)
    envs=sorted(set(r["env"] for r in rows))
    for e in envs:
        ix=[i for i,r in enumerate(rows) if r["env"]==e]
        X=np.vstack([rows[i][key] for i in ix])
        mu=X.mean(axis=0);sd=X.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):
            raise RuntimeError(f"{key} env SD failure e={e}")
        Z[ix]=(X-mu)/sd
    return Z,envs

def residual_rows(rows,mode):
    pulse_z,envs=env_z_matrix(rows,"pulse")
    move_z,_=env_z_matrix(rows,"move")
    cent_z,_=env_z_matrix(rows,"centroid")
    if mode=="C3":
        pred=np.column_stack([move_z,cent_z])
        predictor_names=list(P.FEATURES)+["centroid_x","centroid_y","centroid_z"]
    elif mode=="C4":
        geom_z,_=env_z_matrix(rows,"geom")
        pred=np.column_stack([move_z,geom_z,cent_z])
        predictor_names=list(P.FEATURES)+list(G.FEATURES)+["centroid_x","centroid_y","centroid_z"]
    else:
        raise ValueError(mode)

    X=np.column_stack([np.ones(len(rows)),pred])
    rank=int(np.linalg.matrix_rank(X))
    cond=float(np.linalg.cond(X))
    rdf=len(rows)-rank
    if rdf<15:
        return None,{"status":"STOP_RESIDUAL_DF","rank":rank,"n_rows":len(rows),
                     "residual_df":rdf,"predictor_names":predictor_names,
                     "condition_number":cond if math.isfinite(cond) else None}
    beta,_,rank2,_=np.linalg.lstsq(X,pulse_z,rcond=None)
    resid=pulse_z-X@beta

    # Re-standardize residual pulse features within environment; bad in any env drops feature globally.
    keep=np.ones(6,dtype=bool)
    stats={}
    for e in envs:
        ix=np.array([i for i,r in enumerate(rows) if r["env"]==e],dtype=int)
        mu=resid[ix].mean(axis=0);sd=resid[ix].std(axis=0,ddof=1)
        stats[e]=(ix,mu,sd)
        keep &= np.isfinite(sd)&(sd>0)
    kept=np.where(keep)[0]
    if len(kept)<4:
        return None,{"status":"STOP_RESIDUAL_FEATURE_SUPPORT","rank":rank,"residual_df":rdf,
                     "retained_feature_indices":kept.tolist(),
                     "retained_features":[PULSE_NAMES[i] for i in kept],
                     "predictor_names":predictor_names,
                     "condition_number":cond if math.isfinite(cond) else None}
    rz=np.full((len(rows),len(kept)),np.nan,dtype=float)
    for e,(ix,mu,sd) in stats.items():
        rz[np.arange(len(ix))[:,None],np.arange(len(kept))[None,:]] = 0  # overwritten below
        rz[ix,:]=(resid[np.ix_(ix,kept)]-mu[kept])/sd[kept]

    out=[]
    for i,r in enumerate(rows):
        out.append({**r,"z":rz[i]})
    return out,{
      "status":"PASS_RESIDUALIZATION",
      "rank":rank,"rank_lstsq":int(rank2),"n_rows":len(rows),"residual_df":rdf,
      "condition_number":cond if math.isfinite(cond) else None,
      "n_predictor_columns_excluding_intercept":pred.shape[1],
      "predictor_names":predictor_names,
      "retained_feature_indices":kept.tolist(),
      "retained_features":[PULSE_NAMES[i] for i in kept],
      "usable_envs":envs,
    }

def run(rows,mode,seed):
    rr,meta=residual_rows(rows,mode)
    if rr is None:return meta
    bats,envs,candidates,targets,support=M.target_support(rr)
    obs=P.b_stat(rr,bats,targets,None)
    if obs is None:return {**meta,"status":"STOP_OBSERVED_SUPPORT"}
    Pobs,batmeans,_=obs
    clusters={e:sorted(set(r["bat"] for r in rr if r["env"]==e)) for e in envs}
    rng=np.random.default_rng(seed);null=[]
    for _ in range(NPERM):
        mp={}
        for e,labs in clusters.items():
            perm=list(rng.permutation(np.asarray(labs,dtype=object)))
            for old,new in zip(labs,perm):mp[(e,old)]=str(new)
        x=P.b_stat(rr,bats,targets,mp)
        if x is not None:null.append(float(x[0]))
    pos=sum(v>0 for v in batmeans.values());frac=pos/len(batmeans)
    out={**meta,
      "candidate_bats":candidates,"support_by_bat":support,"n_targets":len(targets),
      "P_residual_obs":float(Pobs),"bat_means":{k:float(v) for k,v in batmeans.items()},
      "positive_bats":pos,"n_bats":len(batmeans),"positive_fraction":float(frac),
      "requested_permutations":NPERM,"valid_permutations":len(null),"seed":seed,
    }
    if len(null)<MIN_VALID:
        out["verdict"]="STOP_RANDOMIZATION_SUPPORT";return out
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=Pobs))/(1+len(a)))
    out.update({
      "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
      "null_q975":float(np.quantile(a,.975)),"p_one_sided":p,
      "verdict":"SUPPORTED_RESIDUAL_PULSE_IDENTITY" if (Pobs>0 and p<=.05 and frac>=.70)
                else "UNSUPPORTED_RESIDUAL_PULSE_IDENTITY"
    })
    return out

def main():
    rows=join_rows()
    print(json.dumps({
      "contract":"ROUTE_CONDITIONED_PULSE_CONTRACT_V1.md",
      "status":"POST_PRIMARY_MECHANISM_DIAGNOSTIC",
      "species":"Rhinolophus nippon","n_joined_trajectories":len(rows),
      "C3_movement_plus_lane":run(rows,"C3",202610042271),
      "C4_movement_geometry_lane":run(rows,"C4",202610042272),
    },ensure_ascii=False,indent=2))

if __name__=="__main__":main()
