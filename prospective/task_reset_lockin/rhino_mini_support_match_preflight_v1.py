#!/usr/bin/env python3
from __future__ import annotations
import itertools, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from prospective.task_reset_lockin import rhino_configuration_identity_primary_v1 as P

MINI_MIN=55033796
MINI_MAX=55033850
RHINO_MIN=55033853
RHINO_MAX=55033985

def counts():
    article=P.get_article()
    mini=Counter(); rhino=Counter()
    mini_bats=set(); rhino_bats=set(); envs=set()
    for f in article.get("files") or []:
        fid=int(f["id"]); name=f.get("name") or ""
        m=P.PAT.match(name)
        if not m: continue
        e=int(m.group("env")); b=str(m.group("bat"))
        if MINI_MIN<=fid<=MINI_MAX:
            mini[(e,b)]+=1; mini_bats.add(b); envs.add(e)
        elif RHINO_MIN<=fid<=RHINO_MAX:
            rhino[(e,b)]+=1; rhino_bats.add(b); envs.add(e)
    return mini,rhino,sorted(mini_bats),sorted(rhino_bats),sorted(envs)

def main():
    mini,rhino,mb,rb,envs=counts()
    valid=[]
    for chosen in itertools.permutations(rb,len(mb)):
        mp=dict(zip(mb,chosen))
        ok=True
        margins=[]
        for (e,b),n in sorted(mini.items()):
            have=rhino.get((e,mp[b]),0)
            margins.append({"environment":e,"mini_bat":b,"rhino_bat":mp[b],"need":n,"have":have})
            if have<n: ok=False
        if ok:
            valid.append({"mapping":mp,"margins":margins})
    out={
        "status":"STRUCTURAL_PREFLIGHT_ONLY",
        "mini_bats":mb,"rhino_bats":rb,"environments":envs,
        "mini_counts":{f"{e}:{b}":n for (e,b),n in sorted(mini.items())},
        "rhino_counts":{f"{e}:{b}":n for (e,b),n in sorted(rhino.items())},
        "candidate_injective_mappings":len(list(itertools.permutations(rb,len(mb)))),
        "valid_exact_mappings":len(valid),
        "gate_pass":len(valid)>=5,
        "valid_mappings":valid
    }
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
