#!/usr/bin/env python3
from __future__ import annotations
import itertools, json, re, urllib.request

API="https://api.figshare.com/v2/articles/29209493"
UA="batter-mini-rhino-centroid-support-preflight-v1/1.0"
PAT=re.compile(r"^Env(?P<env>\d+)_Bat(?P<bat>[A-Za-z]+)_no(?P<trial>.+)\.csv$")
MINI_MIN,MINI_MAX=55033796,55033850
RHINO_MIN,RHINO_MAX=55033853,55033985

def article():
    req=urllib.request.Request(API,headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.load(r)

def fileset(files,lo,hi):
    raw=[]
    for f in files:
        fid=int(f["id"]); name=f.get("name") or ""
        m=PAT.match(name)
        if not m or not(lo<=fid<=hi):
            continue
        raw.append((int(m.group("env")),m.group("bat"),fid,name))
    return raw

def main():
    files=article().get("files") or []
    mini=fileset(files,MINI_MIN,MINI_MAX)
    rhino=fileset(files,RHINO_MIN,RHINO_MAX)
    if len(mini)!=19 or len(rhino)!=45:
        raise RuntimeError(f"structural drift Mini={len(mini)} Rhino={len(rhino)}")
    mcells=sorted(set((e,b) for e,b,_,_ in mini))
    rcells=set((e,b) for e,b,_,_ in rhino)
    mbats=sorted(set(b for e,b in mcells)); rbats=sorted(set(b for e,b in rcells))
    menvs=sorted(set(e for e,b in mcells)); renvs=sorted(set(e for e,b in rcells))
    if len(mbats)!=4 or len(menvs)!=7 or len(mcells)!=12:
        raise RuntimeError("Mini occupancy structure drift")
    feasible=[]
    for chosen in itertools.permutations(rbats,4):
        bmap=dict(zip(mbats,chosen))
        for eperm in itertools.permutations(renvs,7):
            emap=dict(zip(menvs,eperm))
            if all((emap[e],bmap[b]) in rcells for e,b in mcells):
                feasible.append({
                    "bat_map":dict(bmap),
                    "env_map":{str(k):v for k,v in emap.items()}
                })
    payload={
        "status":"OUTCOME_BLIND_STRUCTURAL_PREFLIGHT",
        "mini_raw_files":len(mini),
        "rhino_raw_files":len(rhino),
        "mini_occupied_cells":len(mcells),
        "mini_bats":mbats,
        "mini_envs":menvs,
        "rhino_bats":rbats,
        "rhino_envs":renvs,
        "feasible_mapping_count":len(feasible),
        "gate_min":100,
        "gate_pass":bool(len(feasible)>=100),
        "first_20_feasible_mappings":feasible[:20],
        "behavioural_outcome_opened":False
    }
    print(json.dumps(payload,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
