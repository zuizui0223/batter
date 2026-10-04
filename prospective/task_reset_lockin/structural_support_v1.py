#!/usr/bin/env python3
"""Outcome-blind line-count structural gate for task-reset CSVs.\nScientific rules unchanged; rerun after CI guard repair.\n"""
from __future__ import annotations
import collections, hashlib, json, re, urllib.request

API="https://api.figshare.com/v2/articles/29209493"
UA="batter-task-reset-structural-support/1.0"
PAT=re.compile(r"^Env(?P<env>\d+)_Bat(?P<bat>[A-Za-z]+)_no(?P<trial>.+)\.csv$")

# Frozen species mapping from file-id batches.
def species_from_id(fid:int)->str:
    if 55033796 <= fid <= 55033850:
        return "Miniopterus_fuliginosus"
    if 55033853 <= fid <= 55033985:
        return "Rhinolophus_nippon"
    raise RuntimeError(f"unmapped CSV file id {fid}")

def get_article():
    req=urllib.request.Request(API,headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:return json.load(r)

def get_bytes(url,maxn):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"text/csv,*/*"})
    with urllib.request.urlopen(req,timeout=90) as r:
        b=r.read(maxn+1)
    if len(b)>maxn:
        raise RuntimeError(f"download exceeds budget {maxn}")
    return b

def main():
    a=get_article()
    rows=[]
    for f in a.get("files") or []:
        name=f.get("name") or ""
        m=PAT.match(name)
        if not m:continue
        fid=int(f["id"])
        size=int(f["size"])
        b=get_bytes(f["download_url"],size+4096)
        if len(b)!=size:
            raise RuntimeError(f"size mismatch {name}: {len(b)} != {size}")
        md5=hashlib.md5(b).hexdigest()
        expected=f.get("computed_md5") or f.get("supplied_md5")
        if expected and md5!=expected:
            raise RuntimeError(f"md5 mismatch {name}")
        total_lines=len(b.splitlines())
        data_rows=max(0,total_lines-1)
        rows.append({
            "file_id":fid,"name":name,"species":species_from_id(fid),
            "env":int(m.group("env")),"bat":m.group("bat"),
            "trial_token":m.group("trial"),"bytes":size,
            "total_lines":total_lines,"data_rows":data_rows,
            "pass_ge100_rows":data_rows>=100,
        })

    by_sp_env_bat=collections.defaultdict(list)
    by_sp_bat_env=collections.defaultdict(set)
    for r in rows:
        if r["pass_ge100_rows"]:
            by_sp_env_bat[(r["species"],r["env"],r["bat"])].append(r)
            by_sp_bat_env[(r["species"],r["bat"])].add(r["env"])

    species_out={}
    for sp in sorted(set(r["species"] for r in rows)):
        envs=sorted(set(r["env"] for r in rows if r["species"]==sp))
        bats=sorted(set(r["bat"] for r in rows if r["species"]==sp))
        env_summ=[]
        eligible_A_envs=[]
        for e in envs:
            counts={b:len(by_sp_env_bat[(sp,e,b)]) for b in bats}
            repeat_bats=[b for b,n in counts.items() if n>=2]
            pass_A=len(repeat_bats)>=3
            if pass_A:eligible_A_envs.append(e)
            env_summ.append({
                "env":e,"passing_file_counts_by_bat":counts,
                "repeat_bats_ge2":repeat_bats,
                "pass_A_environment":pass_A,
            })
        bat_summ=[]
        candidate_B=[]
        for b in bats:
            e=sorted(by_sp_bat_env[(sp,b)])
            ok=len(e)>=3
            if ok:candidate_B.append(b)
            bat_summ.append({"bat":b,"passing_envs":e,"n_passing_envs":len(e),"candidate_B":ok})
        pass_A=len(eligible_A_envs)>=2
        pass_B=len(candidate_B)>=3
        species_out[sp]={
            "bat_labels":bats,
            "n_files":sum(r["species"]==sp for r in rows),
            "environment_summary":env_summ,
            "eligible_A_environments":eligible_A_envs,
            "A_verdict":"PASS_A" if pass_A else "STOP_A",
            "bat_summary":bat_summ,
            "candidate_B_bats":candidate_B,
            "B_verdict":"PASS_B" if pass_B else "STOP_B",
        }

    out={
      "contract":"STRUCTURAL_SUPPORT_AMENDMENT_V1.md",
      "numeric_fields_parsed":False,
      "n_csv":len(rows),
      "files":rows,
      "species":species_out,
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
