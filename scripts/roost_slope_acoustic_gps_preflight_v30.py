"""V30 independent-source metadata gate, no track values or locations."""
import json,re
from collections import deque
import requests
from roost_fd_source_audit_v2 import OUT

BASE="https://data.mendeley.com/public-api/datasets/w4s2xrkv6p"
VERSION=1

def get(url,params=None):
    r=requests.get(url,params=params,headers={"Accept":"application/json","User-Agent":"batter-source-audit-v30/1.0"},timeout=(10,25))
    r.raise_for_status()
    return r.json()

def rows(x):
    if isinstance(x,list):return x
    if isinstance(x,dict):
        for k in ("files","folders","data","items","content"):
            if isinstance(x.get(k),list):return x[k]
    return []

def main():
    result={"status":"metadata_only","doi":"10.17632/w4s2xrkv6p.1","version_requested":VERSION,
        "numeric_outcomes_read":False,"files":[],"listing_errors":[]}
    dest=OUT/"audit_v30_acoustic_gps_source.json"
    def save():dest.write_text(json.dumps(result,indent=2,allow_nan=False))
    save()
    try:
        meta=get(BASE,{"version":VERSION})
        result["title"]=meta.get("name") or meta.get("title")
        result["reported_version"]=meta.get("version")
        result["description"]=str(meta.get("description") or "")[:1000]
        todo=deque([("root","")]);seen=set()
        while todo and len(seen)<80:
            folder,prefix=todo.popleft()
            if folder in seen:continue
            seen.add(folder)
            for endpoint in ("files","folders"):
                try:
                    listing=rows(get(BASE+"/"+endpoint,{"folder_id":folder,"version":VERSION}))
                except Exception as e:
                    result["listing_errors"].append({"endpoint":endpoint,"error_type":type(e).__name__})
                    continue
                for f in listing:
                    if not isinstance(f,dict):continue
                    name=str(f.get("filename") or f.get("name") or "")
                    fid=f.get("id")
                    kind=str(f.get("type") or f.get("content_type") or "")
                    detail=f.get("content_details") or {}
                    if not isinstance(detail,dict):detail={}
                    if endpoint=="folders" or "folder" in kind.lower() or f.get("is_folder"):
                        if fid:todo.append((str(fid),prefix+name+"/"))
                    else:
                        if any(x.get("id")==fid for x in result["files"] if fid):continue
                        result["files"].append({"path":prefix+name,"id":fid,"size":f.get("size") or detail.get("size"),
                          "kind":kind,"published_sha256":f.get("sha256_hash") or detail.get("sha256_hash"),
                          "download_url":detail.get("download_url") or f.get("download_url")})
        result["folders_visited"]=len(seen)
        result["listing_truncated"]=bool(todo)
        result["candidate_raw_or_archive_files"]=[f["path"] for f in result["files"] if re.search(r"gps|track|position|altitude|movement|raw|\\.zip$|\\.mat$|\\.csv$",f["path"],re.I)]
        result["status"]="listed_not_admitted" if result["files"] else "no_file_listing"
    except Exception as e:
        result["status"]="blocked";result["error_type"]=type(e).__name__
    save();print(dest.read_text())
    return 0 if result["status"]=="listed_not_admitted" else 2
if __name__=="__main__":raise SystemExit(main())
