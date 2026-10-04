#!/usr/bin/env python3
"""Filename-only architecture audit for Figshare article 29209493."""
from __future__ import annotations
import collections, json, re, urllib.request

API="https://api.figshare.com/v2/articles/29209493"
UA="batter-task-reset-filename-architecture/1.0"
PAT=re.compile(r"^Env(?P<env>\d+)_Bat(?P<bat>[A-Za-z]+)_no(?P<trial>.+)\.csv$")

def get():
    req=urllib.request.Request(API,headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:return json.load(r)

def main():
    a=get()
    parsed=[];other=[]
    for f in a.get("files") or []:
        name=f.get("name") or ""
        m=PAT.match(name)
        if m:
            parsed.append({"id":f.get("id"),"name":name,"size":f.get("size"),
                           "env":int(m.group("env")),"bat":m.group("bat"),"trial_token":m.group("trial")})
        else: other.append({"id":f.get("id"),"name":name,"size":f.get("size")})
    by_name=collections.defaultdict(list)
    by_bat=collections.defaultdict(list)
    by_env=collections.defaultdict(list)
    by_env_bat=collections.defaultdict(list)
    for r in parsed:
        by_name[r["name"]].append(r["id"])
        by_bat[r["bat"]].append(r)
        by_env[r["env"]].append(r)
        by_env_bat[(r["env"],r["bat"])].append(r)
    out={
      "contract":"METADATA_PREFLIGHT_CONTRACT_V1.md",
      "file_contents_downloaded":False,
      "n_csv_pattern_files":len(parsed),
      "other_files":other,
      "environments":sorted(by_env),
      "bat_labels":sorted(by_bat),
      "per_bat":{
        b:{
          "n_files":len(rr),
          "envs":sorted(set(x["env"] for x in rr)),
          "n_envs":len(set(x["env"] for x in rr)),
          "trial_tokens":sorted(set(x["trial_token"] for x in rr)),
          "files_per_env":{str(e):sum(x["env"]==e for x in rr) for e in sorted(set(x["env"] for x in rr))}
        } for b,rr in sorted(by_bat.items())
      },
      "per_environment":{
        str(e):{
          "n_files":len(rr),
          "bat_labels":sorted(set(x["bat"] for x in rr)),
          "files_per_bat":{b:len(by_env_bat[(e,b)]) for b in sorted(set(x["bat"] for x in rr))}
        } for e,rr in sorted(by_env.items())
      },
      "duplicate_filenames":[{"name":n,"n":len(ids),"ids":ids} for n,ids in sorted(by_name.items()) if len(ids)>1],
      "n_duplicate_filename_groups":sum(len(ids)>1 for ids in by_name.values()),
      "unique_filename_count":len(by_name),
      "raw_parsed_files":parsed,
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
