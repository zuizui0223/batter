#!/usr/bin/env python3
"""Read-only DOI and original Dryad file-listing source gate for Dixon 2023.

Do not open original response rows or upload full data. The original paper
cites Dryad 10.5061/dryad.pzgmsbcr7; verify accession rather than guessing.
"""
import json,urllib.request,urllib.error,os
from pathlib import Path

DOI="10.5061/dryad.pzgmsbcr7"
OUT=Path(os.environ.get("H1_DIXON_DRYAD_GATE","/tmp/h1_dixon2023_original_dryad_source.json"))
URLS=[
 f"https://api.datacite.org/dois/{DOI}",
 f"https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.pzgmsbcr7",
 f"https://datadryad.org/api/v2/datasets/doi:10.5061/dryad.pzgmsbcr7",
 f"https://datadryad.org/dataset/doi%3A10.5061/dryad.pzgmsbcr7",
 f"https://doi.org/{DOI}",
]

def fetch(url):
    q=urllib.request.Request(url,headers={"User-Agent":"BatLearning2023EvidenceAudit/1.0 (+publication DOI 10.1093/beheco/arad001)",
                                      "Accept":"application/json,application/vnd.api+json,text/html,*/*"})
    with urllib.request.urlopen(q,timeout=22) as r:
        return r.status,r.geturl(),r.headers.get("content-type",""),r.read(1200000)

def main():
    out={"study_doi":"10.1093/beheco/arad001","cited_dryad_doi":DOI,
         "status":"SOURCE_UNRESOLVED","original_animal_choices_opened":False,
         "trials_or_bat_ids_claimed_open":False,"attempts":[]}
    for u in URLS:
        try:
            status,final,mime,data=fetch(u)
            record={"url":u,"http_status":status,"effective_url":final,"mime":mime,
                    "bytes_read":len(data)}
            if "json" in mime:
                obj=json.loads(data)
                if "api.datacite.org" in u:
                    a=obj.get("data",{}).get("attributes",{})
                    record["source_summary"]={
                        "id":obj.get("data",{}).get("id"),
                        "doi":a.get("doi"),"publicationYear":a.get("publicationYear"),
                        "titles":[z.get("title","") for z in a.get("titles",[])][:2],
                        "url":a.get("url"),"state":a.get("state")}
                    if (a.get("doi") or "").lower()==DOI.lower():
                        out["doi_resolution"]="DATACITE_METADATA_FOUND"
                else:
                    record["source_summary"]={
                        "id":obj.get("id"),"identifier":obj.get("identifier"),
                        "title":obj.get("title"),"versionNumber":obj.get("versionNumber"),
                        "publicationDate":obj.get("publicationDate"),
                        "_links":obj.get("_links",{})}
                    out["dryad_metadata_found"]=True
                record["result"]="JSON_METADATA"
            elif b"<html" in data[:1000].lower():
                record["result"]="HTML_LANDING_ONLY"
            else:
                record["result"]="UNEXPECTED_MIME"
            out["attempts"].append(record)
        except Exception as e:
            code=e.code if isinstance(e,urllib.error.HTTPError) else None
            out["attempts"].append({"url":u,"status":"ERROR","http_status":code,
                                    "exception":type(e).__name__,"detail":str(e)[:200]})
    if out.get("dryad_metadata_found"):
        out["status"]="DRYAD_METADATA_FOUND_NEEDS_ORIGINAL_ROW_SCHEMA"
    elif out.get("doi_resolution"):
        out["status"]="DATACITE_ONLY_NO_ORIGINAL_ROWS"
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(out,ensure_ascii=False,indent=2))
    if not out.get("doi_resolution") and not out.get("dryad_metadata_found"):
        raise SystemExit(2)

if __name__=="__main__":
    main()
