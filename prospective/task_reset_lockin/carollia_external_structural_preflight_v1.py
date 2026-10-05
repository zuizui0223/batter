#!/usr/bin/env python3
"""MAT-directory-only structural preflight for pinned Carollia trial data."""
from __future__ import annotations
import hashlib, io, json, re, urllib.request
import scipy.io

OWNER="00keveland";REPO="Tunnel_2026";PIN="59928a71887d521fec143080b0b187736c046a0e"
API=f"https://api.github.com/repos/{OWNER}/{REPO}/contents/Trial_Data_Carolia?ref={PIN}"
UA="batter-carollia-external-structural/1.0"
PAT=re.compile(r"^C(?P<bat>\d+)_(?P<trial>\d+)_(?P<date>\d+)_traj_bat_pos_RESULTS\.mat$")

def get_json(url):
 req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.github+json"})
 with urllib.request.urlopen(req,timeout=60) as r:return json.load(r)
def get_bytes(url,maxn=5_000_000):
 req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/octet-stream"})
 with urllib.request.urlopen(req,timeout=90) as r:b=r.read(maxn+1)
 if len(b)>maxn:raise RuntimeError("budget")
 return b

def main():
 listing=get_json(API);rows=[]
 for f in listing:
  name=f.get("name") or "";m=PAT.match(name)
  if not m:continue
  raw=f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{PIN}/Trial_Data_Carolia/{name}"
  b=get_bytes(raw)
  who=scipy.io.whosmat(io.BytesIO(b))
  top=[{"name":n,"shape":list(sh),"class":cls} for n,sh,cls in who]
  has=any(x["name"]=="RESULTS" and x["class"]=="struct" for x in top)
  rows.append({"filename":name,"bat":int(m.group("bat")),"trial":int(m.group("trial")),
               "date":m.group("date"),"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest(),
               "top_level":top,"has_RESULTS_struct":has})
 counts={}
 for r in rows:
  if r["has_RESULTS_struct"]:
   counts.setdefault(r["date"],{}).setdefault(str(r["bat"]),0)
   counts[r["date"]][str(r["bat"])]+=1
 eligible={}
 for date,d in counts.items():
  eligible[date]=sorted([b for b,n in d.items() if n>=3],key=int)
 verdict="PASS_TO_FROZEN_EXTERNAL_OUTCOME" if all(len(eligible.get(d,[]))>=3 for d in ["20231216","20231222"]) else "STOP_INSUFFICIENT_STRUCTURAL_SUPPORT"
 print(json.dumps({"contract":"CAROLLIA_EXTERNAL_STRUCTURAL_PREFLIGHT_V1.md",
                   "movement_values_loaded":False,"n_trial_files":len(rows),
                   "files":rows,"counts_by_date_bat":counts,
                   "eligible_bats_by_date":eligible,"verdict":verdict},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
