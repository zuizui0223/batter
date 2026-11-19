#!/usr/bin/env python3
"""Dixon et al. 2023 original Dryad file inventory / schema without outcomes.

Author paper DOI 10.1093/beheco/arad001;
original Dryad DOI 10.5061/dryad.pzgmsbcr7, published version id 212971.
Original 2023 study already established non-guild spatial preference.
"""
import csv,hashlib,io,json,os,urllib.request,urllib.error
from pathlib import Path
BASE="https://datadryad.org"
VERSION_ID=212971
URLS=[
 f"{BASE}/api/v2/versions/{VERSION_ID}",
 f"{BASE}/api/v2/versions/{VERSION_ID}/files",
 f"{BASE}/api/v2/versions/{VERSION_ID}/files?per_page=100",
]
OUT=Path(os.getenv("H1_DIXON_FILES_RECEIPT","/tmp/h1_dixon_original_files_receipt.json"))
def get(u,size=750000):
    req=urllib.request.Request(u,headers={"User-Agent":"BatH1Original2023FileInventory/1.0","Accept":"application/json,application/octet-stream,*/*"})
    with urllib.request.urlopen(req,timeout=30) as r:
        return r.read(size+1),r.status,r.headers.get("Content-Type","")

def main():
    result={"paper_doi":"10.1093/beheco/arad001","dataset_doi":"10.5061/dryad.pzgmsbcr7",
            "version_id":VERSION_ID,"status":"STOP_NO_FILE_LIST",
            "data_rows_opened":False,"attempts":[]}
    for url in URLS:
        try:
            data,status,mime=get(url)
            entry={"url":url,"status":status,"bytes":len(data),"mime":mime}
            obj=json.loads(data)
            if isinstance(obj,dict):
                entry["keys"]=list(obj)[:30]
                entry["_links"]=obj.get("_links",{})
                files=obj.get("_embedded",{}).get("stash:files",[])
                if not files:files=obj.get("files",[])
                if isinstance(files,dict):files=files.get("_embedded",{}).get("stash:files",[])
                entry["files"]=[{"id":f.get("id"),"path":f.get("path"),"filename":f.get("filename") or f.get("name"),
                                "size":f.get("size"),"digest":f.get("digest"),"mimeType":f.get("mimeType"),
                                "_links":f.get("_links",{})} for f in files][:50]
                if entry["files"]:result["status"]="ORIGINAL_FILE_LIST_PASS"
                result["attempts"].append(entry)
            else:
                result["attempts"].append({"url":url,"status":status,"type":type(obj).__name__})
        except Exception as ex:
            result["attempts"].append({"url":url,"status":"ERROR",
                                       "http_status":ex.code if isinstance(ex,urllib.error.HTTPError) else None,
                                       "exception":type(ex).__name__,"message":str(ex)[:180]})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2)[:30000])
    if result["status"]!="ORIGINAL_FILE_LIST_PASS":raise SystemExit(2)
if __name__=="__main__":main()
