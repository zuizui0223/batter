#!/usr/bin/env python3
import json,re,urllib.request
API="https://api.figshare.com/v2/articles/29209493"
UA="batter-teshima-environment-metadata-audit-v1/1.0"
PAT=re.compile(r"^Env(?P<env>\d+)_Bat(?P<bat>[A-Za-z]+)_no(?P<trial>.+)\.csv$")
MINI_MIN,MINI_MAX=55033796,55033850
RHINO_MIN,RHINO_MAX=55033853,55033985
req=urllib.request.Request(API,headers={"User-Agent":UA,"Accept":"application/json"})
with urllib.request.urlopen(req,timeout=60) as r: a=json.load(r)
out=[]
counts={"mini_trajectory":0,"rhino_trajectory":0,"other":0}
for f in a.get("files") or []:
    fid=int(f["id"]); name=f.get("name") or ""
    m=PAT.match(name)
    if m and MINI_MIN<=fid<=MINI_MAX:
        cls="mini_trajectory"
    elif m and RHINO_MIN<=fid<=RHINO_MAX:
        cls="rhino_trajectory"
    else:
        cls="other"
    counts[cls]+=1
    if cls=="other":
        out.append({
          "id":fid,"name":name,"size":int(f.get("size") or 0),
          "mimetype":f.get("mimetype"),"download_url":f.get("download_url")
        })
print(json.dumps({"status":"METADATA_ONLY","counts":counts,"other_files":sorted(out,key=lambda x:(x["name"],x["id"]))},indent=2))
