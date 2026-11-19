#!/usr/bin/env python3
"""Original Zenodo dataset acquisition; fails closed on MD5 mismatch.

No original animal observations committed or uploaded; metadata-only receipt.
"""
import hashlib
import json
import os
import urllib.request
from pathlib import Path

URLS=[
  "https://zenodo.org/records/4953622/files/molossusinddiscrim_data_videoanalysis.csv?download=1",
  "https://zenodo.org/api/records/4953622/files/molossusinddiscrim_data_videoanalysis.csv/content",
]
EXPECTED_MD5="b4b9970eac190601b4a291725137c110"
OUT=Path(os.environ.get("H1_MOLOSSUS_SOURCE","/tmp/molossus_inddiscrim_original.csv"))
RECEIPT=Path(os.environ.get("H1_MOLOSSUS_RECEIPT","/tmp/molossus_2020_original_source_receipt.json"))

def main():
    result={"dataset_doi":"10.5061/dryad.tqjq2bvvx",
            "zenodo_record":"4953622","published_source_md5":EXPECTED_MD5,
            "status":"STOP_ORIGINAL_NOT_VERIFIED","attempts":[]}
    for url in URLS:
        try:
            req=urllib.request.Request(url,headers={
                "User-Agent":"BatSocialInfoOriginalSourceAudit/1.0",
                "Accept":"text/csv, text/plain, application/octet-stream, */*"})
            with urllib.request.urlopen(req,timeout=22) as r:
                data=r.read(200000)
                status=r.status
                effective_url=r.geturl()
            digest=hashlib.md5(data).hexdigest()
            attempt={"url":url,"status":status,"bytes":len(data),
                     "effective_url":effective_url,"md5":digest}
            result["attempts"].append(attempt)
            if digest!=EXPECTED_MD5:
                attempt["decision"]="MD5_MISMATCH_NOT_ORIGINAL"
                continue
            if b"Bat ID," not in data[:100] or b"Dishabituation" not in data[:300]:
                attempt["decision"]="SCHEMA_MISMATCH"
                continue
            OUT.parent.mkdir(parents=True,exist_ok=True)
            OUT.write_bytes(data)
            result.update({"status":"ORIGINAL_MD5_PASS","verified_source_url":url,
                           "original_bytes":len(data),"original_md5":digest,
                           "outcome_content_opened":False})
            attempt["decision"]="PASS"
            break
        except Exception as e:
            result["attempts"].append({"url":url,"status":"ERROR",
                                       "exception":type(e).__name__,
                                       "message":str(e)[:160]})
    RECEIPT.parent.mkdir(parents=True,exist_ok=True)
    RECEIPT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    print(json.dumps(result,indent=2))
    if result["status"]!="ORIGINAL_MD5_PASS":
        raise SystemExit(2)

if __name__=="__main__":
    main()
