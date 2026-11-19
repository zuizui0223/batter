#!/usr/bin/env python3
"""Original 2018 vampire bat maze source gate: CSV schema and study unit only.

Does not compute animal escape effect. Source DOI 10.1098/rsos.172483;
published supplement 10.6084/m9.figshare.c.4128575.
"""
import csv,hashlib,io,json,os,urllib.request,urllib.error,zipfile
from pathlib import Path

URLS=[
 "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6030285/supplementaryFiles",
 "https://pmc.ncbi.nlm.nih.gov/articles/PMC6030285/bin/rsos172483supp1.csv",
 "https://api.figshare.com/v2/collections/4128575/articles",
 "https://api.figshare.com/v2/articles/12183227",
]
OUT=Path(os.getenv("H1_MAZE_2018_RECEIPT","/tmp/h1_vampire_2018_source_schema.json"))
MAX=3000000

def get(url):
    request=urllib.request.Request(url,headers={"User-Agent":"H1-Vampire-Social-Learning-Source/1.0",
       "Accept":"text/csv,application/json,application/zip,*/*"})
    with urllib.request.urlopen(request,timeout=26) as r:
        return r.read(MAX+1),r.status,r.headers.get("content-type","")

def header(data,name):
    if len(data)>MAX:raise ValueError("source_exceeds_cap")
    if data.startswith(b"\xef\xbb\xbf"):data=data[3:]
    text=data.decode("utf-8",errors="replace")
    if "<html" in text[:128].lower():raise ValueError("html_instead_of_csv")
    reader=csv.reader(io.StringIO(text,newline=""))
    h=next(reader)
    if len(h)==1 and ("\t" in h[0] or ";" in h[0]):
        sep="\t" if "\t" in h[0] else ";"
        reader=csv.reader(io.StringIO(text,newline=""),delimiter=sep)
        h=next(reader)
    n=sum(1 for _ in reader)
    return {"source_member_name":name,"sha256":hashlib.sha256(data).hexdigest(),
            "bytes":len(data),"columns":h,"n_data_records":n,
            "raw_exit_outcomes_inspected":False}

def main():
    receipt={"status":"STOP_UNVERIFIED_2018_SUPPLEMENT",
             "paper_doi":"10.1098/rsos.172483","pubmed_central":"PMC6030285",
             "figshare_collection_doi":"10.6084/m9.figshare.c.4128575",
             "outcome_values_not_read":True,"attempts":[]}
    for u in URLS:
        try:
            data,status,mime=get(u)
            entry={"url":u,"status":status,"bytes":len(data),"mime":mime}
            if data.startswith(b"PK\x03\x04"):
                with zipfile.ZipFile(io.BytesIO(data)) as z:
                    entries=[p for p in z.namelist() if p.lower().endswith((".csv",".tsv",".r",".txt"))]
                    entry["archive_sha256"]=hashlib.sha256(data).hexdigest()
                    entry["members"]=entries[:24]
                    csvs=[p for p in entries if "172483" in p and p.lower().endswith(".csv")]
                    if not csvs:csvs=[p for p in entries if p.lower().endswith(".csv")]
                    if not csvs:raise ValueError("no_original_CSV_in_supplement_ZIP")
                    entry["original_csv_header"]=header(z.read(csvs[0]),csvs[0])
                    receipt["source_original"]=entry
                    receipt["status"]="ORIGINAL_CSV_SCHEMA_PASS"
            elif data[:2] in (b"{\n",b'{"') or "json" in mime:
                parsed=json.loads(data)
                entry["metadata_type"]="list" if isinstance(parsed,list) else "object"
                entry["metadata_record_count"]=len(parsed) if isinstance(parsed,list) else None
                entry["preview_items"]=[{"id":x.get("id"),"title":x.get("title"),"doi":x.get("doi")} for x in parsed[:10]] if isinstance(parsed,list) else {
                    "id":parsed.get("id"),"title":parsed.get("title"),"files":[{"id":x.get("id"),"name":x.get("name"),"size":x.get("size"),"supplied_md5":x.get("supplied_md5")} for x in parsed.get("files",[])]}
            else:
                entry["original_csv_header"]=header(data,u.rsplit("/",1)[-1])
                receipt["source_original"]=entry
                receipt["status"]="ORIGINAL_CSV_SCHEMA_PASS"
            receipt["attempts"].append(entry)
            if receipt["status"]=="ORIGINAL_CSV_SCHEMA_PASS":break
        except Exception as e:
            receipt["attempts"].append({"url":u,"status":"ERROR",
                "http_status":e.code if isinstance(e,urllib.error.HTTPError) else None,
                "exception":type(e).__name__,"message":str(e)[:180]})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(receipt,indent=2,ensure_ascii=False))
    if receipt["status"]!="ORIGINAL_CSV_SCHEMA_PASS":raise SystemExit(2)
if __name__=="__main__":main()
