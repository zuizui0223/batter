#!/usr/bin/env python3
"""Post-outcome policy-to-vertical-shape localization in carrier-positive panels only."""
from __future__ import annotations
import importlib.util, json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("B",HERE/"wild_policy_to_vertical_shape_v1.py")
B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)

OPEN={
 "hypsignathus":("contract/hypsignathus_replication_v1.json",202610051321),
 "phyllostomus_2022":("contract/phyllostomus_replication_v1.json",202610051322),
}

def main():
    results={}
    nulls=[]
    obs=[]
    for panel,(path,seed) in OPEN.items():
        q=B.run_panel(panel,path,seed)
        arr=q.pop("_null",None)
        results[panel]=q
        if arr is not None:
            nulls.append(np.asarray(arr,float))
            obs.append(float(q["C_panel"]))
    if len(nulls)==2:
        n=min(map(len,nulls))
        comb=np.mean(np.vstack([x[:n] for x in nulls]),axis=0)
        oc=float(np.mean(obs))
        pc=float((1+np.sum(comb>=oc))/(1+len(comb)))
        combined={
          "status":"DONE","C_equal_two_panel":oc,
          "valid_permutations":int(len(comb)),
          "null_mean":float(comb.mean()),
          "null_q025":float(np.quantile(comb,.025)),
          "null_q975":float(np.quantile(comb,.975)),
          "p_one_sided_descriptive":pc,
        }
    else:
        combined={"status":"STOP_COMBINED_SUPPORT","n_null_panels":len(nulls)}

    out={
      "contract":"CARRIER_POSITIVE_POLICY_SHAPE_BOUNDARY_CONTRACT_V1.md",
      "status":"POST_OUTCOME_BOUNDARY_DIAGNOSTIC",
      "frozen_global_field_bridge_reopened":False,
      "opened_panels":list(OPEN),
      "panels":results,
      "descriptive_equal_two_panel":combined,
      "claim_ceiling":"localization within the two frozen carrier-positive panels only",
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
