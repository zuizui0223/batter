#!/usr/bin/env python3
from __future__ import annotations
import itertools, json, math, re, urllib.request

API="https://api.figshare.com/v2/articles/29209493"
UA="batter-mini-rhino-matched-support-preflight-v1/1.0"
PAT=re.compile(r"^Env(?P<env>\d+)_Bat(?P<bat>[A-Za-z]+)_no(?P<trial>.+)\.csv$")
MINI_MIN,MINI_MAX=55033796,55033850
RHINO_MIN,RHINO_MAX=55033853,55033985

def article():
    req=urllib.request.Request(API,headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.load(r)

def matrix(files,lo,hi):
    out={}
    raw=[]
    for f in files:
        fid=int(f["id"]); name=f.get("name") or ""
        m=PAT.match(name)
        if not m or not(lo<=fid<=hi):
            continue
        e=int(m.group("env")); b=m.group("bat")
        out[(e,b)]=out.get((e,b),0)+1
        raw.append({"id":fid,"name":name,"env":e,"bat":b})
    return out,raw

def main():
    files=article().get("files") or []
    mini,mraw=matrix(files,MINI_MIN,MINI_MAX)
    rhino,rraw=matrix(files,RHINO_MIN,RHINO_MAX)
    if len(mraw)!=19:
        raise RuntimeError(f"Mini structural drift: {len(mraw)}")
    mbats=sorted({b for e,b in mini})
    rbats=sorted({b for e,b in rhino})
    if len(mbats)!=4:
        raise RuntimeError(f"expected 4 Mini bats, got {mbats}")
    feasible=[]
    total_subsets=0
    for chosen in itertools.combinations(rbats,4):
        for perm in itertools.permutations(chosen):
            mp=dict(zip(mbats,perm))
            ok=True
            ways=1
            cell_rows=[]
            for (e,b),need in sorted(mini.items()):
                have=rhino.get((e,mp[b]),0)
                if have<need:
                    ok=False; break
                ways*=math.comb(have,need)
                cell_rows.append({"env":e,"mini_bat":b,"rhino_bat":mp[b],"need":need,"have":have})
            if ok:
                feasible.append({"mapping":mp,"ways":ways,"cells":cell_rows})
                total_subsets+=ways
    payload={
        "status":"OUTCOME_BLIND_STRUCTURAL_PREFLIGHT",
        "mini_total_files":len(mraw),
        "rhino_total_files":len(rraw),
        "mini_bats":mbats,
        "rhino_bats":rbats,
        "mini_cell_counts":{f"{e}:{b}":n for (e,b),n in sorted(mini.items())},
        "rhino_cell_counts":{f"{e}:{b}":n for (e,b),n in sorted(rhino.items())},
        "feasible_mapping_count":len(feasible),
        "total_exact_support_matched_subsets":total_subsets,
        "gate_mapping_min":4,
        "gate_subset_min":100,
        "gate_pass":bool(len(feasible)>=4 and total_subsets>=100),
        "feasible_mappings":feasible,
        "behavioural_outcome_opened":False
    }
    print(json.dumps(payload,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
