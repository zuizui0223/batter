#!/usr/bin/env python3
"""Fast-equivalent held-out policy-to-geometry coupling using precomputed distances."""
from __future__ import annotations
import importlib.util,json,math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("C",HERE/"heldout_policy_geometry_coupling_v1.py")
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)

def prep():
    envs,mc,gc=C.build_centroids()
    blocks=[]
    allx=[];ally=[]
    pair_counts={}
    for e in envs:
        th=C.heldout_theta(envs,mc,e)
        labels=sorted(set(th).intersection(b for ee,b in gc if ee==e))
        n=len(labels)
        if n<2:
            pair_counts[str(e)]=0;continue
        T=np.vstack([th[b] for b in labels])
        G=np.vstack([gc[(e,b)] for b in labels])
        Dt=np.linalg.norm(T[:,None,:]-T[None,:,:],axis=2)
        Dg=np.linalg.norm(G[:,None,:]-G[None,:,:],axis=2)
        iu=np.triu_indices(n,1)
        x=Dt[iu];y=Dg[iu]
        allx.extend(x.tolist());ally.extend(y.tolist())
        pair_counts[str(e)]=len(x)
        blocks.append({"env":e,"labels":labels,"Dg":Dg,"iu":iu,"x":x})
    return envs,blocks,pair_counts,np.asarray(allx,float),np.asarray(ally,float)

def main():
    envs,blocks,pair_counts,x,y=prep()
    rho=C.spearman(x,y);pear=C.corr(x,y)
    if not (math.isfinite(rho) and math.isfinite(pear)):
        raise RuntimeError("observed metric invalid")

    # Keep environment-specific theta pair distances fixed. Randomly reassign
    # complete geometry centroids to biological labels within each environment.
    rng=np.random.default_rng(C.SEED)
    null=np.empty(C.NPERM,float)
    for k in range(C.NPERM):
        ys=[]
        for b in blocks:
            n=len(b["labels"])
            p=rng.permutation(n)
            D=b["Dg"][np.ix_(p,p)]
            ys.extend(D[b["iu"]].tolist())
        null[k]=C.spearman(x,np.asarray(ys,float))

    pval=float((1+np.sum(null>=rho))/(1+len(null)))
    byenv={}
    for b in blocks:
        yy=b["Dg"][b["iu"]]
        sr=C.spearman(b["x"],yy) if len(b["x"])>=3 else math.nan
        pr=C.corr(b["x"],yy) if len(b["x"])>=3 else math.nan
        byenv[str(b["env"])]={"n_pairs":len(b["x"]),
          "spearman":float(sr) if math.isfinite(sr) else None,
          "pearson":float(pr) if math.isfinite(pr) else None}

    print(json.dumps({
      "contract":"HELDOUT_POLICY_GEOMETRY_COUPLING_CONTRACT_V1.md",
      "implementation":"FAST_EQUIVALENT_PRECOMPUTED_DISTANCE_MATRICES",
      "status":"POST_PRIMARY_MECHANISM_DIAGNOSTIC",
      "environments":envs,
      "pair_counts":pair_counts,
      "observed":{"spearman_rho":float(rho),"pearson_r":float(pear),
                  "n_pair_environment_points":len(x),"by_environment":byenv},
      "permutation":{"requested":C.NPERM,"valid":C.NPERM,"seed":C.SEED,
          "null_mean":float(null.mean()),"null_q025":float(np.quantile(null,.025)),
          "null_q975":float(np.quantile(null,.975)),"p_one_sided":pval},
      "diagnostic_verdict":"SUPPORTED_HELDOUT_POLICY_GEOMETRY_COUPLING"
          if (rho>0 and pval<=.05) else "UNSUPPORTED_HELDOUT_POLICY_GEOMETRY_COUPLING"
    },indent=2))

if __name__=="__main__":main()
