#!/usr/bin/env python3
"""List ONLY original OSF sg6dz author SCRIPT folder metadata; no bat records."""
from __future__ import annotations
import argparse,json,hashlib,urllib.request,urllib.parse,urllib.error
from pathlib import Path

URL="https://api.osf.io/v2/nodes/sg6dz/files/osfstorage/698daaafa731d64729dfc7aa/"
VIEW="4624cf1757b34e87bf7a4aca9d889319"
MAX=500000
class Strict(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        p=urllib.parse.urlsplit(newurl)
        if p.scheme!="https" or p.hostname not in ("api.osf.io","osf.io"):
            raise ValueError("DISALLOWED_REDIRECT")
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def get(token=False):
    u=URL+("?view_only="+VIEW if token else "")
    req=urllib.request.Request(u,headers={"Accept":"application/vnd.api+json",
                           "User-Agent":"batter-original-code-metadata-v1"})
    try:
        with urllib.request.build_opener(Strict()).open(req,timeout=18) as r:
            b=r.read(MAX+1)
            status=r.status
        if len(b)>MAX:raise ValueError("LARGE_JSON")
        obj=json.loads(b)
        if not isinstance(obj,dict):raise ValueError("BAD_JSON")
        elems=obj.get("data",[])
        if not isinstance(elems,list):raise ValueError("NOT_LIST")
        out=[]
        for entry in elems[:100]:
            a=entry.get("attributes") or {}
            fname=str(a.get("name") or "")
            out.append({"filename":fname[:160],"kind":str(a.get("kind") or "")[:30],
                 "resource_id":str(entry.get("id") or "")[:100],
                 "size_bytes":a.get("size") if isinstance(a.get("size"),int) else None})
        return {"http_status":status,"ok":True,"list_count_page":len(elems),
                "more_pages":bool((obj.get("links") or {}).get("next")),
                "catalog_sha256":hashlib.sha256(b).hexdigest(),"files":out}
    except urllib.error.HTTPError as e:
        return {"http_status":e.code,"ok":False,"error":"HTTP_ERROR"}
    except Exception as e:
        return {"http_status":None,"ok":False,"error":type(e).__name__}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",default="MYOTIS_AUTHOR_CODE_CATALOG_V1.json")
    a=p.parse_args()
    if a.self_test:
        assert URL.endswith("698daaafa731d64729dfc7aa/")
        print(json.dumps({"source_path_allowlist":"PASS","bat_events_accessed":False}))
        return
    x=get(False)
    if not x["ok"]:x=get(True)
    result={"contract":"MYOTIS_2026_AUTHOR_CODE_CLOCK_SEMANTICS_SOURCE_GATE_V1.md",
            "status":"HOLD_CODE_CATALOG_ONLY" if x["ok"] else "STOP_CODE_CATALOG_INACCESSIBLE",
            "code_folder_metadata":x,
            "bat_detection_values_opened":False,
            "clock_content_interpreted":False,
            "individual_time_records_opened":False}
    Path(a.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":result["status"],"catalog":x,
                      "bat_detection_values_opened":False},sort_keys=True))

if __name__=="__main__":main()
