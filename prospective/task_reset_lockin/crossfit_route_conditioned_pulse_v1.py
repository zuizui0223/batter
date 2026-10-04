#!/usr/bin/env python3
"""Cross-fitted route-conditioned pulse identity robustness."""
from __future__ import annotations
import importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,HERE/path)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

R=loadmod("R","route_conditioned_pulse_v1.py")
P=loadmod("P","rhino_configuration_identity_primary_v1.py")
M=loadmod("M","movement_conditioned_pulse_v1.py")

NPERM=9999
SEED=202610042281
MIN_VALID=9500
PULSE_NAMES=[
 "log_pulse_rate","median_log_ipi","p10_log_ipi",
 "p90_log_ipi","iqr_log_ipi","sd_log_ipi"
]

def main():
    rows=R.join_rows()
    pulse_z,envs=R.env_z_matrix(rows,"pulse")
    move_z,_=R.env_z_matrix(rows,"move")
    geom_z,_=R.env_z_matrix(rows,"geom")
    cent_z,_=R.env_z_matrix(rows,"centroid")
    pred=np.column_stack([move_z,geom_z,cent_z])

    resid=np.full_like(pulse_z,np.nan)
    folds={}
    for e in envs:
        train=np.array([i for i,r in enumerate(rows) if r["env"]!=e],dtype=int)
        test=np.array([i for i,r in enumerate(rows) if r["env"]==e],dtype=int)
        Xtr=np.column_stack([np.ones(len(train)),pred[train]])
        Xte=np.column_stack([np.ones(len(test)),pred[test]])
        rank=int(np.linalg.matrix_rank(Xtr))
        cond=float(np.linalg.cond(Xtr))
        rdf=int(len(train)-rank)
        if rank<2 or rdf<10:
            out={
              "contract":"CROSSFIT_ROUTE_CONDITIONED_PULSE_CONTRACT_V1.md",
              "status":"STOP_FOLD_SUPPORT","target_environment":e,
              "n_train":len(train),"n_test":len(test),"rank":rank,
              "residual_df":rdf,"condition_number":cond if math.isfinite(cond) else None
            }
            print(json.dumps(out,ensure_ascii=False,indent=2)); return
        beta,_,rank2,_=np.linalg.lstsq(Xtr,pulse_z[train],rcond=None)
        if int(rank2)!=rank:
            out={
              "contract":"CROSSFIT_ROUTE_CONDITIONED_PULSE_CONTRACT_V1.md",
              "status":"STOP_RANK_MISMATCH","target_environment":e,
              "matrix_rank":rank,"lstsq_rank":int(rank2)
            }
            print(json.dumps(out,ensure_ascii=False,indent=2)); return
        resid[test]=pulse_z[test]-Xte@beta
        folds[str(e)]={
          "n_train":int(len(train)),"n_test":int(len(test)),
          "rank":rank,"residual_df":rdf,
          "condition_number":cond if math.isfinite(cond) else None
        }

    # Within-target-environment residual standardization.
    keep=np.ones(6,dtype=bool)
    stats={}
    for e in envs:
        ix=np.array([i for i,r in enumerate(rows) if r["env"]==e],dtype=int)
        mu=np.mean(resid[ix],axis=0)
        sd=np.std(resid[ix],axis=0,ddof=1)
        stats[e]=(ix,mu,sd)
        keep &= np.isfinite(sd)&(sd>0)
    kept=np.where(keep)[0]
    if len(kept)<4:
        out={
          "contract":"CROSSFIT_ROUTE_CONDITIONED_PULSE_CONTRACT_V1.md",
          "status":"STOP_RESIDUAL_FEATURE_SUPPORT",
          "folds":folds,
          "retained_feature_indices":kept.tolist(),
          "retained_features":[PULSE_NAMES[i] for i in kept],
        }
        print(json.dumps(out,ensure_ascii=False,indent=2)); return

    rz=np.full((len(rows),len(kept)),np.nan,dtype=float)
    for e,(ix,mu,sd) in stats.items():
        rz[ix,:]=(resid[np.ix_(ix,kept)]-mu[kept])/sd[kept]

    rr=[]
    for i,r in enumerate(rows):
        rr.append({**r,"z":rz[i]})

    bats,usable,candidates,targets,support=M.target_support(rr)
    obs=P.b_stat(rr,bats,targets,None)
    if obs is None:
        out={
          "contract":"CROSSFIT_ROUTE_CONDITIONED_PULSE_CONTRACT_V1.md",
          "status":"STOP_OBSERVED_IDENTITY_SUPPORT",
          "folds":folds,
          "retained_features":[PULSE_NAMES[i] for i in kept],
        }
        print(json.dumps(out,ensure_ascii=False,indent=2)); return

    Pobs,batmeans,_=obs
    clusters={e:sorted(set(r["bat"] for r in rr if r["env"]==e)) for e in usable}
    rng=np.random.default_rng(SEED)
    null=[]
    for _ in range(NPERM):
        mp={}
        for e,labs in clusters.items():
            perm=list(rng.permutation(np.asarray(labs,dtype=object)))
            for old,new in zip(labs,perm):
                mp[(e,old)]=str(new)
        x=P.b_stat(rr,bats,targets,mp)
        if x is not None:
            null.append(float(x[0]))

    pos=sum(v>0 for v in batmeans.values())
    frac=pos/len(batmeans)
    out={
      "contract":"CROSSFIT_ROUTE_CONDITIONED_PULSE_CONTRACT_V1.md",
      "status":"DONE",
      "species":"Rhinolophus nippon",
      "n_trajectories":len(rows),
      "folds":folds,
      "retained_feature_indices":kept.tolist(),
      "retained_features":[PULSE_NAMES[i] for i in kept],
      "candidate_bats":candidates,
      "support_by_bat":support,
      "n_targets":len(targets),
      "P_crossfit_residual_obs":float(Pobs),
      "bat_means":{k:float(v) for k,v in batmeans.items()},
      "positive_bats":pos,"n_bats":len(batmeans),"positive_fraction":float(frac),
      "requested_permutations":NPERM,"valid_permutations":len(null),"seed":SEED,
    }
    if len(null)<MIN_VALID:
        out["verdict"]="STOP_RANDOMIZATION_SUPPORT"
        print(json.dumps(out,ensure_ascii=False,indent=2)); return

    a=np.asarray(null,float)
    p=float((1+np.sum(a>=Pobs))/(1+len(a)))
    out.update({
      "null_mean":float(a.mean()),
      "null_q025":float(np.quantile(a,.025)),
      "null_q975":float(np.quantile(a,.975)),
      "p_one_sided":p,
      "verdict":"SUPPORTED_CROSSFIT_RESIDUAL_PULSE_IDENTITY"
                if (Pobs>0 and p<=.05 and frac>=.70)
                else "UNSUPPORTED_CROSSFIT_RESIDUAL_PULSE_IDENTITY"
    })
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
