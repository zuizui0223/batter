#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json
from collections import Counter, defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("M",HERE/"cross_species_policy_axis_v1.py")
M=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(M)

def main():
    rows=M.mini_standardized()
    by_bat=defaultdict(list)
    by_env=defaultdict(list)
    cell=Counter()
    for r in rows:
        b=str(r["bat"]); e=int(r["env"])
        by_bat[b].append(e); by_env[e].append(b); cell[(b,e)]+=1
    bats=sorted(by_bat)
    envs=sorted(by_env)
    out={
      "status":"STRUCTURAL_INVENTORY_ONLY",
      "n_trajectories":len(rows),
      "bats":bats,
      "environments":envs,
      "environments_per_bat":{b:sorted(set(by_bat[b])) for b in bats},
      "n_environments_per_bat":{b:len(set(by_bat[b])) for b in bats},
      "trajectory_count_per_bat":{b:len(by_bat[b]) for b in bats},
      "bats_per_environment":{str(e):sorted(set(by_env[e])) for e in envs},
      "n_bats_per_environment":{str(e):len(set(by_env[e])) for e in envs},
      "trajectory_count_per_bat_environment":{f"{b}:{e}":cell[(b,e)] for b in bats for e in envs if cell[(b,e)]},
    }
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
