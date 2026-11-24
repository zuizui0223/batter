"""V18 outcome-blind public slope-flight source inventory. No coordinates or outcomes emitted."""
import csv,io,json,hashlib,re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote
import requests
from roost_fd_source_audit_v2 import OUT
from inventory_bat_panel_sources import resolve_files
from run_uplift_reaction_norm import download,EXPECTED_SIZE,EXPECTED_MD5

def get(url,params=None):
    r=requests.get(url,params=params,headers={"Accept":"application/json","User-Agent":"batter-public-source-audit/1.0"},timeout=(10,25))
    r.raise_for_status();return r.json()

def tadarida():
    b=download()
    assert len(b)==EXPECTED_SIZE and hashlib.md5(b).hexdigest()==EXPECTED_MD5
    r=csv.DictReader(io.StringIO(b.decode("utf-8-sig"),newline=""))
    fields=r.fieldnames or []
    n=0;groups=Counter();present=Counter()
    columns=[c for c in fields if re.search("height|altitude|climb|slope|aspect|wind|component|timestamp|elev|speed|long|lat|ground",c,re.I)]
    for x in r:
        n+=1
        groups[(str(x.get("animal-id","")).strip(),str(x.get("BatDay","")).strip())]+=1
        for c in columns:
            if str(x.get(c,"")).strip().lower() not in {"","nan","na","none","null"}:present[c]+=1
    return {"status":"verified_prior_source","bytes":len(b),"md5":EXPECTED_MD5,"rows":n,
        "columns":fields,"candidate_field_nonempty":dict(present),
        "individuals":len({i for i,s in groups if i}),"sessions":len(groups),
        "sessions_ge50":sum(n>=50 for n in groups.values()),"numeric_outcomes_read":False}

def mendeley():
    base="https://data.mendeley.com/public-api/datasets/6mtcs5p56m"
    def rows(x):
        if isinstance(x,list):return x
        for k in ("files","data","items","content"):
            if isinstance(x.get(k),list):return x[k]
        return []
    meta=get(base,{"version":2})
    out={"status":"metadata","title":meta.get("name") or meta.get("title"),"files":[]}
    # List metadata only, including nested directories when exposed.
    todo=["root"];seen=set()
    while todo and len(seen)<30:
        folder=todo.pop(0)
        if folder in seen:continue
        seen.add(folder)
        try:
            data=get(base+"/files",{"folder_id":folder,"version":2})
        except Exception as e:
            out.setdefault("listing_errors",[]).append(type(e).__name__+": "+str(e)[:150]);continue
        for f in rows(data):
            if not isinstance(f,dict):continue
            n=f.get("filename") or f.get("name") or ""
            content=f.get("content_details") or {}
            if not isinstance(content,dict):content={}
            fid=f.get("id");kind=str(f.get("type") or f.get("content_type") or "")
            out["files"].append({"name":n,"id":fid,"kind":kind,"size":f.get("size") or content.get("size"),
               "download_url":content.get("download_url") or f.get("download_url")})
            if ("folder" in kind.lower() or f.get("is_folder")) and fid:todo.append(str(fid))
        try:
            folders=get(base+"/folders",{"folder_id":folder,"version":2})
            for f in rows(folders):
                if isinstance(f,dict) and f.get("id"):todo.append(str(f["id"]))
        except Exception:pass
    out["gps_candidates"]=[f for f in out["files"] if re.search(r"gps|track|flight|fig.?1|trajectory|altitude",f["name"],re.I)]
    return out

def dryad():
    doi="10.5061/dryad.mgqnk993n"
    j=get("https://datadryad.org/api/v2/datasets/"+quote("doi:"+doi,safe=""))
    out={"status":"metadata","title":j.get("title"),"identifier":j.get("identifier"),"links":j.get("_links",{})}
    link=j.get("_links",{}).get("stash:version",{}).get("href")
    if link:
        if link.startswith("/"):link="https://datadryad.org"+link
        v=get(link);fl=v.get("_links",{}).get("stash:files",{}).get("href")
        if fl:
            if fl.startswith("/"):fl="https://datadryad.org"+fl
            z=get(fl);out["files"]=[{k:f.get(k) for k in ("path","size","digest","mimeType","_links")} for f in z.get("_embedded",{}).get("stash:files",[])]
    return out

def movebank():
    out={}
    for doi in ("10.5441/001/1.282","10.5441/001/1.321","10.5441/001/1.322","10.5441/001/1.5d736bf0"):
        try:
            r=resolve_files({"doi":doi})
            out[doi]={"status":"metadata","files":r["files"]}
        except Exception as e:out[doi]={"status":"blocked","error":type(e).__name__+": "+str(e)[:150]}
    return out

def safe(f):
    try:return f()
    except Exception as e:return {"status":"blocked","error":type(e).__name__+": "+str(e)[:220]}
def main():
    tasks={"prior_tadarida":tadarida,"boonman_mendeley":mendeley,"niga_dryad":dryad,"prior_movebank":movebank}
    result={"status":"structural_preflight_only","numeric_outcomes_read":False,"sources":{}}
    dest=OUT/"audit_v18_slope.json"
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures={k:pool.submit(safe,f) for k,f in tasks.items()}
        for k,f in futures.items():
            result["sources"][k]=f.result()
            dest.write_text(json.dumps(result,indent=2,allow_nan=False))
    print(dest.read_text())
if __name__=="__main__":main()
