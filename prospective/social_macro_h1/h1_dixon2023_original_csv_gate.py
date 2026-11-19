#!/usr/bin/env python3
"""Original-byte source quality gate for Dixon 2023 choice data, no outcome values.

Pinned Dryad published version 212971, original paper 10.1093/beheco/arad001.
"""
import csv,hashlib,io,json,os,urllib.request,urllib.error,zipfile
from pathlib import Path
BASE="https://datadryad.org"
VERSION=212971
FILES={
 "first_choices.csv":{"id":2005545,"size":3804,"sha256":"ac9549dc6e8dbbd833aaa5b5f2e84a22b4d544a22c62882ba7f400f31e6bfd6d"},
 "Sensory_visits.csv":{"id":2005546,"size":5578,"sha256":"b9bf1283bbfcb29244f94efd81acc92db5d19d24cfe43187918ad01c778988de"},
 "README.md":{"id":2005547,"size":2076,"sha256":"b1203cccf1c23b8ef879edece5bdac932bb3d3a4bab55d9f97087aa2676359"},
 "Dixon.et.al.Comparative_cue_use_in_bats.Rmd":{"id":2005548,"size":18149,"sha256":"27d1be3e5697ad6950cdc4d9b976dab12ee6e03968c7163fd682e7dd768d5c42"}
}
OUT=Path(os.getenv("H1_DIXON_FILE_GATE","/tmp/h1_dixon2023_original_file_transfer_gate.json"))

def get(url,maxbytes=120000):
    req=urllib.request.Request(url,headers={"User-Agent":"BatCueConflict2023OriginalFileAudit/1.0","Accept":"text/plain,text/csv,application/zip,application/octet-stream,*/*"})
    with urllib.request.urlopen(req,timeout=22) as r:
        buf=r.read(maxbytes+1)
        if len(buf)>maxbytes:raise ValueError("overcap")
        return buf,r.status,r.geturl(),r.headers.get("Content-Type","")

def inspect_csv(buf):
    data=buf.decode("utf-8-sig")
    rd=csv.reader(io.StringIO(data,newline=""))
    fields=next(rd)
    n=sum(1 for _ in rd)
    return {"header_columns":fields,"n_data_rows":n,"outcome_values_opened":False}

def main():
    result={"study_doi":"10.1093/beheco/arad001","dryad_doi":"10.5061/dryad.pzgmsbcr7",
            "pinned_version_id":VERSION,
            "status":"STOP_ORIGINAL_BYTES_UNVERIFIED","original_animal_outcomes_inspected":False,
            "attempts":[]}
    for name,info in FILES.items():
        entry={"file":name,"expected_size":info["size"],"expected_sha256":info["sha256"],"attempts":[]}
        for url in [
          f"{BASE}/api/v2/files/{info['id']}/download",
          f"{BASE}/downloads/file_stream/{info['id']}",
        ]:
            try:
                b,status,final,mime=get(url)
                digest=hashlib.sha256(b).hexdigest()
                a={"url":url,"status":status,"bytes":len(b),"sha256":digest,"mime":mime}
                if digest!=info["sha256"] or len(b)!=info["size"]:
                    a["result"]="INVALID_ORIGINAL_BYTES"
                else:
                    a["result"]="AUTHENTICATED"
                    entry["verified"]=True
                    if name.lower().endswith(".csv"):
                        entry["schema_only"]=inspect_csv(b)
                entry["attempts"].append(a)
                if entry.get("verified"):break
            except Exception as e:
                entry["attempts"].append({"url":url,"status":"STOP",
                    "http_status":e.code if isinstance(e,urllib.error.HTTPError) else None,
                    "exception":type(e).__name__,"detail":str(e)[:160]})
        result["attempts"].append(entry)
    if all(x.get("verified") for x in result["attempts"] if x["file"].endswith(".csv")):
        result["status"]="ORIGINAL_CHOICE_CSVS_SCHEMA_PASS"
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False)[:21000])
    if result["status"]!="ORIGINAL_CHOICE_CSVS_SCHEMA_PASS":raise SystemExit(2)
if __name__=="__main__":main()
