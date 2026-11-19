#!/usr/bin/env python3
"""Outcome-blind Figshare COMBINE data package integrity & schema gate.

No data rows or distribution values opened; no original ZIP uploaded to artifacts.
"""
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import urllib.request
import zipfile

META=["https://api.figshare.com/v2/articles/13028255/versions/4",
      "https://api.figshare.com/v2/articles/13028255"]
OUT=Path(os.getenv("H1_COMBINE_SOURCE_RECEIPT","/tmp/h1_combine_original_headers.json"))
MAX_BYTES=25_000_000

def req(url):
    request=urllib.request.Request(url,headers={"User-Agent":"Bat-Macro-Source-Audit/1.0","Accept":"application/json,application/zip,*/*"})
    with urllib.request.urlopen(request,timeout=35) as r:
        data=r.read(MAX_BYTES+1)
        return data, r.status, r.headers.get("Content-Type","")

def schema_csv(data, filename):
    # only first 4KB; don't inspect biological observations
    lines=data[:4096].decode("utf8-sig",errors="replace").splitlines()
    hdr=lines[0] if lines else ""
    delim="," if hdr.count(",")>=hdr.count("\t") and hdr.count(",")>=hdr.count(";") else "\t" if hdr.count("\t")>=hdr.count(";") else ";"
    return {"format":"delimited","name":filename,"header_fields":next(csv.reader([hdr],delimiter=delim),[]),
            "nonempty_data_bytes":len(data),"line_count_in_file":data.count(b"\n")}
def describe_zip(data,filename,level=0):
    if level>2:return [{"name":filename,"status":"NESTING_LIMIT"}]
    members=[]
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for member in z.infolist():
            ent={"name":member.filename,"bytes":member.file_size,"compressed_bytes":member.compress_size,
                 "directory":member.is_dir()}
            if member.is_dir():
                members.append(ent);continue
            if member.file_size>70_000_000:
                ent["note"]="TOO_LARGE_SCHEMA_UNOPENED"
            elif member.filename.lower().endswith((".csv",".tsv",".txt")):
                buf=z.read(member)
                ent["schema"]=schema_csv(buf,member.filename)
            elif member.filename.lower().endswith(".zip"):
                buf=z.read(member)
                ent["children"]=describe_zip(buf,member.filename,level+1)
            else:
                ent["schema"]="BINARY_OR_NONCSV_NOT_INSPECTED"
            members.append(ent)
    return members

def main():
    receipt={"source_doi":"10.6084/m9.figshare.13028255.v4",
             "source_paper_doi":"10.1002/ecy.3344",
             "status":"STOP_NO_VERIFIED_SOURCE",
             "data_response_values_opened":False,
             "attempts":[]}
    for url in META:
        try:
            raw,status,content_type=req(url)
            m=json.loads(raw)
            receipt["metadata"]={"article_id":m.get("id"),"version":m.get("version"),"doi":m.get("doi"),
                                 "title":m.get("title"),"license":m.get("license"),
                                 "files":[{k:f.get(k) for k in ("id","name","size","is_link_only","download_url","supplied_md5","computed_md5")} for f in m.get("files",[])]}
            receipt["attempts"].append({"url":url,"status":status,"result":"METADATA_VALID"})
            break
        except Exception as e:
            receipt["attempts"].append({"url":url,"error":type(e).__name__,"detail":str(e)[:180]})
    if "metadata" in receipt:
        receipt["files"]=[]
        for f in receipt["metadata"]["files"]:
            url=f.get("download_url");fname=str(f.get("name",""))
            if not url:
                continue
            try:
                data,status,mime=req(url)
                if len(data)>MAX_BYTES:raise ValueError("source_too_big")
                md5=hashlib.md5(data).hexdigest()
                ent={"name":fname,"status":status,"bytes":len(data),"md5":md5,
                     "figshare_md5":f.get("supplied_md5") or f.get("computed_md5")}
                if ent["figshare_md5"] and md5!=ent["figshare_md5"]:
                    raise ValueError("md5_mismatch_original_source")
                if zipfile.is_zipfile(io.BytesIO(data)):
                    ent["zip_members"]=describe_zip(data,fname)
                elif fname.lower().endswith((".csv",".tsv",".txt")):
                    ent["schema"]=schema_csv(data,fname)
                else:
                    ent["schema"]="NONZIP_BINARY_NOT_OPENED"
                receipt["files"].append(ent)
                receipt["status"]="SOURCE_SCHEMA_PASS"
            except Exception as e:
                receipt["files"].append({"name":fname,"status":"STOP","error":type(e).__name__,"detail":str(e)[:160]})
    receipt.setdefault("files",[])
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    # avoid outputating tens of MB
    print(json.dumps(receipt,indent=2,ensure_ascii=False)[:27000])
    if receipt["status"]!="SOURCE_SCHEMA_PASS":raise SystemExit(2)
if __name__=="__main__":
    main()
