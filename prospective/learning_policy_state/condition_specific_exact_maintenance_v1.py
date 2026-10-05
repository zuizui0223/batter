#!/usr/bin/env python3
"""Exact 7! condition-specific robustness for learning-state maintenance."""
from __future__ import annotations

import importlib.util, itertools, json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"learning_state_maintenance_primary_v1.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)

def condition_stat(cb,z,perm_map=None):
    ki={}
    for b in cb:
        assigned=perm_map[b] if perm_map is not None else b
        dself=float(np.linalg.norm(z[(b,1)]-z[(assigned,12)]))
        others=[j for j in cb if j!=assigned]
        dother=float(np.mean([np.linalg.norm(z[(b,1)]-z[(j,12)]) for j in others]))
        ki[b]=dother-dself
    return float(np.mean(list(ki.values()))),ki

def main():
    rows=P.fetch()
    bats,cond,by=P.complete_subjects(rows)
    z,_=P.standardized_state(bats,cond,by)

    out={
      "contract":"CONDITION_SPECIFIC_EXACT_MAINTENANCE_CONTRACT_V1.md",
      "status":"POST_PRIMARY_ROBUSTNESS_DIAGNOSTIC",
      "conditions":{}
    }
    for c in (1,2):
        cb=sorted([b for b in bats if cond[b]==c],key=int)
        if len(cb)!=7:raise RuntimeError(f"condition {c} expected 7, got {len(cb)}")
        obs,ki=condition_stat(cb,z,None)
        null=[]
        for perm in itertools.permutations(cb):
            mp={b:j for b,j in zip(cb,perm)}
            null.append(condition_stat(cb,z,mp)[0])
        a=np.asarray(null,float)
        p=float(np.sum(a>=obs)/len(a))
        pos=sum(v>0 for v in ki.values())
        out["conditions"][str(c)]={
          "K_condition":obs,
          "K_i":ki,
          "positive_subjects":pos,
          "n_subjects":len(cb),
          "exact_permutations":len(a),
          "null_mean":float(np.mean(a)),
          "null_q025":float(np.quantile(a,.025)),
          "null_q975":float(np.quantile(a,.975)),
          "p_exact_one_sided":p,
          "diagnostic_verdict":"SUPPORTED" if (obs>0 and p<=.05) else "UNSUPPORTED"
        }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
